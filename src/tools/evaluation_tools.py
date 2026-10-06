"""Tool cho Evaluator Agent: chấm điểm, kiểm tra định dạng, so sánh kết quả, sinh báo cáo đánh giá."""
import json
import re
from pathlib import Path

from src.tools.base_tool import BaseTool, safe_path

DEFAULT_CRITERIA = {"accuracy": 30, "completeness": 30, "clarity": 20, "performance": 20}


def score_to_grade(score: float) -> str:
    for threshold, grade in ((90, "A"), (80, "B"), (70, "C"), (60, "D")):
        if score >= threshold:
            return grade
    return "F"


class ScoringTool(BaseTool):
    """Điểm có trọng số 0-100.

    Nếu input có `scores` (điểm từng tiêu chí do LLM đánh giá) thì dùng chúng. Tiêu chí nào thiếu thì dùng heuristic
    kiểm chứng được: completeness = tỉ lệ `requirements` (từ khóa) xuất hiện trong kết quả; accuracy bị trừ nếu
    kết quả chứa dấu hiệu lỗi; clarity theo độ dài và cấu trúc; performance = 100 trừ khi có `seconds` vượt ngân sách.
    """

    def __init__(self):
        super().__init__(
            name="score_result",
            description=("Compute a weighted 0-100 score and a letter grade for a result. Pass your own per-criterion "
                         "scores in `scores` (0-100) when you have judged them; missing criteria use heuristics."),
            parameters={"type": "object",
                        "properties": {"result": {"type": "string"},
                                       "criteria": {"type": "object", "description": "criterion -> weight"},
                                       "scores": {"type": "object", "description": "criterion -> 0..100"},
                                       "requirements": {"type": "array", "items": {"type": "string"}},
                                       "seconds": {"type": "number"},
                                       "time_budget": {"type": "number"}},
                        "required": ["result"]},
        )

    def _heuristic(self, result: str, requirements: list, seconds, budget) -> dict:
        low = result.lower()
        if requirements:
            completeness = 100 * sum(1 for r in requirements if str(r).lower() in low) / len(requirements)
        else:
            completeness = 100 if len(result) > 50 else 50 if result else 0
        accuracy = 40 if re.search(r"\b(error|failed|exception|traceback)\b", low) else (85 if result else 0)
        clarity = 0 if not result else 90 if ("\n" in result and len(result) < 4000) else 70
        performance = 100 if seconds is None or seconds <= budget else max(0, 100 - 10 * (seconds - budget) / budget * 10)
        return {"accuracy": accuracy, "completeness": round(completeness, 1), "clarity": clarity,
                "performance": round(performance, 1)}

    def _run(self, input_dict):
        result = str(input_dict.get("result") or "")
        criteria = input_dict.get("criteria") or DEFAULT_CRITERIA
        given = {k: max(0.0, min(100.0, float(v))) for k, v in (input_dict.get("scores") or {}).items()}
        heur = self._heuristic(result, input_dict.get("requirements") or [], input_dict.get("seconds"),
                               float(input_dict.get("time_budget") or 60))
        scores = {c: given.get(c, heur.get(c, 0)) for c in criteria}
        total_weight = sum(criteria.values()) or 1
        weighted = sum(scores[c] * w for c, w in criteria.items()) / total_weight
        return {"scores": scores, "weighted_score": round(weighted, 2), "grade": score_to_grade(weighted),
                "heuristic_criteria": sorted(c for c in criteria if c not in given)}


class ValidationTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="validate_format",
            description=("Check that content has the expected format: `json` (optionally with required_keys), "
                         "`number`, or `nonempty`."),
            parameters={"type": "object",
                        "properties": {"content": {"type": "string"},
                                       "format": {"type": "string", "enum": ["json", "number", "nonempty"]},
                                       "required_keys": {"type": "array", "items": {"type": "string"}}},
                        "required": ["content", "format"]},
        )

    def _run(self, input_dict):
        content, fmt, issues = input_dict["content"], input_dict["format"], []
        if fmt == "json":
            try:
                obj = json.loads(content) if isinstance(content, str) else content
                missing = [k for k in input_dict.get("required_keys") or [] if not isinstance(obj, dict) or k not in obj]
                issues += [f"missing key: {k}" for k in missing]
            except json.JSONDecodeError as exc:
                issues.append(f"invalid JSON: {exc}")
        elif fmt == "number":
            try:
                float(str(content).replace(",", ""))
            except ValueError:
                issues.append("not a number")
        elif not str(content).strip():
            issues.append("empty content")
        return {"valid": not issues, "issues": issues}


class ComparisonTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="compare_results",
            description=("Compare an actual result with an expected one: numbers with a relative tolerance, "
                         "anything else by normalised string equality."),
            parameters={"type": "object",
                        "properties": {"expected": {}, "actual": {}, "tolerance": {"type": "number"}},
                        "required": ["expected", "actual"]},
        )

    def _run(self, input_dict):
        exp, act = input_dict["expected"], input_dict["actual"]
        tol = float(input_dict.get("tolerance", 0.01))
        try:
            e, a = float(str(exp).replace(",", "")), float(str(act).replace(",", ""))
            diff = abs(a - e) / (abs(e) or 1)
            return {"match": diff <= tol, "relative_diff": round(diff, 6)}
        except ValueError:
            norm = lambda x: " ".join(str(x).lower().split())  # noqa: E731
            return {"match": norm(exp) == norm(act)}


class ReportGeneratorTool(BaseTool):
    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else None
        super().__init__(
            name="generate_report",
            description="Render an evaluation as Markdown (and save it if `filename` is given).",
            parameters={"type": "object",
                        "properties": {"title": {"type": "string"}, "score": {"type": "number"},
                                       "scores": {"type": "object"},
                                       "issues": {"type": "array", "items": {"type": "string"}},
                                       "suggestions": {"type": "array", "items": {"type": "string"}},
                                       "filename": {"type": "string"}},
                        "required": ["title"]},
        )

    def _run(self, input_dict):
        lines = [f"# {input_dict['title']}", ""]
        if input_dict.get("score") is not None:
            s = float(input_dict["score"])
            lines.append(f"**Score:** {s:.1f}/100 ({score_to_grade(s)})")
        for k, v in (input_dict.get("scores") or {}).items():
            lines.append(f"- {k}: {v}")
        for title, key in (("Issues", "issues"), ("Suggestions", "suggestions")):
            if input_dict.get(key):
                lines += ["", f"## {title}", *[f"- {x}" for x in input_dict[key]]]
        md = "\n".join(lines) + "\n"
        out = {"markdown": md}
        if input_dict.get("filename") and self.base_path:
            path = safe_path(self.base_path, input_dict["filename"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(md, encoding="utf-8")
            out["path"] = str(path.relative_to(self.base_path.resolve()))
        return out
