import json
from pathlib import Path

from src.render_forecast_readme import _read_json, update_readme


def test_update_readme_reports_upcoming_forecast_and_realized_results(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "# Project\n\n## Predictions\nold section\n\n## 📊 Data Statistics\nkeep stats\n",
        encoding="utf-8",
    )
    forecast_dir = tmp_path / "artifacts/forecast"
    history_dir = forecast_dir / "history"
    results_dir = forecast_dir / "results"
    history_dir.mkdir(parents=True)
    results_dir.mkdir(parents=True)

    forecast = {
        "target_draw_id": "01410",
        "target_draw_date": "2026-10-13",
        "forecast_generated_at_utc": "2026-10-12T13:30:00+00:00",
        "as_of_draw": {"id": "01409", "date": "2026-10-10"},
        "dataset_rows": 1409,
        "predictions": {
            "Bayesian": [1, 2, 3, 4, 5, 6],
            "ExponentialDecay": [7, 8, 9, 10, 11, 12],
            "LogisticProbability": [13, 14, 15, 16, 17, 18],
            "RankEnsemble": [19, 20, 21, 22, 23, 24],
            "PortfolioEnsemble": [[1, 2, 3, 8, 9, 10]],
            "UnseenPortfolioEnsemble": [[1, 2, 3, 4, 5, 7]],
        },
        "portfolio_candidate_pool": {"pool": [1, 2, 3, 4, 5, 6, 7]},
    }
    (forecast_dir / "next_power655.json").write_text(
        json.dumps(forecast), encoding="utf-8"
    )

    evaluated = {
        "target_draw_id": "01409",
        "target_draw_date": "2026-10-10",
        "forecast_generated_at_utc": "2026-10-09T18:57:00+00:00",
        "actual": {
            "id": "01409",
            "date": "2026-10-10",
            "main": [1, 2, 3, 4, 5, 6],
            "special": 7,
        },
        "single_models": {
            "Bayesian": {
                "forecast_numbers": [1, 2, 3, 8, 9, 10],
                "main_matches": 3,
                "prize_vnd": 50000,
            }
        },
        "portfolio_ensemble": {
            "forecast_numbers": [[1, 2, 3, 8, 9, 10]],
            "tickets": 1,
            "tickets_ge3": 1,
            "tickets_ge3_rate_pct": 100.0,
            "gain_vnd": 50000,
            "cost_vnd": 10000,
            "net_profit_vnd": 40000,
            "roi_pct": 400.0,
            "ticket_results": [
                {
                    "main_matches": 3,
                    "special_match": False,
                    "prize_vnd": 50000,
                    "prize_type": "third",
                }
            ],
        },
        "unseen_portfolio_ensemble": {
            "forecast_numbers": [[1, 2, 3, 4, 5, 7]],
            "tickets": 1,
            "tickets_ge3": 1,
            "tickets_ge3_rate_pct": 100.0,
            "gain_vnd": 3000000000,
            "cost_vnd": 10000,
            "net_profit_vnd": 2999990000,
            "roi_pct": 29999900.0,
            "ticket_results": [
                {
                    "main_matches": 5,
                    "special_match": True,
                    "prize_vnd": 3000000000,
                    "prize_type": "jackpot2",
                }
            ],
        },
    }
    report = {
        "evaluated_draws": [evaluated],
        "pending_target_draw_ids": ["01410"],
        "summary": {
            "PortfolioEnsemble": {
                "draws_evaluated": 1,
                "tickets": 1,
                "tickets_ge3": 1,
                "tickets_ge3_rate_pct": 100.0,
                "gain_vnd": 50000,
                "cost_vnd": 10000,
                "net_profit_vnd": 40000,
                "roi_pct": 400.0,
            },
            "UnseenPortfolioEnsemble": {
                "draws_evaluated": 1,
                "tickets": 1,
                "tickets_ge3": 1,
                "tickets_ge3_rate_pct": 100.0,
                "gain_vnd": 3000000000,
                "cost_vnd": 10000,
                "net_profit_vnd": 2999990000,
                "roi_pct": 29999900.0,
            },
        },
    }
    (results_dir / "forecast_results.json").write_text(
        json.dumps(report), encoding="utf-8"
    )

    assert update_readme(tmp_path) is True
    rendered = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "## Predictions" in rendered
    assert "01410" in rendered
    assert "01 02 03 08 09 10" in rendered
    assert "Latest evaluated forecast" in rendered
    assert "01 02 03 04 05 06" in rendered
    assert "3/6" in rendered
    assert "50,000" in rendered
    assert "keep stats" in rendered
    assert "old section" not in rendered


def test_read_json_tolerates_legacy_literal_newline_suffix(tmp_path: Path) -> None:
    target = tmp_path / "legacy.json"
    target.write_text('{"ok": true}' + chr(92) + "n", encoding="utf-8")
    assert _read_json(target) == {"ok": True}
