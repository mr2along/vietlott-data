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
    roi_samples = [float(x) for x in random_report["roi_samples_percent"]]
    gain_samples = [float(x) for x in random_report["gain_samples_vnd"]]
    if len(roi_samples) < RUNS or len(gain_samples) != len(roi_samples):
        raise ValueError("Random Monte Carlo artifact has an invalid sample count")

    results = {}
    for row in summary:
        name = row["strategy"]
        observed = float(row["roi_pct"])
        ge = sum(x >= observed for x in roi_samples)
        p_value = (ge + 1) / (len(roi_samples) + 1)
        results[name] = {
            "observed_gain_vnd": row["gain"],
            "observed_cost_vnd": row["cost"],
            "observed_roi_percent": observed,
            "difference_vs_random_mean_percent": observed - statistics.mean(roi_samples),
            "difference_vs_random_median_percent": observed - statistics.median(roi_samples),
            "random_percentile_rank": float(np.mean(np.asarray(roi_samples) <= observed) * 100.0),
            "empirical_p_value_one_sided": p_value,
            "random_roi_p05_percent": percentile(roi_samples, 5),
            "random_roi_median_percent": statistics.median(roi_samples),
            "random_roi_p95_percent": percentile(roi_samples, 95),
            "conclusion_at_0_05": "evidence_better_than_random" if p_value < 0.05 else "no_evidence_better_than_random",
        }

    report = {
        "method": "one-sided empirical Monte Carlo comparison",
        "null": "strategy ROI is no better than independent uniform random tickets under the same ticket budget",
        "random_runs": len(roi_samples),
        "random_gain_mean_vnd": statistics.mean(gain_samples),
        "random_roi_mean_percent": statistics.mean(roi_samples),
        "results": results,
        "note": "A historical p-value is not evidence that future lottery draws are predictable.",
    }
    (root / "strategy_significance.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
