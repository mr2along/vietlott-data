from __future__ import annotations

import json
import math
import random
import statistics
from pathlib import Path

TICKET_PRICE = 10_000
DRAWS = 1380
TICKETS_PER_DRAW = 30
RUNS = 1000
BASE_SEED = 20260809


def prize(matches: int, special: bool) -> int:
    if matches == 6:
        return 30_000_000_000
    if matches == 5 and special:
        return 3_000_000_000
    if matches == 5:
        return 40_000_000
    if matches == 4:
        return 500_000
    if matches == 3:
        return 50_000
    return 0


def percentile(values: list[float], p: float) -> float:
    xs = sorted(values)
    if not xs:
        return float("nan")
    pos = (len(xs) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return xs[lo]
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def main() -> None:
    path = Path("artifacts/backtest_v2/power655_benchmark.jsonl")
    rows = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    assert len(rows) == 1381
    targets = [(set(r["result"][:6]), r["result"][6]) for r in rows[1:]]

    rois = []
    gains = []
    costs = []
    for run in range(RUNS):
        rng = random.Random(BASE_SEED + run)
        gain = 0
        for target, special in targets:
            for _ in range(TICKETS_PER_DRAW):
                ticket = set(rng.sample(range(1, 56), 6))
                matches = len(ticket & target)
                gain += prize(matches, matches == 5 and special in ticket)
        cost = len(targets) * TICKETS_PER_DRAW * TICKET_PRICE
        rois.append((gain - cost) / cost * 100)
        gains.append(gain)
        costs.append(cost)

    report = {
        "runs": RUNS,
        "draws": len(targets),
        "tickets_per_draw": TICKETS_PER_DRAW,
        "tickets_per_run": len(targets) * TICKETS_PER_DRAW,
        "base_seed": BASE_SEED,
        "roi_percent": {
            "p05": percentile(rois, .05),
            "p25": percentile(rois, .25),
            "median": statistics.median(rois),
            "p75": percentile(rois, .75),
            "p95": percentile(rois, .95),
            "mean": statistics.mean(rois),
            "min": min(rois),
            "max": max(rois),
        },
        "gain_vnd": {
            "p05": percentile(gains, .05),
            "median": statistics.median(gains),
            "p95": percentile(gains, .95),
            "mean": statistics.mean(gains),
        },
        "cost_vnd": costs[0],
    }
    out = Path("artifacts/backtest_v2/random_monte_carlo.json")
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
