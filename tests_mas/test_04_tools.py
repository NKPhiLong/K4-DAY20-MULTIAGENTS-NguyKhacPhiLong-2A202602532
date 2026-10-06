"""Phần 4 - Tools: validate input, an toàn (SQL, sandbox, path traversal), kết quả đúng."""
import sqlite3

from src.tools.code_tools import CreateFileTool, EditFileTool, PythonREPLTool, RunScriptTool
from src.tools.data_tools import AggregationTool, CSVParserTool, DataValidationTool
from src.tools.database_tools import QueryDatabaseTool
from src.tools.evaluation_tools import ComparisonTool, ReportGeneratorTool, ScoringTool, ValidationTool


def test_query_database_tool(demo_db):
    tool = QueryDatabaseTool(demo_db)
    expected = sqlite3.connect(demo_db).execute("SELECT ROUND(SUM(amount),2) FROM sales WHERE region='North'").fetchone()[0]
    r = tool.invoke({"query": "SELECT ROUND(SUM(amount),2) AS rev FROM sales WHERE region='North';"})
    assert r["status"] == "success" and r["data"][0]["rev"] == expected and r["columns"] == ["rev"]
    assert tool.invoke({"query": "SELECT * FROM sales", "limit": 5})["rows"] == 5
    for bad in ("DROP TABLE sales", "SELECT 1; DROP TABLE sales", "DELETE FROM sales", "UPDATE sales SET amount=0",
                "PRAGMA table_info(sales)", ""):
        assert tool.invoke({"query": bad})["status"] == "error", bad
    assert tool.invoke({})["status"] == "error"
    assert sqlite3.connect(demo_db).execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 200   # dữ liệu còn nguyên
    assert tool.validate_input({"query": "SELECT updated_at FROM t"})      # \b: tên cột không bị chặn nhầm


def test_python_repl_tool(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "super-secret-key-123")
    tool = PythonREPLTool(tmp_path, timeout=3)
    r = tool.invoke({"code": "import json\nprint(json.dumps({'x': sum(range(10))}))"})
    assert r["status"] == "success" and '{"x": 45}' in r["stdout"]
    assert "not allowed" in tool.invoke({"code": "import os\nprint(os.environ)"})["error"]
    assert "not allowed" in tool.invoke({"code": "__import__('subprocess')"})["error"]
    leak = tool.invoke({"code": "import sys\nprint(open('/proc/self/environ').read() if sys.platform=='linux' else '')"})
    assert "super-secret-key-123" not in str(leak)                         # tiến trình con không nhận khóa API
    assert "timeout" in tool.invoke({"code": "while True: pass"})["error"]
    assert tool.invoke({"code": "1/0"})["status"] == "error"


def test_create_file_tool(tmp_path):
    tool = CreateFileTool(tmp_path / "out")
    r = tool.invoke({"filename": "reports/a.md", "content": "# hi"})
    assert r["status"] == "success" and (tmp_path / "out" / "reports" / "a.md").read_text() == "# hi"
    for bad in ("../evil.txt", "/etc/passwd", "a/../../evil"):
        assert tool.invoke({"filename": bad, "content": "x"})["status"] == "error", bad
    assert not (tmp_path / "evil.txt").exists()


def test_edit_and_run_script_tools(tmp_path):
    CreateFileTool(tmp_path).invoke({"filename": "s.py", "content": "import sys\nprint('n=' + sys.argv[1])"})
    assert EditFileTool(tmp_path).invoke({"filename": "s.py", "old": "n=", "new": "arg="})["status"] == "success"
    r = RunScriptTool(tmp_path).invoke({"filename": "s.py", "args": ["7"]})
    assert r["status"] == "success" and r["stdout"].strip() == "arg=7"
    CreateFileTool(tmp_path).invoke({"filename": "bad.py", "content": "import subprocess"})
    assert RunScriptTool(tmp_path).invoke({"filename": "bad.py"})["status"] == "error"
    assert RunScriptTool(tmp_path).invoke({"filename": "missing.py"})["status"] == "error"


def test_scoring_tool():
    tool = ScoringTool()
    r = tool.invoke({"result": "x", "scores": {"accuracy": 100, "completeness": 80, "clarity": 50, "performance": 100}})
    assert r["weighted_score"] == 84.0 and r["grade"] == "B" and r["heuristic_criteria"] == []
    h = tool.invoke({"result": "Q3 revenue: 5M\nchart saved", "requirements": ["revenue", "chart", "forecast"]})
    assert h["scores"]["completeness"] == 66.7 and set(h["heuristic_criteria"]) == {"accuracy", "completeness",
                                                                                       "clarity", "performance"}
    assert tool.invoke({"result": ""})["grade"] == "F"


def test_validation_comparison_and_report_tools(tmp_path):
    v = ValidationTool()
    assert v.invoke({"content": '{"a": 1}', "format": "json", "required_keys": ["a"]})["valid"]
    assert v.invoke({"content": '{"a": 1}', "format": "json", "required_keys": ["b"]})["issues"] == ["missing key: b"]
    assert not v.invoke({"content": "abc", "format": "number"})["valid"]
    c = ComparisonTool()
    assert c.invoke({"expected": "1,000", "actual": 1005, "tolerance": 0.01})["match"]
    assert not c.invoke({"expected": "North", "actual": "south"})["match"]
    r = ReportGeneratorTool(tmp_path).invoke({"title": "Eval", "score": 91, "issues": ["none"], "filename": "eval.md"})
    assert "(A)" in r["markdown"] and (tmp_path / "eval.md").exists()


def test_data_tools(tmp_path):
    rows = [{"region": "N", "amount": 10}, {"region": "N", "amount": 5}, {"region": "S", "amount": None},
            {"region": "S", "amount": 2}, {"region": "S", "amount": 2}]
    agg = AggregationTool().invoke({"rows": rows, "metric": "amount", "op": "sum", "group_by": "region"})
    assert agg["result"] == {"N": 15, "S": 4} and agg["skipped_rows"] == 1
    assert AggregationTool().invoke({"rows": rows, "metric": "amount", "op": "median"})["status"] == "error"
    dq = DataValidationTool().invoke({"rows": rows})
    assert dq["missing_by_column"] == {"amount": 1} and dq["duplicate_rows"] == 1 and not dq["clean"]
    (tmp_path / "x.csv").write_text("a,b\n1,2\n3,4\n")
    csv = CSVParserTool(tmp_path).invoke({"filename": "x.csv"})
    assert csv["columns"] == ["a", "b"] and csv["rows"] == 2
    assert CSVParserTool(tmp_path).invoke({"filename": "../x.csv"})["status"] == "error"
