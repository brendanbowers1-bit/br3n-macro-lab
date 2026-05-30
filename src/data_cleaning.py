"""FX quote normalization and outlier repair for Yahoo/Stooq feeds."""

from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import pandas as pd

# USD per unit of foreign — median levels (order of magnitude checks)
_EXPECTED_MEDIAN = {
    "USDMXN=X": (10.0, 30.0),
    "USDBRL=X": (1.5, 8.0),
    "USDCOP=X": (1500.0, 6000.0),
    "USDJPY=X": (80.0, 200.0),
    "EURUSD=X": (0.5, 1.6),
    "USDINR=X": (40.0, 120.0),
    "USDPHP=X": (40.0, 70.0),
    "USDZAR=X": (8.0, 25.0),
    "USDTRY=X": (0.5, 60.0),
}

# Max |daily return| before interpolation (TRY allows larger moves)
_MAX_DAILY_RET = {
    "USDTRY=X": 0.35,
    "USDCOP=X": 0.15,
    "USDZAR=X": 0.18,
}


def _expected_band(ticker: str) -> Tuple[float, float] | None:
    return _EXPECTED_MEDIAN.get(ticker)


def _max_daily_ret(ticker: str) -> float:
    return _MAX_DAILY_RET.get(ticker, 0.12)


def _maybe_invert(p: pd.Series, ticker: str) -> Tuple[pd.Series, bool]:
    """Invert quotes when feed appears to be foreign-per-USD instead of USD-per-foreign."""
    med = float(p.median())
    band = _expected_band(ticker)
    if band is None:
        return p, False
    lo, hi = band
    if lo <= med <= hi:
        return p, False
    inv = 1.0 / p.replace(0, np.nan)
    inv_med = float(inv.median())
    if lo <= inv_med <= hi:
        return inv, True
    return p, False


def _repair_spikes(p: pd.Series, ticker: str) -> Tuple[pd.Series, int]:
    """Interpolate isolated bad prints (common on EM FX Yahoo series)."""
    max_ret = _max_daily_ret(ticker)
    ret = p.pct_change()
    bad = ret.abs() > max_ret
    n = int(bad.sum())
    if n == 0:
        return p, 0
    fixed = p.copy()
    fixed.loc[bad] = np.nan
    fixed = fixed.interpolate(method="linear").ffill().bfill()
    return fixed, n


def sanitize_fx_prices(df: pd.DataFrame, ticker: str) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """
    Return cleaned price frame and diagnostics.
    """
    out = df[["price"]].astype(float).copy()
    meta: Dict[str, object] = {"ticker": ticker, "rows_in": len(out)}

    med0 = float(out["price"].median())
    meta["median_before"] = round(med0, 6)

    out["price"], inverted = _maybe_invert(out["price"], ticker)
    meta["inverted"] = inverted
    meta["median_after_invert"] = round(float(out["price"].median()), 6)

    out["price"], spikes = _repair_spikes(out["price"], ticker)
    meta["spikes_repaired"] = spikes

    ret = out["price"].pct_change()
    meta["max_abs_daily_ret"] = round(float(ret.abs().max()), 6)
    meta["rows_out"] = len(out.dropna())

    band = _expected_band(ticker)
    if band:
        med = float(out["price"].median())
        meta["median_in_band"] = band[0] <= med <= band[1]
    else:
        meta["median_in_band"] = None

    return out.dropna(), meta


def validate_series(df: pd.DataFrame, ticker: str) -> bool:
    """False if series still looks unusable after cleaning."""
    if df.empty or len(df) < 100:
        return False
    med = float(df["price"].median())
    band = _expected_band(ticker)
    if band and not (band[0] <= med <= band[1]):
        return False
    if df["price"].pct_change().abs().max() > 0.5:
        return False
    return True
