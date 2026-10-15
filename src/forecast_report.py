"""Render forecast predictions and realized outcomes into the repository README.

This module intentionally depends only on the Python standard library so the
daily data-crawl workflow can render the README without installing ML extras.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    """Read a JSON object, returning an empty mapping if it is absent or invalid."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _latest_draw_id(path: Path) -> int | None:
    """Return the largest valid numeric draw ID in the raw JSONL file."""
    if not path.exists():
        return None
    ids: list[int] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            ident = str(json.loads(line).get("id", ""))
        except json.JSONDecodeError:
            continue
        if ident.isdigit():
            ids.append(int(ident))
    return max(ids) if ids else None


def _draw_id(value: Any) -> str:
    text = str(value or "")
    return f"{int(text):05d}" if text.isdigit() else text


def _numbers(values: Any) -> str:
    if not isinstance(values, list):
        return "—"
    try:
        return ", ".join(f"{int(number):02d}" for number in sorted(int(x) for x in values))
    except (TypeError, ValueError):
        return "—"


def _money(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def _portfolio_rows(tickets: Any, results: Any, actual_main: list[int], special: int) -> list[str]:
    """Render a ticket-by-ticket outcome table for one strategy."""
    tickets = tickets if isinstance(tickets, list) else []
    results = results if isinstance(results, list) else []
    lines = [
        "| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |",
        "|---:|---|---:|---|---|---:|---|",
    ]
    actual_set = set(actual_main)
    for index, ticket in enumerate(tickets):
        try:
            normalized = [int(number) for number in ticket]
        except (TypeError, ValueError):
            continue
        result = results[index] if index < len(results) and isinstance(results[index], dict) else {}
        matched = sorted(set(normalized) & actual_set)
        main_matches = int(result.get("main_matches", len(matched)))
        special_hit = bool(result.get("special_match", special in normalized))
        prize_type = str(result.get("prize_type", "none"))
        lines.append(
            f"| {index + 1} | {_numbers(normalized)} | {main_matches}/6 | "
            f"{_numbers(matched) if matched else '—'} | {'Yes' if special_hit else 'No'} | "
            f"{_money(result.get('prize_vnd', 0))} | {prize_type} |"
        )
    if not tickets:
        lines.append("| — | No ticket forecast recorded | — | — | — | 0 | — |")
    return lines


def _upcoming_section(payload: dict[str, Any], latest_draw_id: int | None) -> list[str]:
    """Render the upcoming forecast only when it targets the next draw."""
    predictions = payload.get("predictions")
    if not isinstance(predictions, dict) or not predictions:
        return ["### Next-draw forecast", "", "> No usable next-draw forecast is available yet.", ""]

    target = int(payload.get("target_draw_id", 0) or 0)
    if latest_draw_id is not None and target != latest_draw_id + 1:
        expected = _draw_id(latest_draw_id + 1)
        return [
            "### Next-draw forecast",
            "",
            (
                f"> The stored forecast targets draw **#{_draw_id(target)}**, but the latest result "
                f"loaded is **#{_draw_id(latest_draw_id)}**. The forecast is not presented as upcoming; "
                f"the next expected target is **#{expected}**."
            ),
            "",
        ]

    as_of = payload.get("as_of_draw") if isinstance(payload.get("as_of_draw"), dict) else {}
    lines = [
        f"### Next-draw forecast — draw **#{_draw_id(target)}**",
        "",
        (
            f"- **Target date:** {payload.get('target_draw_date', 'unknown')} "
            f"({payload.get('target_draw_weekday', 'unknown')})"
        ),
        f"- **Data cutoff:** draw #{_draw_id(as_of.get('id'))} dated {as_of.get('date', 'unknown')}",
        f"- **Generated (UTC):** {payload.get('forecast_generated_at_utc', 'unknown')}",
        "",
        "These are research forecasts, not guaranteed outcomes. The special number is excluded from model features.",
        "",
        "#### Single-line model predictions",
        "",
        "| Model | Predicted numbers |",
        "|---|---|",
    ]
    for name in (
        "Bayesian", "ExponentialDecay", "LogisticProbability", "RankEnsemble",
        "PositionWiseEnsemble",
    ):
        if predictions.get(name):
            lines.append(f"| {name} | {_numbers(predictions[name])} |")

    analysis = payload.get("positionwise_analysis")
    positions = analysis.get("positions", []) if isinstance(analysis, dict) else []
    if isinstance(positions, list) and positions:
        lines += [
            "",
            "#### Position-by-position forecast",
            "",
            (
                "Each slot is trained on that same sorted position in previous draws. "
                "The final combination is constrained to six distinct, increasing numbers."
            ),
            "",
            "| Position | Selected number | Highest-scoring candidates from that position |",
            "|---:|---:|---|",
        ]
        for item in positions:
            if not isinstance(item, dict):
                continue
            candidates = item.get("top_candidates", [])
            candidate_text = ", ".join(
                f"{int(candidate['number']):02d} ({float(candidate['score']):.4f})"
                for candidate in candidates
                if isinstance(candidate, dict)
                and str(candidate.get("number", "")).isdigit()
                and isinstance(candidate.get("score"), (int, float))
            )
            lines.append(
                f"| {item.get('position', '—')} | {int(item.get('selected_number', 0)):02d} | "
                f"{candidate_text or '—'} |"
            )

    comparison = payload.get("positionwise_model_comparison")
    components = comparison.get("components", {}) if isinstance(comparison, dict) else {}
    component_names = [
        "PositionWiseBayesian",
        "PositionWiseExponentialDecay",
        "PositionWiseRecent",
        "PositionWiseEnsemble",
    ]
    if isinstance(components, dict) and any(name in components for name in component_names):
        lines += [
            "",
            "#### Compare previous model families at each sorted position",
            "",
            "Each component below is recalculated from the historical value at the same sorted position; it is not simply the original unordered six-number ranking.",
            "",
            "| Position | Bayesian slot model | Exponential-decay slot model | Recent-slot model | Position-wise ensemble |",
            "|---:|---:|---:|---:|---:|",
        ]
        for index in range(6):
            values = []
            for name in component_names:
                component = components.get(name, {})
                numbers = component.get("predicted_numbers", []) if isinstance(component, dict) else []
                values.append(f"{int(numbers[index]):02d}" if len(numbers) > index else "—")
            lines.append(f"| {index + 1} | {values[0]} | {values[1]} | {values[2]} | {values[3]} |")

    for name, label in (
        ("PortfolioEnsemble", "PortfolioEnsemble"),
        ("UnseenPortfolioEnsemble", "UnseenPortfolioEnsemble"),
    ):
        tickets = predictions.get(name, [])
        lines += [
            "",
            "<details>",
            f"<summary>{label} — {len(tickets)} ticket combinations</summary>",
            "",
            "| # | Predicted combination |",
            "|---:|---|",
        ]
        for index, ticket in enumerate(tickets, start=1):
            lines.append(f"| {index} | {_numbers(ticket)} |")
        lines += ["", "</details>", ""]
    return lines


def _evaluated_section(report: dict[str, Any]) -> list[str]:
    """Render aggregate, rolling and expandable per-draw evaluation details."""
    evaluated = report.get("evaluated_draws", [])
    evaluated = evaluated if isinstance(evaluated, list) else []
    evaluated.sort(key=lambda row: (str(row.get("target_draw_date", "")), str(row.get("target_draw_id", ""))))
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    pending = report.get("pending_target_draw_ids", [])
    pending = sorted({_draw_id(value) for value in pending if str(value).isdigit()})

    lines = [
        "### Realized forecast results",
        "",
        (
            f"Completed forecasts: **{len(evaluated)}**; pending forecasts: **{len(pending)}**. "
            "A small historical sample does not establish predictive advantage."
        ),
        "",
        "| Strategy | Draws | Tickets | Tickets with ≥3 matches | ≥3-match rate | Payout (VND) | Net (VND) | ROI |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key, label in (
        ("PortfolioEnsemble", "PortfolioEnsemble"),
        ("UnseenPortfolioEnsemble", "UnseenPortfolioEnsemble"),
    ):
        item = summary.get(key, {}) if isinstance(summary.get(key), dict) else {}
        lines.append(
            f"| {label} | {item.get('draws_evaluated', 0)} | {item.get('tickets', 0)} | "
            f"{item.get('tickets_ge3', 0)} | {float(item.get('tickets_ge3_rate_pct', 0.0)):.2f}% | "
            f"{_money(item.get('gain_vnd', 0))} | {_money(item.get('net_profit_vnd', 0))} | "
            f"{float(item.get('roi_pct', 0.0)):.2f}% |"
        )
    lines += [
        "",
        "Ticket cost is assumed to be 10,000 VND. Payouts use the configured prize values in the evaluator.",
        "",
        "#### Rolling results — latest 10 evaluated draws",
        "",
        "| Draw | Date | Actual main numbers | Special | Portfolio tickets ≥3 | Payout (VND) | Net (VND) |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for row in reversed(evaluated[-10:]):
        portfolio = row.get("portfolio_ensemble") or {}
        actual = row.get("actual") or {}
        cost = int(portfolio.get("cost_vnd", 0) or 0)
        gain = int(portfolio.get("gain_vnd", 0) or 0)
        lines.append(
            f"| {_draw_id(row.get('target_draw_id'))} | {row.get('target_draw_date', '—')} | "
            f"{_numbers(actual.get('main'))} | {actual.get('special', '—')} | "
            f"{portfolio.get('tickets_ge3', 0)} | {_money(gain)} | {_money(gain - cost)} |"
        )

    lines += ["", "#### Forecast sequence and outcome for each evaluated draw", ""]
    if not evaluated:
        lines += ["> No completed forecast has been evaluated yet.", ""]
    for row in reversed(evaluated):
        actual = row.get("actual") or {}
        actual_main = [int(x) for x in actual.get("main", [])]
        special = int(actual.get("special", 0) or 0)
        portfolio = row.get("portfolio_ensemble") or {}
        lines += [
            "<details>",
            (
                f"<summary>Draw #{_draw_id(row.get('target_draw_id'))} — {row.get('target_draw_date', 'unknown')} "
                f"| actual: {_numbers(actual_main)} | ≥3-match tickets: {portfolio.get('tickets_ge3', 0)} "
                f"| payout: {_money(portfolio.get('gain_vnd', 0))} VND</summary>"
            ),
            "",
            f"- Forecast generated (UTC): {row.get('forecast_generated_at_utc', 'unknown')}",
            f"- Actual main numbers: **{_numbers(actual_main)}**",
            f"- Actual special number: **{special:02d}**",
            "",
            "**Single-line model predictions and outcomes**",
            "",
            "| Model | Forecast numbers | Main matches | Matched numbers | Payout (VND) | Prize |",
            "|---|---|---:|---|---:|---|",
        ]
        models = row.get("single_models", {}) if isinstance(row.get("single_models"), dict) else {}
        for name in (
            "Bayesian", "ExponentialDecay", "LogisticProbability", "RankEnsemble",
            "PositionWiseEnsemble",
        ):
            result = models.get(name)
            if not isinstance(result, dict):
                continue
            forecast_numbers = result.get("forecast_numbers", [])
            matched = sorted(set(int(x) for x in forecast_numbers) & set(actual_main))
            lines.append(
                f"| {name} | {_numbers(forecast_numbers)} | {result.get('main_matches', len(matched))}/6 | "
                f"{_numbers(matched) if matched else '—'} | {_money(result.get('prize_vnd', 0))} | "
                f"{result.get('prize_type', 'none')} |"
            )

        positionwise = row.get("positionwise_analysis")
        positionwise_positions = (
            positionwise.get("positions", []) if isinstance(positionwise, dict) else []
        )
        positionwise_result = models.get("PositionWiseEnsemble")
        forecast_by_position = (
            positionwise_result.get("forecast_numbers", [])
            if isinstance(positionwise_result, dict) else []
        )
        if positionwise_positions and len(forecast_by_position) == 6 and len(actual_main) == 6:
            actual_by_position = sorted(actual_main)
            lines += [
                "",
                "**Position-by-position outcome — PositionWiseEnsemble**",
                "",
                "| Position | Forecast | Actual at same position | Exact position hit | Top candidates at forecast time |",
                "|---:|---:|---:|---|---|",
            ]
            for item in positionwise_positions:
                if not isinstance(item, dict):
                    continue
                index = int(item.get("position", 0)) - 1
                if not 0 <= index < 6:
                    continue
                candidates = item.get("top_candidates", [])
                candidate_text = ", ".join(
                    f"{int(candidate['number']):02d} ({float(candidate['score']):.4f})"
                    for candidate in candidates
                    if isinstance(candidate, dict)
                    and str(candidate.get("number", "")).isdigit()
                    and isinstance(candidate.get("score"), (int, float))
                )
                forecast_number = int(forecast_by_position[index])
                actual_number = actual_by_position[index]
                lines.append(
                    f"| {index + 1} | {forecast_number:02d} | {actual_number:02d} | "
                    f"{'Yes' if forecast_number == actual_number else 'No'} | {candidate_text or '—'} |"
                )

        for key, label in (
            ("portfolio_ensemble", "PortfolioEnsemble"),
            ("unseen_portfolio_ensemble", "UnseenPortfolioEnsemble"),
        ):
            strategy = row.get(key) or {}
            lines += [
                "",
                f"**{label} — {len(strategy.get('forecast_numbers', []))} tickets**",
                "",
            ]
            lines += _portfolio_rows(
                strategy.get("forecast_numbers", []),
                strategy.get("ticket_results", []),
                actual_main,
                special,
            )
        lines += ["", "</details>", ""]
    lines += [
        "**Machine-readable and full reports:** "
        "[Evaluation JSON](./artifacts/forecast/results/forecast_results.json) · "
        "[Evaluation Markdown](./artifacts/forecast/results/forecast_results.md) · "
        "[Latest forecast JSON](./artifacts/forecast/next_power655.json)",
        "",
    ]
    return lines


def generate_forecast_section(root: Path | None = None) -> str:
    """Build the README's Predictions section from archived forecasts and evaluations."""
    root = root or Path.cwd()
    latest_draw_id = _latest_draw_id(root / "data/power655.jsonl")
    forecast = _read_json(root / "artifacts/forecast/next_power655.json")
    results = _read_json(root / "artifacts/forecast/results/forecast_results.json")

    lines = [
        (
            "Forecasts are published for research and retrospective evaluation only. Lottery draws "
            "are random; model outputs do not guarantee future results."
        ),
        "",
    ]
    lines.extend(_upcoming_section(forecast, latest_draw_id))
    lines.extend(_evaluated_section(results))
    return "\n".join(lines).rstrip() + "\n"
