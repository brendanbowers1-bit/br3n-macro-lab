"""Mock data generators for offline FX terminal development."""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from .constants import CORE_FX_PAIRS, DEFAULT_CARRY_BPS, DXY_TICKERS


def _business_dates(years: int = 10) -> pd.DatetimeIndex:
    end = pd.Timestamp(datetime.utcnow().date())
    start = end - pd.DateOffset(years=years)
    return pd.bdate_range(start, end)


def generate_mock_market_panel(
    pairs: list[str] | None = None,
    years: int = 10,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic spot prices with pair-specific drift and vol."""
    rng = np.random.default_rng(seed)
    pairs = pairs or CORE_FX_PAIRS
    dates = _business_dates(years)
    rows = []
    for pair in pairs:
        n = len(dates)
        base = 20.0 if "MXN" in pair else (80.0 if "JPY" in pair else 1.05)
        vol = 0.008 if pair in ("EURUSD=X", "GBPUSD=X") else 0.012
        rets = rng.normal(0, vol, n)
        prices = base * np.exp(np.cumsum(rets))
        for d, p in zip(dates, prices):
            rows.append({"date": d, "pair": pair, "price": float(p), "source": "mock"})
    return pd.DataFrame(rows)


def generate_mock_macro_panel(years: int = 10, seed: int = 42) -> pd.DataFrame:
    """Synthetic macro panel: DXY, VIX, yields, equities, commodities."""
    rng = np.random.default_rng(seed + 1)
    dates = _business_dates(years)
    n = len(dates)
    dxy = 100 * np.exp(np.cumsum(rng.normal(0, 0.003, n)))
    vix = np.clip(15 + rng.normal(0, 3, n).cumsum() * 0.05, 10, 45)
    us2y = 4.0 + rng.normal(0, 0.02, n).cumsum() * 0.1
    us10y = us2y + 0.5 + rng.normal(0, 0.01, n)
    sp500_ret = rng.normal(0.0003, 0.01, n)
    sp500 = 4000 * np.exp(np.cumsum(sp500_ret))
    oil = 75 * np.exp(np.cumsum(rng.normal(0, 0.015, n)))
    gold = 1900 * np.exp(np.cumsum(rng.normal(0, 0.005, n)))
    copper = 4.0 * np.exp(np.cumsum(rng.normal(0, 0.012, n)))
    em_proxy = 100 * np.exp(np.cumsum(rng.normal(0, 0.008, n)))

    df = pd.DataFrame(
        {
            "date": dates,
            "dxy": dxy,
            "vix": vix,
            "us_2y": us2y,
            "us_10y": us10y,
            "sp500": sp500,
            "sp500_return": sp500_ret,
            "oil": oil,
            "gold": gold,
            "copper": copper,
            "em_proxy": em_proxy,
            "source": "mock",
        }
    )
    return df


def generate_mock_rates_panel(pairs: list[str] | None = None, years: int = 10) -> pd.DataFrame:
    """Policy rate placeholders per pair for carry features."""
    pairs = pairs or CORE_FX_PAIRS
    dates = _business_dates(years)
    rows = []
    for pair in pairs:
        carry_bps = DEFAULT_CARRY_BPS.get(pair, 0)
        foreign_rate = 5.0 + carry_bps / 100.0
        domestic_rate = 5.25
        for d in dates:
            rows.append(
                {
                    "date": d,
                    "pair": pair,
                    "domestic_policy_rate": domestic_rate,
                    "foreign_policy_rate": foreign_rate,
                    "rate_differential": domestic_rate - foreign_rate,
                    "carry_score": carry_bps / 100.0,
                    "source": "mock",
                }
            )
    return pd.DataFrame(rows)


def generate_mock_sentiment_panel(years: int = 10) -> pd.DataFrame:
    """CFTC / news / central-bank tone placeholders."""
    dates = _business_dates(years)
    return pd.DataFrame(
        {
            "date": dates,
            "cftc_usd_net_speculative": 0.0,
            "news_sentiment_score": 0.0,
            "central_bank_tone_score": 0.0,
            "cpi_surprise": 0.0,
            "growth_surprise": 0.0,
            "political_risk_score": 0.0,
            "source": "mock_placeholder",
        }
    )
