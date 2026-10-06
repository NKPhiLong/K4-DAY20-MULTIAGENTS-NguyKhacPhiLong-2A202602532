#!/usr/bin/env python3
"""Phần 2.4 - Test coordinator độc lập với mock worker (0 token).

    python scripts_mas/test_coordinator_standalone.py
"""
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agents.mock_worker import MockWorker  # noqa: E402
from src.coordinator import Coordinator  # noqa: E402


async def main() -> int:
    passed = 0
    print("Testing Coordinator with mock workers...\n")

    # Test 1: một worker
    coord = Coordinator(None, [MockWorker("data_agent", reply="[mock data returned]", delay=0.2),
                               MockWorker("code_agent", "code", reply="[mock code returned]", delay=0.2)])
    print('Test 1: Simple task\n  Input: "Analyze sales data"')
    parsed = coord.parse_request("Analyze sales data")
    r = await coord.handle_request("Analyze sales data")
    print(f"  Parsed: task_type={parsed['task_type']}\n  Routed to: {', '.join(s['worker'] for s in r['trace'])}")
    print(f"  Result: {r['data']}")
    ok = r["status"] == "success" and parsed["task_type"] == "data_analysis"
    passed += ok
    print("  ✓ Pass\n" if ok else "  ✗ Fail\n")

    # Test 2: nhiều worker song song (cùng một giai đoạn) qua message queue
    print('Test 2: Multiple tasks\n  Input: "Analyze AND create report" (2 workers in parallel)')
    t0 = time.perf_counter()
    results = await coord.execute_tasks(coord.build_tasks(["data_agent", "code_agent"], "Analyze AND create report", {}))
    dt = time.perf_counter() - t0
    print(f"  Routed to: {', '.join(x['worker'] for x in results)}\n  Results: both returned in {dt:.2f}s "
          f"(sequential would be ~0.40s)")
    ok = all(x["status"] == "success" for x in results) and dt < 0.38
    passed += ok
    print("  ✓ Pass\n" if ok else "  ✗ Fail\n")

    # Test 3: timeout -> retry -> fallback
    print('Test 3: Timeout handling\n  Input: "Long task" (data_agent hangs 3s, timeout 0.5s)')
    coord = Coordinator(None, [MockWorker("data_agent", delay=3.0), MockWorker("code_agent", "code", reply="fallback ok")],
                        timeout=0.5, max_retries=1, fallbacks={"data_agent": ["code_agent"]})
    [res] = await coord.execute_tasks_with_retry(coord.build_tasks(["data_agent"], "Long task", {}))
    print(f"  Timeout after {coord.timeout}s (x{1 + coord.max_retries} attempts)")
    print(f"  Fallback triggered: {res.get('fallback_from')} -> {res['worker']} ({res['status']})")
    ok = res["status"] == "success" and res.get("fallback_from") == "data_agent"
    passed += ok
    print("  ✓ Pass\n" if ok else "  ✗ Fail\n")

    print(f"{'All coordinator tests passed!' if passed == 3 else 'Some tests failed.'} ({passed}/3)")
    return 0 if passed == 3 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
