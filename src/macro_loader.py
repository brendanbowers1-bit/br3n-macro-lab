"""Macro series for regime context: DXY, VIX, rate spreads."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
MACRO_CACHE = ROOT / "data" / "processed" / "macro_panel.csv"


def fetch_fred_series(series_id: str, timeout: int = 120, retries: int = 3) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            from io import StringIO

            raw = pd.read_csv(StringIO(r.text))
            date_col = raw.columns[0]
            val_col = raw.columns[1]
            raw[date_col] = pd.to_datetime(raw[date_col])
            s = raw.set_index(date_col)[val_col].replace(".", np.nan).astype(float)
            s.index.name = "date"
            return s.sort_index()
        except Exception as exc:
            last_exc = exc
            if attempt < retries - 1:
                import time

                time.sleep(2 ** attempt)
    raise last_exc  # type: ignore[misc]


def fetch_yahoo_series(ticker: str, years: int = 25) -> pd.Series:
    import yfinance as yf

    period = "max" if years >= 10 else f"{max(years, 1)}y"
    hist = yf.Ticker(ticker).history(period=period, interval="1d", auto_adjust=True)
    if hist.empty:
        raise RuntimeError(f"No Yahoo data for {ticker}")
    close = hist["Close"] if "Close" in hist.columns else hist["close"]
    s = close.copy()
    s.index = pd.to_datetime(s.index).tz_localize(None)
    s.index.name = "date"
    return s.sort_index()


def load_macro_panel(cfg: dict, force_refresh: bool = False) -> pd.DataFrame:
    """Daily macro panel aligned for merge onto FX features."""
    macro_cfg = cfg.get("macro", {})
    if not macro_cfg.get("enabled", True):
        return pd.DataFrame()

    if MACRO_CACHE.exists() and not force_refresh:
        panel = pd.read_csv(MACRO_CACHE, parse_dates=[0], index_col=0)
        panel.index.name = "date"
        return panel

    years = int(cfg["data"].get("history_years", 20))
    rows: Dict[str, pd.Series] = {}

    yahoo = macro_cfg.get("yahoo", {})
    for name, ticker in yahoo.items():
        try:
            rows[name] = fetch_yahoo_series(ticker, years)
        except Exception as exc:
            print(f"  Macro Yahoo {name} ({ticker}): {exc}")

    fred = macro_cfg.get("fred", {})
    for name, series_id in fred.items():
        try:
            rows[name] = fetch_fred_series(series_id)
        except Exception as exc:
            print(f"  Macro FRED {name} ({series_id}): {exc}")

    if not rows:
        return pd.DataFrame()

    panel = pd.DataFrame(rows)
    panel = panel.sort_index().ffill()

    if "us_rate" in panel.columns and "mx_rate" in panel.columns:
        panel["us_mx_rate_spread"] = panel["mx_rate"] - panel["us_rate"]

    if "dxy" in panel.columns:
        panel["dxy_return"] = panel["dxy"].pct_change()
        w = int(macro_cfg.get("dxy_trend_window", 20))
        panel["dxy_ma"] = panel["dxy"].rolling(w).mean()
        panel["dxy_uptrend"] = (panel["dxy"] > panel["dxy_ma"]).astype(int)

    if "vix" in panel.columns:
        win = int(macro_cfg.get("vix_percentile_window", 252))
        pct = float(macro_cfg.get("vix_stress_percentile", 0.75))
        panel["vix_pct"] = panel["vix"].rolling(win, min_periods=60).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
        )
        panel["risk_off"] = (panel["vix_pct"] > pct).astype(int)

    if "dxy" in panel.columns:
        dxy_pct = float(macro_cfg.get("dxy_stress_percentile", 0.70))
        win = int(macro_cfg.get("vix_percentile_window", 252))
        panel["dxy_vol"] = panel["dxy_return"].rolling(20).std() * np.sqrt(252)
        panel["dxy_vol_pct"] = panel["dxy_vol"].rolling(win, min_periods=60).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
        )
        panel["dollar_stress"] = (
            (panel["dxy_vol_pct"] > dxy_pct) | (panel.get("dxy_uptrend", 0) == 1)
        ).astype(int)

    if "us_mx_rate_spread" in panel.columns:
        carry_pct = float(macro_cfg.get("carry_high_percentile", 0.60))
        win = int(macro_cfg.get("vix_percentile_window", 252))
        panel["carry_spread_pct"] = panel["us_mx_rate_spread"].rolling(win, min_periods=60).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
        )
        panel["high_carry"] = (panel["carry_spread_pct"] > carry_pct).astype(int)

    panel.index.name = "date"
    MACRO_CACHE.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(MACRO_CACHE)
    print(f"Saved macro panel -> {MACRO_CACHE} ({len(panel)} rows)")
    return panel


def merge_macro_features(df: pd.DataFrame, cfg: dict, force_refresh: bool = False) -> pd.DataFrame:
    """Left-join macro columns onto FX feature frame."""
    panel = load_macro_panel(cfg, force_refresh=force_refresh)
    if panel.empty:
        return df
    out = df.join(panel, how="left")
    macro_cols = [c for c in panel.columns if c in out.columns]
    out[macro_cols] = out[macro_cols].ffill().bfill()
    return out
