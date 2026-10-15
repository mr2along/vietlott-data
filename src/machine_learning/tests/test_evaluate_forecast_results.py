import json

from src.machine_learning.evaluate_forecast_results import (
    PRIZES,
    TICKET_PRICE,
    evaluate_portfolio,
    main,
    ticket_result,
)

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


def test_main_writes_parseable_json_and_multiline_markdown(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    data_path = tmp_path / "data/power655.jsonl"
    data_path.parent.mkdir(parents=True)
    data_path.write_text(
        json.dumps(
            {
                "id": "00001",
                "date": "2026-01-01",
                "result": [1, 2, 3, 4, 5, 6, 7],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    history = tmp_path / "artifacts/forecast/history"
    history.mkdir(parents=True)
    forecast = {
        "target_draw_id": "00001",
        "target_draw_date": "2026-01-01",
        "forecast_generated_at_utc": "2025-12-31T12:00:00+00:00",
        "predictions": {
            "PortfolioEnsemble": [[1, 2, 3, 4, 5, 6]],
            "UnseenPortfolioEnsemble": [[7, 8, 9, 10, 11, 12]],
        },
    }
    (history / "forecast_00001.json").write_text(
        json.dumps(forecast), encoding="utf-8"
    )

    main()

    results_path = tmp_path / "artifacts/forecast/results/forecast_results.json"
    results = json.loads(results_path.read_text(encoding="utf-8"))
    assert results["evaluated_draws"][0]["target_draw_id"] == "00001"

    markdown = (
        tmp_path / "artifacts/forecast/results/forecast_results.md"
    ).read_text(encoding="utf-8")
    assert markdown.startswith("# Power 6/55 Forecast Results\n")
    assert "## Latest evaluated draws\n" in markdown
    assert "\\n" not in markdown
