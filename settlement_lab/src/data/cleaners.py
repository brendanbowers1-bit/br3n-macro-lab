"""Standardize dates, currencies, and countries."""

from __future__ import annotations

import pandas as pd


def standardize_dates(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
    out = df.copy()
    if col in out.columns:
        out[col] = pd.to_datetime(out[col], errors="coerce")
    return out


def standardize_currencies(df: pd.DataFrame, col: str = "currency") -> pd.DataFrame:
    out = df.copy()
    if col in out.columns:
        out[col] = out[col].astype(str).str.upper().str.strip()
    return out


def standardize_countries(df: pd.DataFrame, col: str = "country") -> pd.DataFrame:
    out = df.copy()
    if col in out.columns:
        out[col] = out[col].astype(str).str.strip()
    return out
