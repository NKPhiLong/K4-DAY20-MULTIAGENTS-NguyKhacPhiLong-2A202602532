"""Evaluator Agent: chấm chất lượng kết quả của Data/Code Agent và đưa phản hồi.

Hai chế độ:
- single_pass=True (mặc định, v2): MỘT lần gọi LLM trả điểm từng tiêu chí (JSON); điểm có trọng số và kiểm tra
  định dạng do tool chạy TẤT ĐỊNH trong code (ScoringTool, ValidationTool) - không tốn thêm vòng LLM.
- single_pass=False (v1): vòng lặp agentic, LLM tự gọi tool. Benchmark v1 cho thấy chế độ này là nút cổ chai
  (11-21 s, 4-10k token mỗi lần đánh giá) vì mỗi vòng gửi lại toàn bộ ngữ cảnh.
"""
import json
import re
import time

from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.base_worker import BaseWorker
from src.logger import log_event
from src.tools.evaluation_tools import (DEFAULT_CRITERIA, ComparisonTool, ReportGeneratorTool, ScoringTool,
                                        ValidationTool)

AGENTIC_PROMPT = (
    "You are a Quality Evaluation Specialist. You receive the user request and the results of other agents.\n"
    "1. Judge each criterion 0-100: accuracy (correctness, numbers backed by evidence such as SQL), "
    "completeness (every part of the request answered), clarity, performance (efficiency).\n"
    "2. Call score_result with your judged `scores` (weights: accuracy 30, completeness 30, clarity 20, "
    "performance 20) to get the weighted score; use validate_format / compare_results when useful.\n"
    "3. Reply with ONLY a JSON object: {\"score\": 0-100, \"feedback\": \"...\", \"issues\": [...], "
    "\"suggestions\": [...]}"
)
SINGLE_PASS_PROMPT = (
    "You are a Quality Evaluation Specialist. You receive the user request and the results of other agents.\n"
    "Judge each criterion from 0 to 100: accuracy (correctness; numbers backed by evidence such as SQL), "
    "completeness (every part of the request answered), clarity, performance (efficiency of the solution).\n"
    "Reply with ONLY a JSON object: {\"scores\": {\"accuracy\": n, \"completeness\": n, \"clarity\": n, "
    "\"performance\": n}, \"feedback\": \"one or two sentences\", \"issues\": [...], \"suggestions\": [...]}"
)


class EvaluatorAgent(BaseWorker):
    result_type = "evaluation"

    def __init__(self, model, output_dir=None, single_pass: bool = True, name: str = "evaluator_agent", **kwargs):
        tools = [ScoringTool(), ValidationTool(), ComparisonTool(), ReportGeneratorTool(output_dir)]
        super().__init__(name, model, tools, **kwargs)
        self.single_pass = single_pass
        self.system_prompt = SINGLE_PASS_PROMPT if single_pass else AGENTIC_PROMPT

    def process(self, task_content, parameters=None):
        if not self.single_pass:
            out = super().process(task_content, parameters)
            if out["status"] == "success":
                out["parsed"] = parse_evaluation(out["result"])
            return out
        return self._process_single_pass(task_content, parameters)

    def _process_single_pass(self, task_content, parameters):
        t0, used = time.perf_counter(), []
        tokens = {"input": 0, "output": 0, "total": 0}
        log_event(self.logger, "task_start", task=task_content[:300], mode="single_pass")
        try:
            if self.model is None:
                raise RuntimeError("no model configured")
            response = self.model.invoke([SystemMessage(content=self.system_prompt),
                                          HumanMessage(content=self._build_prompt(task_content, parameters))])
            tokens = self._track_usage(response)
            text = self._content(response)
            judged = parse_json_object(text, "scores")
            check = self._execute_tool("validate_format", {"content": json.dumps(judged) if judged else text,
                                                           "format": "json", "required_keys": ["scores"]}, used)
            if not check.get("valid"):
                raise ValueError(f"evaluator reply is not valid JSON with scores: {check.get('issues')}")
            scored = self._execute_tool("score_result", {"result": json.dumps(parameters or {}, default=str),
                                                         "criteria": DEFAULT_CRITERIA, "scores": judged["scores"]}, used)
            parsed = {"score": scored["weighted_score"], "grade": scored["grade"], "scores": scored["scores"],
                      "feedback": judged.get("feedback", ""), "issues": judged.get("issues", []),
                      "suggestions": judged.get("suggestions", [])}
            out = {"status": "success", "worker": self.name, "type": self.result_type,
                   "result": json.dumps(parsed, ensure_ascii=False), "parsed": parsed}
        except Exception as exc:  # noqa: BLE001
            out = {"status": "error", "worker": self.name, "type": self.result_type, "result": None,
                   "error": f"{type(exc).__name__}: {exc}"}
        out["metadata"] = {"tools_used": used, "iterations": 1, "tokens": tokens,
                           "seconds": round(time.perf_counter() - t0, 2)}
        log_event(self.logger, "task_end", status=out["status"], error=out.get("error"), **out["metadata"])
        return out


def parse_json_object(text: str, required_key: str) -> dict | None:
    """Lấy object JSON đầu tiên có `required_key` trong câu trả lời (LLM đôi khi bọc trong ```json)."""
    decoder = json.JSONDecoder()
    for m in re.finditer(r"\{", text or ""):
        try:
            obj, _ = decoder.raw_decode(text[m.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and required_key in obj:
            return obj
    return None


def parse_evaluation(text: str) -> dict | None:
    return parse_json_object(text, "score")
