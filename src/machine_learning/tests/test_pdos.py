from datetime import date, timedelta

import pandas as pd

from machine_learning.strategies.pdos import PDOSStrategy


def _frame(count: int = 80):
    start = date(2024, 1, 1)
    rows = []
    for i in range(count):
        main = sorted([1 + i % 8, 12 + i % 7, 22 + i % 8, 32 + i % 9, 42 + i % 8, 50 + i % 6])
        # Keep six distinct values if the synthetic cycles collide.
        main = sorted(set(main))
        while len(main) < 6:
            candidate = next(n for n in range(1, 56) if n not in main)
            main.append(candidate)
            main.sort()
        rows.append({"date": start + timedelta(days=3 * i), "result": main[:6]})
    return pd.DataFrame(rows)


def test_pdos_returns_six_valid_increasing_numbers():
    model = PDOSStrategy(_frame())
    predicted = model.predict(date(2025, 1, 1))
    assert len(predicted) == 6
    assert predicted == sorted(set(predicted))
    assert all(1 <= value <= 55 for value in predicted)


def test_pdos_ignores_draws_on_or_after_target_date():
    frame = _frame()
    target = date(2024, 4, 1)
    original = PDOSStrategy(frame).predict(target)
    # Change only rows at/after the target. The forecast must remain identical.
    changed = frame.copy()
    mask = pd.to_datetime(changed["date"]).dt.date >= target
    changed.loc[mask, "result"] = [[1, 2, 3, 4, 5, 6] for _ in range(int(mask.sum()))]
    assert PDOSStrategy(changed).predict(target) == original
