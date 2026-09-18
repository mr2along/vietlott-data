from datetime import date, timedelta

import pandas as pd

from machine_learning.strategies.logistic_probability import LogisticProbabilityStrategy
from machine_learning.normalize_power655 import _canonical_date, _validate_row_shape


def _make_df(n: int = 40) -> pd.DataFrame:
    start = date(2023, 1, 1)
    return pd.DataFrame(
        {
            "date": [start + timedelta(days=i * 3) for i in range(n)],
            "result": [sorted(((i + offset) % 55) + 1 for offset in range(6)) for i in range(n)],
        }
    )


def test_logistic_trains_before_first_eligible_prediction():
    df = _make_df()
    model = LogisticProbabilityStrategy(df, min_training_rows=30)
    target = df["date"].iloc[30]
    prediction = model.predict(target)

    assert len(prediction) == 6
    assert model._model is not None
    assert model._trained_until == 30


def test_power655_normalizer_canonicalizes_dates_and_ids():
    ident, canonical_date, result = _validate_row_shape(
        {"id": " 01399 ", "date": "2026-09-17T00:00:00", "result": [6, 11, 25, 27, 37, 45, 15]}
    )

    assert ident == "01399"
    assert canonical_date == "2026-09-17"
    assert result == [6, 11, 25, 27, 37, 45, 15]
    assert _canonical_date("2026-09-17") == "2026-09-17"
