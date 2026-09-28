from ..ensemble_weight_selection import DEFAULT_WEIGHTS, select_regularized_weights


def test_weights_are_simplex_and_regularized_against_noisy_validation():
    selected = select_regularized_weights(
        {
            "Bayesian": [1.0] * 20,
            "ExponentialDecay": [0.0] * 20,
            "LogisticProbability": [0.0] * 20,
        }
    )
    assert abs(sum(selected.values()) - 1.0) < 1e-12
    assert all(value >= 0 for value in selected.values())
    assert all(abs(selected[key] - DEFAULT_WEIGHTS[key]) <= 0.08 for key in selected)


def test_empty_validation_preserves_baseline_weights():
    assert select_regularized_weights({}) == DEFAULT_WEIGHTS
