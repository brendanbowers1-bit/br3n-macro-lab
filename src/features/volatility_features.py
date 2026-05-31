"""
Volatility and market-regime features (VIX, DXY, realized vol, trend/range/crisis).

TODO: consolidate with src/features.py regime columns.
"""

from __future__ import annotations

import pandas as pd


def build_volatility_features(ohlcv_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute realized volatility, trend regime, mean-reversion, and crisis flags.

    Args:
        ohlcv_df: OHLCV panel for one or more FX pairs.

    Returns:
        Volatility and regime feature frame.

    Raises:
        NotImplementedError: Phase 4 pipeline not yet implemented.
    """
    raise NotImplementedError("Volatility feature pipeline — Phase 4")
