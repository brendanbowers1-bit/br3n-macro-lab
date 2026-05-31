"""Country sovereignty / dollar exposure manual research layer."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils.paths import RAW_DIR

DEFAULT_PATH = RAW_DIR / "manual" / "country_sovereignty.csv"


def load_country_sovereignty(path: Path | None = None) -> pd.DataFrame:
    p = path or DEFAULT_PATH
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


def sovereignty_lookup() -> dict[str, dict]:
    df = load_country_sovereignty()
    if df.empty:
        return {}
    out = {}
    for _, r in df.iterrows():
        out[str(r["country"])] = r.to_dict()
    return out
