# Vietlott Power 6/55 ML Research

This directory contains experimental strategies and the canonical V2 benchmark.

## Canonical benchmark

`src/machine_learning/run_backtest_v2.py` is the research entrypoint. It evaluates strategies walk-forward using only the six main numbers as model inputs. The special number is retained only for prize evaluation.

The V2 benchmark uses 30 tickets per historical draw, 10,000 VND per ticket, Jackpot 1 30B VND, Jackpot 2 3B VND, First prize 40M VND, Second prize 500k VND, and Third prize 50k VND.

## Validation

The audit pipeline includes data normalization, unit/leakage tests, decay validation with a locked holdout, an independent random baseline, Monte Carlo testing, horizon-matched comparisons, paired per-draw comparisons, and bootstrap confidence intervals.

Historical backtest performance is descriptive only. It does not establish that future lottery results are predictable.

## Strategies

Current V2 benchmark strategies include Random, Pattern, PairFrequency, Markov, Bayesian, ExponentialDecay, LogisticProbability, RankEnsemble, PortfolioEnsemble, and UnseenSetGap.

`LogisticProbabilityStrategy` uses `SGDClassifier.partial_fit` for incremental walk-forward training so the benchmark remains computationally tractable without using future draws.

## Running locally

```bash
PYTHONPATH=src python -m src.machine_learning.normalize_power655
PYTHONPATH=src python -m src.machine_learning.run_decay_validation
PYTHONPATH=src python -m src.machine_learning.run_backtest_v2
PYTHONPATH=src python -m src.machine_learning.random_audit
PYTHONPATH=src python -m src.machine_learning.random_monte_carlo
PYTHONPATH=src python -m src.machine_learning.monte_carlo_significance
PYTHONPATH=src python -m src.machine_learning.paired_significance
```

For reproducibility, treat `artifacts/backtest_v2/` as the canonical generated evidence rather than legacy prediction reports.
