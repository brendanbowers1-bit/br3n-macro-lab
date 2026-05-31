"""Data cleaning utilities for canonical research tables."""

from __future__ import annotations

import re

import pandas as pd

from .schema import SCHEMAS


def _snake(s: str) -> str:
    s = re.sub(r"[^\w\s]", "", str(s).strip().lower())
    return re.sub(r"\s+", "_", s)


def standardize_columns(df: pd.DataFrame, column_map: dict[str, str] | None = None) -> pd.DataFrame:
    out = df.copy()
    out.columns = [_snake(c) for c in out.columns]
    if column_map:
        out = out.rename(columns={_snake(k): v for k, v in column_map.items()})
    return out


def enforce_schema(df: pd.DataFrame, table_name: str, *, fill_missing: bool = True) -> pd.DataFrame:
    cols = SCHEMAS[table_name]
    out = df.copy()
    if fill_missing:
        for c in cols:
            if c not in out.columns:
                out[c] = pd.NA
    return out[cols]


def parse_dates(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
    out = df.copy()
    if col in out.columns:
        out[col] = pd.to_datetime(out[col], errors="coerce")
    return out


def dedupe_corridor_prices(df: pd.DataFrame) -> pd.DataFrame:
    keys = ["date", "corridor", "provider", "send_amount_usd"]
    present = [k for k in keys if k in df.columns]
    return df.drop_duplicates(subset=present, keep="last")


def clean_percent_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
            if out[c].dropna().max() and out[c].dropna().max() > 1.5:
                out[c] = out[c] / 100.0
    return out
