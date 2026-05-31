"""Spot FX loading for the research terminal."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from src.data_loader import load_config, load_or_fetch
from src.utils.paths import PROCESSED_DIR

from .constants import CORE_FX_PAIRS
from .mock import generate_mock_market_panel


def load_pair_spot(
    pair: str,
    cfg: dict | None = None,
    *,
    use_mock_on_failure: bool = True,
) -> pd.DataFrame:
    """
    Load daily spot for one pair. Uses cached processed CSV or yfinance/Stooq.

    Returns DataFrame with columns: date (index), price, pair.
    """
    cfg = cfg or load_config()
    years = cfg.get("data", {}).get("history_years", 10)
    safe = pair.replace("=", "_")
    cache = PROCESSED_DIR / f"{safe}.csv"

    try:
        if cache.exists():
            df = pd.read_csv(cache, parse_dates=["date"], index_col="date")
            if "price" not in df.columns and "close" in df.columns:
                df = df.rename(columns={"close": "price"})
            df = df[["price"]].copy()
        else:
            raw_cfg = {**cfg, "data": {**cfg.get("data", {}), "ticker": pair}}
            df = load_or_fetch(raw_cfg)
            if "price" not in df.columns:
                raise ValueError(f"No price column for {pair}")
            df = df[["price"]].copy()
            df.index.name = "date"
            df.to_csv(cache)
    except Exception:
        if not use_mock_on_failure:
            raise
        mock = generate_mock_market_panel(pairs=[pair], years=years)
        df = mock[mock["pair"] == pair].set_index("date")[["price"]]

    out = df.sort_index().copy()
    out["pair"] = pair
    return out


def load_all_core_pairs(cfg: dict | None = None, *, use_mock_on_failure: bool = True) -> pd.DataFrame:
    """Long-format panel: date, pair, price."""
    frames = []
    for pair in CORE_FX_PAIRS:
        try:
            df = load_pair_spot(pair, cfg, use_mock_on_failure=use_mock_on_failure)
            frames.append(df.reset_index())
        except Exception:
            continue
    if not frames:
        return generate_mock_market_panel(pairs=CORE_FX_PAIRS)
    panel = pd.concat(frames, ignore_index=True)
    panel["date"] = pd.to_datetime(panel["date"])
    return panel.sort_values(["pair", "date"]).reset_index(drop=True)
