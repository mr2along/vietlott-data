from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np


def bootstrap_total_ci(values: np.ndarray, rng: np.random.Generator, n: int = 5000) -> list[float]:
    m = len(values)
    if m == 0:
        return [0.0, 0.0]
    totals = np.empty(n)
    for i in range(n):
        totals[i] = np.sum(values[rng.integers(0, m, size=m)])
    return [float(np.percentile(totals, 2.5)), float(np.percentile(totals, 97.5))]


def main() -> None:
    root = Path("artifacts/backtest_v2")
    rows = json.loads((root / "backtest_per_draw.json").read_text(encoding="utf-8"))
    mc = np.asarray(json.loads((root / "random_monte_carlo_per_draw.json").read_text(encoding="utf-8")), dtype=float)
    if mc.ndim != 2 or mc.shape[0] < 1000:
        raise ValueError(f"Expected 1000+ Monte Carlo runs, got {mc.shape}")

    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["strategy"]].append(row)

    rng = np.random.default_rng(20260809)
    results = {}
    for strategy, payload in grouped.items():
        observed = np.asarray([float(x["gain"]) for x in sorted(payload, key=lambda x: x["draw_index"])])
        draw_indices = np.asarray([int(x["draw_index"]) for x in sorted(payload, key=lambda x: x["draw_index"])])
        # Random MC column j corresponds to normalized target draw_index j+1.
        mc_cols = draw_indices - 1
        if np.any(mc_cols < 0) or np.any(mc_cols >= mc.shape[1]):
            raise ValueError(f"Invalid draw indices for {strategy}")
        random_matrix = mc[:, mc_cols]
        random_totals = random_matrix.sum(axis=1)
        observed_total = float(observed.sum())
        costs = np.asarray([float(x["cost"]) for x in sorted(payload, key=lambda x: x["draw_index"])])
        cost_total = float(costs.sum())
        diffs = observed_total - random_totals
        p_value = float((np.sum(diffs <= 0) + 1) / (len(diffs) + 1))
        ci = bootstrap_total_ci(observed, rng)
        results[strategy] = {
            "draws": int(len(observed)),
            "observed_gain_vnd": observed_total,
            "observed_cost_vnd": cost_total,
            "observed_roi_percent": float((observed_total - cost_total) / cost_total * 100.0),
            "random_mean_gain_vnd": float(random_totals.mean()),
            "mean_gain_difference_vnd": float(diffs.mean()),
            "median_gain_difference_vnd": float(np.median(diffs)),
            "empirical_p_value_one_sided": p_value,
            "bootstrap_observed_total_gain_ci_95_vnd": ci,
            "bootstrap_observed_roi_ci_95_percent": [
                float((ci[0] - cost_total) / cost_total * 100.0),
                float((ci[1] - cost_total) / cost_total * 100.0),
            ],
            "random_gain_p05_vnd": float(np.percentile(random_totals, 5)),
            "random_gain_median_vnd": float(np.median(random_totals)),
            "random_gain_p95_vnd": float(np.percentile(random_totals, 95)),
            "conclusion_at_0_05": "evidence_better_than_random" if p_value < 0.05 else "no_evidence_better_than_random",
        }

    report = {
        "method": "paired per-draw Monte Carlo test aligned by historical draw index",
        "random_runs": int(mc.shape[0]),
        "random_draws": int(mc.shape[1]),
        "description": "Each strategy is compared with random tickets against the same historical draws; strategies with a longer warm-up are aligned by draw index.",
        "results": results,
    }
    (root / "paired_significance.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
