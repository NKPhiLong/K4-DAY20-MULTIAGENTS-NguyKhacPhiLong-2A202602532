#!/usr/bin/env python3
"""Phần 4.5 - Test tool integration: mỗi worker dùng tool của mình trên dữ liệu thật (gọi tool trực tiếp, 0 token).

    python scripts_mas/test_tool_integration.py
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.system import DEFAULT_DB  # noqa: E402
from src.tools.code_tools import CreateFileTool, PythonREPLTool  # noqa: E402
from src.tools.database_tools import QueryDatabaseTool, create_demo_db  # noqa: E402
from src.tools.evaluation_tools import ScoringTool  # noqa: E402

SVG = '''rows = {rows}
w, h, pad = 420, 220, 30
top = max(v for _, v in rows)
bw = (w - 2 * pad) // len(rows)
bars = "".join(
    f'<rect x="{{pad + i * bw + 5}}" y="{{h - pad - v / top * (h - 2 * pad):.0f}}" width="{{bw - 10}}" '
    f'height="{{v / top * (h - 2 * pad):.0f}}" fill="#4a78c2"/><text x="{{pad + i * bw + 8}}" y="{{h - 10}}" '
    f'font-size="12">{{k}}</text>' for i, (k, v) in enumerate(rows))
open("sales_chart.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{{w}}" height="{{h}}">{{bars}}</svg>')
print("written sales_chart.svg with", len(rows), "bars")
'''


def main() -> int:
    passed = 0
    if not DEFAULT_DB.exists():
        create_demo_db(DEFAULT_DB)
    out_dir = Path(tempfile.mkdtemp(prefix="mas-tools-"))

    print("Test: Data Agent queries database")
    sql = ("SELECT region, ROUND(SUM(amount), 2) AS revenue FROM sales "
           "WHERE order_date >= '2026-07-01' AND order_date < '2026-10-01' GROUP BY region ORDER BY revenue DESC")
    q = QueryDatabaseTool(DEFAULT_DB).invoke({"query": sql})
    print(f'  ├─ SQL: "{sql[:70]}..."\n  └─ Result: {q.get("rows")} rows returned {"✓" if q["status"] == "success" else "✗"}')
    passed += q["status"] == "success" and q["rows"] == 4
    blocked = QueryDatabaseTool(DEFAULT_DB).invoke({"query": "SELECT * FROM sales; DROP TABLE sales"})
    print(f"     (injection blocked: {blocked.get('error')})")

    print("\nTest: Code Agent creates visualization")
    rows = [(r["region"], r["revenue"]) for r in q.get("data", [])]
    CreateFileTool(out_dir).invoke({"filename": "make_chart.py", "content": SVG.format(rows=rows)})
    repl = PythonREPLTool(out_dir).invoke({"code": (out_dir / "make_chart.py").read_text()})
    ok = repl["status"] == "success" and (out_dir / "sales_chart.svg").exists()
    print(f"  ├─ Python code: builds an SVG bar chart (stdlib only)\n  ├─ REPL: {repl['status']} - {repl.get('stdout', '').strip()}")
    print(f"  └─ File created: {out_dir / 'sales_chart.svg'} {'✓' if ok else '✗'}")
    passed += ok

    print("\nTest: Evaluator scores the result")
    summary = "Q3 2026 revenue by region:\n" + "\n".join(f"{k}: {v}" for k, v in rows) + "\nChart: sales_chart.svg"
    s = ScoringTool().invoke({"result": summary, "requirements": ["revenue", "chart", "north", "south"]})
    for k, v in s["scores"].items():
        print(f"  ├─ {k.capitalize()}: {v}/100")
    print(f"  └─ Overall: {s['weighted_score']}/100 ({s['grade']}) {'✓' if s['status'] == 'success' else '✗'}")
    passed += s["status"] == "success"

    print(f"\n{'All tool tests passed!' if passed == 3 else 'Some tool tests failed.'} ({passed}/3)")
    print(json.dumps({"q3_revenue_by_region": dict(rows)}, indent=None))
    return 0 if passed == 3 else 1


if __name__ == "__main__":
    sys.exit(main())
