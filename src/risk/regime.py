"""FX regime classification for the research terminal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


REGIMES = [
    "usd_bull",
    "usd_bear",
    "risk_on_carry",
    "risk_off_dollar_squeeze",
    "high_vol_crisis",
    "range_neutral",
]

REGIME_DESCRIPTIONS = {
    "usd_bull": "Broad USD strength — DXY trending up, often pressure on EM FX.",
    "usd_bear": "USD weakening — supportive for carry and EM receivers.",
    "risk_on_carry": "Low vol, positive risk appetite — carry trades favored.",
    "risk_off_dollar_squeeze": "Flight to USD liquidity — funding stress, EM underperformance.",
    "high_vol_crisis": "Extreme volatility — reduce size, widen stops, favor hedging.",
    "range_neutral": "No dominant macro trend — mean-reversion more likely.",
}

PAIR_IMPLICATIONS = {
    "usd_bull": {"USDJPY=X": "often supported", "USDMXN=X": "headwind for MXN", "EURUSD=X": "downside bias"},
    "usd_bear": {"USDJPY=X": "downside bias", "USDMXN=X": "MXN supportive", "EURUSD=X": "upside bias"},
    "risk_on_carry": {"USDBRL=X": "carry attractive if stable", "USDINR=X": "monitor RBI"},
    "risk_off_dollar_squeeze": {"USDMXN=X": "MXN vulnerable", "USDINR=X": "INR stress risk"},
    "high_vol_crisis": {"ALL": "reduce conviction; costs and gaps rise"},
    "range_neutral": {"ALL": "smaller directional edge; focus on costs"},
}


@dataclass
class RegimeState:
    current_regime: str
    regime_confidence: float
    regime_description: str
    implications_for_major_pairs: dict[str, str]
    as_of_date: pd.Timestamp | None = None


def classify_fx_regime(row: pd.Series) -> RegimeState:
    """
    Rule-based regime classifier using macro features available as of date.

    Expects columns: dxy_trend_20d, vix, vix_change, sp500_return, carry_score,
    vol_20d, oil_return (optional).
    """
    dxy_trend = float(row.get("dxy_trend_20d", 0) or 0)
    vix = float(row.get("vix", 20) or 20)
    vix_chg = float(row.get("vix_change", 0) or 0)
    sp_ret = float(row.get("sp500_return", 0) or 0)
    carry = float(row.get("carry_score", 0) or 0)
    vol = float(row.get("vol_20d", 0.1) or 0.1)
    oil = float(row.get("oil_return", 0) or 0)

    scores = {r: 0.0 for r in REGIMES}

    if dxy_trend > 0.02:
        scores["usd_bull"] += 2
    elif dxy_trend < -0.02:
        scores["usd_bear"] += 2

    if vix > 28 or vix_chg > 0.1:
        scores["high_vol_crisis"] += 2
        scores["risk_off_dollar_squeeze"] += 1
    elif vix < 16 and sp_ret > 0:
        scores["risk_on_carry"] += 2

    if sp_ret < -0.01 and vix_chg > 0.05:
        scores["risk_off_dollar_squeeze"] += 2

    if carry > 2 and vix < 20:
        scores["risk_on_carry"] += 1

    if vol > 0.2:
        scores["high_vol_crisis"] += 1

    if abs(dxy_trend) < 0.005 and vix < 22:
        scores["range_neutral"] += 2

    if abs(oil) > 0.03:
        scores["high_vol_crisis"] += 0.5

    regime = max(scores, key=scores.get)
    total = sum(scores.values()) or 1
    confidence = float(scores[regime] / total)

    return RegimeState(
        current_regime=regime,
        regime_confidence=confidence,
        regime_description=REGIME_DESCRIPTIONS[regime],
        implications_for_major_pairs=PAIR_IMPLICATIONS.get(regime, {}),
        as_of_date=pd.Timestamp(row.get("date")) if "date" in row.index else None,
    )


def classify_regime_series(macro_df: pd.DataFrame) -> pd.DataFrame:
    """Apply regime classifier to macro/feature panel."""
    rows = []
    for _, row in macro_df.iterrows():
        state = classify_fx_regime(row)
        rows.append(
            {
                "date": row.get("date"),
                "current_regime": state.current_regime,
                "regime_confidence": state.regime_confidence,
                "regime_description": state.regime_description,
            }
        )
    return pd.DataFrame(rows)
