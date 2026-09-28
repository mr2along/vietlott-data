from datetime import date, timedelta

import pytest

from src.machine_learning.backtest_v2 import PrizeConfig, evaluate_ticket, summarize
from src.machine_learning.run_backtest_v2 import run_strategy


def test_jackpot1_uses_six_main_only():
    p = PrizeConfig()
    assert evaluate_ticket([1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6, 7], p).prize == 30_000_000_000


def test_jackpot2_is_five_main_plus_special():
    p = PrizeConfig()
    assert evaluate_ticket([1, 2, 3, 4, 5, 7], [1, 2, 3, 4, 5, 6, 7], p).prize == 3_000_000_000


def test_first_prize_is_five_main_without_special():
    p = PrizeConfig()
    assert evaluate_ticket([1, 2, 3, 4, 5, 8], [1, 2, 3, 4, 5, 6, 7], p).prize == 40_000_000


def test_second_and_third_prizes():
    p = PrizeConfig()
    assert evaluate_ticket([1, 2, 3, 4, 8, 9], [1, 2, 3, 4, 5, 6, 7], p).prize == 500_000
    assert evaluate_ticket([1, 2, 3, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7], p).prize == 50_000


def test_special_number_cannot_be_counted_as_main_match():
    p = PrizeConfig()
    result = evaluate_ticket([1, 2, 3, 4, 5, 7], [1, 2, 3, 4, 5, 8, 7], p)
    assert result.main_matches == 5
    assert result.special_match is True
    assert result.prize == 3_000_000_000


def test_summary_reports_portfolio_diversity_coverage_and_stability():
    summary = summarize(
        "fixture",
        [[1, 2, 3, 4, 5, 6, 55]],
        [[[1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]],
        PrizeConfig(tickets_per_draw=3),
    )
    assert summary.draws_with_p3_plus_pct == 100.0
    assert summary.duplicate_ticket_rate_pct == pytest.approx(100 / 3)
    assert summary.average_unique_numbers_per_draw == 12
    assert summary.maximum_pair_reuse == 2
    assert summary.average_main_number_coverage_pct == 100.0
    assert summary.max_matches_stdev == 0.0


def test_locked_holdout_never_enters_strategy_training_history():
    rows = [
        {
            "id": f"{index + 1:05d}",
            "date": date(2026, 1, 1) + timedelta(days=index),
            "result": [1, 2, 3, 4, 5, 6, 7],
        }
        for index in range(20)
    ]
    observed_history_sizes = []

    class FixedModel:
        def predict(self, target_date):
            return [1, 2, 3, 4, 5, 6]

    def make_strategy(history, target_date, weights=None):
        observed_history_sizes.append(len(history))
        return FixedModel()

    run_strategy("Fixture", rows, make_strategy, seed=0, min_history=1)

    holdout_start = int(len(rows) * 0.85)
    holdout_offset = holdout_start - 1
    assert observed_history_sizes[holdout_offset:] == [holdout_start] * (len(rows) - holdout_start)
