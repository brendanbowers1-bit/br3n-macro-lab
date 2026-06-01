"""Generate corridor intelligence brief markdown."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .risk_score import CorridorRiskScore


def generate_corridor_brief(
    df: pd.DataFrame,
    score: CorridorRiskScore,
    validation: dict,
) -> str:
    latest_row = df.iloc[-1]
    month_label = latest_row.get("month_label", str(latest_row["month"]))
    source = latest_row.get("source", "unknown")
    methodology = latest_row.get("methodology_version", score.methodology_version)

    comp_lines = "\n".join(
        f"| {name.replace('_', ' ').title()} | {val:.1f} | {score.weights[name]*100:.0f}% |"
        for name, val in score.components.items()
    )

    warnings = validation.get("warnings") or []
    warn_block = "\n".join(f"- {w}" for w in warnings) if warnings else "- None"

    return f"""# Bowers Frontier Macro Labs — Corridor Intelligence Brief

**Corridor:** {score.corridor}  
**As of:** {month_label} ({score.as_of_month})  
**Corridor Risk Score:** {score.score:.1f}/100 ({score.band})  
**Generated:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

> {score.disclaimer}

## Executive summary

Latest validated monthly remittance flow is **{score.metrics['latest_flow_usd_millions']:,.0f} USD millions**
({month_label}). Year-over-year change: **{score.metrics['yoy_pct']:+.1f}%**; month-over-month:
**{score.metrics['mom_pct']:+.1f}%**. Structural corridor stress is assessed as **{score.band}**
(CRS {score.score:.1f}/100).

## Data lineage

| Field | Value |
|-------|-------|
| Source | {source} |
| Methodology | {methodology} |
| Rows validated | {validation.get('row_count', len(df))} |
| Data quality score | {score.metrics['data_quality_score']:.0f}/100 |
| Validation passed | {validation.get('passed', False)} |

## Risk score breakdown

| Component | Score (0–100) | Weight |
|-----------|---------------|--------|
{comp_lines}

**Interpretation:** Higher component scores indicate elevated structural stress (momentum weakness,
flow volatility, distance from recent peak, or data-quality gaps). This is **not** a trading signal.

## Flow context

- Peak flow in series: {score.metrics['peak_flow_usd_millions']:,.0f} USD millions
- Drawdown from peak: {score.metrics['drawdown_from_peak_pct']:.1f}%
- 2025 YTD (if applicable): computed from validated monthly series in pipeline output JSON

## Validation notes

{warn_block}

## Limitations

- Starter Banxico-aligned research series; replace with live official feed when licensed.
- CRS describes remittance-flow structure only — not MXN spot, policy, or settlement outages.
- Research and treasury decision-support framing only. Not financial advice.
"""


def write_corridor_brief(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
