from __future__ import annotations

import json
import statistics
from pathlib import Path

import numpy as np

RUNS = 1000


def percentile(values, p: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=float), p))


def main() -> None:
    root = Path("artifacts/backtest_v2")
    summary = json.loads((root / "backtest_summary.json").read_text(encoding="utf-8"))
    random_report = json.loads((root / "random_monte_carlo_raw.json").read_text(encoding="utf-8"))
    random_per_draw = np.asarray(json.loads((root / "random_monte_carlo_per_draw.json").read_text(encoding="utf-8")), dtype=float)
    roi_samples = [float(x) for x in random_report["roi_samples_percent"]]
    gain_samples = [float(x) for x in random_report["gain_samples_vnd"]]
    if len(roi_samples) < RUNS or len(gain_samples) != len(roi_samples):
        raise ValueError("Random Monte Carlo artifact has an invalid sample count")
    if random_per_draw.ndim != 2 or random_per_draw.shape[0] < RUNS:
        raise ValueError("Random per-draw artifact has an invalid shape")

    results = {}
    draw_rows = json.loads((root / "backtest_per_draw.json").read_text(encoding="utf-8"))
    for row in summary:
        name = row["strategy"]
        payload = sorted([x for x in draw_rows if x["strategy"] == name], key=lambda x: x["draw_index"])
        columns = np.asarray([int(x["draw_index"]) - 1 for x in payload], dtype=int)
        if np.any(columns < 0) or np.any(columns >= random_per_draw.shape[1]):
            raise ValueError(f"Invalid draw alignment for {name}")
        aligned_random_gain = random_per_draw[:, columns].sum(axis=1)
        observed_gain = float(row["gain"])
        cost = float(row["cost"])
        observed = float((observed_gain - cost) / cost * 100.0)
        aligned_random_roi = (aligned_random_gain - cost) / cost * 100.0
        ge = int(np.sum(aligned_random_roi >= observed))
        p_value = (ge + 1) / (len(aligned_random_roi) + 1)
        results[name] = {
            "observed_gain_vnd": observed_gain,
            "observed_cost_vnd": cost,
            "observed_roi_percent": observed,
            "matched_horizon_draws": int(len(payload)),
            "random_aligned_gain_mean_vnd": float(aligned_random_gain.mean()),
            "random_aligned_roi_mean_percent": float(aligned_random_roi.mean()),
            "difference_vs_random_aligned_mean_percent": observed - float(aligned_random_roi.mean()),
            "random_percentile_rank": float(np.mean(aligned_random_roi <= observed) * 100.0),
            "empirical_p_value_one_sided": p_value,
            "random_roi_p05_percent": percentile(aligned_random_roi, 5),
            "random_roi_median_percent": float(np.median(aligned_random_roi)),
            "random_roi_p95_percent": percentile(aligned_random_roi, 95),
        }

    m = max(1, len(results))
    for value in results.values():
        raw_p = float(value["empirical_p_value_one_sided"])
        value["bonferroni_adjusted_p_value"] = min(1.0, raw_p * m)
        value["conclusion_at_0_05_bonferroni"] = (
            "evidence_better_than_random"
            if value["bonferroni_adjusted_p_value"] < 0.05
            else "no_evidence_better_than_random"
        )
    report = {
        "method": "one-sided empirical Monte Carlo comparison with horizon matching",
        "null": "strategy ROI is no better than independent uniform random tickets under the same ticket budget",
        "random_runs": len(roi_samples),
        "random_gain_mean_vnd": statistics.mean(gain_samples),
        "random_roi_mean_percent": statistics.mean(roi_samples),
        "multiple_testing": "Bonferroni correction across strategies",
        "results": results,
        "note": "Historical significance does not establish future lottery predictability.",
    }
    (root / "strategy_significance.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
