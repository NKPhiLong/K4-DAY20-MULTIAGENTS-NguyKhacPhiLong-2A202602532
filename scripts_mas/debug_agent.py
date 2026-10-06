#!/usr/bin/env python3
"""Phần 5.2 - Chạy MỘT worker độc lập (TỐN TOKEN), để khoanh vùng lỗi.

    python scripts_mas/debug_agent.py --agent data_agent --task "What is the total revenue per region?"
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.system import MultiAgentSystem  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", choices=["data_agent", "code_agent", "evaluator_agent"], required=True)
    ap.add_argument("--task", required=True)
    args = ap.parse_args()
    worker = MultiAgentSystem().coordinator.workers[args.agent]
    out = worker.process(args.task)
    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
