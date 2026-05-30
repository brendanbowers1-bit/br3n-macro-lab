"""
Model hooks for future ML regime classifiers (v1 uses rule-based regimes).
"""

from __future__ import annotations

import pandas as pd

from .regimes import classify_regimes


def predict_regimes(df: pd.DataFrame, cfg: dict) -> pd.Series:
    """Rule-based regime labels (default). Swap for sklearn/HMM later."""
    labeled = classify_regimes(df, cfg)
    return labeled["regime"]
