"""Leakage-safe walk-forward runner for Power 6/55 Backtest V2."""
from __future__ import annotations

import ast
import random
from dataclasses import dataclass
from typing import Any, Callable, Sequence

import pandas as pd

from .backtest_v2 import PrizeConfig, BacktestSummary, summarize


@dataclass(frozen=True)
class Draw:
    date: Any
    main: tuple[int, ...]
    special: int


def parse_draw(row: dict[str, Any]) -> Draw:
    value = row["result"]
    if isinstance(value, str):
        value = ast.literal_eval(value)
    values = tuple(int(x) for x in value)
    if len(values) != 7:
        raise ValueError(f"Power 6/55 draw must contain 7 numbers, got {len(values)}")
    return Draw(row["date"], values[:6], values[6])


def _ticket_gain(ticket: Sequence[int], target: Draw, prizes: PrizeConfig) -> int:
    matches = len(set(ticket) & set(target.main))
    special_hit = matches == 5 and target.special in ticket
    if matches == 6:
        return prizes.jackpot1
    if matches == 5 and special_hit:
        return prizes.jackpot2
    if matches == 5:
        return prizes.first
    if matches == 4:
        return prizes.second
    if matches == 3:
        return prizes.third
    return 0


def walk_forward(
    name: str,
    rows: Sequence[dict[str, Any]],
    strategy_factory: Callable[[pd.DataFrame, Any], Any],
    tickets_per_draw: int = 30,
    seed: int = 0,
    prizes: PrizeConfig | None = None,
    min_history: int = 1,
) -> tuple[BacktestSummary, list[dict[str, Any]]]:
    """Generate tickets for each target draw from strictly prior main numbers."""
    prizes = prizes or PrizeConfig(tickets_per_draw=tickets_per_draw)
    draws = sorted((parse_draw(row) for row in rows), key=lambda d: d.date)
    random.seed(seed)
    evaluation_results: list[Sequence[int]] = []
    tickets_by_draw: list[list[Sequence[int]]] = []
    details: list[dict[str, Any]] = []

    for index in range(min_history, len(draws)):
        target = draws[index]
        history_df = pd.DataFrame([{"date": d.date, "result": list(d.main)} for d in draws[:index]])
        strategy = strategy_factory(history_df, target.date)
        tickets = [strategy.predict(target.date) for _ in range(tickets_per_draw)]
        draw_gain = sum(_ticket_gain(ticket, target, prizes) for ticket in tickets)
        evaluation_results.append(list(target.main) + [target.special])
        tickets_by_draw.append(tickets)
        details.append({"date": str(target.date), "gain_vnd": draw_gain, "cost_vnd": tickets_per_draw * prizes.ticket_price})

    summary = summarize(name, evaluation_results, tickets_by_draw, prizes)
    return summary, details
