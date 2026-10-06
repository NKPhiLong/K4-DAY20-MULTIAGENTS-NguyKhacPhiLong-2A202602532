#!/usr/bin/env python3
"""Phần 5.2 - Debug MỘT request với log đầy đủ ra console (TỐN TOKEN: gọi mô hình thật trong .env).

    python scripts_mas/debug_system.py "Analyze Q3 sales and create report"
Log JSON nằm ở logs/coordinator.log, logs/communication.log, logs/<worker>.log  (xem: cat logs/communication.log | jq .)
"""
import asyncio
import json
import os
import sys
import traceback
from pathlib import Path

os.environ.setdefault("MAS_DEBUG", "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import logging  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
for noisy in ("httpx", "openai", "httpcore"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

from src.system import MultiAgentSystem  # noqa: E402


async def debug_request(request: str, evaluate: bool) -> None:
    system = MultiAgentSystem()
    print(f"🔍 Debugging: {request}\n" + "-" * 50)
    try:
        result = await system.process(request, debug=True, evaluate=evaluate)
        print(f"\n{'✅' if result['status'] == 'success' else '⚠️'} Status: {result['status']}  "
              f"({result['seconds']}s, {result['tokens']['total']} tokens)")
        print(f"Parsed: {result['parsed']}")
        print(f"Data: {str(result.get('data'))[:600]}")
        print(f"Code: {str(result.get('code'))[:600]}")
        print(f"Evaluation: {json.dumps(result.get('evaluation'), ensure_ascii=False)[:600]}")
        if result["errors"]:
            print(f"Errors: {result['errors']}")
    except Exception as e:  # noqa: BLE001
        print(f"\n❌ Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--evaluate"]
    asyncio.run(debug_request(args[0] if args else "Analyze Q3 sales and create report", "--evaluate" in sys.argv))
