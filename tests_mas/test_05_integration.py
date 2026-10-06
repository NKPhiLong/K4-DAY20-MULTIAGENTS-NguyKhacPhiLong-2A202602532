"""Phần 5 - Tích hợp và end-to-end (mô hình giả, 0 token): coordinator <-> worker <-> tool, handoff, hiệu suất."""
import asyncio
import json
import time

from langchain_core.messages import AIMessage

from conftest import tool_call
from src.agents.code_agent import CodeAgent
from src.agents.data_agent import DataAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.agents.mock_worker import MockWorker
from src.coordinator import Coordinator
from src.system import MultiAgentSystem, percentile


def build_scripted_system(scripted, demo_db, out_dir):
    data_model = scripted(tool_call("query_database", {"query": "SELECT ROUND(SUM(amount),2) AS q3 FROM sales "
                                                       "WHERE order_date >= '2026-07-01' AND order_date < '2026-10-01'"}),
                          AIMessage(content="Q3 revenue: 777.0"))
    code_model = scripted(tool_call("create_file", {"filename": "chart.svg", "content": "<svg></svg>"}),
                          AIMessage(content="Created chart.svg"))
    eval_model = scripted(AIMessage(content=json.dumps({"scores": {"accuracy": 90, "completeness": 90, "clarity": 80,
                                                                   "performance": 90}, "feedback": "good"})))
    workers = [DataAgent(data_model, demo_db), CodeAgent(code_model, out_dir), EvaluatorAgent(eval_model)]
    return MultiAgentSystem(coordinator=Coordinator(None, workers)), (data_model, code_model, eval_model)


def test_coordinator_with_real_workers_and_tools(scripted, demo_db, tmp_path):
    system, (data_model, code_model, _) = build_scripted_system(scripted, demo_db, tmp_path)
    result = asyncio.run(system.process("Calculate Q3 revenue and create a chart"))
    assert result["status"] == "success"
    assert result["data"] == "Q3 revenue: 777.0" and result["code"] == "Created chart.svg"
    assert (tmp_path / "chart.svg").exists()
    assert [s["worker"] for s in result["trace"]] == ["data_agent", "code_agent"]
    assert "Q3 revenue: 777.0" in code_model.prompts[0]        # handoff: code agent nhận kết quả của data agent


def test_full_pipeline_with_evaluation(scripted, demo_db, tmp_path):
    system, _ = build_scripted_system(scripted, demo_db, tmp_path)
    result = asyncio.run(system.process("What was Q3 revenue? Create a visualization and evaluate the result."))
    assert result["status"] == "success" and result["evaluation"]["score"] == 88.0     # 27+27+16+18
    assert [s["stage"] for s in result["trace"]] == [0, 1, 2]
    assert result["tokens"]["total"] == 5 * 120                  # 2 + 2 + 1 lần gọi mô hình giả
    assert result["parsed"]["parameters"]["quarter"] == 3


def test_partial_result_when_one_worker_fails():
    workers = [MockWorker("data_agent", reply="5M"), MockWorker("code_agent", "code", raise_error=True)]
    system = MultiAgentSystem(coordinator=Coordinator(None, workers, max_retries=0))
    result = system.process_sync("Analyze revenue and create a chart")
    assert result["status"] == "partial" and result["data"] == "5M" and result["errors"][0]["worker"] == "code_agent"


def test_latency_with_mock_workers():
    workers = [MockWorker("data_agent", delay=0.05), MockWorker("code_agent", "code", delay=0.05)]
    system = MultiAgentSystem(coordinator=Coordinator(None, workers))
    t0 = time.perf_counter()
    result = system.process_sync("Analyze sales and create report")
    assert result["status"] == "success" and time.perf_counter() - t0 < 2      # overhead của coordinator nhỏ


def test_concurrent_requests():
    workers = [MockWorker("data_agent", delay=0.05)]
    system = MultiAgentSystem(coordinator=Coordinator(None, workers))

    async def burst():
        return await asyncio.gather(*(system.process(f"Total revenue of task {i}") for i in range(10)))
    results = asyncio.run(burst())
    assert sum(r["status"] == "success" for r in results) >= 8
    m = system.metrics()
    assert m["requests"] == 10 and m["error_rate"] <= 0.2 and m["latency_p50"] is not None


def test_percentile():
    assert percentile([1, 2, 3, 4], 50) == 2.5 and percentile([5], 99) == 5 and percentile([], 50) is None


def test_handoff_is_truncated(scripted, demo_db, tmp_path):
    long_answer = "x" * 5000
    workers = [MockWorker("data_agent", reply=long_answer), MockWorker("code_agent", "code")]
    system = MultiAgentSystem(coordinator=Coordinator(None, workers))
    system.process_sync("Analyze revenue and create a chart")
    handed = workers[1].received[0][1]["previous_results"]["data_agent"]
    assert len(handed) < 1600 and handed.endswith("[truncated]")


def test_default_system_builds_demo_db_and_workers(scripted, tmp_path):
    system = MultiAgentSystem(model=scripted(AIMessage(content="done")), db_path=tmp_path / "db" / "sales.db",
                              output_dir=tmp_path / "out", auto_evaluate=True, timeout=5)
    assert (tmp_path / "db" / "sales.db").exists() and system.coordinator.timeout == 5
    assert set(system.coordinator.workers) == {"data_agent", "code_agent", "evaluator_agent"}
    assert system.message_queue is system.coordinator.task_queue and system.active_task_count() == 0
    assert system.metrics()["requests"] == 0 and system.metrics()["latency_p50"] is None
