"""
Hidden FX Tax Index — VSI sub-index for transfer frictions.

Hidden FX Tax = explicit fee + FX margin + timing + volatility + payout friction

Research-only. Transparent component breakdown required.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.indices._utils import interpret_burden, normalize_index, rank_series
from src.indices.value_survival import (
    calculate_explicit_fee_loss,
    calculate_fx_spread_loss,
    calculate_payout_friction,
    calculate_timing_loss,
    calculate_volatility_loss,
)


HIDDEN_FX_TAX_LIMITATIONS = (
    "Sub-index of VSI — excludes inflation, trust, and dollar drag. "
    "Timing and volatility penalties use starter formulas. Not a trading signal."
)


def calculate_timing_risk(transfer_speed_days: float, fx_daily_volatility: float) -> float:
    """Timing risk grows with transfer delay and FX volatility (legacy helper)."""
    return calculate_timing_loss(transfer_speed_days, fx_daily_volatility)


def calculate_inflation_erosion(inflation_yoy: float, days_held: float) -> float:
    from src.indices.value_survival import calculate_inflation_erosion as _ce

    return _ce(inflation_yoy, days_held)


def calculate_volatility_penalty(volatility_30d: float, hedge_access_score: float = 0.0) -> float:
    return calculate_volatility_loss(volatility_30d, hedge_access_score)


def calculate_hidden_fx_tax(row: pd.Series) -> dict:
    """VSI sub-index: fee + spread + timing + volatility + payout friction."""
    vol_30d = float(row.get("volatility_30d") or row.get("fx_volatility_30d") or 0.12)
    daily_vol = vol_30d / np.sqrt(252)
    fee = calculate_explicit_fee_loss(row.get("fee_pct"))
    margin = calculate_fx_spread_loss(row.get("fx_margin_pct"))
    timing = calculate_timing_loss(row.get("transfer_speed_days"), daily_vol)
    vol_loss = calculate_volatility_loss(vol_30d, row.get("hedge_access_score", 0))
    payout = calculate_payout_friction(row.get("payout_method"), row.get("manual_payout_friction_pct"))
    total = fee + margin + timing + vol_loss + payout
    return {
        "fee_pct": fee,
        "fx_margin_pct": margin,
        "timing_risk_pct": timing,
        "volatility_penalty_pct": vol_loss,
        "payout_friction_pct": payout,
        "hidden_fx_tax_pct": total,
    }


def rank_corridors_by_hidden_fx_tax(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    agg = df.groupby("corridor", as_index=False).agg(
        hidden_fx_tax_pct=("hidden_fx_tax_pct", "mean"),
        fee_pct=("fee_pct", "mean"),
        fx_margin_pct=("fx_margin_pct", "mean"),
        timing_risk_pct=("timing_risk_pct", "mean"),
        volatility_penalty_pct=("volatility_penalty_pct", "mean"),
        payout_friction_pct=("payout_friction_pct", "mean"),
    )
    agg["rank"] = rank_series(agg["hidden_fx_tax_pct"])
    return agg.sort_values("hidden_fx_tax_pct", ascending=False)


def explain_hidden_fx_tax(row: pd.Series) -> str:
    corridor = row.get("corridor", "Unknown corridor")
    total = float(row.get("hidden_fx_tax_pct", 0)) * 100
    fee = float(row.get("fee_pct", 0)) * 100
    margin = float(row.get("fx_margin_pct", 0)) * 100
    timing = float(row.get("timing_risk_pct", 0)) * 100
    vol = float(row.get("volatility_penalty_pct", 0)) * 100
    payout = float(row.get("payout_friction_pct", 0)) * 100
    return (
        f"{corridor}: hidden FX tax ≈ {total:.2f}% of sent value "
        f"(fee {fee:.2f}%, spread {margin:.2f}%, timing {timing:.2f}%, "
        f"volatility {vol:.2f}%, payout {payout:.2f}%). "
        "Sub-index of VSI — excludes inflation, trust, and dollar drag."
    )


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
    comp_cols = list(components.columns)
    base = df.drop(columns=[c for c in comp_cols if c in df.columns], errors="ignore")
    out = pd.concat([base, components], axis=1)
    out["hidden_fx_tax_index_0_100"] = normalize_index(out["hidden_fx_tax_pct"])
    out["rank"] = rank_series(out["hidden_fx_tax_pct"])
    out["interpretation"] = out["hidden_fx_tax_index_0_100"].apply(interpret_burden)
    out["explanation"] = out.apply(explain_hidden_fx_tax, axis=1)
    return out
