from src.machine_learning.backtest_v2 import PrizeConfig, evaluate_ticket, summarize


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


def test_summary_exact_distribution_and_gain():
    p = PrizeConfig()
    result = [1, 2, 3, 4, 5, 6, 7]
    tickets = [
        [8, 9, 10, 11, 12, 13],  # 0
        [1, 2, 3, 8, 9, 10],      # 3
        [1, 2, 3, 4, 8, 9],       # 4
        [1, 2, 3, 4, 5, 8],       # 5 only
        [1, 2, 3, 4, 5, 7],       # 5 + special
        [1, 2, 3, 4, 5, 6],       # 6
    ]
    summary = summarize("test", [result], [tickets], p)

    assert summary.tickets == 6
    assert summary.zero_match == 1
    assert summary.three_match == 1
    assert summary.four_match == 1
    assert summary.five_main_only == 1
    assert summary.five_plus_special == 1
    assert summary.six_main == 1
    assert summary.jackpot1_hits == 1
    assert summary.jackpot2_hits == 1
    assert summary.first_prize_hits == 1
    assert summary.second_prize_hits == 1
    assert summary.third_prize_hits == 1

    expected_gain = 30_000_000_000 + 3_000_000_000 + 40_000_000 + 500_000 + 50_000
    assert summary.gain == expected_gain
    assert summary.cost == 60_000
    assert summary.net_profit == expected_gain - 60_000
