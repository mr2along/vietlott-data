from __future__ import annotations

import json
import random
import statistics
from pathlib import Path

import numpy as np

TICKET_PRICE = 10_000
TICKETS_PER_DRAW = 30
RUNS = 1000
BASE_SEED = 20260809


def prize(matches: int, special_hit: bool) -> int:
    if matches == 6:
        return 30_000_000_000
    if matches == 5 and special_hit:
        return 3_000_000_000
    if matches == 5:
        return 40_000_000
    if matches == 4:
        return 500_000
    if matches == 3:
        return 50_000
    return 0


def load_targets() -> list[tuple[set[int], int]]:
    path = Path("artifacts/backtest_v2/power655_benchmark.jsonl")
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(rows) != 1381 or not all(len(r["result"]) == 7 for r in rows):
        raise ValueError("Benchmark must contain exactly 1381 complete 7-number rows")
    return [(set(r["result"][:6]), int(r["result"][6])) for r in rows[1:]]


def pct(values, p: float) -> float:
    return float(np.percentile(np.asarray(values), p))


def main() -> None:
    targets = load_targets()
    cost = len(targets) * TICKETS_PER_DRAW * TICKET_PRICE
    roi_samples: list[float] = []
    gain_samples: list[int] = []
    per_draw_samples: list[list[int]] = []

    for run in range(RUNS):
        rng = random.Random(BASE_SEED + run)
        total_gain = 0
        draw_gains: list[int] = []
        for target, special in targets:
            gain = 0
            for _ in range(TICKETS_PER_DRAW):
                ticket = set(rng.sample(range(1, 56), 6))
                matches = len(ticket & target)
                gain += prize(matches, special in ticket and matches == 5)
            draw_gains.append(gain)
            total_gain += gain
        gain_samples.append(total_gain)
        roi_samples.append((total_gain - cost) / cost * 100.0)
        per_draw_samples.append(draw_gains)

    out = Path("artifacts/backtest_v2")
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "runs": RUNS,
        "draws": len(targets),
        "tickets_per_draw": TICKETS_PER_DRAW,
        "tickets_per_run": len(targets) * TICKETS_PER_DRAW,
        "base_seed": BASE_SEED,
        "cost_vnd": cost,
        "gain_samples_vnd": gain_samples,
        "roi_samples_percent": roi_samples,
        "roi_percent": {
            "p05": pct(roi_samples, 5),
            "p25": pct(roi_samples, 25),
            "median": statistics.median(roi_samples),
            "p75": pct(roi_samples, 75),
            "p95": pct(roi_samples, 95),
            "mean": statistics.mean(roi_samples),
            "min": min(roi_samples),
            "max": max(roi_samples),
        },
        "null": "independent uniform random 6-of-55 tickets under the same 30-ticket/draw budget",
    }
    (out / "random_monte_carlo_raw.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (out / "random_monte_carlo_per_draw.json").write_text(json.dumps(per_draw_samples) + "\n", encoding="utf-8")
    print(json.dumps(report["roi_percent"], indent=2))


if __name__ == "__main__":
    main()
