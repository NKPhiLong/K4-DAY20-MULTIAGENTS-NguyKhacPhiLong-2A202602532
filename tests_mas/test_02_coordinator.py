"""Phần 2 - Coordinator: parse, route, execute (timeout/retry/fallback), aggregate, xử lý lỗi."""
import asyncio

import pytest
from langchain_core.messages import AIMessage

from src.agents.mock_worker import MockWorker
from src.communication.message_queue import MessageQueue
from src.coordinator import Coordinator, InvalidRequestError, ResourceExhaustedError


def make_coordinator(**kwargs):
    workers = kwargs.pop("workers", None) or [MockWorker("data_agent", "data", "Total: 5M USD"),
                                              MockWorker("code_agent", "code", "chart.svg created"),
                                              MockWorker("evaluator_agent", "evaluation", '{"score": 90}')]
    return Coordinator(model=kwargs.pop("model", None), worker_agents=workers, **kwargs), workers


def test_coordinator_init():
    queue = MessageQueue()
    coord, workers = make_coordinator(message_queue=queue)
    assert set(coord.workers) == {"data_agent", "code_agent", "evaluator_agent"}
    assert coord.task_queue is queue and {"coordinator", "data_agent"} <= set(queue.queues)
    assert coord.active_tasks == {}


def test_parse_request():
    coord, _ = make_coordinator()
    p = coord.parse_request("Analyze sales data for Q3 2026 in the North region")
    assert p["task_type"] == "data_analysis" and p["parameters"] == {"quarter": 3, "year": 2026, "regions": ["North"]}
    assert p["priority"] == "normal" and p["source"] == "rule"
    p = coord.parse_request("Tính tổng doanh thu Q3 và tạo biểu đồ, gấp")
    assert p["task_type"] == "complex" and p["task_types"] == ["data_analysis", "code_generation"]
    assert p["priority"] == "high"
    assert coord.parse_request("Write a Python script to read a CSV file")["task_type"] == "code_generation"
    assert coord.parse_request("Analyze sales data for Q3 2026 in the North region")["source"] == "cache"


def test_parse_request_uses_llm_only_when_rules_do_not_match(scripted):
    model = scripted(AIMessage(content='{"task_types": ["code_generation"]}'))
    coord, _ = make_coordinator(model=model)
    assert coord.parse_request("Hello there, do the thing")["task_type"] == "code_generation"
    coord.parse_request("What is total revenue?")
    assert model.calls == 1                               # câu thứ hai khớp luật -> không tốn token


def test_route_task():
    coord, _ = make_coordinator()
    assert coord.route_task("data_analysis") == ["data_agent"]
    assert coord.route_task("code_generation") == ["code_agent"]
    assert coord.route_task("evaluation") == ["evaluator_agent"]
    assert coord.route_task("complex") == ["data_agent", "code_agent"]
    assert coord.route_task("complex", "analyze revenue and evaluate quality") == ["data_agent", "evaluator_agent"]
    assert coord.route_task("unknown") == ["data_agent"]


def test_execute_tasks_runs_workers_in_parallel_via_queue():
    workers = [MockWorker("data_agent", "data", delay=0.3), MockWorker("code_agent", "code", delay=0.3)]
    coord, _ = make_coordinator(workers=workers)
    tasks = coord.build_tasks(["data_agent", "code_agent"], "req", {})
    loop_time = asyncio.new_event_loop()
    t0 = loop_time.time()
    results = loop_time.run_until_complete(coord.execute_tasks(tasks))
    elapsed = loop_time.time() - t0
    loop_time.close()
    assert [r["status"] for r in results] == ["success", "success"]
    assert [r["task_id"] for r in results] == [t["id"] for t in tasks]
    assert elapsed < 0.55                                  # song song: ~0.3s chứ không phải 0.6s
    log = coord.task_queue.get_message_log()
    assert [m["type"] for m in log].count("task") == 2 and [m["type"] for m in log].count("result") == 2


def test_aggregate_results():
    coord, _ = make_coordinator()
    agg = coord.aggregate_results([
        {"status": "success", "type": "data", "worker": "data_agent", "result": "Total: 5M",
         "metadata": {"tokens": {"input": 1, "output": 2, "total": 3}, "seconds": 1.0}},
        {"status": "success", "type": "code", "worker": "code_agent", "result": "chart.svg",
         "metadata": {"tokens": {"input": 1, "output": 1, "total": 2}}},
        {"status": "success", "type": "evaluation", "worker": "evaluator_agent", "result": "...", "parsed": {"score": 88}},
    ])
    assert agg["status"] == "success" and agg["data"] == "Total: 5M" and agg["code"] == "chart.svg"
    assert agg["evaluation"] == {"score": 88} and agg["tokens"]["total"] == 5 and agg["timestamp"]
    partial = coord.aggregate_results([{"status": "success", "type": "data", "result": "x"},
                                       {"status": "timeout", "type": "code", "worker": "code_agent", "error": "slow"}])
    assert partial["status"] == "partial" and partial["errors"][0]["status"] == "timeout"
    assert coord.aggregate_results([])["status"] == "error"


def test_worker_timeout_is_reported_not_raised():
    coord, _ = make_coordinator(workers=[MockWorker("data_agent", delay=1.0)], max_retries=0)
    tasks = coord.build_tasks(["data_agent"], "slow", {})
    [r] = asyncio.run(coord.execute_tasks(tasks, timeout=0.2))
    assert r["status"] == "timeout" and coord.active_tasks == {}


def test_worker_error_is_retried():
    flaky = MockWorker("data_agent", fail_times=1)
    coord, _ = make_coordinator(workers=[flaky], max_retries=2)
    [r] = asyncio.run(coord.execute_tasks_with_retry(coord.build_tasks(["data_agent"], "x", {})))
    assert r["status"] == "success" and r["attempts"] == 2 and flaky.calls == 2


def test_worker_exception_falls_back_to_other_worker():
    broken = MockWorker("data_agent", raise_error=True)
    backup = MockWorker("code_agent", "code", reply="computed by code agent")
    coord, _ = make_coordinator(workers=[broken, backup], max_retries=1, fallbacks={"data_agent": ["code_agent"]})
    [r] = asyncio.run(coord.execute_tasks_with_retry(coord.build_tasks(["data_agent"], "x", {})))
    assert r["status"] == "success" and r["fallback_from"] == "data_agent" and broken.calls == 2


def test_invalid_input_and_resource_exhaustion():
    coord, _ = make_coordinator(max_tasks=1)
    for bad in ("", "   ", None, 42, "x" * 6000):
        with pytest.raises(InvalidRequestError):
            coord.parse_request(bad)
    assert asyncio.run(coord.handle_request(""))["status"] == "error"
    with pytest.raises(ResourceExhaustedError):
        asyncio.run(coord.execute_tasks(coord.build_tasks(["data_agent", "code_agent"], "x", {})))
