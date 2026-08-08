from src.machine_learning.backtest_v2 import PrizeConfig, evaluate_ticket


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
