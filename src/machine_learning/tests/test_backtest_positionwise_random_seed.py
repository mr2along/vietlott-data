from datetime import date, timedelta

from machine_learning.backtest_positionwise_random_seed import (
    render_markdown,
    run_random_seed_validation,
)


def _rows(count: int = 120):
    start = date(2024, 1, 1)
    rows = []
    for index in range(count):
        main = sorted({
            1 + index % 10,
            12 + index % 10,
            23 + index % 10,
            34 + index % 10,
            40 + index % 10,
            50 + index % 6,
        })
        if len(main) < 6:
            main = [1, 12, 23, 34, 45, 55]
        special = next(number for number in range(1, 56) if number not in main)
        rows.append({
            "id": f"{index + 1:05d}",
            "date": start + timedelta(days=3 * index),
            "result": main + [special],
        })
    return rows


def test_multi_seed_random_baseline_uses_same_draws_and_is_reproducible():
    report = run_random_seed_validation(
        _rows(),
        min_history=100,
        seed_start=1234,
        seed_count=20,
        block_size=10,
        rolling_size=15,
        trailing_sizes=(5, 10, 20),
    )

    assert report["dataset"]["evaluation_draws"] == 20
    assert report["random_seed_policy"]["seed_count"] == 20
    assert report["random_seed_policy"]["seed_end_inclusive"] == 1253
    assert report["random_seed_policy"]["same_seed_ticket_stream_reused_across_scopes"]
    scopes = report["scopes"]
    full = scopes["overall/full_walk_forward"]
    holdout = scopes["overall/tail_holdout_last_15pct"]
    assert full["draws"] == 20
    assert holdout["draws"] == 3
    assert full["random_seed_roi_distribution"]["seed_count"] == 20

    polynomial = full["model_comparisons_vs_random"]["PositionWisePolynomial"]
    assert 0 <= polynomial["model_random_percentile_pct"] <= 100
    assert 0 <= polynomial["random_seeds_roi_at_least_model_pct"] <= 100
    assert 0 < polynomial["empirical_one_sided_p_random_roi_ge_model"] <= 1
    assert full["model_metrics"]["PositionWisePolynomial"]["cost"] == 200_000
    assert full["model_metrics"]["PositionWiseEnsemble"]["cost"] == 200_000
    assert scopes["fixed_blocks_10/block_01"]["draws"] == 10
    assert scopes["rolling_15_step_10/rolling_01"]["draws"] == 15
    assert scopes["trailing_windows/last_20"]["draws"] == 20
    assert "Multi-seed Random Baseline" in render_markdown(report)
    assert "Window-by-window detail" in render_markdown(report)
