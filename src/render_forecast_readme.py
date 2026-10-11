#!/usr/bin/env python3
"""Render the current Power 6/55 forecast and realized evaluation into README.md.

This module intentionally uses only the Python standard library so it can run in
both the lightweight data-crawl workflow and the ML forecast workflow.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
START_MARKER = "## Predictions"
END_MARKER = "## 📊 Data Statistics"
SINGLE_MODELS = ("Bayesian", "ExponentialDecay", "LogisticProbability", "RankEnsemble")


def _read_json(path: Path) -> dict[str, Any] | None:
    """Read JSON, tolerating the literal \\n suffix written by older report runs."""
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        # Older evaluator versions wrote the two characters backslash + n at EOF.
        legacy_suffix = chr(92) + "n"
        if not text.endswith(legacy_suffix):
            raise
        value = json.loads(text[:-2].rstrip())
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def _numbers(values: Any) -> str:
    if not isinstance(values, list):
        return "—"
    try:
        return " ".join(f"{int(value):02d}" for value in values)
    except (TypeError, ValueError):
        return "—"


def _comma_numbers(values: Any) -> str:
    if not isinstance(values, list):
        return "—"
    try:
        return ", ".join(f"{int(value):02d}" for value in values)
    except (TypeError, ValueError):
        return "—"


def _money(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def _matches(ticket: Any, actual: Any) -> list[int]:
    if not isinstance(ticket, list) or not isinstance(actual, list):
        return []
    try:
        return sorted(set(int(x) for x in ticket) & set(int(x) for x in actual))
    except (TypeError, ValueError):
        return []


def _portfolio_table(
    strategy: str, strategy_result: dict[str, Any], actual: dict[str, Any]
) -> list[str]:
    tickets = strategy_result.get("forecast_numbers", [])
    ticket_results = strategy_result.get("ticket_results", [])
    lines = [
        f"<details><summary>{strategy} — {len(tickets)} tickets</summary>",
        "",
        "| # | Predicted numbers | Main matches | Matched main numbers | Special matched | Payout (VND) |",
        "|---:|---|---:|---|:---:|---:|",
    ]
    actual_main = actual.get("main", [])
    special = actual.get("special")
    for index, ticket in enumerate(tickets, start=1):
        result = ticket_results[index - 1] if index - 1 < len(ticket_results) else {}
        matched = _matches(ticket, actual_main)
        matches = result.get("main_matches", len(matched))
        special_match = result.get("special_match", special in ticket if isinstance(ticket, list) else False)
        payout = result.get("prize_vnd", 0)
        lines.append(
            f"| {index} | {_numbers(ticket)} | {matches}/6 | {_numbers(matched) if matched else '—'} "
            f"| {'Yes' if special_match else 'No'} | {_money(payout)} |"
        )
    lines.extend(["", "</details>", ""])
    return lines


def build_predictions_section(
    forecast: dict[str, Any] | None, report: dict[str, Any] | None
) -> str:
    """Build the README section from the upcoming forecast and evaluated history."""
    evaluated = report.get("evaluated_draws", []) if report else []
    pending = report.get("pending_target_draw_ids", []) if report else []
    summary = report.get("summary", {}) if report else {}
    lines = [
        START_MARKER,
        "",
        "Forecasts are experimental and provided for retrospective research only. "
        "Lottery draws are random; model outputs are not guarantees of future results.",
        "",
    ]

    if forecast:
        target_id = str(forecast.get("target_draw_id", "unknown"))
        target_date = str(forecast.get("target_draw_date", "date unavailable"))
        as_of = forecast.get("as_of_draw", {})
        generated = str(forecast.get("forecast_generated_at_utc", "unknown"))
        predictions = forecast.get("predictions", {})
        portfolio = predictions.get("PortfolioEnsemble", [])
        unseen = predictions.get("UnseenPortfolioEnsemble", [])
        lines.extend(
            [
                "### Next scheduled forecast",
                "",
                f"- **Target draw:** #{target_id} — {target_date}",
                f"- **Forecast generated (UTC):** {generated}",
                f"- **Historical cutoff:** draw **#{as_of.get('id', 'unknown')}** "
                f"({as_of.get('date', 'date unavailable')}); "
                f"{forecast.get('dataset_rows', 'unknown')} rows used",
                "- The special number is excluded from model features and is shown separately in results.",
                "",
                "#### Single-line model predictions",
                "",
                "| Model | Predicted main numbers |",
                "|---|---|",
            ]
        )
        for model in SINGLE_MODELS:
            if isinstance(predictions.get(model), list):
                lines.append(f"| {model} | {_numbers(predictions[model])} |")
        if portfolio or unseen:
            lines.extend(
                [
                    "",
                    f"#### 30-ticket portfolio — target #{target_id}",
                    "",
                    "| Ticket | PortfolioEnsemble | UnseenPortfolioEnsemble |",
                    "|---:|---|---|",
                ]
            )
            total = max(len(portfolio), len(unseen))
            for index in range(total):
                main_ticket = _numbers(portfolio[index]) if index < len(portfolio) else "—"
                unseen_ticket = _numbers(unseen[index]) if index < len(unseen) else "—"
                lines.append(f"| {index + 1:02d} | {main_ticket} | {unseen_ticket} |")
            pool = forecast.get("portfolio_candidate_pool", {}).get("pool", [])
            if pool:
                lines.extend(["", f"**Candidate pool ({len(pool)} numbers):** {_numbers(pool)}"])
        lines.extend(["", f"[Forecast JSON for draw #{target_id}](./artifacts/forecast/next_power655.json)", ""])

    if evaluated:
        evaluated = sorted(
            evaluated,
            key=lambda row: (str(row.get("target_draw_date", "")), str(row.get("target_draw_id", ""))),
        )
        latest = evaluated[-1]
        actual = latest.get("actual", {})
        lines.extend(
            [
                "### Latest evaluated forecast",
                "",
                f"- **Target draw:** #{latest.get('target_draw_id')} — {latest.get('target_draw_date')}",
                f"- **Forecast generated (UTC):** {latest.get('forecast_generated_at_utc', 'unknown')}",
                f"- **Actual main numbers:** {_numbers(actual.get('main', []))}",
                f"- **Actual special number:** {_numbers([actual.get('special')])}",
                "",
                "#### Single-line model results",
                "",
                "| Model | Predicted numbers | Main matches | Payout (VND) |",
                "|---|---|---:|---:|",
            ]
        )
        for model in SINGLE_MODELS:
            result = latest.get("single_models", {}).get(model)
            if result:
                lines.append(
                    f"| {model} | {_numbers(result.get('forecast_numbers'))} "
                    f"| {result.get('main_matches', 0)}/6 | {_money(result.get('prize_vnd', 0))} |"
                )

        for key, title in (
            ("portfolio_ensemble", "PortfolioEnsemble"),
            ("unseen_portfolio_ensemble", "UnseenPortfolioEnsemble"),
        ):
            result = latest.get(key)
            if result:
                lines.extend(["", f"#### {title} — ticket-by-ticket result", ""])
                lines.extend(_portfolio_table(title, result, actual))

        lines.extend(
            [
                "### Rolling realized results — latest 10 evaluated draws",
                "",
                "| Draw | Date | Actual main numbers | Special | Tickets with ≥3 main matches | Payout (VND) | Net (VND) | ROI |",
                "|---:|---|---|---:|---:|---:|---:|---:|",
            ]
        )
        for row in reversed(evaluated[-10:]):
            actual_row = row.get("actual", {})
            portfolio_result = row.get("portfolio_ensemble") or {}
            lines.append(
                f"| {row.get('target_draw_id')} | {row.get('target_draw_date')} "
                f"| {_numbers(actual_row.get('main', []))} | {_numbers([actual_row.get('special')])} "
                f"| {portfolio_result.get('tickets_ge3', 0)} | {_money(portfolio_result.get('gain_vnd', 0))} "
                f"| {_money(portfolio_result.get('net_profit_vnd', 0))} "
                f"| {portfolio_result.get('roi_pct', 0):.2f}% |"
            )

        lines.extend(
            [
                "",
                "### Aggregate portfolio performance",
                "",
                f"- **Evaluated draws:** {len(evaluated)}",
                f"- **Pending forecasts:** {len(pending)}",
                "",
                "| Strategy | Draws | Tickets | Tickets ≥3 | ≥3 rate | Payout (VND) | Cost (VND) | Net (VND) | ROI |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for name in ("PortfolioEnsemble", "UnseenPortfolioEnsemble"):
            item = summary.get(name)
            if not item:
                continue
            lines.append(
                f"| {name} | {item.get('draws_evaluated', 0)} | {item.get('tickets', 0)} "
                f"| {item.get('tickets_ge3', 0)} | {item.get('tickets_ge3_rate_pct', 0):.2f}% "
                f"| {_money(item.get('gain_vnd', 0))} | {_money(item.get('cost_vnd', 0))} "
                f"| {_money(item.get('net_profit_vnd', 0))} | {item.get('roi_pct', 0):.2f}% |"
            )
        lines.extend(
            [
                "",
                "Amounts assume 10,000 VND per ticket and the prize values recorded in the evaluation artifact. "
                "This observed sample does not establish a predictive advantage.",
            ]
        )

    lines.extend(
        [
            "",
            "**Reports and artifacts:** "
            "[Full ticket-level evaluation report](./artifacts/forecast/results/forecast_results.md) · "
            "[Machine-readable results](./artifacts/forecast/results/forecast_results.json) · "
            "[Forecast history](./artifacts/forecast/history/)",
            "",
        ]
    )
    return "\n".join(lines).rstrip()


def update_readme(root: Path | str | None = None) -> bool:
    """Replace only the README Predictions section, preserving all other sections."""
    root_path = Path(root).resolve() if root is not None else ROOT
    readme_path = root_path / "README.md"
    if not readme_path.exists():
        raise FileNotFoundError(f"README not found: {readme_path}")

    forecast = _read_json(root_path / "artifacts/forecast/next_power655.json")
    report = _read_json(root_path / "artifacts/forecast/results/forecast_results.json")
    if not forecast and not report:
        return False

    current = readme_path.read_text(encoding="utf-8")
    start = current.find(START_MARKER)
    end = current.find(END_MARKER, start + len(START_MARKER)) if start >= 0 else -1
    if start < 0 or end < 0:
        raise ValueError("README must contain the Predictions and Data Statistics section markers")

    section = build_predictions_section(forecast, report)
    updated = current[:start] + section + "\n\n" + current[end:]
    if updated != current:
        readme_path.write_text(updated, encoding="utf-8")
    return updated != current


def main() -> None:
    changed = update_readme()
    print("README forecast section updated." if changed else "README forecast section unchanged.")


if __name__ == "__main__":
    main()
