"""Generate markdown research reports."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from . import LAB_NAME
from .hedging import format_guidance, recommend


def _table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def generate_report(
    df: pd.DataFrame,
    scorecard_df: pd.DataFrame,
    wf_is: pd.DataFrame,
    wf_oos: pd.DataFrame,
    cfg: dict,
    ticker: str,
) -> Path:
    report_dir = Path(__file__).resolve().parents[1] / cfg["reporting"]["report_dir"]
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / "usdmxn_regime_report.md"

    latest = df.iloc[-1]
    hedge = recommend(latest["regime"], "us_entity_long_mxn")
    best = scorecard_df.loc[scorecard_df["sharpe"].idxmax()]
    legacy = scorecard_df[scorecard_df["strategy"] == "legacy"].iloc[0]
    flat = scorecard_df[scorecard_df["strategy"] == "flat_range"].iloc[0]
    flat_beats = flat["sharpe"] > legacy["sharpe"] and flat["total_return_pct"] > legacy["total_return_pct"]

    body = f"""# USD/MXN Regime Research Report

**Generated:** {datetime.now():%Y-%m-%d %H:%M}  
**Ticker:** {ticker}  
**Period:** {df.index.min().date()} → {df.index.max().date()}  
**Bars:** {len(df)}

> Research only. Not investment advice. No live trading.

## Latest snapshot

| Field | Value |
|-------|-------|
| Date | {df.index[-1].date()} |
| Price | {latest['price']:.4f} |
| Regime | {latest['regime']} |
| MA20 | {latest['ma20']:.4f} |
| MA60 | {latest['ma60']:.4f} |

## Strategy scorecard (net of {cfg['backtest']['transaction_cost_bps']} bps turnover cost)

{_table(scorecard_df)}

**Best Sharpe:** `{best['strategy']}` ({best['sharpe']})  
**flat_range beats legacy (after costs):** {'Yes' if flat_beats else 'No'}

## Walk-forward (train {cfg['backtest']['train_years']}y / test {cfg['backtest']['test_years']}y)

### In-sample (train windows)
{_table(wf_is) if not wf_is.empty else '_Insufficient history for walk-forward._'}

### Out-of-sample (test windows)
{_table(wf_oos) if not wf_oos.empty else '_Insufficient history for walk-forward._'}

"""
    if not wf_is.empty and not wf_oos.empty:
        is_sh = wf_is.groupby("strategy")["sharpe"].mean()
        oos_sh = wf_oos.groupby("strategy")["sharpe"].mean()
        body += "### Walk-forward vs full-sample\n\n"
        for s in ["legacy", "flat_range"]:
            if s in is_sh.index and s in oos_sh.index:
                weaker = oos_sh[s] < is_sh[s]
                body += f"- **{s}:** mean train Sharpe {is_sh[s]:.3f}, mean OOS Sharpe {oos_sh[s]:.3f} — OOS {'weaker' if weaker else 'similar/better'} than in-sample\n"

    body += f"""
## Regime mix

"""
    mix = df["regime"].value_counts(normalize=True).mul(100).round(1)
    for reg, pct in mix.items():
        body += f"- {reg}: {pct}%\n"

    body += f"""
## Hedging guidance (US entity long MXN)

{format_guidance(hedge)}

## Limitations

- Rule-based regimes; no forward curve or live execution.
- Transaction costs are turnover-based bps only.
- Walk-forward requires long history; short samples bias results.

---
_{LAB_NAME}_
"""
    path.write_text(body, encoding="utf-8")
    return path
