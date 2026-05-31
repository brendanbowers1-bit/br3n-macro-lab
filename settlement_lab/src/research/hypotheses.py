"""Research hypotheses for Settlement Economics Lab."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Hypothesis:
    id: str
    title: str
    statement: str
    dependent: str
    independent: list[str]
    controls: list[str]
    expected_sign: str
    identification_limitation: str


HYPOTHESES = [
    Hypothesis("H1", "Settlement delay and liquidity burden",
               "Higher settlement delay is associated with higher liquidity burden.",
               "operational_liquidity_burden_score", ["settlement_lag_days"],
               ["payment volume", "country", "rail_type"], "positive",
               "Endogenous liquidity requirements; no exogenous lag shock."),
    Hypothesis("H2", "Finality and fragility",
               "Higher finality quality is associated with lower payment fragility.",
               "payment_network_fragility_score", ["finality_quality_index"],
               ["volume shock", "FX volatility"], "negative",
               "Finality scores may be manual; reverse causality possible."),
    Hypothesis("H3", "Cost of capital and settlement drag",
               "Higher cost of capital increases settlement drag per $100.",
               "settlement_drag_cost_per_100", ["annual_cost_of_capital_pct"],
               ["settlement lag", "volume"], "positive",
               "Interest rates correlate with macro conditions."),
    Hypothesis("H4", "Payment access and friction",
               "Payment access reduces exposure to high-friction systems.",
               "payment_friction_score", ["digital_payment_usage_pct"],
               ["GDP per capita", "inflation"], "negative",
               "Findex is household-level; settlement data is system-level."),
    Hypothesis("H5", "Stress propagation",
               "Payment-system stress propagates through liquidity channels.",
               "fragility_regime", ["liquidity_buffer_ratio", "failure_rate"],
               ["settlement_lag_change"], "negative on buffer",
               "Stress events are rare; thin event sample."),
]


def hypotheses_dataframe():
    import pandas as pd
    return pd.DataFrame([{
        "id": h.id, "title": h.title, "hypothesis": h.statement,
        "dependent": h.dependent, "independent": "; ".join(h.independent),
        "expected_sign": h.expected_sign, "limitation": h.identification_limitation,
    } for h in HYPOTHESES])
