"""
Macro economic feature engineering for BR3N FX models.

TODO: wire to FRED / OECD / national statistics feeds used by src/data_ingest.py.
"""

from __future__ import annotations

import pandas as pd


def build_macro_features(macro_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build inflation, unemployment, GDP, PMI, trade balance, and fiscal stress features.

    Args:
        macro_df: Raw macro panel indexed by date.

    Returns:
        Feature frame aligned to FX bars.

    Raises:
        NotImplementedError: Phase 4 pipeline not yet implemented.
    """
    raise NotImplementedError("Macro feature pipeline — Phase 4")
