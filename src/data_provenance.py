"""
Run provenance stamps for model and backtest scorecards.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]

PROVENANCE_COLUMNS = [
    "source",
    "data_tier",
    "currency_pair",
    "sample_start",
    "sample_end",
    "observations",
    "run_timestamp",
    "config_hash",
    "model_version",
    "price_convention",
    "frequency",
]


def config_hash(cfg: dict) -> str:
    """Stable short hash of config for reproducibility."""
    blob = json.dumps(cfg, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:12]


def build_run_provenance(
    cfg: dict,
    df: Optional[pd.DataFrame] = None,
    *,
    currency_pair: Optional[str] = None,
    source: Optional[str] = None,
    data_tier: Optional[str] = None,
    price_convention: Optional[str] = None,
    frequency: str = "daily",
    model_version: str = "fx_lab_v1",
) -> Dict[str, Any]:
    """Build provenance dict from config and optional price dataframe."""
    ticker = cfg.get("data", {}).get("ticker", "USDMXN=X")
    pair = currency_pair or ticker.replace("=X", "").replace("USD", "USD/")

    prov: Dict[str, Any] = {
        "source": source or "unknown",
        "data_tier": data_tier or "prototype",
        "currency_pair": pair if "/" in pair else "USD/MXN",
        "sample_start": None,
        "sample_end": None,
        "observations": 0,
        "run_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "config_hash": config_hash(cfg),
        "model_version": model_version,
        "price_convention": price_convention or "",
        "frequency": frequency,
    }

    if df is not None and not df.empty:
        work = df.copy()
        if "date" in work.columns:
            dates = pd.to_datetime(work["date"])
        elif isinstance(work.index, pd.DatetimeIndex):
            dates = work.index
        else:
            dates = pd.to_datetime(work.iloc[:, 0])

        prov["sample_start"] = str(dates.min().date())
        prov["sample_end"] = str(dates.max().date())
        prov["observations"] = int(len(work))

        if source is None and "source" in work.columns:
            prov["source"] = str(work["source"].dropna().iloc[0])
        if data_tier is None and "data_tier" in work.columns:
            prov["data_tier"] = str(work["data_tier"].dropna().iloc[0])
        if not prov["price_convention"] and "convention" in work.columns:
            prov["price_convention"] = str(work["convention"].dropna().iloc[0])

    return prov


def provenance_from_cache(ticker: str = "USDMXN=X") -> Dict[str, Any]:
    """Read provenance from processed cache if available."""
    safe = ticker.replace("=", "_")
    path = ROOT / "data" / "processed" / f"{safe}.csv"
    if not path.exists():
        return {}
    cache = pd.read_csv(path, parse_dates=[0], index_col=0, nrows=1)
    full = pd.read_csv(path, parse_dates=[0], index_col=0)
    cfg = {}
    try:
        with open(ROOT / "config.yaml", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except Exception:
        pass
    source = str(full["source"].iloc[0]) if "source" in full.columns else ""
    tier = str(full["data_tier"].iloc[0]) if "data_tier" in full.columns else ""
    conv = str(full["convention"].iloc[0]) if "convention" in full.columns else ""

    if not source:
        pref = cfg.get("data", {}).get("preferred_source", "")
        if pref in ("fred_h10", "fed_h10") and cfg.get("data", {}).get("prefer_tier1_spot", False):
            source = "fred_h10"
            tier = tier or "official"
            conv = conv or f"USD/MXN ({cfg.get('data', {}).get('official_spot_series', 'DEXMXUS')})"
        else:
            source = "cache"

    if not tier:
        tier = "academic" if source in ("fred_h10", "fred", "fed_h10") else "prototype"

    return build_run_provenance(
        cfg,
        full,
        currency_pair="USD/MXN" if ticker == "USDMXN=X" else ticker,
        source=source,
        data_tier=tier,
        price_convention=conv,
    )


def stamp_scorecard(
    scorecard: Union[pd.DataFrame, Dict[str, Any]],
    provenance: Dict[str, Any],
) -> pd.DataFrame:
    """Attach provenance columns to every row of a scorecard."""
    if isinstance(scorecard, dict):
        df = pd.DataFrame([scorecard])
    else:
        df = scorecard.copy()

    for col in PROVENANCE_COLUMNS:
        if col in provenance:
            df[col] = provenance[col]
    return df
