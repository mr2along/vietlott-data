"""Audit historical candidate-pool coverage without look-ahead leakage.

The audit compares the score-only candidate pool with the hybrid pool that
reserves a historical coverage/repeat tier. It reports how many actual main
numbers were already inside each pool and how often all six were covered.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .forecast_next import load_complete_rows
from .strategies import PortfolioEnsembleStrategy


def audit_candidate_coverage(
    rows: list[dict],
    last_draws: int = 60,
    candidate_pool_size: int = 24,
    coverage_rescue_size: int = 0,
    ensemble_score_mode: str = "full_rank",
) -> dict[str, object]:
    if last_draws < 1:
        raise ValueError("last_draws must be >= 1")
    if candidate_pool_size < 6:
        raise ValueError("candidate_pool_size must be >= 6")
    if not 0 <= coverage_rescue_size <= candidate_pool_size - 6:
        raise ValueError("coverage_rescue_size must leave room for six-number tickets")

    if len(rows) < 31:
        raise ValueError("need at least 31 complete rows for walk-forward audit")

    df = pd.DataFrame(
        [{"date": r["date"], "result": r["result"][:6]} for r in rows]
    )
    start = max(30, len(rows) - last_draws)
    targets = rows[start:]

    baseline = PortfolioEnsembleStrategy(
        df,
        tickets_per_draw=30,
        candidate_pool_size=candidate_pool_size,
        coverage_rescue_size=0,
        ensemble_score_mode=ensemble_score_mode,
    )
    hybrid = PortfolioEnsembleStrategy(
        df,
        tickets_per_draw=30,
        candidate_pool_size=candidate_pool_size,
        coverage_rescue_size=coverage_rescue_size,
        ensemble_score_mode=ensemble_score_mode,
    )

    baseline_hits = 0
    hybrid_hits = 0
    baseline_full = 0
    hybrid_full = 0
    rescued_hits = 0
    total_numbers = 6 * len(targets)
    per_draw: list[dict[str, object]] = []

    for row in targets:
        target_date = row["date"]
        actual = set(int(x) for x in row["result"][:6])

        baseline_pool = set(baseline.candidate_pool_details(target_date)["pool"])
        hybrid_details = hybrid.candidate_pool_details(target_date)
        hybrid_pool = set(hybrid_details["pool"])
        rescue = set(hybrid_details["coverage_rescue"])

        baseline_hit = len(actual & baseline_pool)
        hybrid_hit = len(actual & hybrid_pool)

        baseline_hits += baseline_hit
        hybrid_hits += hybrid_hit
        baseline_full += baseline_hit == 6
        hybrid_full += hybrid_hit == 6
        draw_rescued = sorted(actual & rescue)
        rescued_hits += len(draw_rescued)
        per_draw.append(
            {
                "id": row["id"],
                "date": row["date"].isoformat(),
                "actual_main": sorted(actual),
                "baseline_matches": baseline_hit,
                "hybrid_matches": hybrid_hit,
                "rescued_actual_numbers": draw_rescued,
            }
        )

    return {
        "target_draws": len(targets),
        "target_first_id": targets[0]["id"],
        "target_last_id": targets[-1]["id"],
        "candidate_pool_size": candidate_pool_size,
        "coverage_rescue_size": coverage_rescue_size,
        "ensemble_score_mode": ensemble_score_mode,
        "baseline_score_only": {
            "matched_numbers": baseline_hits,
            "coverage_rate": baseline_hits / total_numbers,
            "draws_with_all_six": baseline_full,
            "all_six_rate": baseline_full / len(targets),
        },
        "hybrid_coverage_rescue": {
            "matched_numbers": hybrid_hits,
            "coverage_rate": hybrid_hits / total_numbers,
            "draws_with_all_six": hybrid_full,
            "all_six_rate": hybrid_full / len(targets),
            "rescued_actual_numbers": rescued_hits,
        },
        "per_draw": per_draw,
        "gain": {
            "matched_numbers": hybrid_hits - baseline_hits,
            "coverage_rate": (hybrid_hits - baseline_hits) / total_numbers,
            "draws_with_all_six": hybrid_full - baseline_full,
        },
        "note": (
            "Walk-forward candidate coverage only. A higher candidate coverage "
            "does not establish future lottery predictability."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/power655.jsonl")
    parser.add_argument("--last-draws", type=int, default=60)
    parser.add_argument("--candidate-pool-size", type=int, default=24)
    parser.add_argument("--coverage-rescue-size", type=int, default=0)
    parser.add_argument("--ensemble-score-mode", choices=("top6", "full_rank"), default="full_rank")
    args = parser.parse_args()

    rows = load_complete_rows(Path(args.data))
    audit = audit_candidate_coverage(
        rows,
        last_draws=args.last_draws,
        candidate_pool_size=args.candidate_pool_size,
        coverage_rescue_size=args.coverage_rescue_size,
        ensemble_score_mode=args.ensemble_score_mode,
    )

    output = Path("artifacts/audit/forecast_candidate_coverage.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
