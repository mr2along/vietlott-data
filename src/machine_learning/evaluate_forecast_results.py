"""Evaluate stored Power 6/55 forecasts against newly published draws."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

PRIZES = {"jackpot1": 30_000_000_000, "jackpot2": 3_000_000_000, "first": 40_000_000, "second": 500_000, "third": 50_000}
TICKET_PRICE = 10_000

def _load_draws(path: Path) -> dict[str, dict[str, Any]]:
    draws = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        row = json.loads(line)
        result = [int(x) for x in row.get("result", [])]
        ident = str(row.get("id", ""))
        if len(result) == 7 and ident.isdigit() and len(ident) == 5 and len(set(result[:6])) == 6 and all(1 <= x <= 55 for x in result) and result[6] not in result[:6]:
            draws[ident] = {"id": ident, "date": str(row["date"]), "main": result[:6], "special": result[6]}
    return draws

def _ticket_result(ticket, draw):
    ticket_set = set(int(x) for x in ticket)
    main_matches = len(ticket_set.intersection(draw["main"]))
    special_match = int(draw["special"]) in ticket_set
    if main_matches == 6: prize, kind = PRIZES["jackpot1"], "jackpot1"
    elif main_matches == 5 and special_match: prize, kind = PRIZES["jackpot2"], "jackpot2"
    elif main_matches == 5: prize, kind = PRIZES["first"], "first"
    elif main_matches == 4: prize, kind = PRIZES["second"], "second"
    elif main_matches == 3: prize, kind = PRIZES["third"], "third"
    else: prize, kind = 0, "none"
    return {"main_matches": main_matches, "special_match": special_match, "prize_vnd": prize, "prize_type": kind}

def _evaluate_tickets(tickets, draw):
    rows = [_ticket_result(ticket, draw) for ticket in tickets]
    gain = sum(x["prize_vnd"] for x in rows)
    return {
        "tickets": len(rows),
        "tickets_ge3": sum(x["main_matches"] >= 3 for x in rows),
        "tickets_ge3_rate_pct": sum(x["main_matches"] >= 3 for x in rows) / len(rows) * 100.0 if rows else 0.0,
        "tickets_ge4": sum(x["main_matches"] >= 4 for x in rows),
        "tickets_ge5": sum(x["main_matches"] >= 5 for x in rows),
        "jackpot1_hits": sum(x["prize_type"] == "jackpot1" for x in rows),
        "jackpot2_hits": sum(x["prize_type"] == "jackpot2" for x in rows),
        "match_histogram": {str(k): sum(x["main_matches"] == k for x in rows) for k in range(7)},
        "gain_vnd": gain,
        "cost_vnd": len(rows) * TICKET_PRICE,
        "net_profit_vnd": gain - len(rows) * TICKET_PRICE,
        "roi_pct": (gain - len(rows) * TICKET_PRICE) / (len(rows) * TICKET_PRICE) * 100.0 if rows else 0.0,
        "ticket_results": rows,
    }

def main():
    root = Path.cwd()
    history_dir = root / "artifacts/forecast/history"
    out = root / "artifacts/forecast/results"
    out.mkdir(parents=True, exist_ok=True)
    draws = _load_draws(root / "data/power655.jsonl")
    evaluated, pending = [], []

    for path in sorted(history_dir.glob("forecast_*.json")) if history_dir.exists() else []:
        payload = json.loads(path.read_text(encoding="utf-8"))
        target_id = str(payload.get("target_draw_id", ""))
        if target_id not in draws:
            pending.append(target_id)
            continue
        draw = draws[target_id]
        predictions = payload.get("predictions", {})
        row = {
            "target_draw_id": target_id,
            "target_draw_date": payload.get("target_draw_date"),
            "forecast_generated_at_utc": payload.get("forecast_generated_at_utc"),
            "actual": draw,
            "portfolio_ensemble": _evaluate_tickets(predictions.get("PortfolioEnsemble", []), draw) if predictions.get("PortfolioEnsemble") else None,
            "unseen_portfolio_ensemble": _evaluate_tickets(predictions.get("UnseenPortfolioEnsemble", []), draw) if predictions.get("UnseenPortfolioEnsemble") else None,
            "single_models": {},
        }
        for name in ("Bayesian", "ExponentialDecay", "LogisticProbability", "RankEnsemble"):
            ticket = predictions.get(name)
            if isinstance(ticket, list) and len(ticket) == 6:
                row["single_models"][name] = _ticket_result(ticket, draw)
        evaluated.append(row)

    evaluated.sort(key=lambda x: (str(x.get("target_draw_date")), x["target_draw_id"]))

    def aggregate(key):
        rows = [x[key] for x in evaluated if x.get(key)]
        tickets = sum(x["tickets"] for x in rows)
        gain = sum(x["gain_vnd"] for x in rows)
        cost = sum(x["cost_vnd"] for x in rows)
        return {
            "draws_evaluated": len(rows),
            "tickets": tickets,
            "tickets_ge3": sum(x["tickets_ge3"] for x in rows),
            "tickets_ge3_rate_pct": sum(x["tickets_ge3"] for x in rows) / tickets * 100.0 if tickets else 0.0,
            "tickets_ge4": sum(x["tickets_ge4"] for x in rows),
            "tickets_ge5": sum(x["tickets_ge5"] for x in rows),
            "jackpot1_hits": sum(x["jackpot1_hits"] for x in rows),
            "jackpot2_hits": sum(x["jackpot2_hits"] for x in rows),
            "gain_vnd": gain,
            "cost_vnd": cost,
            "net_profit_vnd": gain - cost,
            "roi_pct": (gain - cost) / cost * 100.0 if cost else 0.0,
        }

    report = {
        "report_version": 1,
        "evaluated_draws": evaluated,
        "pending_target_draw_ids": sorted(set(x for x in pending if x)),
        "summary": {
            "PortfolioEnsemble": aggregate("portfolio_ensemble"),
            "UnseenPortfolioEnsemble": aggregate("unseen_portfolio_ensemble"),
        },
        "method": {
            "ticket_price_vnd": TICKET_PRICE,
            "ge3_definition": "at least 3 main numbers",
            "jackpot2_definition": "5 main numbers + special number",
            "special_used_only_for_prize": True,
        },
    }
    (out / "forecast_results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = ["# Power 6/55 Forecast Results", "", f"- Evaluated draws: **{len(evaluated)}**", f"- Pending forecasts: **{len(report['pending_target_draw_ids'])}**", "", "| Strategy | Draws | Tickets | >=3 | >=3 rate | Gain (VND) | Net (VND) | ROI |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name in ("PortfolioEnsemble", "UnseenPortfolioEnsemble"):
        x = report["summary"][name]
        md.append(f"| {name} | {x['draws_evaluated']} | {x['tickets']} | {x['tickets_ge3']} | {x['tickets_ge3_rate_pct']:.2f}% | {x['gain_vnd']:,} | {x['net_profit_vnd']:,} | {x['roi_pct']:.2f}% |")
    md += ["", "## Latest evaluated draws", "", "| Draw | Date | Actual main | Portfolio >=3 | Portfolio gain |", "|---:|---|---|---:|---:|"]
    for row in reversed(evaluated[-10:]):
        p = row.get("portfolio_ensemble") or {}
        md.append(f"| {row['target_draw_id']} | {row.get('target_draw_date')} | {row['actual']['main']} | {p.get('tickets_ge3', 0)} | {p.get('gain_vnd', 0):,} |")
    (out / "forecast_results.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
