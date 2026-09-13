from datetime import date

import pandas as pd

from ..strategies.rank_ensemble import RankEnsembleStrategy


def test_rank_ensemble_returns_six_unique_main_numbers():
    df = pd.DataFrame(
        [
            {"date": date(2026, 1, 1), "result": [1, 2, 3, 4, 5, 6]},
            {"date": date(2026, 1, 3), "result": [7, 8, 9, 10, 11, 12]},
            {"date": date(2026, 1, 5), "result": [13, 14, 15, 16, 17, 18]},
            {"date": date(2026, 1, 7), "result": [19, 20, 21, 22, 23, 24]},
            {"date": date(2026, 1, 9), "result": [25, 26, 27, 28, 29, 30]},
            {"date": date(2026, 1, 11), "result": [31, 32, 33, 34, 35, 55]},
        ]
    )
    model = RankEnsembleStrategy(
        df,
        weights={"Bayesian": 0.5, "ExponentialDecay": 0.5, "LogisticProbability": 0.0},
    )
    result = model.predict(date(2026, 1, 13))
    assert len(result) == 6
    assert len(set(result)) == 6
    assert all(1 <= n <= 55 for n in result)


def test_rank_ensemble_does_not_use_target_or_special_number():
    history = pd.DataFrame(
        [
            {"date": date(2026, 1, 1), "result": [1, 2, 3, 4, 5, 6, 55]},
            {"date": date(2026, 1, 3), "result": [7, 8, 9, 10, 11, 12, 54]},
            {"date": date(2026, 1, 5), "result": [13, 14, 15, 16, 17, 18, 53]},
            {"date": date(2026, 1, 7), "result": [19, 20, 21, 22, 23, 24, 52]},
            {"date": date(2026, 1, 9), "result": [25, 26, 27, 28, 29, 30, 51]},
            {"date": date(2026, 1, 11), "result": [31, 32, 33, 34, 35, 36, 50]},
        ]
    )
    model = RankEnsembleStrategy(
        history,
        weights={"Bayesian": 1.0, "ExponentialDecay": 0.0, "LogisticProbability": 0.0},
    )
    first = model.predict(date(2026, 1, 13))

    leaked = history.copy(deep=True)
    leaked.loc[5, "result"] = [1, 2, 3, 4, 5, 6, 49]
    leaked_model = RankEnsembleStrategy(
        leaked,
        weights={"Bayesian": 1.0, "ExponentialDecay": 0.0, "LogisticProbability": 0.0},
    )
    second = leaked_model.predict(date(2026, 1, 13))

    assert first == second
