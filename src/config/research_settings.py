"""
Project-wide research credibility settings for BR3N Value Survival Index.

When RESEARCH_MODE = "credible", all outputs use conservative language,
visible mock warnings, source traceability, and component breakdowns.
"""

from __future__ import annotations

from typing import Literal

RESEARCH_MODE: Literal["credible", "demo"] = "credible"

METHODOLOGY_VERSION = "vsi-credible-1.0"

DEFAULT_SEND_AMOUNT_USD = 200
BASELINE_DAYS_HELD = 30

HEDGE_ACCESS_SCORE_HOUSEHOLD = 0.0
HEDGE_ACCESS_SCORE_INSTITUTION = 1.0

# Sensitivity case weights
SENSITIVITY_CASES = ("conservative", "baseline", "severe")

TIMING_RISK_WEIGHT = {
    "conservative": 0.10,
    "baseline": 0.25,
    "severe": 0.50,
}

VOLATILITY_WEIGHT = {
    "conservative": 0.05,
    "baseline": 0.10,
    "severe": 0.20,
}

# Conservative language enforced in credible mode
CREDIBLE_VERBS = ("estimates", "suggests", "is associated with", "under this specification")
FORBIDDEN_CLAIMS = ("proves", "guarantees", "predicts returns", "investment advice")

PAYOUT_FRICTION_DEFAULTS = {
    "bank_account": 0.001,
    "bank": 0.001,
    "mobile_wallet": 0.002,
    "cash_pickup": 0.005,
    "cash": 0.005,
    "unknown": 0.003,
}


def is_credible_mode() -> bool:
    return RESEARCH_MODE == "credible"


def conservative_label(phrase: str) -> str:
    """Prefix interpretation with credible-mode qualifier when needed."""
    if not is_credible_mode():
        return phrase
    if any(w in phrase.lower() for w in FORBIDDEN_CLAIMS):
        return phrase.replace("proves", "suggests").replace("Proves", "Suggests")
    return phrase
