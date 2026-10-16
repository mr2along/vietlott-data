from datetime import date, timedelta

from machine_learning.backtest_positionwise_roi import render_markdown, run_backtest


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


def test_positionwise_roi_backtest_uses_one_ticket_and_reports_holdout():
    report = run_backtest(_rows(), min_history=100, seed=655)
    full = report["full_walk_forward"]
    holdout = report["tail_holdout_last_15pct"]

    assert full["PositionWiseEnsemble"]["draws"] == 20
    assert full["PositionWiseEnsemble"]["tickets"] == 20
    assert full["PositionWiseEnsemble"]["cost"] == 200_000
    assert full["RandomOneTicket"]["cost"] == 200_000
    assert holdout["PositionWiseEnsemble"]["draws"] == 3
    assert holdout["RandomOneTicket"]["draws"] == 3
    assert report["dataset"]["tickets_per_model_per_draw"] == 1
    base_models = {
        "PositionWiseBayesian",
        "PositionWiseExponentialDecay",
        "PositionWiseRecent",
        "PositionWiseEnsemble",
    }
    expected_models = base_models | {
        f"{name}_Mirror56Minus" for name in base_models
    } | {"RandomOneTicket"}
    assert set(full) == expected_models
    assert set(holdout) - {"start_draw_id", "end_draw_id"} == expected_models
    assert {full[name]["cost"] for name in expected_models} == {200_000}
    assert all(full[name]["draws"] == 20 for name in expected_models)
    assert all(len(report["position_accuracy_full_walk_forward"][name]["positions"]) == 6 for name in expected_models)
    assert "exact position hits" in render_markdown(report)
    assert "ROI" in render_markdown(report)
    for name in base_models:
        original = report["per_draw"][0]["forecasts"][name]
        mirrored = report["per_draw"][0]["forecasts"][f"{name}_Mirror56Minus"]
        assert mirrored == sorted(56 - number for number in original)
        assert len(set(mirrored)) == 6
        assert min(mirrored) >= 1 and max(mirrored) <= 55
    assert report["mirror_transform"]["formula"] == "56 - n"
