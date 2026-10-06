"""Coordinator (supervisor/router): nhận yêu cầu, phân tích, định tuyến tới worker, chờ kết quả, gộp kết quả.

Luồng của `handle_request`:
    parse_request -> route_task -> chia giai đoạn (data -> code -> evaluator) -> execute_tasks_with_retry
    (mỗi giai đoạn chạy song song qua MessageQueue; kết quả giai đoạn trước được "handoff" sang giai đoạn sau
    qua shared state) -> aggregate_results.
Guardrail: timeout mỗi task, số lần retry, worker dự phòng (fallback), giới hạn số task, giới hạn số vòng lặp
của worker (trong BaseWorker).
"""
import asyncio
import json
import re
import time
import uuid
from datetime import datetime, timezone

from src.base_agent import AgentError, BaseAgent
from src.communication.message_queue import MessageQueue
from src.logger import log_event


class CoordinatorException(AgentError):
    pass


class InvalidRequestError(CoordinatorException):
    pass


class ResourceExhaustedError(CoordinatorException):
    pass


TASK_TYPES = ("data_analysis", "code_generation", "evaluation")
KEYWORDS = {
    "data_analysis": ("revenue", "sales", "doanh thu", "doanh số", "query", "sql", "analy", "phân tích", "total",
                      "tổng", "average", "trung bình", "how many", "bao nhiêu", "region", "khu vực", "data",
                      "dữ liệu", "quarter", "quý", "top "),
    "code_generation": ("script", "code", "chart", "biểu đồ", "plot", "visuali", "graph", "report", "báo cáo",
                        "python", "function", "program", "create file", "tạo file", "csv", "svg"),
    "evaluation": ("evaluat", "đánh giá", "score", "chấm điểm", "review", "quality", "chất lượng", "validate",
                   "kiểm tra"),
}
URGENT = ("urgent", "asap", "immediately", "gấp", "khẩn")
ROUTING_MAP = {
    "data_analysis": ["data_agent"],
    "code_generation": ["code_agent"],
    "evaluation": ["evaluator_agent"],
    "complex": ["data_agent", "code_agent"],
}
WORKER_TYPE = {"data_agent": "data_analysis", "code_agent": "code_generation", "evaluator_agent": "evaluation"}
STAGE = {"data_agent": 0, "code_agent": 1, "evaluator_agent": 2}     # thứ tự handoff
ROLE_HINT = {
    "data_agent": "Your part: answer the data / analysis questions of this request with exact figures.",
    "code_agent": ("Your part: write and run the code or create the files this request asks for, using the "
                   "previous results in the parameters as input data."),
    "evaluator_agent": "Your part: evaluate how well the previous results answer the user request.",
}
MAX_REQUEST_CHARS = 5000
MAX_HANDOFF_CHARS = 1500      # v2: chỉ bàn giao phần đầu kết quả của giai đoạn trước (giảm input token)


class Coordinator(BaseAgent):
    def __init__(self, model=None, worker_agents=(), message_queue=None, timeout: float = 120, max_retries: int = 1,
                 max_tasks: int = 10, fallbacks: dict | None = None, use_llm_parser: bool = True):
        super().__init__("coordinator", model)
        self.workers = {agent.name: agent for agent in worker_agents}
        self.task_queue = message_queue or MessageQueue()
        self.task_queue.register_agent(self.name)
        for name in self.workers:
            self.task_queue.register_agent(name)
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_tasks = max_tasks
        self.fallbacks = fallbacks or {}              # {"data_agent": ["code_agent"]} - worker dự phòng
        self.use_llm_parser = use_llm_parser
        self.active_tasks: dict[str, dict] = {}
        self.routing_cache: dict[str, dict] = {}

    # ------------------------------------------------------------------ 1. phân tích yêu cầu
    def parse_request(self, user_input) -> dict:
        """Trích loại task, tham số, độ ưu tiên. Luật từ khóa trước (nhanh, 0 token); chỉ gọi LLM khi không khớp."""
        if isinstance(user_input, dict):
            user_input = user_input.get("request") or user_input.get("content")
        if not isinstance(user_input, str) or not user_input.strip():
            raise InvalidRequestError("request must be a non-empty string")
        if len(user_input) > MAX_REQUEST_CHARS:
            raise InvalidRequestError(f"request longer than {MAX_REQUEST_CHARS} characters")
        key = " ".join(user_input.lower().split())
        if key in self.routing_cache:
            return {**self.routing_cache[key], "source": "cache", "llm_tokens": {"input": 0, "output": 0, "total": 0}}

        types = self._detect_types(key)
        source, llm_tokens = "rule", {"input": 0, "output": 0, "total": 0}
        if not types and self.model is not None and self.use_llm_parser:
            (types, llm_tokens), source = self._llm_types(user_input), "llm"
        if not types:
            types, source = ["data_analysis"], "default"
        parsed = {
            "task_type": types[0] if len(types) == 1 else "complex",
            "task_types": types,
            "parameters": self._extract_parameters(user_input),
            "priority": "high" if any(w in key for w in URGENT) else "normal",
            "source": source,
            "llm_tokens": llm_tokens,
        }
        self.routing_cache[key] = parsed
        log_event(self.logger, "parse_request", request=user_input[:200], **parsed)
        return parsed

    @staticmethod
    def _detect_types(text: str) -> list[str]:
        return [t for t in TASK_TYPES if any(k in text for k in KEYWORDS[t])]

    @staticmethod
    def _extract_parameters(text: str) -> dict:
        params = {}
        if m := re.search(r"\bq([1-4])\b|quý\s*([1-4])", text, re.I):
            params["quarter"] = int(m.group(1) or m.group(2))
        if m := re.search(r"\b(20\d\d)\b", text):
            params["year"] = int(m.group(1))
        regions = [r for r in ("North", "South", "East", "West") if re.search(rf"\b{r}\b", text, re.I)]
        if regions:
            params["regions"] = regions
        return params

    def _llm_types(self, user_input: str) -> tuple[list[str], dict]:
        prompt = ("Classify this user request for a multi-agent system. Possible task types: data_analysis "
                  "(questions answered from a sales database), code_generation (write/run code, create files or "
                  "charts), evaluation (judge the quality of a result). Reply with ONLY JSON like "
                  '{"task_types": ["data_analysis"]}.\n\nUser request: ' + user_input)
        try:
            response = self.model.invoke(prompt)
            usage = self._track_usage(response)
            m = re.search(r"\{.*\}", str(response.content), re.S)
            types = json.loads(m.group(0)).get("task_types", []) if m else []
            return [t for t in TASK_TYPES if t in types], usage
        except Exception as exc:  # noqa: BLE001 - parser lỗi thì dùng mặc định
            log_event(self.logger, "llm_parse_failed", error=str(exc))
            return [], {"input": 0, "output": 0, "total": 0}

    # ------------------------------------------------------------------ 2. định tuyến
    def route_task(self, task_type: str, content: str | None = None) -> list[str]:
        """Worker nào xử lý loại task này. `complex`: suy ra từ nội dung nếu có, mặc định data + code."""
        if task_type == "complex" and content:
            types = self._detect_types(" ".join(content.lower().split()))
            if len(types) > 1:
                return [w for t in types for w in ROUTING_MAP[t]]
        return list(ROUTING_MAP.get(task_type, ["data_agent"]))

    def build_tasks(self, workers: list[str], user_input: str, parameters: dict, previous: dict | None = None) -> list[dict]:
        tasks = []
        for w in workers:
            params = dict(parameters)
            if previous:
                params["previous_results"] = {k: (v if not isinstance(v, str) or len(v) <= MAX_HANDOFF_CHARS
                                                  else v[:MAX_HANDOFF_CHARS] + " ...[truncated]")
                                              for k, v in previous.items()}
            tasks.append({"id": f"{w}-{uuid.uuid4().hex[:8]}", "worker": w, "parameters": params,
                          "content": f"User request: {user_input}\n{ROLE_HINT.get(w, '')}"})
        return tasks

    # ------------------------------------------------------------------ 3. thực thi
    async def execute_tasks(self, tasks: list[dict], timeout: float | None = None) -> list[dict]:
        """Gửi task qua MessageQueue, các worker chạy SONG SONG, chờ kết quả (qua hộp thư reply_to) với timeout.

        Không ném lỗi của worker: timeout/ngoại lệ được trả về dạng {"status": "timeout" | "error", ...}.
        """
        timeout = timeout or self.timeout
        if len(tasks) > self.max_tasks:
            raise ResourceExhaustedError(f"{len(tasks)} tasks > max_tasks={self.max_tasks}")

        async def run_one(task):
            worker = self.workers.get(task["worker"])
            if worker is None:
                return {"status": "error", "error": f"unknown worker: {task['worker']}"}
            reply_box = f"{self.name}/{task['id']}"           # hộp thư trả lời riêng của task này
            self.task_queue.register_agent(reply_box)
            self.active_tasks[task["id"]] = {"worker": worker.name, "started": time.time()}
            log_event(self.logger, "task_sent", task_id=task["id"], worker=worker.name)

            async def send_and_wait():
                await self.task_queue.send_message(self.name, worker.name, {
                    "type": "task", "task_id": task["id"], "reply_to": reply_box, "content": task["content"],
                    "parameters": task.get("parameters", {})})
                await worker.handle_next(self.task_queue, timeout=timeout)   # worker nhận 1 task từ hộp thư của nó
                return (await self.task_queue.receive_message(reply_box, timeout=timeout))["result"]

            try:
                return await asyncio.wait_for(send_and_wait(), timeout)
            except TimeoutError:
                self.task_queue.discard(worker.name, task["id"])         # bỏ task chưa được nhận, nếu còn
                log_event(self.logger, "task_timeout", task_id=task["id"], worker=worker.name, timeout=timeout)
                return {"status": "timeout", "error": f"no result within {timeout}s"}
            except Exception as exc:  # noqa: BLE001
                return {"status": "error", "error": f"{type(exc).__name__}: {exc}"}
            finally:
                self.active_tasks.pop(task["id"], None)
                self.task_queue.unregister_agent(reply_box)

        outcomes = await asyncio.gather(*(run_one(t) for t in tasks))
        results = []
        for task, outcome in zip(tasks, outcomes):
            r = {"type": self.workers[task["worker"]].result_type if task["worker"] in self.workers else "unknown",
                 **outcome, "task_id": task["id"], "worker": task["worker"]}
            log_event(self.logger, "task_done", task_id=task["id"], worker=task["worker"], status=r["status"],
                      seconds=(r.get("metadata") or {}).get("seconds"))
            results.append(r)
        return results

    async def execute_tasks_with_retry(self, tasks: list[dict], max_retries: int | None = None,
                                       timeout: float | None = None) -> list[dict]:
        """execute_tasks + thử lại các task lỗi/timeout + chuyển sang worker dự phòng (fallback) nếu vẫn lỗi."""
        max_retries = self.max_retries if max_retries is None else max_retries
        results = await self.execute_tasks(tasks, timeout)
        by_id = {t["id"]: t for t in tasks}
        for attempt in range(1, max_retries + 1):
            failed = [r for r in results if r["status"] != "success"]
            if not failed:
                break
            log_event(self.logger, "retry", attempt=attempt, max_retries=max_retries, tasks=[r["task_id"] for r in failed])
            redo = await self.execute_tasks([by_id[r["task_id"]] for r in failed], timeout)
            redo = {r["task_id"]: {**r, "attempts": attempt + 1} for r in redo}
            results = [redo.get(r["task_id"], r) for r in results]
        for i, r in enumerate(results):
            if r["status"] == "success":
                continue
            for alt in self.fallbacks.get(r["worker"], []):
                if alt not in self.workers:
                    continue
                log_event(self.logger, "fallback", task_id=r["task_id"], from_worker=r["worker"], to_worker=alt)
                task = {**by_id[r["task_id"]], "worker": alt}
                alt_r = (await self.execute_tasks([task], timeout))[0]
                if alt_r["status"] == "success":
                    results[i] = {**alt_r, "fallback_from": r["worker"]}
                    break
        return results

    # ------------------------------------------------------------------ 4. gộp kết quả
    def aggregate_results(self, results: list[dict]) -> dict:
        aggregated = {"status": "success", "data": None, "code": None, "evaluation": None, "errors": [],
                      "workers": [], "tokens": {"input": 0, "output": 0, "total": 0},
                      "timestamp": datetime.now(timezone.utc).isoformat()}
        ok = 0
        for r in results:
            aggregated["workers"].append({"worker": r.get("worker"), "status": r["status"],
                                          "seconds": (r.get("metadata") or {}).get("seconds")})
            for k, v in ((r.get("metadata") or {}).get("tokens") or {}).items():
                aggregated["tokens"][k] += v
            if r["status"] != "success":
                aggregated["errors"].append({"worker": r.get("worker"), "status": r["status"], "error": r.get("error")})
                continue
            ok += 1
            slot = {"data": "data", "code": "code", "evaluation": "evaluation"}.get(r.get("type"))
            if slot is None:
                continue
            value = r.get("parsed") or r.get("result") if slot == "evaluation" else r.get("result")
            prev = aggregated[slot]
            aggregated[slot] = value if prev is None else f"{prev}\n\n{value}"
        if results and ok == 0:
            aggregated["status"] = "error"
        elif ok < len(results):
            aggregated["status"] = "partial"
        elif not results:
            aggregated["status"] = "error"
            aggregated["errors"].append({"error": "no task was executed"})
        return aggregated

    # ------------------------------------------------------------------ toàn bộ luồng
    async def handle_request(self, user_input, evaluate: bool = False) -> dict:
        t0 = time.perf_counter()
        try:
            parsed = self.parse_request(user_input)
        except InvalidRequestError as exc:
            return {"status": "error", "errors": [{"error": str(exc)}], "data": None, "code": None,
                    "evaluation": None, "trace": [], "seconds": 0.0}
        text = user_input if isinstance(user_input, str) else str(user_input.get("request") or user_input.get("content"))
        workers = [w for t in parsed["task_types"] for w in ROUTING_MAP[t]]
        if evaluate and "evaluator_agent" not in workers:
            workers.append("evaluator_agent")
        workers = list(dict.fromkeys(workers))
        if len(workers) > self.max_tasks:
            raise ResourceExhaustedError(f"{len(workers)} tasks > max_tasks={self.max_tasks}")

        all_results, trace, shared = [], [], {}
        for stage in sorted({STAGE.get(w, 0) for w in workers}):
            stage_workers = [w for w in workers if STAGE.get(w, 0) == stage]
            tasks = self.build_tasks(stage_workers, text, parsed["parameters"], previous=dict(shared) or None)
            results = await self.execute_tasks_with_retry(tasks)
            for r in results:
                trace.append({"stage": stage, "worker": r["worker"], "status": r["status"],
                              "seconds": (r.get("metadata") or {}).get("seconds"),
                              "tokens": ((r.get("metadata") or {}).get("tokens") or {}).get("total"),
                              "tools_used": (r.get("metadata") or {}).get("tools_used")})
                if r["status"] == "success":
                    shared[r["worker"]] = r.get("result")          # handoff: ghi vào "hồ sơ" chung
            all_results += results

        out = self.aggregate_results(all_results)
        for k in out["tokens"]:
            out["tokens"][k] += parsed["llm_tokens"][k]               # token của chính coordinator (LLM parser)
        out.update({"request": text, "parsed": parsed, "trace": trace, "seconds": round(time.perf_counter() - t0, 2)})
        log_event(self.logger, "request_done", status=out["status"], seconds=out["seconds"],
                  tokens=out["tokens"]["total"], workers=[t["worker"] for t in trace])
        return out
