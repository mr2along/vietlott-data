from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


def percentile_rank(values: np.ndarray, x: float) -> float:
    return float(np.mean(values <= x) * 100.0)


def bootstrap_mean_diff(a: np.ndarray, b: np.ndarray, rng: np.random.Generator, n: int = 5000) -> tuple[float, float]:
    if len(a) != len(b):
        raise ValueError("paired samples must have equal length")
    diffs = np.empty(n)
    m = len(a)
    for i in range(n):
        idx = rng.integers(0, m, size=m)
        diffs[i] = np.mean(a[idx] - b[idx])
    return float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))


def main() -> None:
    root = Path("artifacts/backtest_v2")
    summary_path = root / "backtest_summary.json"
    mc_path = root / "random_monte_carlo.json"
    if not summary_path.exists():
        raise FileNotFoundError(summary_path)
    if not mc_path.exists():
        raise FileNotFoundError(mc_path)

    summary = json.loads(summary_path.read_text())
    mc = json.loads(mc_path.read_text())
    # Monte Carlo stores summary quantiles, not the raw 1000 observations.
    # Use the stored distribution bounds only for an initial screening rank.
    median = float(mc["roi_percent"]["median"])
    p05 = float(mc["roi_percent"]["p05"])
    p95 = float(mc["roi_percent"]["p95"])

    results = {}
    for row in summary:
        name = row["name"]
        roi = float(row["roi_percent"])
        results[name] = {
            "roi_percent": roi,
            "difference_vs_random_median": roi - median,
            "inside_random_p05_p95": p05 <= roi <= p95,
            "screening_conclusion": "not_better_than_random" if roi <= p95 else "above_random_p95",
        }

    report = {
        "method": "Monte Carlo percentile screening",
        "random_median_roi_percent": median,
        "random_p05_roi_percent": p05,
        "random_p95_roi_percent": p95,
        "strategies": results,
        "warning": "This is a screening result only. Exact empirical p-values require raw Monte Carlo ROI samples and paired per-draw strategy results.",
    }
    (root / "strategy_significance.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
