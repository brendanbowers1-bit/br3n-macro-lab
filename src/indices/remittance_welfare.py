"""
Remittance Welfare Loss — aggregate value lost when remittances cross borders.

Uses VSI / total value loss estimates × annual corridor volumes.
"""

from __future__ import annotations

import pandas as pd

from src.indices._utils import normalize_index, rank_series

REMITTANCE_WELFARE_LIMITATIONS = (
    "Aggregate USD losses multiply VSI estimates by KNOMAD-style flow volumes. "
    "Flows and loss rates are research estimates — not official household survey data."
)


def calculate_aggregate_value_loss(
    annual_remittance_usd: float,
    total_value_loss_pct: float,
) -> float:
    return float(annual_remittance_usd or 0) * float(total_value_loss_pct or 0)


def calculate_real_value_delivered(
    annual_remittance_usd: float,
    real_usable_value_delivered_pct: float,
) -> float:
    return float(annual_remittance_usd or 0) * float(real_usable_value_delivered_pct or 0)


def calculate_welfare_loss_row(
    gross_sent_usd: float,
    hidden_fx_tax_pct: float,
    cashout_loss_pct: float = 0.005,
) -> dict:
    explicit_fee = hidden_fx_tax_pct * 0.35
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


def calculate_remittance_welfare_from_vsi(
    vsi_outputs: pd.DataFrame,
    remittance_flows: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate welfare loss using full VSI loss estimates."""
    vsi_agg = vsi_outputs.groupby("corridor", as_index=False).agg(
        total_value_loss_pct=("total_value_loss_pct", "mean"),
        real_usable_value_delivered_pct=("real_usable_value_delivered_pct", "mean"),
        value_survival_index=("value_survival_index", "mean"),
        date=("date", "max"),
    )
    flows = remittance_flows.groupby(["corridor", "year"], as_index=False).agg(
        remittance_usd=("remittance_usd", "sum"),
        corridor_weight=("corridor_weight", "mean"),
    )
    merged = flows.merge(vsi_agg, on="corridor", how="left")
    rows = []
    for _, row in merged.iterrows():
        annual = float(row.get("remittance_usd", 0))
        loss_pct = float(row.get("total_value_loss_pct", 0.05))
        real_pct = float(row.get("real_usable_value_delivered_pct", 1 - loss_pct))
        rows.append(
            {
                "corridor": row["corridor"],
                "year": row["year"],
                "date": row.get("date"),
                "annual_remittance_usd": annual,
                "total_value_loss_pct": loss_pct,
                "aggregate_value_loss_usd": calculate_aggregate_value_loss(annual, loss_pct),
                "real_value_delivered_usd": calculate_real_value_delivered(annual, real_pct),
                "real_usable_value_delivered_pct": real_pct,
                "vsi_score": row.get("value_survival_index"),
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        out["rank"] = rank_series(out["aggregate_value_loss_usd"])
    return out


def rank_corridors_by_welfare_loss(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return df.sort_values("aggregate_value_loss_usd", ascending=False)


def calculate_remittance_welfare_table(
    hidden_fx_tax: pd.DataFrame,
    remittance_flows: pd.DataFrame,
    vsi_outputs: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Aggregate welfare loss by corridor. Prefers VSI outputs when provided."""
    if vsi_outputs is not None and not vsi_outputs.empty:
        return calculate_remittance_welfare_from_vsi(vsi_outputs, remittance_flows)

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
            float(row.get("remittance_usd", 0)),
            float(row.get("hidden_fx_tax_pct", 0.05)),
        )
        agg_loss = float(row.get("remittance_usd", 0)) * wl["welfare_loss_pct"]
        rows.append(
            {
                "corridor": row["corridor"],
                "year": row["year"],
                "date": row.get("date"),
                "annual_remittance_usd": row["remittance_usd"],
                "remittance_usd": row["remittance_usd"],
                "hidden_fx_tax_pct": row.get("hidden_fx_tax_pct"),
                "welfare_loss_pct": wl["welfare_loss_pct"],
                "aggregate_welfare_loss_usd": agg_loss,
                "aggregate_value_loss_usd": agg_loss,
                "real_value_delivered_usd": wl["real_value_delivered_usd"],
                "real_value_delivered_pct": wl["real_value_delivered_pct"],
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        out["welfare_loss_index_0_100"] = normalize_index(out["welfare_loss_pct"])
        out["rank"] = rank_series(out["aggregate_welfare_loss_usd"])
    return out
