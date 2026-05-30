"""Regime classifier R1–R4."""

from __future__ import annotations

import pandas as pd

R1 = "R1_trend_high_vol"
R2 = "R2_trend_low_vol"
R3 = "R3_range_high_vol"
R4 = "R4_range_low_vol"
TREND_REGIMES = (R1, R2)
RANGE_REGIMES = (R3, R4)
ALL_REGIMES = (R1, R2, R3, R4)


def classify_regimes(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    out = df.copy()
    trending = out["trend_flag"] == 1
    high_vol = out["high_vol_flag"]
    out["regime"] = R4
    out.loc[trending & high_vol, "regime"] = R1
    out.loc[trending & ~high_vol, "regime"] = R2
    out.loc[~trending & high_vol, "regime"] = R3
    out.loc[~trending & ~high_vol, "regime"] = R4

    out["regime_context"] = out["regime"].astype(str)
    if "dollar_stress" in out.columns:
        out.loc[out["dollar_stress"] == 1, "regime_context"] = (
            out.loc[out["dollar_stress"] == 1, "regime_context"] + "+dollar_stress"
        )
    if "risk_off" in out.columns:
        out.loc[out["risk_off"] == 1, "regime_context"] = (
            out.loc[out["risk_off"] == 1, "regime_context"] + "+risk_off"
        )
    if "high_carry" in out.columns:
        out.loc[out["high_carry"] == 1, "regime_context"] = (
            out.loc[out["high_carry"] == 1, "regime_context"] + "+high_carry"
        )

    return out
