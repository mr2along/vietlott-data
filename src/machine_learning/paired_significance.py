from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, n: int = 5000) -> list[float]:
    m = len(values)
    means = np.empty(n)
    for i in range(n):
        means[i] = np.mean(values[rng.integers(0, m, size=m)])
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def main() -> None:
    root = Path("artifacts/backtest_v2")
    backtest = json.loads((root / "backtest_per_draw.json").read_text())
    mc = np.asarray(json.loads((root / "random_monte_carlo_per_draw.json").read_text()), dtype=float)

    if mc.ndim != 2 or mc.shape[0] < 1000:
        raise ValueError(f"Expected 1000+ Monte Carlo runs, got {mc.shape}")

    results = {}
    for strategy, payload in backtest.items():
        observed = np.asarray(payload["draw_gains_vnd"], dtype=float)
        costs = np.asarray(payload["draw_costs_vnd"], dtype=float)
        if observed.shape[0] != mc.shape[1]:
            raise ValueError(f"Draw count mismatch for {strategy}: {observed.shape[0]} vs {mc.shape[1]}")
        if costs.shape != observed.shape or np.any(costs <= 0):
            raise ValueError(f"Invalid per-draw costs for {strategy}: {costs.shape}")

        observed_total = float(observed.sum())
        cost = float(costs.sum())
        random_totals = mc.sum(axis=1)
        observed_minus_random = observed_total - random_totals

        # One-sided Monte Carlo test of H1: strategy gain > random gain.
        # The +1 correction avoids a zero p-value with a finite simulation count.
        p_value = float((np.sum(observed_minus_random <= 0) + 1) / (len(observed_minus_random) + 1))

        # Compare the observed strategy ROI against every random ROI using the same total cost.
        diff_roi = observed_minus_random / cost * 100.0
        rng = np.random.default_rng(20260809)
        ci = bootstrap_ci(observed, rng)
        results[strategy] = {
            "observed_gain_vnd": observed_total,
            "observed_cost_vnd": cost,
            "observed_roi_percent": float(observed_total / cost * 100.0),
            "random_mean_gain_vnd": float(random_totals.mean()),
            "mean_gain_difference_vnd": float(observed_minus_random.mean()),
            "median_gain_difference_vnd": float(np.median(observed_minus_random)),
            "paired_roi_difference_percent_mean": float(diff_roi.mean()),
            "paired_roi_difference_percent_median": float(np.median(diff_roi)),
            "empirical_p_value_one_sided": p_value,
            "bootstrap_observed_gain_ci_95_vnd": ci,
            "random_gain_p05_vnd": float(np.percentile(random_totals, 5)),
            "random_gain_median_vnd": float(np.median(random_totals)),
            "random_gain_p95_vnd": float(np.percentile(random_totals, 95)),
            "conclusion_at_0_05": "evidence_better_than_random" if p_value < 0.05 else "no_evidence_better_than_random",
        }

    report = {
        "method": "paired per-draw Monte Carlo test",
        "random_runs": int(mc.shape[0]),
        "draws": int(mc.shape[1]),
        "description": "Each strategy is compared with random tickets evaluated against the same historical draw sequence, preserving the draw-level prize environment.",
        "results": results,
    }
    (root / "paired_significance.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
