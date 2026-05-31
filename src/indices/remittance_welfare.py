"""
Remittance Welfare Loss Index — purchasing power lost between sender and recipient.
"""

from __future__ import annotations

import pandas as pd

from src.indices._utils import normalize_index, rank_series


def calculate_welfare_loss_row(
    gross_sent_usd: float,
    hidden_fx_tax_pct: float,
    cashout_loss_pct: float = 0.005,
) -> dict:
    explicit_fee = hidden_fx_tax_pct * 0.35  # approximate split from components
    fx_spread = hidden_fx_tax_pct * 0.35
    timing = hidden_fx_tax_pct * 0.15
    inflation = hidden_fx_tax_pct * 0.15
    total_loss_pct = min(hidden_fx_tax_pct + cashout_loss_pct, 0.25)
    real_delivered = gross_sent_usd * (1 - total_loss_pct)
    welfare_loss_pct = 1 - real_delivered / gross_sent_usd if gross_sent_usd > 0 else 0
    return {
        "gross_sent_usd": gross_sent_usd,
        "real_value_delivered_usd": real_delivered,
        "welfare_loss_pct": welfare_loss_pct,
        "real_value_delivered_pct": 1 - welfare_loss_pct,
        "explicit_fee_usd": gross_sent_usd * explicit_fee,
        "fx_spread_loss_usd": gross_sent_usd * fx_spread,
        "timing_loss_usd": gross_sent_usd * timing,
        "inflation_loss_usd": gross_sent_usd * inflation,
        "cashout_loss_usd": gross_sent_usd * cashout_loss_pct,
    }


def calculate_remittance_welfare_table(
    hidden_fx_tax: pd.DataFrame,
    remittance_flows: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate welfare loss by corridor using hidden FX tax and flow volumes."""
    hft = hidden_fx_tax.groupby("corridor", as_index=False).agg(
        hidden_fx_tax_pct=("hidden_fx_tax_pct", "mean"),
        date=("date", "max"),
    )
    flows = remittance_flows.groupby(["corridor", "year"], as_index=False).agg(
        remittance_usd=("remittance_usd", "sum"),
        corridor_weight=("corridor_weight", "mean"),
    )
    merged = flows.merge(hft, on="corridor", how="left")
    rows = []
    for _, row in merged.iterrows():
        wl = calculate_welfare_loss_row(
            float(row.get("remittance_usd", 0) / max(len(flows["year"].unique()), 1)),
            float(row.get("hidden_fx_tax_pct", 0.05)),
        )
        agg_loss = float(row.get("remittance_usd", 0)) * wl["welfare_loss_pct"]
        rows.append(
            {
                "corridor": row["corridor"],
                "year": row["year"],
                "date": row.get("date"),
                "remittance_usd": row["remittance_usd"],
                "hidden_fx_tax_pct": row.get("hidden_fx_tax_pct"),
                "welfare_loss_pct": wl["welfare_loss_pct"],
                "aggregate_welfare_loss_usd": agg_loss,
                "real_value_delivered_pct": wl["real_value_delivered_pct"],
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        out["welfare_loss_index_0_100"] = normalize_index(out["welfare_loss_pct"])
        out["rank"] = rank_series(out["aggregate_welfare_loss_usd"])
    return out
