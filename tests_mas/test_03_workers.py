"""Phần 3 - Worker agents (Data, Code, Evaluator) và MessageQueue."""
import asyncio
import json

import pytest
from langchain_core.messages import AIMessage

from conftest import tool_call
from src.agents.code_agent import CodeAgent
from src.agents.data_agent import DataAgent
from src.agents.evaluator_agent import EvaluatorAgent, parse_evaluation
from src.agents.mock_worker import MockWorker
from src.communication.message_queue import MessageQueue, QueueFullError


def test_data_agent_init(demo_db, scripted):
    agent = DataAgent(scripted(), demo_db)
    assert agent.name == "data_agent" and agent.result_type == "data"
    assert set(agent.tools) == {"query_database", "aggregate", "parse_csv", "validate_data"}
    assert "Data Analysis Specialist" in agent.system_prompt
    assert "CREATE TABLE sales" in agent.tools["query_database"].description     # LLM thấy schema


def test_data_agent_process(demo_db, scripted):
    model = scripted(tool_call("query_database", {"query": "SELECT ROUND(SUM(amount),2) AS revenue FROM sales"}),
                     AIMessage(content="Revenue: see tool"))
    out = DataAgent(model, demo_db).process("What is total revenue?", {"year": 2026})
    assert out["status"] == "success" and out["result"] == "Revenue: see tool"
    assert out["metadata"]["tools_used"] == ["query_database"] and out["metadata"]["iterations"] == 2
    assert out["metadata"]["tokens"]["total"] == 240                     # 2 lần gọi x 120 token (mô hình giả)
    assert "Data Analysis Specialist" in model.system_prompts[0] and '"year": 2026' in model.prompts[0]


def test_code_agent_process(tmp_path, scripted):
    model = scripted(tool_call("create_file", {"filename": "hello.py", "content": "print(6 * 7)"}, "1"),
                     tool_call("run_script", {"filename": "hello.py"}, "2"),
                     AIMessage(content="Created hello.py, output 42"))
    agent = CodeAgent(model, tmp_path)
    out = agent.process("Write a script that prints 42")
    assert out["status"] == "success" and (tmp_path / "hello.py").exists()
    assert out["metadata"]["tools_used"] == ["create_file", "run_script"]


def test_evaluator_agent(scripted):
    final = json.dumps({"score": 84, "feedback": "ok", "issues": [], "suggestions": ["add SQL"]})
    model = scripted(tool_call("score_result", {"result": "Revenue 5M", "scores": {"accuracy": 80, "completeness": 90,
                                                                                    "clarity": 80, "performance": 85}}),
                     AIMessage(content=f"```json\n{final}\n```"))
    out = EvaluatorAgent(model).process("Evaluate: Revenue 5M")
    assert out["status"] == "success" and out["parsed"]["score"] == 84
    assert parse_evaluation("no json here") is None


def test_max_iterations_guardrail(demo_db, scripted):
    loop_forever = scripted(tool_call("query_database", {"query": "SELECT 1"}))      # luôn gọi tool, không bao giờ dừng
    out = DataAgent(loop_forever, demo_db, max_iterations=3).process("x")
    assert out["status"] == "error" and "max_iterations" in out["error"] and loop_forever.calls == 3


def test_unknown_tool_and_model_errors_do_not_crash(demo_db, scripted):
    out = DataAgent(scripted(tool_call("rm_rf", {}), AIMessage(content="sorry")), demo_db).process("x")
    assert out["status"] == "success"                                       # lỗi tool được trả lại cho LLM
    assert DataAgent(None, demo_db).process("x")["status"] == "error"


def test_message_queue_send_receive_and_log():
    async def scenario():
        q = MessageQueue()
        for name in ("coordinator", "data_agent"):
            q.register_agent(name)
        mid = await q.send_message("coordinator", "data_agent", {"type": "task", "content": "hi"})
        msg = await q.receive_message("data_agent", timeout=1)
        assert msg["id"] == mid and msg["from"] == "coordinator" and msg["timestamp"]
        with pytest.raises(TimeoutError):
            await q.receive_message("data_agent", timeout=0.05)
        with pytest.raises(ValueError):
            await q.send_message("coordinator", "ghost", {})
        assert len(q.get_message_log("data_agent")) == 1 and q.get_message_log("ghost") == []
    asyncio.run(scenario())


def test_message_queue_full_and_new_event_loop():
    q = MessageQueue(maxsize=1)
    q.register_agent("a")
    asyncio.run(q.send_message("x", "a", {}))
    with pytest.raises(QueueFullError):
        asyncio.run(q.send_message("x", "a", {}))                  # loop mới: hộp thư được tạo lại, vẫn giữ thông điệp
    assert q.queue_size("a") == 1


def test_worker_handle_next_replies_to_sender():
    async def scenario():
        q = MessageQueue()
        w = MockWorker("data_agent", reply="42")
        for name in ("coordinator", "data_agent"):
            q.register_agent(name)
        await q.send_message("coordinator", "data_agent", {"type": "task", "task_id": "t1", "content": "q"})
        await w.handle_next(q, timeout=1)
        reply = await q.receive_message("coordinator", timeout=1)
        assert reply["task_id"] == "t1" and reply["result"]["result"] == "42"
    asyncio.run(scenario())
