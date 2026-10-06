"""MultiAgentSystem: lắp coordinator + 3 worker + message queue, và thu thập số liệu hiệu suất."""
import asyncio
import statistics
from pathlib import Path

from src.agents.code_agent import CodeAgent
from src.agents.data_agent import DataAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.communication.message_queue import MessageQueue
from src.coordinator import Coordinator
from src.tools.database_tools import create_demo_db

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "sales.db"
DEFAULT_OUTPUT = ROOT / "outputs"


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    k = (len(xs) - 1) * p / 100
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return round(xs[lo] + (xs[hi] - xs[lo]) * (k - lo), 3)


class MultiAgentSystem:
    def __init__(self, coordinator: Coordinator | None = None, workers=None, model=None, db_path=None, output_dir=None,
                 auto_evaluate: bool = False, **coordinator_kwargs):
        if coordinator is None:
            if model is None:
                from lab.model import make_model          # cấu hình mô hình từ .env (dùng chung với lab)
                model = make_model()
            if workers is None:
                db_path = Path(db_path or DEFAULT_DB)
                if not db_path.exists():
                    create_demo_db(db_path)
                output_dir = Path(output_dir or DEFAULT_OUTPUT)
                workers = [DataAgent(model, db_path), CodeAgent(model, output_dir), EvaluatorAgent(model, output_dir)]
            coordinator = Coordinator(model, workers, MessageQueue(), **coordinator_kwargs)
        self.coordinator = coordinator
        self.auto_evaluate = auto_evaluate
        self.history: list[dict] = []

    @property
    def message_queue(self) -> MessageQueue:
        return self.coordinator.task_queue

    async def process(self, request, debug: bool = False, evaluate: bool | None = None) -> dict:
        result = await self.coordinator.handle_request(request, evaluate=self.auto_evaluate if evaluate is None else evaluate)
        self.history.append({"request": str(request)[:200], "status": result["status"], "seconds": result.get("seconds", 0),
                             "tokens": (result.get("tokens") or {}).get("total", 0)})
        if debug:
            for step in result.get("trace", []):
                print(f"  [stage {step['stage']}] {step['worker']:16s} {step['status']:8s} "
                      f"{step['seconds']}s tokens={step['tokens']} tools={step['tools_used']}")
        return result

    def process_sync(self, request, **kwargs) -> dict:
        return asyncio.run(self.process(request, **kwargs))

    def active_task_count(self) -> int:
        return len(self.coordinator.active_tasks)

    def metrics(self) -> dict:
        lat = [h["seconds"] for h in self.history]
        n = len(self.history)
        return {"requests": n,
                "latency_p50": percentile(lat, 50), "latency_p99": percentile(lat, 99),
                "latency_avg": round(statistics.fmean(lat), 3) if lat else None,
                "error_rate": round(sum(h["status"] != "success" for h in self.history) / n, 3) if n else None,
                "tokens_total": sum(h["tokens"] for h in self.history),
                "throughput_per_min": round(60 * n / sum(lat), 2) if lat and sum(lat) else None}
