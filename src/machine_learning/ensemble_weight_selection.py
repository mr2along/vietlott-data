"""Regularized online selection from strictly out-of-sample component results."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

DEFAULT_WEIGHTS = {
    "Bayesian": 0.35,
    "ExponentialDecay": 0.35,
    "LogisticProbability": 0.30,
}


def select_regularized_weights(
    validation_hits: Mapping[str, Sequence[float]],
    prior: Mapping[str, float] | None = None,
    *,
    regularization: float = 60.0,
    max_deviation: float = 0.08,
) -> dict[str, float]:
    """Blend recent OOS hit rates with prior weights and cap per-update movement.

    Hit rates are shrunk using a 60-draw prior, then converted to a simplex.
    The returned weights can only move a bounded distance from the fixed
    baseline, limiting noisy validation swings.
    """
    baseline = dict(prior or DEFAULT_WEIGHTS)
    if regularization <= 0 or not 0 <= max_deviation < 1:
        raise ValueError("invalid weight regularization settings")
    names = list(baseline)
    total = sum(float(baseline[n]) for n in names)
    if total <= 0 or any(float(baseline[n]) < 0 for n in names):
        raise ValueError("prior weights must be non-negative with a positive sum")
    baseline = {n: float(baseline[n]) / total for n in names}
    rates: dict[str, float] = {}
    n_obs = max((len(validation_hits.get(n, ())) for n in names), default=0)
    for name in names:
        values = [float(v) for v in validation_hits.get(name, ())]
        if any(v < 0 or v > 6 for v in values):
            raise ValueError("validation hit counts must be between 0 and 6")
        prior_rate = 36.0 / 55.0
        rates[name] = (sum(values) + regularization * prior_rate) / (len(values) + regularization)
    rate_mean = sum(rates.values()) / len(names)
    reliability = n_obs / (n_obs + regularization)
    raw = {name: baseline[name] + reliability * (rates[name] - rate_mean) for name in names}
    raw = {name: max(0.0, value) for name, value in raw.items()}
    raw_total = sum(raw.values())
    if raw_total <= 0:
        return baseline
    proposed = {name: raw[name] / raw_total for name in names}
    # Bound movement relative to the baseline, then renormalize.
    limited = {
        name: min(baseline[name] + max_deviation, max(baseline[name] - max_deviation, proposed[name])) for name in names
    }
    limited_total = sum(limited.values())
    return {name: limited[name] / limited_total for name in names}
