from datetime import date

import pandas as pd

from ..strategies.portfolio_ensemble import PortfolioEnsembleStrategy


def _history():
    return pd.DataFrame(
        [
            {"date": date(2026, 1, 1), "result": [1, 2, 3, 4, 5, 6, 55]},
            {"date": date(2026, 1, 3), "result": [7, 8, 9, 10, 11, 12, 54]},
            {"date": date(2026, 1, 5), "result": [13, 14, 15, 16, 17, 18, 53]},
            {"date": date(2026, 1, 7), "result": [19, 20, 21, 22, 23, 24, 52]},
            {"date": date(2026, 1, 9), "result": [25, 26, 27, 28, 29, 30, 51]},
            {"date": date(2026, 1, 11), "result": [31, 32, 33, 34, 35, 36, 50]},
        ]
    )


def test_portfolio_returns_30_distinct_tickets():
    model = PortfolioEnsembleStrategy(
        _history(),
        weights={"Bayesian": 1.0, "ExponentialDecay": 0.0, "LogisticProbability": 0.0},
        tickets_per_draw=30,
        candidate_pool_size=18,
    )
    tickets = [tuple(model.predict(date(2026, 1, 13))) for _ in range(30)]
    assert len(tickets) == 30
    assert len(set(tickets)) == 30
    assert all(len(t) == 6 for t in tickets)
    assert all(len(set(t)) == 6 for t in tickets)
    assert all(all(1 <= n <= 55 for n in t) for t in tickets)


def test_portfolio_ignores_special_number():
    original = _history()
    changed = original.copy(deep=True)
    changed.loc[5, "result"] = [31, 32, 33, 34, 35, 36, 1]

    kwargs = {
        "weights": {"Bayesian": 1.0, "ExponentialDecay": 0.0, "LogisticProbability": 0.0},
        "tickets_per_draw": 30,
        "candidate_pool_size": 18,
    }
    first_model = PortfolioEnsembleStrategy(original, **kwargs)
    second_model = PortfolioEnsembleStrategy(changed, **kwargs)
    first = [tuple(first_model.predict(date(2026, 1, 13))) for _ in range(30)]
    second = [tuple(second_model.predict(date(2026, 1, 13))) for _ in range(30)]
    assert first == second

def test_portfolio_usage_cap_preserves_coverage():
    model = PortfolioEnsembleStrategy(
        _history(),
        weights={"Bayesian": 1.0, "ExponentialDecay": 0.0, "LogisticProbability": 0.0},
        tickets_per_draw=30,
        candidate_pool_size=24,
        max_number_usage=8,
    )
    tickets = [tuple(model.predict(date(2026, 1, 13))) for _ in range(30)]
    usage = {
        number: sum(number in ticket for ticket in tickets)
        for number in range(1, 56)
        if any(number in ticket for ticket in tickets)
    }
    assert len(tickets) == 30
    assert len(set(tickets)) == 30
    assert len(usage) == 24
    assert max(usage.values()) <= 8
    assert sum(usage.values()) == 180


def test_portfolio_usage_cap_rejects_insufficient_capacity():
    try:
        PortfolioEnsembleStrategy(
            _history(),
            tickets_per_draw=30,
            candidate_pool_size=24,
            max_number_usage=7,
        )
    except ValueError as exc:
        assert "capacity" in str(exc)
    else:
        raise AssertionError("expected insufficient capacity to fail")
