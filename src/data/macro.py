"""Macro and cross-asset data for the terminal."""

from __future__ import annotations

import pandas as pd

from src.macro_loader import load_macro_panel, merge_macro_features

from .mock import generate_mock_macro_panel, generate_mock_rates_panel, generate_mock_sentiment_panel


def load_terminal_macro(cfg: dict, *, force_refresh: bool = False) -> pd.DataFrame:
    """Load macro panel; fall back to mock if empty."""
    try:
        panel = load_macro_panel(cfg, force_refresh=force_refresh)
        if panel.empty:
            raise ValueError("empty macro panel")
        panel = panel.reset_index()
        if "date" not in panel.columns:
            panel = panel.rename(columns={panel.columns[0]: "date"})
        panel["date"] = pd.to_datetime(panel["date"])
        return panel
    except Exception:
        return generate_mock_macro_panel(years=cfg.get("data", {}).get("history_years", 10))


def load_rates_carry_panel(cfg: dict, pairs: list[str]) -> pd.DataFrame:
    """Rate differential / carry panel — mock until FRED per-pair wired."""
    return generate_mock_rates_panel(pairs=pairs, years=cfg.get("data", {}).get("history_years", 10))


def load_sentiment_panel(cfg: dict) -> pd.DataFrame:
    """Positioning and sentiment placeholders."""
    return generate_mock_sentiment_panel(years=cfg.get("data", {}).get("history_years", 10))
