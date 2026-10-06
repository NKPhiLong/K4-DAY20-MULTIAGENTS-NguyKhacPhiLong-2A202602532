"""Evaluator Agent: chấm chất lượng kết quả của Data/Code Agent và đưa phản hồi."""
import json
import re

from src.agents.base_worker import BaseWorker
from src.tools.evaluation_tools import ComparisonTool, ReportGeneratorTool, ScoringTool, ValidationTool


class EvaluatorAgent(BaseWorker):
    result_type = "evaluation"

    def __init__(self, model, output_dir=None, **kwargs):
        tools = [ScoringTool(), ValidationTool(), ComparisonTool(), ReportGeneratorTool(output_dir)]
        super().__init__("evaluator_agent", model, tools, **kwargs)
        self.system_prompt = (
            "You are a Quality Evaluation Specialist. You receive the user request and the results of other agents.\n"
            "1. Judge each criterion 0-100: accuracy (correctness, numbers backed by evidence such as SQL), "
            "completeness (every part of the request answered), clarity, performance (efficiency).\n"
            "2. Call score_result with your judged `scores` (weights: accuracy 30, completeness 30, clarity 20, "
            "performance 20) to get the weighted score; use validate_format / compare_results when useful.\n"
            "3. Reply with ONLY a JSON object: {\"score\": 0-100, \"feedback\": \"...\", \"issues\": [...], "
            "\"suggestions\": [...]}"
        )

    def process(self, task_content, parameters=None):
        out = super().process(task_content, parameters)
        if out["status"] == "success":
            out["parsed"] = parse_evaluation(out["result"])
        return out


def parse_evaluation(text: str) -> dict | None:
    """Lấy object JSON đầu tiên có khóa `score` trong câu trả lời (LLM đôi khi bọc trong ```json)."""
    decoder = json.JSONDecoder()
    for m in re.finditer(r"\{", text or ""):
        try:
            obj, _ = decoder.raw_decode(text[m.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "score" in obj:
            return obj
    return None
