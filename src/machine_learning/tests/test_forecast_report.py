import json

from src.forecast_report import generate_forecast_section


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_forecast_report_shows_upcoming_tickets_and_each_evaluated_draw(tmp_path):
    data = tmp_path / "data/power655.jsonl"
    data.parent.mkdir(parents=True)
    data.write_text(
        json.dumps({"id": "00002", "date": "2026-01-02", "result": [1, 2, 3, 4, 5, 6, 7]}) + "\n",
        encoding="utf-8",
    )
    _write_json(
        tmp_path / "artifacts/forecast/next_power655.json",
        {
            "target_draw_id": "00003",
            "target_draw_date": "2026-01-05",
            "target_draw_weekday": "Monday",
            "forecast_generated_at_utc": "2026-01-04T12:00:00+00:00",
            "as_of_draw": {"id": "00002", "date": "2026-01-02"},
            "predictions": {
                "Bayesian": [1, 2, 3, 4, 5, 6],
                "PortfolioEnsemble": [[1, 2, 3, 4, 5, 6]],
                "UnseenPortfolioEnsemble": [[7, 8, 9, 10, 11, 12]],
            },
        },
    )
    _write_json(
        tmp_path / "artifacts/forecast/results/forecast_results.json",
        {
            "evaluated_draws": [
                {
                    "target_draw_id": "00001",
                    "target_draw_date": "2026-01-01",
                    "forecast_generated_at_utc": "2025-12-31T12:00:00+00:00",
                    "actual": {"main": [1, 2, 3, 4, 5, 6], "special": 7},
                    "portfolio_ensemble": {
                        "forecast_numbers": [[1, 2, 3, 10, 11, 12]],
                        "ticket_results": [
                            {
                                "main_matches": 3,
                                "special_match": False,
                                "prize_vnd": 50000,
                                "prize_type": "third",
                            }
                        ],
                        "tickets": 1,
                        "tickets_ge3": 1,
                        "gain_vnd": 50000,
                        "cost_vnd": 10000,
                        "net_profit_vnd": 40000,
                    },
                    "unseen_portfolio_ensemble": {
                        "forecast_numbers": [[7, 8, 9, 10, 11, 12]],
                        "ticket_results": [
                            {
                                "main_matches": 0,
                                "special_match": False,
                                "prize_vnd": 0,
                                "prize_type": "none",
                            }
                        ],
                        "tickets": 1,
                        "tickets_ge3": 0,
                        "gain_vnd": 0,
                        "cost_vnd": 10000,
                        "net_profit_vnd": -10000,
                    },
                    "single_models": {
                        "Bayesian": {
                            "forecast_numbers": [1, 2, 3, 10, 11, 12],
                            "main_matches": 3,
                            "prize_vnd": 50000,
                            "prize_type": "third",
                        }
                    },
                }
            ],
            "pending_target_draw_ids": ["00003"],
            "summary": {
                "PortfolioEnsemble": {
                    "draws_evaluated": 1,
                    "tickets": 1,
                    "tickets_ge3": 1,
                    "tickets_ge3_rate_pct": 100.0,
                    "gain_vnd": 50000,
                    "net_profit_vnd": 40000,
                    "roi_pct": 400.0,
                },
                "UnseenPortfolioEnsemble": {
                    "draws_evaluated": 1,
                    "tickets": 1,
                    "tickets_ge3": 0,
                    "tickets_ge3_rate_pct": 0.0,
                    "gain_vnd": 0,
                    "net_profit_vnd": -10000,
                    "roi_pct": -100.0,
                },
            },
        },
    )

    report = generate_forecast_section(tmp_path)

    assert "Next-draw forecast — draw **#00003**" in report
    assert "| 01, 02, 03, 04, 05, 06 |" in report
    assert "Forecast sequence and outcome for each evaluated draw" in report
    assert "Draw #00001" in report
    assert "3/6" in report
    assert "50,000" in report
    assert "Matched main numbers" in report


def test_forecast_report_does_not_present_stale_forecast_as_upcoming(tmp_path):
    data = tmp_path / "data/power655.jsonl"
    data.parent.mkdir(parents=True)
    data.write_text(
        json.dumps({"id": "00010", "date": "2026-01-02", "result": [1, 2, 3, 4, 5, 6, 7]}) + "\n",
        encoding="utf-8",
    )
    _write_json(
        tmp_path / "artifacts/forecast/next_power655.json",
        {
            "target_draw_id": "00010",
            "predictions": {"PortfolioEnsemble": [[1, 2, 3, 4, 5, 6]]},
        },
    )

    report = generate_forecast_section(tmp_path)

    assert "stored forecast targets draw **#00010**" in report
    assert "not presented as upcoming" in report
    assert "Next-draw forecast — draw **#00010**" not in report
