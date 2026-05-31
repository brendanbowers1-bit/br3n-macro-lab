"""
Load VSI dataset from processed outputs or rebuild from raw/mock sources.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils.paths import OUTPUTS_DIR, PROCESSED_DIR

from .build_dataset import build_value_survival_dataset
from .vsi_quality import annotate_vsi_outputs


def _read_csv(name: str) -> pd.DataFrame | None:
    p = PROCESSED_DIR / f"{name}.csv"
    if p.exists():
        return pd.read_csv(p, parse_dates=["date"] if name in ("corridor_prices", "fx_rates", "value_survival_outputs") else None)
    return None


def load_vsi_dataset(rebuild: bool = False) -> dict[str, pd.DataFrame]:
    """Prefer processed artifacts; rebuild when missing or rebuild=True."""
    vsi_path = OUTPUTS_DIR / "value_survival_outputs.csv"
    if not rebuild and vsi_path.exists() and (PROCESSED_DIR / "corridor_prices.csv").exists():
        tables = {
            "corridor_prices": _read_csv("corridor_prices"),
            "remittance_flows": _read_csv("remittance_flows"),
            "fx_rates": _read_csv("fx_rates"),
            "macro_country_panel": _read_csv("macro_country_panel"),
            "currency_market_structure": _read_csv("currency_market_structure"),
            "country_sovereignty": _read_csv("country_sovereignty"),
            "currency_trust": _read_csv("currency_trust"),
            "dollar_dependency": _read_csv("dollar_dependency"),
            "value_survival_outputs": pd.read_csv(vsi_path, parse_dates=["date"]),
        }
        tables = {k: v for k, v in tables.items() if v is not None}
        if len(tables) >= 5:
            vsi = annotate_vsi_outputs(tables["value_survival_outputs"], tables)
            tables["value_survival_outputs"] = vsi
            return tables

    ds = build_value_survival_dataset()
    ds["value_survival_outputs"] = annotate_vsi_outputs(ds["value_survival_outputs"], ds)
    return ds
