"""Worker giả (không gọi LLM) để test coordinator độc lập: trả lời cố định, có thể chậm hoặc lỗi theo kịch bản."""
import threading
import time

from src.agents.base_worker import BaseWorker


class MockWorker(BaseWorker):
    def __init__(self, name: str, result_type: str = "data", reply: str = "mock result", delay: float = 0.0,
                 fail_times: int = 0, raise_error: bool = False):
        super().__init__(name, model=None, tools=[])
        self.result_type = result_type
        self.reply = reply
        self.delay = delay
        self.fail_times = fail_times          # số lần đầu trả về lỗi (để test retry)
        self.raise_error = raise_error        # ném ngoại lệ thay vì trả dict lỗi
        self.calls = 0
        self.received: list[tuple[str, dict | None]] = []
        self._lock = threading.Lock()

    def process(self, task_content, parameters=None):
        with self._lock:
            self.calls += 1
            call = self.calls
            self.received.append((task_content, parameters))
        time.sleep(self.delay)
        if self.raise_error:
            raise RuntimeError(f"{self.name} crashed")
        meta = {"tools_used": [], "iterations": 1, "tokens": {"input": 10, "output": 5, "total": 15},
                "seconds": self.delay}
        if call <= self.fail_times:
            return {"status": "error", "worker": self.name, "type": self.result_type, "result": None,
                    "error": f"simulated failure {call}", "metadata": meta}
        return {"status": "success", "worker": self.name, "type": self.result_type, "result": self.reply, "metadata": meta}
