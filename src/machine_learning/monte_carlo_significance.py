from __future__ import annotations

import json
import math
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
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if len(rows) != 1381 or not all(len(r["result"]) == 7 for r in rows):
        raise ValueError("Benchmark must contain exactly 1381 complete 7-number rows")
    return [(set(r["result"][:6]), int(r["result"][6])) for r in rows[1:]]


def percentile(values: list[float], p: float) -> float:
    return float(np.percentile(np.asarray(values), p))


def main() -> None:
    targets = load_targets()
    cost = len(targets) * TICKETS_PER_DRAW * TICKET_PRICE
    roi_samples: list[float] = []
    gain_samples: list[int] = []
    per_draw_samples: list[list[int]] = []

    for run in range(RUNS):
        rng = random.Random(BASE_SEED + run)
        run_gain = 0
        draw_gains: list[int] = []
        for target, special in targets:
            draw_gain = 0
            for _ in range(TICKETS_PER_DRAW):
                ticket = set(rng.sample(range(1, 56), 6))
                matches = len(ticket & target)
                draw_gain += prize(matches, matches == 5 and special in ticket)
            draw_gains.append(draw_gain)
            run_gain += draw_gain
        gain_samples.append(run_gain)
        roi_samples.append((run_gain - cost) / cost * 100.0)
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
        "roi_samples_percent": roi_samples,
        "gain_samples_vnd": gain_samples,
        "roi_percent": {
            "p05": percentile(roi_samples, 5),
            "p25": percentile(roi_samples, 25),
            "median": statistics.median(roi_samples),
            "p75": percentile(roi_samples, 75),
            "p95": percentile(roi_samples, 95),
            "mean": statistics.mean(roi_samples),
            "min": min(roi_samples),
            "max": max(roi_samples),
        },
    }
    (out / "random_monte_carlo_raw.json").write_text(json.dumps(report) + "\n", encoding="utf-8")
    (out / "random_monte_carlo_per_draw.json").write_text(json.dumps(per_draw_samples) + "\n", encoding="utf-8")

    summary = json.loads((out / "backtest_summary.json").read_text())
    results = {}
    rng = np.random.default_rng(BASE_SEED)
    for row in summary:
        name = row["strategy"]
        observed = float(row["roi_pct"])
        # One-sided empirical p-value: probability that random achieves >= observed ROI.
        ge = sum(x >= observed for x in roi_samples)
        p_value = (ge + 1) / (RUNS + 1)
        q = percentile(roi_samples, 100 * (1 - p_value))
        results[name] = {
            "observed_roi_percent": observed,
            "difference_vs_random_median_percent": observed - statistics.median(roi_samples),
            "random_percentile_rank": percentile_rank(roi_samples, observed),
            "empirical_p_value_one_sided": p_value,
            "random_threshold_at_same_percentile": q,
        }

    # Bootstrap the observed strategy ROI itself from its per-draw gains.
    # This measures uncertainty across historical draws, not prediction certainty.
    details_path = out / "backtest_per_draw.json"
    if details_path.exists():
        details = json.loads(details_path.read_text())
        for name, item in results.items():
            gains = np.asarray(details[name]["draw_gains_vnd"], dtype=float)
            if len(gains):
                boot = np.empty(5000)
                for i in range(len(boot)):
                    idx = rng.integers(0, len(gains), len(gains))
                    boot[i] = (gains[idx].sum() - len(gains) * TICKETS_PER_DRAW * TICKET_PRICE) / (len(gains) * TICKETS_PER_DRAW * TICKET_PRICE) * 100
                item["bootstrap_roi_ci_95_percent"] = [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]

    significance = {
        "method": "one-sided empirical Monte Carlo test against 1000 Random runs",
        "null": "strategy has no better ROI than Random under the same ticket budget",
        "random_runs": RUNS,
        "results": results,
        "note": "Lottery draws remain random; statistical significance in historical backtests does not establish future predictive power.",
    }
    (out / "strategy_significance.json").write_text(json.dumps(significance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(significance, indent=2))


def percentile_rank(values: list[float], x: float) -> float:
    return float(np.mean(np.asarray(values) <= x) * 100.0)


if __name__ == "__main__":
    main()
