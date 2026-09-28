from datetime import date, timedelta

from .. import audit_forecast_candidates as audit


def test_candidate_audit_uses_prior_rows_and_stops_before_locked_holdout(monkeypatch):
    history_sizes = []

    class StubPortfolio:
        def __init__(self, history, **kwargs):
            history_sizes.append(len(history))
            self.coverage_rescue_size = kwargs["coverage_rescue_size"]

        def candidate_pool_details(self, target_date):
            pool = list(range(1, 31))
            return {
                "pool": pool,
                "coverage_rescue": pool[-self.coverage_rescue_size :]
                if self.coverage_rescue_size
                else [],
            }

    monkeypatch.setattr(audit, "PortfolioEnsembleStrategy", StubPortfolio)
    first_date = date(2026, 1, 1)
    rows = [
        {
            "id": f"{index + 1:05d}",
            "date": first_date + timedelta(days=index),
            "result": [1, 2, 3, 4, 5, 6, 7],
        }
        for index in range(40)
    ]

    result = audit.audit_candidate_coverage(rows, last_draws=2, candidate_pool_size=30)
    holdout_start = int(len(rows) * 0.85)

    assert result["target_draws"] == 2
    assert result["validation_window"]["locked_holdout_used"] is False
    assert history_sizes == [holdout_start - 2, holdout_start - 2, holdout_start - 1, holdout_start - 1]
