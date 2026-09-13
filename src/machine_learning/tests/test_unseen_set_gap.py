from datetime import date

import pandas as pd

from machine_learning.strategies import UnseenSetGapStrategy


def _make_df():
    return pd.DataFrame(
        [
            {"date": date(2024, 1, 1), "result": [1, 2, 3, 4, 5, 6, 55]},
            {"date": date(2024, 1, 2), "result": [7, 8, 9, 10, 11, 12, 54]},
            {"date": date(2024, 1, 3), "result": [13, 14, 15, 16, 17, 18, 53]},
        ]
    )


def test_prediction_is_valid_and_exact_set_is_unseen():
    model = UnseenSetGapStrategy(_make_df(), candidate_pool_size=18, max_attempts=50)
    prediction = model.predict(date(2024, 1, 10))

    assert len(prediction) == 6
    assert len(set(prediction)) == 6
    assert prediction == sorted(prediction)
    assert all(1 <= n <= 55 for n in prediction)

    historical_sets = {
        tuple(sorted(row[:6])) for row in _make_df()["result"]
    }
    assert tuple(prediction) not in historical_sets


def test_only_strictly_prior_draws_are_used_for_exclusion():
    df = pd.DataFrame(
        [
            {"date": date(2024, 1, 1), "result": [1, 2, 3, 4, 5, 6, 55]},
            {"date": date(2024, 1, 10), "result": [7, 8, 9, 10, 11, 12, 54]},
        ]
    )
    model = UnseenSetGapStrategy(df, candidate_pool_size=18)
    _, _, seen_sets = model._prepare(date(2024, 1, 10))

    assert (1, 2, 3, 4, 5, 6) in seen_sets
    assert (7, 8, 9, 10, 11, 12) not in seen_sets


def test_special_number_is_not_part_of_exact_set_key():
    df = pd.DataFrame(
        [
            {"date": date(2024, 1, 1), "result": [1, 2, 3, 4, 5, 6, 55]},
        ]
    )
    model = UnseenSetGapStrategy(df, candidate_pool_size=18)
    _, _, seen_sets = model._prepare(date(2024, 1, 2))

    assert (1, 2, 3, 4, 5, 6) in seen_sets
    assert all(len(ticket) == 6 for ticket in seen_sets)


def test_future_draw_does_not_change_prior_prediction_state():
    df = pd.DataFrame(
        [
            {"date": date(2024, 1, 1), "result": [1, 2, 3, 4, 5, 6, 55]},
            {"date": date(2024, 1, 20), "result": [7, 8, 9, 10, 11, 12, 54]},
        ]
    )
    model = UnseenSetGapStrategy(df, candidate_pool_size=18)
    _, gaps, seen_sets = model._prepare(date(2024, 1, 10))

    assert (7, 8, 9, 10, 11, 12) not in seen_sets
    assert gaps[7] == float("inf")
