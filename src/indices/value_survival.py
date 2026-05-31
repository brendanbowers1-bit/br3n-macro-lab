"""
BR3N Value Survival Index (VSI)

Measures how much economic value survives when money crosses borders.

VSI = 100 × Real Usable Value Delivered / Original Value Sent

Research-only. Not investment advice. Not a trading signal.
"""

from __future__ import annotations

import pandas as pd

from src.indices._utils import rank_series

# Payout friction defaults by method (% of sent value)
PAYOUT_FRICTION = {
    "bank_account": 0.001,
    "bank": 0.001,
    "mobile_wallet": 0.002,
    "cash_pickup": 0.005,
    "cash": 0.005,
    "unknown": 0.003,
}


def calculate_explicit_fee_loss(fee_pct: float) -> float:
    return max(float(fee_pct or 0), 0.0)


def calculate_fx_spread_loss(fx_margin_pct: float) -> float:
    return max(float(fx_margin_pct or 0), 0.0)


def calculate_timing_loss(transfer_speed_days: float, fx_daily_volatility: float) -> float:
    """
    Conservative placeholder: expected loss from FX exposure during transfer delay.

    timing_loss_pct = transfer_speed_days × fx_daily_volatility × 0.25
    """
    days = max(float(transfer_speed_days or 0), 0)
    vol = max(float(fx_daily_volatility or 0.01), 0.0001)
    return min(days * vol * 0.25, 0.05)


def calculate_volatility_loss(volatility_30d: float, hedge_access_score: float = 0.0) -> float:
    """
    Poor households usually cannot hedge (hedge_access_score ≈ 0).

    volatility_loss_pct = volatility_30d × (1 - hedge_access_score) × 0.10
    """
    vol = max(float(volatility_30d or 0), 0)
    hedge = min(max(float(hedge_access_score), 0), 1)
    return vol * (1 - hedge) * 0.10


def calculate_inflation_erosion(inflation_yoy: float, days_held: float = 30) -> float:
    """inflation_erosion_pct = inflation_yoy × days_held / 365"""
    infl = max(float(inflation_yoy or 0), 0)
    days = max(float(days_held or 30), 0)
    return infl * days / 365.0


def calculate_payout_friction(
    payout_method: str | None,
    manual_payout_friction_pct: float | None = None,
) -> float:
    if manual_payout_friction_pct is not None and pd.notna(manual_payout_friction_pct):
        return max(float(manual_payout_friction_pct), 0)
    key = str(payout_method or "unknown").lower().replace(" ", "_")
    for k, v in PAYOUT_FRICTION.items():
        if k in key:
            return v
    return PAYOUT_FRICTION["unknown"]


def calculate_dollar_dependency_drag(dollar_dependency_score: float) -> float:
    """drag_pct = dollar_dependency_score / 100 × 0.75"""
    score = min(max(float(dollar_dependency_score or 0), 0), 100)
    return score / 100.0 * 0.0075  # 0.75% at score=100, scaled as pct fraction


def calculate_trust_discount(currency_trust_score: float) -> float:
    """trust_discount_pct = (100 - currency_trust_score) / 100 × 1.00 (as fraction)"""
    score = min(max(float(currency_trust_score or 50), 0), 100)
    return (100 - score) / 100.0 * 0.01  # max ~1% discount at zero trust


def calculate_total_value_loss(row: pd.Series) -> float:
    components = [
        row.get("explicit_fee_loss_pct", 0),
        row.get("fx_spread_loss_pct", 0),
        row.get("timing_loss_pct", 0),
        row.get("volatility_loss_pct", 0),
        row.get("inflation_erosion_pct", 0),
        row.get("payout_friction_pct", 0),
        row.get("dollar_dependency_drag_pct", 0),
        row.get("trust_discount_pct", 0),
    ]
    return min(sum(float(c or 0) for c in components), 0.50)


def calculate_real_usable_value_delivered(total_value_loss_pct: float) -> float:
    return max(1.0 - float(total_value_loss_pct or 0), 0.0)


def calculate_vsi(real_usable_value_delivered_pct: float) -> float:
    """VSI = 100 × share of value that survives (already net of losses)."""
    return 100.0 * max(float(real_usable_value_delivered_pct or 0), 0.0)


def calculate_value_loss_usd_per_100(total_value_loss_pct: float) -> float:
    return 100.0 * float(total_value_loss_pct or 0)


def classify_vsi(vsi_score: float) -> str:
    v = float(vsi_score or 0)
    if v >= 95:
        return "High value survival"
    if v >= 90:
        return "Moderate value leakage"
    if v >= 80:
        return "High value leakage"
    return "Severe value destruction"


def _daily_vol_from_30d(volatility_30d: float) -> float:
    """Convert annualized 30d vol to approximate daily vol."""
    import numpy as np

    return float(volatility_30d or 0.12) / np.sqrt(252)


def calculate_vsi_row(row: pd.Series) -> dict:
    fee = calculate_explicit_fee_loss(row.get("fee_pct"))
    spread = calculate_fx_spread_loss(row.get("fx_margin_pct"))
    vol_30d = float(row.get("volatility_30d") or row.get("fx_volatility_30d") or 0.12)
    daily_vol = _daily_vol_from_30d(vol_30d)
    speed = float(row.get("transfer_speed_days") or 1)
    infl = float(row.get("inflation_yoy") or 0.05)
    hedge = float(row.get("hedge_access_score") or 0.0)

    timing = calculate_timing_loss(speed, daily_vol)
    vol_loss = calculate_volatility_loss(vol_30d, hedge)
    inflation = calculate_inflation_erosion(infl, days_held=speed + 1)
    payout = calculate_payout_friction(
        row.get("payout_method"),
        row.get("manual_payout_friction_pct"),
    )
    dollar_drag = calculate_dollar_dependency_drag(row.get("dollar_dependency_score", 50))
    trust = calculate_trust_discount(row.get("currency_trust_score", 50))

    comp = {
        "explicit_fee_loss_pct": fee,
        "fx_spread_loss_pct": spread,
        "timing_loss_pct": timing,
        "volatility_loss_pct": vol_loss,
        "inflation_erosion_pct": inflation,
        "payout_friction_pct": payout,
        "dollar_dependency_drag_pct": dollar_drag,
        "trust_discount_pct": trust,
    }
    total_loss = calculate_total_value_loss(pd.Series(comp))
    real_delivered = calculate_real_usable_value_delivered(total_loss)
    vsi = calculate_vsi(real_delivered)

    return {
        **comp,
        "total_value_loss_pct": total_loss,
        "real_usable_value_delivered_pct": real_delivered,
        "value_survival_index": vsi,
        "value_loss_usd_per_100": calculate_value_loss_usd_per_100(total_loss),
        "interpretation": classify_vsi(vsi),
    }


def calculate_vsi_for_corridors(
    corridor_prices: pd.DataFrame,
    fx_rates: pd.DataFrame | None = None,
    macro: pd.DataFrame | None = None,
    trust_scores: pd.DataFrame | None = None,
    dollar_dependency: pd.DataFrame | None = None,
    mock_data_flag: bool = False,
) -> pd.DataFrame:
    """Compute VSI for each corridor-price observation with full component breakdown."""
    df = corridor_prices.copy()
    if "year" not in df.columns and "date" in df.columns:
        df["year"] = pd.to_datetime(df["date"]).dt.year

    if fx_rates is not None and not fx_rates.empty:
        vol_map = (
            fx_rates.sort_values("date")
            .groupby("currency")["volatility_30d"]
            .last()
            .to_dict()
        )
        df["volatility_30d"] = df["receiver_currency"].map(vol_map).fillna(0.12)
        df["fx_volatility_30d"] = df["volatility_30d"]

    if macro is not None and not macro.empty:
        infl_map = (
            macro.sort_values("date")
            .groupby("country")["inflation_yoy"]
            .last()
            .to_dict()
        )
        df["inflation_yoy"] = df["receiver_country"].map(infl_map).fillna(0.05)

    if trust_scores is not None and not trust_scores.empty:
        trust_map = trust_scores.set_index("country")["currency_trust_score"].to_dict()
        df["currency_trust_score"] = df["receiver_country"].map(trust_map).fillna(50)

    if dollar_dependency is not None and not dollar_dependency.empty:
        dep_map = dollar_dependency.set_index("country")["dollar_dependency_score"].to_dict()
        df["dollar_dependency_score"] = df["receiver_country"].map(dep_map).fillna(50)

    components = df.apply(calculate_vsi_row, axis=1, result_type="expand")
    out = pd.concat([df, components], axis=1)

    out["original_value_sent_usd"] = out.get("send_amount_usd", 100.0)
    out["source"] = out.get("source", "vsi_pipeline")
    out["rank"] = rank_series(out["total_value_loss_pct"])

    cols = [
        "date", "year", "quarter", "corridor", "sender_country", "receiver_country",
        "original_value_sent_usd",
        "explicit_fee_loss_pct", "fx_spread_loss_pct", "timing_loss_pct",
        "volatility_loss_pct", "inflation_erosion_pct", "payout_friction_pct",
        "dollar_dependency_drag_pct", "trust_discount_pct",
        "total_value_loss_pct", "real_usable_value_delivered_pct",
        "value_survival_index", "value_loss_usd_per_100",
    "interpretation", "data_quality_score", "mock_data_flag", "data_mode", "limitations",
]
    existing = [c for c in cols if c in out.columns]
    return out[existing + [c for c in out.columns if c not in existing]]
