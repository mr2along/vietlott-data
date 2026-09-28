from datetime import date

from ..forecast_next import next_draw_date


def test_next_draw_date_sequence():
    assert next_draw_date(date(2026, 9, 24)) == date(2026, 9, 26)
    assert next_draw_date(date(2026, 9, 26)) == date(2026, 9, 29)
    assert next_draw_date(date(2026, 9, 29)) == date(2026, 10, 1)
