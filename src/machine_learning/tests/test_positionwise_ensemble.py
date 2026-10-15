from datetime import date, timedelta

import pandas as pd

from machine_learning.strategies import PositionWiseEnsembleStrategy


def _make_history(rows: int = 180) -> pd.DataFrame:
    start = date(2024, 1, 1)
    records = []
    for index in range(rows):
        result = [
            1 + index % 3,
            8 + index % 4,
            16 + index % 5,
            26 + index % 5,
            37 + index % 6,
            49 + index % 7,
        ]
        records.append({"date": start + timedelta(days=3 * index), "result": result})
    return pd.DataFrame(records)


def test_positionwise_predict_returns_six_distinct_increasing_values():
    df = _make_history()
    target = df["date"].iloc[-1] + timedelta(days=3)
    model = PositionWiseEnsembleStrategy(df)

    prediction = model.predict(target)
    details = model.position_details(target)

    assert len(prediction) == 6
    assert prediction == sorted(prediction)
    assert len(set(prediction)) == 6
    assert all(1 <= value <= 55 for value in prediction)
    assert [item["selected_number"] for item in details["positions"]] == prediction
    assert len(details["positions"]) == 6
    for index, item in enumerate(details["positions"]):
        assert item["position"] == index + 1
        assert item["top_candidates"]
        assert item["selected_number"] in {
            candidate["number"] for candidate in item["top_candidates"]
        }


def test_positionwise_score_distributions_are_normalized_and_slot_feasible():
    df = _make_history()
    target = df["date"].iloc[-1] + timedelta(days=3)
    model = PositionWiseEnsembleStrategy(df)

    distributions = model.score_positions(target)
    assert len(distributions) == 6
    for position, scores in enumerate(distributions):
        assert abs(sum(scores.values()) - 1.0) < 1e-9
        assert min(scores) >= 1 + position
        assert max(scores) <= 55 - (5 - position)


def test_positionwise_model_does_not_use_future_rows():
    df = _make_history()
    cutoff = df["date"].iloc[120]
    earlier = df[df["date"] < cutoff].copy()
    future_rows = df[df["date"] >= cutoff].copy()
    baseline = PositionWiseEnsembleStrategy(earlier).predict(cutoff)

    # Rows at and after the target must not affect a forecast for the target.
    expanded = pd.concat([earlier, future_rows], ignore_index=True)
    with_future_data = PositionWiseEnsembleStrategy(expanded).predict(cutoff)
    assert with_future_data == baseline


def test_positionwise_first_and_last_slots_learn_their_own_history():
    df = _make_history()
    target = df["date"].iloc[-1] + timedelta(days=3)
    details = PositionWiseEnsembleStrategy(df).position_details(target)

    first_candidates = {x["number"] for x in details["positions"][0]["top_candidates"]}
    last_candidates = {x["number"] for x in details["positions"][5]["top_candidates"]}
    assert first_candidates.intersection({1, 2, 3})
    assert last_candidates.intersection({49, 50, 51, 52, 53, 54, 55})
