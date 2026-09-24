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

def test_portfolio_excludes_historical_exact_sets():
    target = date(2026, 1, 13)
    baseline = PortfolioEnsembleStrategy(
        _history(),
        weights={"Bayesian": 1.0, "ExponentialDecay": 0.0, "LogisticProbability": 0.0},
        tickets_per_draw=30,
        candidate_pool_size=24,
        max_number_usage=8,
    )
    blocked_ticket = tuple(baseline.predict(target))

    model = PortfolioEnsembleStrategy(
        _history(),
        weights={"Bayesian": 1.0, "ExponentialDecay": 0.0, "LogisticProbability": 0.0},
        tickets_per_draw=30,
        candidate_pool_size=24,
        max_number_usage=8,
        excluded_sets={blocked_ticket},
    )
    tickets = [tuple(model.predict(target)) for _ in range(30)]

    assert blocked_ticket not in tickets
    assert len(set(tickets)) == 30
    assert all(ticket not in {blocked_ticket} for ticket in tickets)

def test_portfolio_filters_long_consecutive_runs():
    model = PortfolioEnsembleStrategy(
        _history(),
        weights={"Bayesian": 1.0, "ExponentialDecay": 0.0, "LogisticProbability": 0.0},
        tickets_per_draw=30,
        candidate_pool_size=24,
        max_number_usage=8,
        max_consecutive_run=3,
    )
    tickets = [tuple(model.predict(date(2026, 1, 13))) for _ in range(30)]

    def max_run(ticket):
        run = best = 1
        for left, right in zip(ticket, ticket[1:]):
            run = run + 1 if right == left + 1 else 1
            best = max(best, run)
        return best

    assert len(set(tickets)) == 30
    assert max(max_run(ticket) for ticket in tickets) <= 3
    assert model._valid_shape((1, 2, 3, 4, 9, 12)) is False
    assert model._valid_shape((1, 2, 3, 8, 9, 12)) is True

def test_candidate_pool_reserves_coverage_tier():
    target = date(2026, 1, 13)
    model = PortfolioEnsembleStrategy(
        _history(),
        weights={"Bayesian": 1.0, "ExponentialDecay": 0.0, "LogisticProbability": 0.0},
        tickets_per_draw=30,
        candidate_pool_size=18,
        coverage_rescue_size=2,
    )

    forced_scores = {number: 0.0 for number in range(1, 56)}
    for number in range(1, 17):
        forced_scores[number] = float(100 - number)
    model._scores = lambda _: forced_scores

    details = model.candidate_pool_details(target)

    assert details["core"] == list(range(1, 17))
    assert len(details["coverage_rescue"]) == 2
    assert set(details["coverage_rescue"]).issubset(set(range(17, 56)))
    assert len(details["pool"]) == 18
    assert set(details["core"]).isdisjoint(details["coverage_rescue"])

def test_full_rank_ensemble_keeps_signal_outside_component_top_six():
    class StubModel:
        def score_numbers(self, target_date):
            return {number: float(56 - number) for number in range(1, 56)}

    model = PortfolioEnsembleStrategy(
        _history(),
        weights={"Bayesian": 1.0},
        tickets_per_draw=30,
        candidate_pool_size=24,
        ensemble_score_mode="full_rank",
    )
    model._components = lambda: [("Stub", 1.0, StubModel())]

    scores = model._scores(date(2026, 1, 13))
    details = model.candidate_pool_details(date(2026, 1, 13))

    assert len(scores) == 55
    assert scores[24] > scores[25]
    assert details["core"] == list(range(1, 25))
    assert details["coverage_rescue"] == []


def test_full_rank_mode_rejects_missing_score_api():
    class LegacyOnlyModel:
        def predict(self, target_date):
            return [1, 2, 3, 4, 5, 6]

    model = PortfolioEnsembleStrategy(
        _history(),
        weights={"Bayesian": 1.0},
        tickets_per_draw=30,
        candidate_pool_size=24,
        ensemble_score_mode="full_rank",
    )
    model._components = lambda: [("LegacyOnly", 1.0, LegacyOnlyModel())]

    try:
        model._scores(date(2026, 1, 13))
    except RuntimeError as exc:
        assert "full number scores" in str(exc)
    else:
        raise AssertionError("expected full-score API validation to fail")


def test_protected_core_is_not_displaced_by_reservoir():
    target = date(2026, 1, 13)
    model = PortfolioEnsembleStrategy(
        _history(),
        weights={"Bayesian": 1.0, "ExponentialDecay": 0.0, "LogisticProbability": 0.0},
        tickets_per_draw=30,
        candidate_pool_size=30,
        coverage_rescue_size=8,
        ensemble_score_mode="full_rank",
    )
    forced_scores = {number: 0.0 for number in range(1, 56)}
    for number in range(1, 23):
        forced_scores[number] = float(1000 - number)
    model._scores = lambda _: forced_scores
    model._coverage_rank = lambda _target, _excluded: list(range(23, 56))

    details = model.candidate_pool_details(target)

    assert details["core"] == list(range(1, 23))
    assert details["coverage_rescue"] == list(range(23, 31))
    assert set(details["core"]).isdisjoint(details["coverage_rescue"])
    assert len(details["pool"]) == 30


def test_soft_exposure_allows_strong_numbers_more_than_six_times():
    target = date(2026, 1, 13)
    model = PortfolioEnsembleStrategy(
        _history(),
        weights={"Bayesian": 1.0, "ExponentialDecay": 0.0, "LogisticProbability": 0.0},
        tickets_per_draw=30,
        candidate_pool_size=30,
        ensemble_score_mode="full_rank",
        exposure_power=1.35,
        pair_reuse_penalty=0.75,
    )
    forced_scores = {number: 0.0 for number in range(1, 56)}
    for number in range(1, 31):
        forced_scores[number] = float(1000 - number * number)
    model._scores = lambda _: forced_scores

    tickets = [tuple(model.predict(target)) for _ in range(30)]
    usage = Counter(n for ticket in tickets for n in ticket)

    assert len(tickets) == 30
    assert len(set(tickets)) == 30
    assert sum(usage.values()) == 180
    assert max(usage.values()) > 6
