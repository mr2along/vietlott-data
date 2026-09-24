from datetime import date, timedelta

import pandas as pd
import pytest

from machine_learning.strategies.logistic_probability import LogisticProbabilityStrategy
from machine_learning.normalize_power655 import _canonical_date, _validate_row_shape
from machine_learning.forecast_next import load_complete_rows


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


def test_verified_power655_00944_is_a_complete_draw():
    row = {
        "id": "00944",
        "date": "2023-10-14",
        "result": [8, 23, 30, 34, 38, 47, 10],
    }
    ident, canonical_date, result = _validate_row_shape(row)
    assert ident == "00944"
    assert canonical_date == "2023-10-14"
    assert result == [8, 23, 30, 34, 38, 47, 10]


def test_forecast_loader_rejects_internal_draw_id_gap(tmp_path):
    path = tmp_path / "power655.jsonl"
    rows = []
    for ident in range(1, 102):
        if ident == 50:
            continue
        rows.append(
            {
                "id": f"{ident:05d}",
                "date": (date(2020, 1, 1) + timedelta(days=ident)).isoformat(),
                "result": [1, 2, 3, 4, 5, 6, 7],
            }
        )
    path.write_text("\n".join(__import__("json").dumps(row) for row in rows) + "\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="missing draw IDs"):
        load_complete_rows(path)
