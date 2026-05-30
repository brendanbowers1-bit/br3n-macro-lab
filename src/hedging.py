"""Treasury hedge-ratio guidance by regime (research only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Exposure = Literal["us_entity_long_mxn", "mx_entity_usd_liabilities"]

GRID = {
    "us_entity_long_mxn": {
        "R1_trend_high_vol": (0.60, 0.80, "Tranches, options, collars."),
        "R2_trend_low_vol": (0.50, 0.75, "Plain forwards."),
        "R3_range_high_vol": (0.30, 0.50, "Smaller tranches; avoid overreaction."),
        "R4_range_low_vol": (0.25, 0.40, "Base hedge; avoid full reload on bounces."),
    },
    "mx_entity_usd_liabilities": {
        "R1_trend_high_vol": (0.75, 1.00, "USD/MXN rising hurts; strong forward hedge."),
        "R2_trend_low_vol": (0.60, 0.85, "Build hedge on sustained USD strength."),
        "R3_range_high_vol": (0.40, 0.55, "Stagger; avoid panic hedging."),
        "R4_range_low_vol": (0.35, 0.50, "Base hedge; confirm breaks."),
    },
}


@dataclass
class HedgeGuidance:
    regime: str
    exposure: str
    ratio_low: float
    ratio_high: float
    instrument: str
    notes: str


def recommend(regime: str, exposure: Exposure = "us_entity_long_mxn") -> HedgeGuidance:
    low, high, notes = GRID[exposure].get(regime, (0.35, 0.55, "Review with treasury policy."))
    inst = "Forwards + options" if "high_vol" in regime else ("Plain forwards" if "R2" in regime else "Staggered forwards")
    return HedgeGuidance(regime, exposure, low, high, inst, notes)


def format_guidance(g: HedgeGuidance) -> str:
    return (
        f"**Regime:** {g.regime}\n"
        f"**Exposure:** {g.exposure}\n"
        f"**Hedge ratio:** {g.ratio_low:.0%} – {g.ratio_high:.0%}\n"
        f"**Instruments:** {g.instrument}\n"
        f"**Notes:** {g.notes}\n"
    )
