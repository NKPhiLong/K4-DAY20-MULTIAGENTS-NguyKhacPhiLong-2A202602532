#!/usr/bin/env python3
"""Phần 5.4 - Benchmark với mô hình thật (TỐN TOKEN): mỗi kịch bản chạy `--iterations` lần.

    python scripts_mas/benchmark.py --iterations 3 --rounds 3 --concurrency 10   # -> benchmark_results.json
Đo: độ trễ (min/max/avg/median/p50/p99), token, tỉ lệ thành công, điểm của Evaluator; và kiểm chứng câu trả lời
của Data Agent với giá trị tính trực tiếp bằng SQL (ground truth) để chấm accuracy khách quan.
"""
import argparse
import asyncio
import json
import re
import sqlite3
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.system import DEFAULT_DB, MultiAgentSystem, percentile  # noqa: E402
from src.tools.database_tools import create_demo_db  # noqa: E402

TEST_CASES = [
    ("Simple data query", "What is the total revenue in 2026?",
     "SELECT ROUND(SUM(amount), 2) FROM sales", False),
    ("Code generation", "Write a Python script that reads a CSV file and prints the number of rows, then run it on a "
     "small sample CSV you create.", None, False),
    ("Complex workflow", "Analyze Q3 2026 revenue by region, create an SVG bar chart of it and evaluate the result.",
     "SELECT ROUND(SUM(amount), 2) FROM sales WHERE order_date >= '2026-07-01' AND order_date < '2026-10-01'", True),
]


def numbers_in(text) -> list[float]:
    return [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*\.?\d*", str(text or ""))]


def answer_correct(text, truth: float | None, tol: float = 0.005) -> bool | None:
    """True nếu câu trả lời chứa con số khớp ground truth (sai số tương đối 0.5%), hoặc tổng các con số theo vùng khớp."""
    if truth is None:
        return None
    nums = numbers_in(text)
    if any(abs(n - truth) / truth <= tol for n in nums):
        return True
    big = [n for n in nums if n >= truth * 0.05]
    return any(abs(sum(big[i:i + 4]) - truth) / truth <= tol for i in range(len(big)))


class Benchmark:
    def __init__(self):
        self.results = []

    async def run_test(self, name, request, system, iterations=3, truth=None, evaluate=False):
        print(f"\n📊 Benchmarking: {name}")
        runs = []
        for i in range(iterations):
            start = time.perf_counter()
            result = await system.process(request, evaluate=evaluate)
            latency = time.perf_counter() - start
            ok = answer_correct(result.get("data"), truth)
            ev = result.get("evaluation")
            runs.append({"latency": round(latency, 2), "status": result["status"], "tokens": result["tokens"]["total"],
                         "correct": ok, "eval_score": ev.get("score") if isinstance(ev, dict) else None,
                         "workers": [(s["worker"], s["status"], s["seconds"], s["tokens"]) for s in result["trace"]],
                         "errors": result["errors"]})
            mark = "✓" if result["status"] == "success" else "✗"
            print(f"  Iteration {i + 1}: {latency:.2f}s {mark} tokens={result['tokens']['total']}"
                  + (f" correct={ok}" if ok is not None else "") + (f" eval={runs[-1]['eval_score']}" if evaluate else ""))
        lat = [r["latency"] for r in runs]
        stats = {"name": name, "request": request, "iterations": iterations,
                 "min": min(lat), "max": max(lat), "avg": round(statistics.fmean(lat), 2),
                 "median": round(statistics.median(lat), 2), "p99": percentile(lat, 99),
                 "success_rate": sum(r["status"] == "success" for r in runs) / iterations,
                 "avg_tokens": round(statistics.fmean(r["tokens"] for r in runs)),
                 "accuracy": (sum(bool(r["correct"]) for r in runs) / iterations) if truth is not None else None,
                 "ground_truth": truth, "runs": runs}
        self.results.append(stats)
        print(f"  Summary: min {stats['min']:.2f}s | max {stats['max']:.2f}s | avg {stats['avg']:.2f}s | "
              f"median {stats['median']:.2f}s | tokens {stats['avg_tokens']}")
        return stats


async def concurrency_test(system, n: int) -> dict:
    """Gửi n truy vấn đơn ĐỒNG THỜI để đo thông lượng (coordinator xử lý song song qua MessageQueue)."""
    print(f"\n🚀 Concurrency: {n} simple requests at once")
    t0 = time.perf_counter()
    regions = (["North", "South", "East", "West"] * (n // 4 + 1))[:n]
    results = await asyncio.gather(*(system.process(f"What is the total revenue of region {r} in 2026?")
                                     for r in regions))
    wall = time.perf_counter() - t0
    lat = [r["seconds"] for r in results]
    out = {"requests": n, "wall_seconds": round(wall, 2), "requests_per_min": round(60 * n / wall, 2),
           "success": sum(r["status"] == "success" for r in results), "latency_p50": percentile(lat, 50),
           "latency_p99": percentile(lat, 99), "avg_tokens": round(statistics.fmean(r["tokens"]["total"] for r in results))}
    print(f"  {out}")
    return out


async def main(iterations: int, rounds: int, concurrency: int, out: Path) -> None:
    if not DEFAULT_DB.exists():
        create_demo_db(DEFAULT_DB)
    con = sqlite3.connect(DEFAULT_DB)
    system = MultiAgentSystem()
    round_summaries, by_case = [], {}
    t0 = time.perf_counter()
    for rnd in range(1, rounds + 1):
        print(f"\n========== Round {rnd}/{rounds} ==========")
        bench = Benchmark()
        for name, request, truth_sql, evaluate in TEST_CASES:
            truth = con.execute(truth_sql).fetchone()[0] if truth_sql else None
            stats = await bench.run_test(name, request, system, iterations, truth, evaluate)
            by_case.setdefault(name, {"name": name, "request": request, "ground_truth": truth, "runs": []})
            by_case[name]["runs"] += [{**r, "round": rnd} for r in stats["runs"]]
        lat = [r["latency"] for s in bench.results for r in s["runs"]]
        round_summaries.append({"round": rnd, "latency_p50": percentile(lat, 50), "latency_p99": percentile(lat, 99),
                                "avg_latency": round(statistics.fmean(lat), 2),
                                "tokens": sum(r["tokens"] for s in bench.results for r in s["runs"]),
                                "success": sum(r["status"] == "success" for s in bench.results for r in s["runs"]),
                                "requests": len(lat)})
    sequential_wall = time.perf_counter() - t0
    cases = []
    for c in by_case.values():
        lat = [r["latency"] for r in c["runs"]]
        cases.append({**c, "n": len(lat), "min": min(lat), "max": max(lat), "avg": round(statistics.fmean(lat), 2),
                      "median": round(statistics.median(lat), 2), "p99": percentile(lat, 99),
                      "stdev": round(statistics.stdev(lat), 2) if len(lat) > 1 else 0.0,
                      "success_rate": sum(r["status"] == "success" for r in c["runs"]) / len(lat),
                      "avg_tokens": round(statistics.fmean(r["tokens"] for r in c["runs"])),
                      "accuracy": (sum(bool(r["correct"]) for r in c["runs"]) / len(lat)) if c["ground_truth"] is not None else None,
                      "avg_eval_score": (round(statistics.fmean(r["eval_score"] for r in c["runs"] if r["eval_score"] is not None), 1)
                                         if any(r["eval_score"] is not None for r in c["runs"]) else None)})
    all_lat = [r["latency"] for c in cases for r in c["runs"]]
    overall = {"requests": len(all_lat), "latency_p50": percentile(all_lat, 50), "latency_p99": percentile(all_lat, 99),
               "latency_avg": round(statistics.fmean(all_lat), 2),
               "error_rate": round(sum(r["status"] != "success" for c in cases for r in c["runs"]) / len(all_lat), 4),
               "tokens_total": sum(r["tokens"] for c in cases for r in c["runs"]),
               "tokens_per_request": round(statistics.fmean(r["tokens"] for c in cases for r in c["runs"])),
               "sequential_requests_per_min": round(60 * len(all_lat) / sequential_wall, 2)}
    conc = await concurrency_test(system, concurrency) if concurrency else None
    import os
    payload = {"timestamp": datetime.now(timezone.utc).isoformat(), "model": os.getenv("LAB_MODEL"),
               "version": "v2 (single-pass evaluator, SVG chart tool, truncated handoff)",
               "overall": overall, "rounds": round_summaries, "concurrency": conc, "cases": cases}
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nOverall: {json.dumps(overall)}\nRounds: {json.dumps(round_summaries)}\n"
          f"✅ Benchmark complete. Results saved to {out.name}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--iterations", type=int, default=3)
    ap.add_argument("--rounds", type=int, default=1, help="repeat the whole suite (to measure run-to-run noise)")
    ap.add_argument("--concurrency", type=int, default=0, help="also send N simple requests at once")
    ap.add_argument("--out", default=str(ROOT / "benchmark_results.json"))
    a = ap.parse_args()
    asyncio.run(main(a.iterations, a.rounds, a.concurrency, Path(a.out)))
