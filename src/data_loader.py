"""Pull daily FX data via yfinance (Stooq fallback); cache raw and processed."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import requests
import yaml

from .data_cleaning import sanitize_fx_prices, validate_series

ROOT = Path(__file__).resolve().parents[1]

STOOQ = {
    "USDMXN=X": "usdmxn",
    "USDBRL=X": "usdbrl",
    "USDCOP=X": "usdcop",
    "USDJPY=X": "usdjpy",
    "EURUSD=X": "eurusd",
    "USDINR=X": "usdinr",
    "USDPHP=X": "usdphp",
    "USDZAR=X": "usdzar",
    "USDTRY=X": "usdtry",
}


def load_config(path: Optional[Path] = None) -> dict:
    with open(path or ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _trim_years(df: pd.DataFrame, years: int) -> pd.DataFrame:
    if years > 0 and not df.empty:
        cutoff = df.index.max() - pd.DateOffset(years=years)
        df = df.loc[df.index >= cutoff]
    return df


def fetch_yfinance(ticker: str, years: int) -> pd.DataFrame:
    import yfinance as yf

    period = "max" if years >= 10 else f"{max(years, 1)}y"
    # Try Ticker.history first (more reliable than download for some FX tickers)
    hist = yf.Ticker(ticker).history(period=period, interval="1d", auto_adjust=True)
    if hist.empty:
        hist = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)
    if hist.empty:
        raise RuntimeError(f"No Yahoo data for {ticker}")
    if isinstance(hist.columns, pd.MultiIndex):
        hist.columns = [c[0].lower() if isinstance(c, tuple) else str(c).lower() for c in hist.columns]
    else:
        hist.columns = [str(c).lower() for c in hist.columns]
    close = hist["close"] if "close" in hist.columns else hist["adj close"]
    df = pd.DataFrame({"price": close}).dropna()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.index.name = "date"
    return _trim_years(df, years)


def fetch_stooq(ticker: str, years: int) -> pd.DataFrame:
    code = STOOQ.get(ticker, ticker.replace("=X", "").lower())
    url = f"https://stooq.com/q/d/l/?s={code}&i=d"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    raw = pd.read_csv(StringIO(r.text))
    raw["Date"] = pd.to_datetime(raw["Date"])
    df = pd.DataFrame({"price": raw["Close"]}, index=raw["Date"]).sort_index()
    df.index.name = "date"
    return _trim_years(df, years)


def fetch_prices(ticker: str, years: int) -> pd.DataFrame:
    try:
        return fetch_yfinance(ticker, years)
    except Exception as exc:
        print(f"  Yahoo failed: {exc}")
        return fetch_stooq(ticker, years)


def _read_cache(proc_path: Path) -> pd.DataFrame:
    cached = pd.read_csv(proc_path, parse_dates=[0], index_col=0)
    cached.index.name = "date"
    if "price" in cached.columns:
        return cached[["price"]]
    if "close" in cached.columns:
        return pd.DataFrame({"price": cached["close"]}, index=cached.index)
    raise ValueError(f"Unexpected columns: {list(cached.columns)}")


def load_or_fetch(cfg: dict, force_refresh: bool = False) -> Tuple[pd.DataFrame, Path]:
    ticker = cfg["data"]["ticker"]
    years = int(cfg["data"]["history_years"])
    proc_dir = ROOT / "data" / "processed"
    proc_dir.mkdir(parents=True, exist_ok=True)
    safe = ticker.replace("=", "_")
    proc_path = proc_dir / f"{safe}.csv"

    if proc_path.exists() and not force_refresh:
        return _read_cache(proc_path), proc_path

    fallbacks = [
        ROOT / "data" / "outputs" / "usdmxn_labeled.csv",
        Path.home() / "fx-regime-research/data/USDMXN_X.csv",
        Path.home() / "usdmxn_backtest_output/backtest_series.csv",
    ]

    df = None
    source = "download"
    try:
        df = fetch_prices(ticker, years)
    except Exception as exc:
        print(f"  Download failed: {exc}")
        df = None

    if df is None:
        for fb in fallbacks:
            if fb.exists():
                ohlc = pd.read_csv(fb, parse_dates=[0], index_col=0)
                ohlc.columns = [str(c).lower() for c in ohlc.columns]
                df = pd.DataFrame({"price": ohlc["close"]}, index=ohlc.index)
                df.index.name = "date"
                df = _trim_years(df, years)
                source = f"fallback:{fb.name}"
                print(f"  Using fallback: {fb} ({len(df)} rows)")
                break

    if df is None:
        raise RuntimeError("No data source available. Run with network or restore cache.")

    # Never replace a longer good cache with a shorter fallback on refresh
    if proc_path.exists() and force_refresh and source.startswith("fallback"):
        old = _read_cache(proc_path)
        if len(old) > len(df) * 1.2:
            print(
                f"  Keeping existing cache ({len(old)} rows) — "
                f"fallback only has {len(df)} rows"
            )
            return old[["price"]], proc_path

    df, _ = sanitize_fx_prices(df, ticker)
    df[["price"]].to_csv(proc_path)
    print(f"Saved {len(df)} rows -> {proc_path} ({df.index.min().date()} to {df.index.max().date()})")
    return df[["price"]], proc_path


def load_pair_prices(
    ticker: str,
    years: int,
    force_refresh: bool = False,
) -> Tuple[pd.DataFrame, dict]:
    """
    Load one FX pair with per-ticker cache and quote sanitization.
    """
    proc_dir = ROOT / "data" / "processed"
    proc_dir.mkdir(parents=True, exist_ok=True)
    safe = ticker.replace("=", "_")
    proc_path = proc_dir / f"{safe}.csv"
    meta: dict = {"ticker": ticker, "source": "cache"}

    if proc_path.exists() and not force_refresh:
        df = _read_cache(proc_path)
        df, clean_meta = sanitize_fx_prices(df, ticker)
        meta.update(clean_meta)
        meta["source"] = "cache_resanitized"
        if validate_series(df, ticker):
            return df[["price"]], meta
        force_refresh = True

    downloaded = None
    try:
        downloaded = fetch_prices(ticker, years)
        meta["source"] = "download"
    except Exception as exc:
        meta["download_error"] = str(exc)[:120]

    if downloaded is not None:
        df = downloaded
    elif proc_path.exists():
        df = _read_cache(proc_path)
        meta["source"] = "cache_fallback"
    else:
        raise RuntimeError(f"No data for {ticker}: download failed and no cache")

    if (
        proc_path.exists()
        and force_refresh
        and meta["source"] != "download"
    ):
        old = _read_cache(proc_path)
        if len(old) > len(df) * 1.2:
            meta["source"] = "cache_kept_longer"
            return old[["price"]], meta

    df, clean_meta = sanitize_fx_prices(df, ticker)
    meta.update(clean_meta)
    if not validate_series(df, ticker):
        raise RuntimeError(
            f"{ticker}: price series failed validation after cleaning "
            f"(median={meta.get('median_after_invert')})"
        )
    df[["price"]].to_csv(proc_path)
    meta["rows"] = len(df)
    meta["path"] = str(proc_path)
    return df[["price"]], meta
