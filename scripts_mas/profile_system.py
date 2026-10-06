#!/usr/bin/env python3
"""Phần 5.3 - Profile hệ thống bằng cProfile.

    python scripts_mas/profile_system.py            # mock worker, 0 token: đo overhead của chính hệ thống
    python scripts_mas/profile_system.py --real > results/multiagent/profile_real.txt   # mô hình thật (TỐN TOKEN)
"""
import asyncio
import cProfile
import io
import pstats
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agents.mock_worker import MockWorker  # noqa: E402
from src.coordinator import Coordinator  # noqa: E402
from src.system import MultiAgentSystem  # noqa: E402

REQUESTS = ["What is total revenue?", "Analyze sales and create a chart", "Total revenue per region in Q3",
            "Write a Python script that summarises sales", "Analyze revenue, create a report and evaluate it"]


def build(real: bool) -> MultiAgentSystem:
    if real:
        return MultiAgentSystem()
    workers = [MockWorker("data_agent", delay=0.01), MockWorker("code_agent", "code", delay=0.01),
               MockWorker("evaluator_agent", "evaluation", reply='{"score": 80}', delay=0.01)]
    return MultiAgentSystem(coordinator=Coordinator(None, workers))


async def run_system(system: MultiAgentSystem, n: int) -> None:
    for i in range(n):
        await system.process(REQUESTS[i % len(REQUESTS)])


def main() -> None:
    real = "--real" in sys.argv
    system = build(real)
    profiler = cProfile.Profile()
    profiler.enable()
    asyncio.run(run_system(system, 5 if real else 50))
    profiler.disable()
    buf = io.StringIO()
    pstats.Stats(profiler, stream=buf).sort_stats("cumulative").print_stats(20)
    print(buf.getvalue())
    print("metrics:", system.metrics())


if __name__ == "__main__":
    main()
