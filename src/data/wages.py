"""Load hourly wage table for Labor Conversion Index."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils.paths import RAW_DIR


def load_hourly_wages(path: Path | None = None) -> pd.DataFrame:
    p = path or RAW_DIR / "manual" / "hourly_wages.csv"
    if not p.exists():
        return pd.DataFrame(columns=["country", "currency", "local_hourly_wage", "source"])
    return pd.read_csv(p)


def wage_lookup() -> dict[str, float]:
    df = load_hourly_wages()
    if df.empty:
        return {}
    return dict(zip(df["country"], df["local_hourly_wage"]))
