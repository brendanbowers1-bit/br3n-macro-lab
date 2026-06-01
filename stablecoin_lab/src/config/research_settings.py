"""
Project-wide research settings for BR3N Stablecoin Settlement Window Lab.

Research-only. Not financial advice. Not investment recommendation.
"""

from __future__ import annotations

from typing import Literal

RESEARCH_MODE: Literal["credible", "demo"] = "credible"
NO_UNLABELED_DATA = True
METHODOLOGY_VERSION = "stablecoin-lab-credible-1.0"

DEFAULT_DEPEG_RISK_PENALTY_BPS = 5.0
BASELINE_LEDGER_FINALITY_SECONDS = 12.0
BASELINE_COMPLIANCE_DELAY_HOURS = 4.0

SENSITIVITY_CASES = ("conservative", "baseline", "severe")

COMPLIANCE_DELAY_HOURS = {
    "conservative": 2.0,
    "baseline": 4.0,
    "severe": 12.0,
}

OFF_RAMP_TIME_HOURS = {
    "conservative": 1.0,
    "baseline": 6.0,
    "severe": 48.0,
}

REDEMPTION_TIME_HOURS = {
    "conservative": 4.0,
    "baseline": 24.0,
    "severe": 72.0,
}

DEPEG_RISK_PENALTY_BPS = {
    "conservative": 2.0,
    "baseline": 5.0,
    "severe": 25.0,
}

CHAIN_FEE_MULTIPLIER = {
    "conservative": 0.8,
    "baseline": 1.0,
    "severe": 2.5,
}

RESERVE_LIQUIDITY_WEIGHT = {
    "conservative": 1.2,
    "baseline": 1.0,
    "severe": 0.7,
}

MOCK_MAX_QUALITY_SCORE = 30
MOCK_SOURCE_ID = "MOCK_DEMO_ONLY"

CREDIBLE_VERBS = ("estimates", "suggests", "is associated with", "under this specification")
FORBIDDEN_CLAIMS = ("proves", "guarantees", "predicts returns", "investment advice")

LAB_LIMITATIONS = (
    "Measurement framework only — studies stablecoin settlement windows, finality, "
    "and payment-infrastructure risk under stated assumptions. "
    "Does not prove causal effects without identification. "
    "Not financial advice, not investment recommendation, not a recommendation to buy, "
    "sell, or hold any stablecoin or crypto asset, "
    "and not operational guidance for live treasury or payment systems."
)
