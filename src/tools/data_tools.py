"""Tool xử lý dữ liệu cho Data Agent (chỉ dùng thư viện chuẩn; repo không cài pandas)."""
import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from src.tools.base_tool import BaseTool, safe_path

_OPS = {
    "sum": lambda xs: round(sum(xs), 2),
    "avg": lambda xs: round(statistics.fmean(xs), 2) if xs else None,
    "count": len,
    "min": lambda xs: min(xs) if xs else None,
    "max": lambda xs: max(xs) if xs else None,
}


class CSVParserTool(BaseTool):
    def __init__(self, base_path, preview_rows: int = 20):
        self.base_path = Path(base_path)
        self.preview_rows = preview_rows
        super().__init__(
            name="parse_csv",
            description="Read a CSV file inside the data folder and return its columns, row count and the first rows.",
            parameters={"type": "object", "properties": {"filename": {"type": "string"}}, "required": ["filename"]},
        )

    def _run(self, input_dict):
        path = safe_path(self.base_path, input_dict["filename"])
        with path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        return {"columns": list(rows[0].keys()) if rows else [], "rows": len(rows), "data": rows[: self.preview_rows]}


class AggregationTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="aggregate",
            description=("Group rows (a list of objects, e.g. the `data` of query_database) by a column and compute "
                         "sum/avg/count/min/max of a numeric column. Rows with a missing metric are skipped."),
            parameters={"type": "object",
                        "properties": {"rows": {"type": "array", "items": {"type": "object"}},
                                       "metric": {"type": "string"},
                                       "op": {"type": "string", "enum": sorted(_OPS)},
                                       "group_by": {"type": "string", "description": "optional"}},
                        "required": ["rows", "metric", "op"]},
        )

    def validate_input(self, input_dict):
        super().validate_input(input_dict)
        if input_dict["op"] not in _OPS:
            raise ValueError(f"op must be one of {sorted(_OPS)}")
        if not isinstance(input_dict["rows"], list):
            raise ValueError("rows must be a list")
        return True

    def _run(self, input_dict):
        groups, skipped = defaultdict(list), 0
        key = input_dict.get("group_by")
        for row in input_dict["rows"]:
            value = row.get(input_dict["metric"])
            try:
                value = float(value)
            except (TypeError, ValueError):
                skipped += 1
                continue
            groups[row.get(key) if key else "all"].append(value)
        op = _OPS[input_dict["op"]]
        return {"result": {str(g): op(xs) for g, xs in groups.items()}, "skipped_rows": skipped}


class DataValidationTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="validate_data",
            description="Check rows for data-quality problems: missing values per column and exact duplicate rows.",
            parameters={"type": "object", "properties": {"rows": {"type": "array", "items": {"type": "object"}}},
                        "required": ["rows"]},
        )

    def _run(self, input_dict):
        rows = input_dict["rows"]
        missing = Counter(k for r in rows for k, v in r.items() if v in (None, "", "NA", "null"))
        dupes = sum(c - 1 for c in Counter(json.dumps(r, sort_keys=True, default=str) for r in rows).values() if c > 1)
        return {"rows": len(rows), "missing_by_column": dict(missing), "duplicate_rows": dupes,
                "clean": not missing and not dupes}
