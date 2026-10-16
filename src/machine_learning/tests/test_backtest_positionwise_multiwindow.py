from datetime import date, timedelta

from machine_learning.backtest_positionwise_multiwindow import (
    render_markdown,
    run_multiwindow_backtest,
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


def test_multiwindow_backtest_has_comparable_chronological_windows():
    report = run_multiwindow_backtest(
        _rows(),
        min_history=100,
        seed=655,
        block_size=10,
        rolling_size=15,
        trailing_sizes=(5, 10, 20),
    )

    assert report["dataset"]["evaluation_draws"] == 20
    assert report["window_policy"]["no_lookahead"]
    families = report["families"]
    blocks = families["fixed_blocks_10"]["windows"]
    rolling = families["rolling_15_step_10"]["windows"]
    trailing = families["trailing_windows"]["windows"]

    assert [window["draws"] for window in blocks] == [10, 10]
    assert [window["draws"] for window in rolling] == [15, 15]
    assert {window["draws"] for window in trailing} == {5, 10, 20}
    assert all(window["start_index"] < window["stop_index_exclusive"] for family in families.values() for window in family["windows"])

    strategies = report["families"]["fixed_blocks_10"]["windows"][0]["metrics"]
    expected_models = {
        "PositionWiseBayesian",
        "PositionWiseExponentialDecay",
        "PositionWiseRecent",
        "PositionWiseEnsemble",
        "PositionWisePolynomial",
        "PositionWiseBayesian_Mirror56Minus",
        "PositionWiseExponentialDecay_Mirror56Minus",
        "PositionWiseRecent_Mirror56Minus",
        "PositionWiseEnsemble_Mirror56Minus",
        "PositionWisePolynomial_Mirror56Minus",
        "RandomOneTicket",
    }
    assert set(strategies) == expected_models
    for window in [*blocks, *rolling, *trailing]:
        expected_cost = window["draws"] * 10_000
        assert {row["cost"] for row in window["metrics"].values()} == {expected_cost}

    stability = families["fixed_blocks_10"]["mirror_stability"]["PositionWiseEnsemble"]
    assert stability["window_count"] == 2
    assert 0 <= stability["mirror_beats_original_windows"] <= 2
    assert 0 <= stability["mirror_beats_random_windows"] <= 2

    rendered = render_markdown(report)
    assert "Window-by-window comparison" in rendered
    assert "Strategy ROI stability by window family" in rendered
    assert "Does the mirror beat its corresponding original?" in rendered
