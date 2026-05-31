"""
Position risk engine — sizing, stops, and trade acceptability rules.

Research-only decision support; not live execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from src.risk.regime import RegimeState


@dataclass
class RiskAssessment:
    entry: float
    stop_loss: float
    take_profit: float
    suggested_position_size: float
    reward_risk_ratio: float
    expected_value: float
    max_loss: float
    invalidation_level: float
    risk_notes: str
    trade_decision: str  # accept, reduce, reject


def compute_atr_stop(price: float, vol_20d: float, direction: str, atr_mult: float = 2.0) -> float:
    """ATR proxy from annualized vol."""
    daily_vol = vol_20d / np.sqrt(252) if vol_20d > 0 else 0.01
    stop_dist = price * daily_vol * atr_mult
    if direction == "long":
        return price - stop_dist
    if direction == "short":
        return price + stop_dist
    return price


def assess_trade_risk(
    *,
    entry: float,
    direction: str,
    confidence: float,
    expected_return: float,
    vol_20d: float,
    carry_score: float,
    regime: RegimeState | None = None,
    capital: float = 1_000_000,
    risk_pct: float = 0.0075,
    min_rr: float = 2.0,
) -> RiskAssessment:
    """
    Evaluate whether a research signal meets BR3N risk rules.

    Default: 0.75% capital at risk, min 2:1 reward/risk, no trade in crisis.
    """
    notes = []
    if direction == "neutral":
        return RiskAssessment(
            entry=entry,
            stop_loss=entry,
            take_profit=entry,
            suggested_position_size=0.0,
            reward_risk_ratio=0.0,
            expected_value=0.0,
            max_loss=0.0,
            invalidation_level=entry,
            risk_notes="Neutral signal — no position.",
            trade_decision="reject",
        )

    stop = compute_atr_stop(entry, vol_20d, direction)
    risk_per_unit = abs(entry - stop)
    target_dist = risk_per_unit * min_rr
    take_profit = entry + target_dist if direction == "long" else entry - target_dist
    rr = target_dist / risk_per_unit if risk_per_unit > 0 else 0

    risk_dollars = capital * risk_pct
    size = risk_dollars / risk_per_unit if risk_per_unit > 0 else 0
    max_loss = risk_dollars
    ev = expected_return * size - (1 - confidence) * max_loss * 0.5

    decision = "accept"
    if regime and regime.current_regime == "high_vol_crisis":
        size *= 0.5
        notes.append("Crisis regime — size reduced 50%.")
        decision = "reduce"
    if vol_20d > 0.25:
        notes.append("Extreme volatility — consider avoid.")
        decision = "reject"
        size = 0.0
    if rr < min_rr:
        notes.append(f"Reward/risk {rr:.2f} below minimum {min_rr}.")
        decision = "reject"
        size = 0.0
    if confidence < 0.15 and carry_score < 0:
        notes.append("Low confidence with negative carry.")
        decision = "reject"
        size = 0.0
    if confidence < 0.25:
        size *= 0.5
        notes.append("Low confidence — size reduced.")
        if decision == "accept":
            decision = "reduce"

    invalidation = stop
    return RiskAssessment(
        entry=entry,
        stop_loss=stop,
        take_profit=take_profit,
        suggested_position_size=float(size),
        reward_risk_ratio=float(rr),
        expected_value=float(ev),
        max_loss=float(max_loss),
        invalidation_level=float(invalidation),
        risk_notes="; ".join(notes) if notes else "Meets default research risk rules.",
        trade_decision=decision,
    )


def correlation_warning(open_pairs: list[str]) -> str | None:
    """Flag if multiple similar USD/EM positions."""
    em = [p for p in open_pairs if any(x in p for x in ("MXN", "BRL", "COP", "INR", "PHP"))]
    if len(em) >= 3:
        return "Multiple EM USD shorts/long exposure — correlation risk elevated."
    return None
