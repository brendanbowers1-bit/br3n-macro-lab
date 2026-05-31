"""Unified data bundle for the FX research terminal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.data_loader import load_config

from .constants import CORE_FX_PAIRS
from .macro import load_rates_carry_panel, load_sentiment_panel, load_terminal_macro
from .market import load_all_core_pairs
from .mock import generate_mock_market_panel


@dataclass
class TerminalDataBundle:
    market: pd.DataFrame
    macro: pd.DataFrame
    rates: pd.DataFrame
    sentiment: pd.DataFrame
    meta: dict[str, Any]


def build_terminal_data_bundle(
    cfg: dict | None = None,
    *,
    use_mock_on_failure: bool = True,
) -> TerminalDataBundle:
    """
    Load or synthesize all terminal inputs.

    Returns long-format market panel plus macro, rates, and sentiment tables.
    """
    cfg = cfg or load_config()
    market = load_all_core_pairs(cfg, use_mock_on_failure=use_mock_on_failure)
    if market.empty and use_mock_on_failure:
        market = generate_mock_market_panel()

    macro = load_terminal_macro(cfg)
    rates = load_rates_carry_panel(cfg, CORE_FX_PAIRS)
    sentiment = load_sentiment_panel(cfg)

    sources = {
        "market": market["source"].iloc[0] if "source" in market.columns else "cached",
        "macro": macro["source"].iloc[0] if "source" in macro.columns else "unknown",
        "rates": rates["source"].iloc[0] if "source" in rates.columns else "unknown",
        "sentiment": sentiment["source"].iloc[0] if "source" in sentiment.columns else "unknown",
    }
    return TerminalDataBundle(
        market=market,
        macro=macro,
        rates=rates,
        sentiment=sentiment,
        meta={"pairs": CORE_FX_PAIRS, "sources": sources},
    )
