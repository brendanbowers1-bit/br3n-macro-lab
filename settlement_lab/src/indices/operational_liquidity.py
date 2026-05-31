"""
Operational Liquidity Burden (OLB) — capital trapped to support settlement.

Research-only. Not financial advice.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import LAB_LIMITATIONS, METHODOLOGY_VERSION

OLB_LIMITATIONS = (
    "OLB estimates liquidity opportunity cost from prefunding, collateral, and buffers. "
    + LAB_LIMITATIONS
)


def calculate_operational_liquidity_row(row: pd.Series) -> dict:
    prefund = float(row.get("prefunding_required_usd", 0) or 0)
    collateral = float(row.get("collateral_required_usd", 0) or 0)
    balance = float(row.get("settlement_account_balance_usd", 0) or 0)
    buffer = float(row.get("liquidity_buffer_usd", 0) or 0)
    intraday = float(row.get("intraday_credit_used_usd", 0) or 0)
    coc = float(row.get("cost_of_capital_pct", 0.05) or 0.05)
    adv = float(row.get("average_daily_settlement_value_usd", 1) or 1)

    required = prefund + collateral + balance + buffer
    intraday_cost = intraday * coc / 365
    opp_cost = required * coc
    ratio = required / adv if adv > 0 else 0.0
    per_100 = (opp_cost / adv * 100) if adv > 0 else 0.0
    score = max(0, 100 - min(100, ratio * 50 + per_100))

    return {
        "required_liquidity_usd": required,
        "liquidity_opportunity_cost_usd": opp_cost,
        "intraday_credit_cost_usd": intraday_cost,
        "liquidity_burden_ratio": ratio,
        "liquidity_cost_per_100": per_100,
        "operational_liquidity_burden_score": score,
        "interpretation": "High trapped liquidity" if ratio > 0.3 else "Moderate liquidity burden" if ratio > 0.15 else "Efficient liquidity (estimated)",
        "methodology_version": METHODOLOGY_VERSION,
        "limitations": OLB_LIMITATIONS,
        "data_quality_score": row.get("data_quality_score"),
        "mock_data_flag": row.get("mock_data_flag", False),
    }


def calculate_operational_liquidity_table(liquidity: pd.DataFrame) -> pd.DataFrame:
    if liquidity.empty:
        return pd.DataFrame()
    rows = []
    for _, row in liquidity.iterrows():
        calc = calculate_operational_liquidity_row(row)
        calc["entity"] = row.get("payment_system", "unknown")
        calc["entity_type"] = "payment_system"
        calc["country"] = row.get("country", "")
        calc["payment_system"] = row.get("payment_system", "")
        rows.append({**row.to_dict(), **calc})
    return pd.DataFrame(rows)
