from src.machine_learning.evaluate_forecast_results import PRIZES, TICKET_PRICE, evaluate_portfolio, ticket_result

def test_ticket_result_counts_three_main_hits():
    draw = {"main": [1, 2, 3, 4, 5, 6], "special": 7}
    result = ticket_result([1, 2, 3, 10, 11, 12], draw)
    assert result["main_matches"] == 3
    assert result["prize_vnd"] == PRIZES["third"]

def test_ticket_result_five_plus_special_gets_jackpot2():
    draw = {"main": [1, 2, 3, 4, 5, 6], "special": 7}
    result = ticket_result([1, 2, 3, 4, 5, 7], draw)
    assert result["main_matches"] == 5
    assert result["special_match"] is True
    assert result["prize_type"] == "jackpot2"
    assert result["prize_vnd"] == PRIZES["jackpot2"]

def test_portfolio_counts_ge3_and_gain():
    draw = {"main": [1, 2, 3, 4, 5, 6], "special": 7}
    tickets = [
        [1, 2, 3, 10, 11, 12],
        [1, 2, 3, 4, 9, 10],
        [1, 2, 3, 4, 5, 7],
    ]
    report = evaluate_portfolio(tickets, draw)
    assert report["tickets"] == 3
    assert report["tickets_ge3"] == 3
    assert report["tickets_ge4"] == 2
    assert report["tickets_ge5"] == 1
    assert report["gain_vnd"] == PRIZES["third"] + PRIZES["second"] + PRIZES["jackpot2"]
    assert report["cost_vnd"] == 3 * TICKET_PRICE
