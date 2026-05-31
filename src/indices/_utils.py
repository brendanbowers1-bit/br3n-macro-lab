"""Shared utilities for flagship research indices."""

from __future__ import annotations

import numpy as np
import pandas as pd


def normalize_index(series: pd.Series, scale: float = 100, invert: bool = False) -> pd.Series:
    """Min-max normalize to 0–scale. Higher = more burden/stress unless invert=True for scores."""
    s = pd.to_numeric(series, errors="coerce")
    lo, hi = s.min(), s.max()
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return pd.Series(50.0, index=s.index)
    norm = (s - lo) / (hi - lo) * scale
    return (scale - norm) if invert else norm


def rank_series(series: pd.Series, ascending: bool = False) -> pd.Series:
    return series.rank(ascending=ascending, method="min")


def interpret_burden(score: float) -> str:
    if score < 25:
        return "Low burden"
    if score < 50:
        return "Moderate burden"
    if score < 75:
        return "High burden"
    return "Severe hidden FX tax"


def interpret_credibility(score: float) -> str:
    if score >= 70:
        return "High credibility"
    if score >= 50:
        return "Stable but vulnerable"
    if score >= 30:
        return "Fragile"
    return "Crisis-prone"


def interpret_stress(score: float) -> str:
    if score < 25:
        return "normal"
    if score < 50:
        return "watchlist"
    if score < 75:
        return "stressed"
    return "crisis"
