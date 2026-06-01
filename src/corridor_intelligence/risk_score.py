"""Transparent USD/MXN corridor risk score (structural stress, not prediction)."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass
class CorridorRiskScore:
    corridor: str
    as_of_month: str
    score: float
    band: str
    components: dict[str, float]
    weights: dict[str, float]
    metrics: dict[str, float]
    methodology_version: str
    disclaimer: str

    def to_dict(self) -> dict:
        return asdict(self)


WEIGHTS = {
    "momentum_stress": 0.30,
    "volatility_stress": 0.25,
    "drawdown_stress": 0.25,
    "data_quality_gap": 0.20,
}


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return float(max(lo, min(hi, x)))


def _band(score: float) -> str:
    if score < 33:
        return "Low"
    if score < 66:
        return "Moderate"
    return "Elevated"


def compute_corridor_risk_score(
    df: pd.DataFrame,
    *,
    data_quality_score: float = 85.0,
    methodology_version: str = "us_mx_corridor_v1",
) -> CorridorRiskScore:
    """Score 0–100: higher = elevated structural corridor stress (not a FX forecast)."""
    flows = df["remittance_usd_millions"].astype(float).values
    n = len(flows) - 1
    latest = flows[n]
    prev = flows[n - 1]

    yoy_ref_idx = n - 12 if n >= 12 else 0
    yoy_ref = flows[yoy_ref_idx]
    yoy_pct = ((latest - yoy_ref) / yoy_ref * 100.0) if yoy_ref else 0.0
    mom_pct = ((latest - prev) / prev * 100.0) if prev else 0.0

    # Negative YoY / MoM → higher stress (capped)
    momentum_stress = _clamp(50 - yoy_pct * 2.5)

    mom_returns = np.diff(flows) / flows[:-1] * 100.0
    window = mom_returns[-12:] if len(mom_returns) >= 12 else mom_returns
    vol = float(np.std(window)) if len(window) else 0.0
    vol_baseline = float(np.std(mom_returns)) if len(mom_returns) else 1.0
    vol_ratio = vol / vol_baseline if vol_baseline else 1.0
    volatility_stress = _clamp(35 + (vol_ratio - 1.0) * 40)

    peak = float(np.max(flows))
    drawdown_pct = (peak - latest) / peak * 100.0 if peak else 0.0
    drawdown_stress = _clamp(drawdown_pct * 2.0)

    data_quality_gap = _clamp(100.0 - data_quality_score)

    components = {
        "momentum_stress": round(momentum_stress, 2),
        "volatility_stress": round(volatility_stress, 2),
        "drawdown_stress": round(drawdown_stress, 2),
        "data_quality_gap": round(data_quality_gap, 2),
    }
    score = sum(components[k] * WEIGHTS[k] for k in WEIGHTS)

    as_of = df.iloc[-1]["month"]
    as_of_label = pd.Timestamp(as_of).strftime("%Y-%m")

    return CorridorRiskScore(
        corridor="United States→Mexico (USD/MXN)",
        as_of_month=as_of_label,
        score=round(score, 1),
        band=_band(score),
        components=components,
        weights=WEIGHTS,
        metrics={
            "latest_flow_usd_millions": round(float(latest), 1),
            "mom_pct": round(mom_pct, 2),
            "yoy_pct": round(yoy_pct, 2),
            "peak_flow_usd_millions": round(peak, 1),
            "drawdown_from_peak_pct": round(drawdown_pct, 2),
            "data_quality_score": round(data_quality_score, 1),
        },
        methodology_version=methodology_version,
        disclaimer=(
            "Corridor Risk Score measures structural flow stress from validated remittance data. "
            "Research only. Not investment advice. Not a price or FX prediction."
        ),
    )
