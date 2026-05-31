"""
Hidden FX Tax Index — measures the full burden of moving money across currencies.

Research-only. Transparent component breakdown required.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.indices._utils import interpret_burden, normalize_index, rank_series


def calculate_timing_risk(transfer_speed_days: float, fx_daily_volatility: float) -> float:
    """Timing risk grows with transfer delay and FX volatility."""
    days = max(float(transfer_speed_days or 0), 0)
    vol = max(float(fx_daily_volatility or 0.01), 0.001)
    return min(days * vol * np.sqrt(252) * 0.5, 0.05)


def calculate_inflation_erosion(inflation_yoy: float, days_held: float) -> float:
    infl = max(float(inflation_yoy or 0), 0)
    days = max(float(days_held or 1), 0)
    return infl * (days / 365.0) * 0.5


def calculate_volatility_penalty(volatility_30d: float, hedge_access_score: float = 0.3) -> float:
    vol = max(float(volatility_30d or 0.1), 0)
    hedge = min(max(float(hedge_access_score), 0), 1)
    return vol * (1 - hedge) * 0.15


def calculate_hidden_fx_tax(row: pd.Series) -> dict:
    fee = float(row.get("fee_pct") or 0)
    margin = float(row.get("fx_margin_pct") or 0)
    speed = float(row.get("transfer_speed_days") or 0)
    vol = float(row.get("volatility_30d") or row.get("fx_volatility_30d") or 0.12)
    infl = float(row.get("inflation_yoy") or 0.05)
    transparent = bool(row.get("transparency_flag", True))

    timing = calculate_timing_risk(speed, vol / np.sqrt(252))
    inflation_e = calculate_inflation_erosion(infl, speed + 1)
    vol_pen = calculate_volatility_penalty(vol)
    payout_friction = 0.01 if str(row.get("payout_method", "")).lower() == "cash" else 0.003
    transparency_pen = 0.0 if transparent else 0.008

    total = fee + margin + timing + inflation_e + vol_pen + payout_friction + transparency_pen
    return {
        "fee_pct": fee,
        "fx_margin_pct": margin,
        "timing_risk_pct": timing,
        "inflation_erosion_pct": inflation_e,
        "volatility_penalty_pct": vol_pen,
        "payout_friction_pct": payout_friction,
        "transparency_penalty_pct": transparency_pen,
        "hidden_fx_tax_pct": total,
    }


def calculate_hidden_fx_tax_table(
    corridor_prices: pd.DataFrame,
    fx_rates: pd.DataFrame | None = None,
    macro: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Compute Hidden FX Tax Index for all corridor-price rows."""
    df = corridor_prices.copy()
    if fx_rates is not None and not fx_rates.empty:
        vol_map = (
            fx_rates.sort_values("date")
            .groupby("currency")["volatility_30d"]
            .last()
            .to_dict()
        )
        df["volatility_30d"] = df["receiver_currency"].map(vol_map).fillna(0.12)
    if macro is not None and not macro.empty:
        infl_map = (
            macro.sort_values("date")
            .groupby("country")["inflation_yoy"]
            .last()
            .to_dict()
        )
        df["inflation_yoy"] = df["receiver_country"].map(infl_map).fillna(0.05)

    components = df.apply(calculate_hidden_fx_tax, axis=1, result_type="expand")
    out = pd.concat([df, components], axis=1)
    out["hidden_fx_tax_index_0_100"] = normalize_index(out["hidden_fx_tax_pct"])
    out["rank"] = rank_series(out["hidden_fx_tax_pct"])
    out["interpretation"] = out["hidden_fx_tax_index_0_100"].apply(interpret_burden)
    return out
