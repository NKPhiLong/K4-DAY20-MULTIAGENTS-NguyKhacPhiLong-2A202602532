"""Lớp cơ sở cho worker agent: vòng lặp agentic (LLM -> tool -> LLM ...) với guardrail số vòng lặp."""
import asyncio
import json
import time

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from src.base_agent import BaseAgent
from src.logger import log_event


class WorkerError(Exception):
    """Worker không hoàn thành được việc (lỗi mô hình, vượt số vòng lặp, ...)."""


class BaseWorker(BaseAgent):
    result_type = "generic"      # "data" | "code" | "evaluation": coordinator dùng để gộp kết quả
    system_prompt = ""

    def __init__(self, name: str, model, tools, max_iterations: int = 6, max_tool_output: int = 6000):
        super().__init__(name, model)
        self.tools = {tool.name: tool for tool in tools}
        self.max_iterations = max_iterations          # guardrail: chặn vòng lặp vô hạn, đốt token
        self.max_tool_output = max_tool_output

    # ------------------------------------------------------------------ đồng bộ
    def process(self, task_content: str, parameters: dict | None = None) -> dict:
        """Xử lý một task. KHÔNG ném lỗi: trả về {"status": "success" | "error", ...}."""
        t0 = time.perf_counter()
        used: list[str] = []                                   # tool đã gọi trong RIÊNG task này
        tokens = {"input": 0, "output": 0, "total": 0}         # token của RIÊNG task này
        log_event(self.logger, "task_start", task=task_content[:300])
        try:
            if self.model is None:
                raise WorkerError("no model configured")
            messages = [SystemMessage(content=self.system_prompt), HumanMessage(content=self._build_prompt(task_content, parameters))]
            llm = self.model.bind_tools([t.to_schema() for t in self.tools.values()]) if self.tools else self.model
            for iteration in range(1, self.max_iterations + 1):
                response = llm.invoke(messages)
                for k, v in self._track_usage(response).items():
                    tokens[k] += v
                messages.append(response)
                if not response.tool_calls:
                    status, content = "success", self._content(response)
                    break
                for tc in response.tool_calls:
                    result = self._execute_tool(tc["name"], tc.get("args") or {}, used)
                    messages.append(ToolMessage(content=self._to_text(result), tool_call_id=tc.get("id") or tc["name"]))
            else:
                status, content = "error", f"max_iterations ({self.max_iterations}) reached without a final answer"
            out = {"status": status, "worker": self.name, "type": self.result_type,
                   "result": content if status == "success" else None}
            if status == "error":
                out["error"] = content
        except Exception as exc:  # noqa: BLE001 - lỗi API, mạng, ...
            out = {"status": "error", "worker": self.name, "type": self.result_type, "result": None,
                   "error": f"{type(exc).__name__}: {exc}"}
            iteration = 0
        out["metadata"] = {"tools_used": used, "iterations": iteration, "tokens": tokens,
                           "seconds": round(time.perf_counter() - t0, 2)}
        log_event(self.logger, "task_end", status=out["status"], error=out.get("error"), **out["metadata"])
        return out

    # ------------------------------------------------------------------ bất đồng bộ
    async def process_async(self, task_content: str, parameters: dict | None = None, timeout: float | None = None) -> dict:
        """Chạy `process` trong thread pool (không chặn event loop) với timeout tùy chọn.

        Lưu ý: khi timeout, thread bên dưới không thể bị hủy cưỡng bức; nó chạy nốt rồi kết quả bị bỏ.
        """
        coro = asyncio.to_thread(self.process, task_content, parameters)
        return await (asyncio.wait_for(coro, timeout) if timeout else coro)

    async def handle_next(self, queue, timeout: float = 30) -> dict:
        """Nhận MỘT thông điệp task từ hộp thư, xử lý, gửi kết quả về `reply_to` (hoặc người gửi), kèm task_id."""
        msg = await queue.receive_message(self.name, timeout=timeout)
        result = await self.process_async(msg["content"], msg.get("parameters"))
        await queue.send_message(self.name, msg.get("reply_to") or msg["from"],
                                 {"type": "result", "task_id": msg.get("task_id"), "result": result})
        return result

    # ------------------------------------------------------------------ tiện ích
    def _build_prompt(self, task_content: str, parameters: dict | None) -> str:
        parts = [f"Task: {task_content}"]
        if parameters:
            parts.append("Parameters / context from other agents:\n" + json.dumps(parameters, ensure_ascii=False, default=str)[:8000])
        parts.append(f"Available tools: {', '.join(self.tools) or 'none'}")
        return "\n\n".join(parts)

    def _execute_tool(self, tool_name: str, tool_input: dict, used: list | None = None) -> dict:
        """Gọi tool; tool không tồn tại -> trả lỗi cho LLM (không ném) để nó tự sửa. Ghi tên tool vào `used`."""
        tool = self.tools.get(tool_name)
        if tool is None:
            return {"status": "error", "error": f"Unknown tool: {tool_name}. Available: {list(self.tools)}"}
        if used is not None:
            used.append(tool_name)
        return tool.invoke(tool_input)

    def _to_text(self, result) -> str:
        return json.dumps(result, ensure_ascii=False, default=str)[: self.max_tool_output]

    @staticmethod
    def _content(response) -> str:
        c = response.content
        if isinstance(c, list):      # một số provider trả danh sách block
            c = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in c)
        return str(c)
