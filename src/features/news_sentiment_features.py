"""
News and sentiment features for FX forecasting and regime detection.

TODO: integrate with src/news_features.py and central-bank speech corpora.
"""

from __future__ import annotations

import pandas as pd


def build_news_sentiment_features(news_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build FOMC/ECB/BOJ tone, geopolitical risk, and crisis-headline features.

    Args:
        news_df: Raw news / headline panel.

    Returns:
        Sentiment features aligned to FX bars.

    Raises:
        NotImplementedError: Phase 4 pipeline not yet implemented.
    """
    raise NotImplementedError("News sentiment feature pipeline — Phase 4")
