"""
FX desk decision registry — cross-border payments and treasury decision modules.

Research and risk-framing only. Not investment advice. Does not replace desk policy.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

FX_DESK_DECISION_REGISTRY: Dict[str, Dict[str, Any]] = {
    "exposure_measurement": {
        "key": "exposure_measurement",
        "title": "Real-Time Exposure Measurement",
        "question": (
            "What is our true net exposure by currency, corridor, value date, "
            "entity, counterparty, and settlement account?"
        ),
        "inputs": [
            "customer sends",
            "payout obligations",
            "prefunding balances",
            "agent balances",
            "bank balances",
            "pending settlements",
            "failed/reversed transactions",
            "value dates",
            "holidays",
        ],
        "outputs": [
            "net exposure by currency",
            "net exposure by corridor",
            "exposure by value date",
            "exposure confidence score",
            "data-quality warning",
        ],
        "primary_risks": [
            "stale exposure",
            "missing transactions",
            "duplicated transactions",
            "value-date mismatch",
            "wrong currency convention",
        ],
        "br3n_model_link": "Exposure dashboard and corridor risk engine.",
    },
    "hedge_timing": {
        "key": "hedge_timing",
        "title": "Hedge Timing and Hedge Ratio",
        "question": "Should we hedge now, later, partially, or not at all?",
        "inputs": [
            "net exposure",
            "current FX regime",
            "volatility",
            "forward points",
            "hedge cost",
            "liquidity",
            "policy hedge limits",
            "upcoming flow windows",
        ],
        "outputs": [
            "suggested hedge posture",
            "hedge ratio range",
            "instrument preference",
            "hedge timing warning",
        ],
        "primary_risks": [
            "over-hedging",
            "under-hedging",
            "hedge churn",
            "false trend signal",
            "forward cost drag",
        ],
        "br3n_model_link": "Hedge governance scorecard and no-change-in-range policy.",
    },
    "customer_pricing": {
        "key": "customer_pricing",
        "title": "Customer FX Pricing and Spread",
        "question": "How do we quote competitively without underpricing FX risk?",
        "inputs": [
            "market spot",
            "estimated hedge cost",
            "corridor volatility",
            "competition proxy",
            "customer sensitivity",
            "liquidity risk",
            "agent cost",
            "compliance/country risk",
        ],
        "outputs": [
            "pricing posture",
            "spread band",
            "volatility surcharge flag",
            "stale-rate warning",
        ],
        "primary_risks": [
            "underpriced FX risk",
            "customer churn",
            "arbitrage risk",
            "stale pricing",
            "regulatory pressure",
        ],
        "br3n_model_link": "Corridor risk spread indicator.",
    },
    "exotic_currency_liquidity": {
        "key": "exotic_currency_liquidity",
        "title": "Exotic and Controlled Currency Liquidity",
        "question": "Can we actually source the local currency at the rate we quote?",
        "inputs": [
            "official rate",
            "executable rate if available",
            "bid/ask spread",
            "capital controls",
            "local bank access",
            "parallel-market proxy",
            "NDF availability",
            "reserves stress",
        ],
        "outputs": [
            "liquidity risk score",
            "executable-rate warning",
            "controlled-currency flag",
            "corridor restriction warning",
        ],
        "primary_risks": [
            "official/executable rate mismatch",
            "trapped cash",
            "capital controls",
            "payout failure",
            "convertibility risk",
        ],
        "br3n_model_link": "Currency liquidity risk monitor.",
    },
    "prefunding_optimization": {
        "key": "prefunding_optimization",
        "title": "Prefunding and Local Currency Inventory",
        "question": "How much local currency should be held before demand arrives?",
        "inputs": [
            "forecast payout demand",
            "local currency balances",
            "volatility",
            "devaluation risk",
            "capital controls",
            "settlement timing",
            "holiday calendar",
            "corridor seasonality",
        ],
        "outputs": [
            "prefunding buffer recommendation",
            "underfunding warning",
            "trapped-cash warning",
            "emergency trade risk",
        ],
        "primary_risks": [
            "payout failure",
            "trapped cash",
            "devaluation loss",
            "excessive working capital",
            "emergency liquidity cost",
        ],
        "br3n_model_link": "Corridor flow-pressure and liquidity buffer model.",
    },
    "counterparty_selection": {
        "key": "counterparty_selection",
        "title": "Bank and Liquidity Provider Selection",
        "question": "Is the cheapest quote also the safest quote?",
        "inputs": [
            "bank quote",
            "spread",
            "settlement reliability",
            "counterparty limits",
            "credit exposure",
            "operational history",
            "local market access",
            "failed-trade history",
        ],
        "outputs": [
            "best all-in counterparty",
            "execution-quality score",
            "reliability warning",
            "counterparty limit warning",
        ],
        "primary_risks": [
            "failed settlement",
            "credit limit breach",
            "poor execution",
            "operational failure",
            "hidden liquidity cost",
        ],
        "br3n_model_link": "Liquidity provider scorecard.",
    },
    "settlement_timing": {
        "key": "settlement_timing",
        "title": "Value-Date and Settlement Timing",
        "question": (
            "Do we have currency and cash in the right place, on the right value date, "
            "before customers need it?"
        ),
        "inputs": [
            "value dates",
            "settlement calendar",
            "currency holidays",
            "bank cutoffs",
            "payout timing",
            "incoming funds",
            "outgoing funds",
        ],
        "outputs": [
            "settlement gap warning",
            "funding timing risk",
            "holiday mismatch alert",
            "weekend gap risk",
        ],
        "primary_risks": [
            "failed payout",
            "overdraft",
            "late settlement",
            "emergency FX trade",
            "value-date mismatch",
        ],
        "br3n_model_link": "Settlement and calendar risk engine.",
    },
    "forward_carry_economics": {
        "key": "forward_carry_economics",
        "title": "Forward Points and Carry Economics",
        "question": "Is the forward hedge worth the cost?",
        "inputs": [
            "spot rate",
            "forward points",
            "interest-rate differential",
            "hedge tenor",
            "exposure certainty",
            "volatility",
            "policy hedge ratio",
        ],
        "outputs": [
            "forward cost estimate",
            "carry drag estimate",
            "hedge value score",
            "instrument recommendation",
        ],
        "primary_risks": [
            "forward cost drag",
            "bad roll timing",
            "interest-rate surprise",
            "NDF basis risk",
            "overpaying for hedge",
        ],
        "br3n_model_link": "Carry-adjusted hedge scorecard.",
    },
    "crisis_response": {
        "key": "crisis_response",
        "title": "Crisis Response and Stress Regime",
        "question": "What do we do when the market moves sharply and liquidity disappears?",
        "inputs": [
            "regime shift",
            "volatility spike",
            "spread widening",
            "central-bank intervention",
            "sanctions event",
            "capital controls",
            "bank liquidity",
            "payout obligations",
        ],
        "outputs": [
            "crisis level",
            "hedge escalation flag",
            "spread widening flag",
            "corridor pause flag",
            "executive escalation memo",
        ],
        "primary_risks": [
            "liquidity freeze",
            "devaluation",
            "sanctions breach",
            "failed payout",
            "uncontrolled FX loss",
            "reputational risk",
        ],
        "br3n_model_link": "FX shock dashboard and crisis memo generator.",
    },
    "speculation_control": {
        "key": "speculation_control",
        "title": "Exposure Hedging vs Directional Speculation",
        "question": "Are we hedging real exposure or taking an unauthorized directional view?",
        "inputs": [
            "documented exposure",
            "hedge size",
            "hedge instrument",
            "hedge timing",
            "policy limits",
            "approval record",
            "model signal",
            "trader rationale",
        ],
        "outputs": [
            "hedge policy compliance flag",
            "speculative-risk warning",
            "documentation checklist",
            "approval requirement",
        ],
        "primary_risks": [
            "unauthorized trading",
            "policy breach",
            "model overconfidence",
            "audit failure",
            "P&L volatility",
        ],
        "br3n_model_link": "Hedge governance and model-risk controls.",
    },
}


def get_decision_module(key: str) -> Dict[str, Any]:
    """Return one FX desk decision module by registry key."""
    if key not in FX_DESK_DECISION_REGISTRY:
        raise KeyError(f"Unknown decision module: {key}")
    return FX_DESK_DECISION_REGISTRY[key]


def list_decision_modules() -> List[Dict[str, Any]]:
    """Return all decision modules in registry order."""
    return list(FX_DESK_DECISION_REGISTRY.values())


def decision_registry_dataframe() -> pd.DataFrame:
    """Summary table of decision modules."""
    rows = []
    for mod in FX_DESK_DECISION_REGISTRY.values():
        rows.append(
            {
                "key": mod["key"],
                "title": mod["title"],
                "question": mod["question"],
                "br3n_model_link": mod["br3n_model_link"],
            }
        )
    return pd.DataFrame(rows)


def decision_inputs_dataframe() -> pd.DataFrame:
    """Long-form inputs per decision module."""
    rows = []
    for mod in FX_DESK_DECISION_REGISTRY.values():
        for inp in mod["inputs"]:
            rows.append({"key": mod["key"], "title": mod["title"], "input": inp})
    return pd.DataFrame(rows)


def decision_risk_dataframe() -> pd.DataFrame:
    """Long-form primary risks per decision module."""
    rows = []
    for mod in FX_DESK_DECISION_REGISTRY.values():
        for risk in mod["primary_risks"]:
            rows.append({"key": mod["key"], "title": mod["title"], "primary_risk": risk})
    return pd.DataFrame(rows)
