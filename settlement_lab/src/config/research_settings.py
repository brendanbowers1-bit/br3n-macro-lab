"""
Project-wide research settings for Bowers Frontier Settlement Economics Lab.

Research-only. Not financial advice. Not operational payment guidance.
"""

from __future__ import annotations

from typing import Literal

RESEARCH_MODE: Literal["credible", "demo"] = "credible"
NO_UNLABELED_DATA = True
METHODOLOGY_VERSION = "settlement-lab-credible-1.0"

DEFAULT_COST_OF_CAPITAL_PCT = 0.05
BASELINE_SETTLEMENT_LAG_DAYS = 1.0
BASELINE_FAILURE_RATE = 0.001

SENSITIVITY_CASES = ("conservative", "baseline", "severe")

COST_OF_CAPITAL = {
    "conservative": 0.03,
    "baseline": 0.05,
    "severe": 0.08,
}

FAILURE_RATE_WEIGHT = {
    "conservative": 0.5,
    "baseline": 1.0,
    "severe": 1.5,
}

FX_EXPOSURE_WEIGHT = {
    "conservative": 0.05,
    "baseline": 0.10,
    "severe": 0.20,
}

OPERATIONAL_COST_PER_100 = {
    "conservative": 0.02,
    "baseline": 0.05,
    "severe": 0.10,
}

MOCK_MAX_QUALITY_SCORE = 30
MOCK_SOURCE_ID = "MOCK_DEMO_ONLY"

CREDIBLE_VERBS = ("estimates", "suggests", "is associated with", "under this specification")
FORBIDDEN_CLAIMS = ("proves", "guarantees", "predicts returns", "investment advice")

LAB_LIMITATIONS = (
    "Measurement framework only — estimates settlement economics under stated assumptions. "
    "Does not prove causal effects without identification. "
    "Not financial advice, not investment recommendation, "
    "not operational guidance for live payment systems."
)
