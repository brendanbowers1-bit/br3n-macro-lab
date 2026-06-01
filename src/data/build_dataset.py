"""
Build processed datasets for the Bowers Frontier Value Survival Index.

Loads real data when available; falls back to mock with warnings.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd

from src.indices.currency_trust import calculate_currency_trust_table
from src.indices.dollar_dependency import calculate_dollar_dependency_table
from src.indices.value_survival import calculate_vsi_for_corridors
from src.utils.paths import OUTPUTS_DIR, PROCESSED_DIR

from .file_discovery import discover_all_sources
from .loaders import load_all_canonical_tables, data_provenance_summary
from .mock_data import create_mock_dataset, is_using_mock_data
from .validators import validate_all_tables
from .vsi_quality import annotate_vsi_outputs, provenance_summary_df


def _using_mock(tables: dict[str, pd.DataFrame]) -> bool:
    for name, df in tables.items():
        if name.startswith("_"):
            continue
        if "source" in df.columns:
            src = str(df["source"].dropna().iloc[0]) if df["source"].notna().any() else ""
            if "mock" in src.lower():
                return True
    return is_using_mock_data(tables)


def build_value_survival_dataset(use_mock_fallback: bool = True) -> dict[str, pd.DataFrame]:
    """Load canonical tables, compute trust/dependency, return VSI-ready dataset."""
    try:
        tables = load_all_canonical_tables(use_mock_fallback=use_mock_fallback)
    except Exception:
        if not use_mock_fallback:
            raise
        warnings.warn("Falling back to mock data for VSI build.", stacklevel=2)
        tables = create_mock_dataset()

    mock_flag = _using_mock(tables)

    trust = calculate_currency_trust_table(
        tables["macro_country_panel"], tables.get("fx_rates")
    )
    dollar_dep = calculate_dollar_dependency_table(
        tables["macro_country_panel"],
        tables["currency_market_structure"],
        tables.get("remittance_flows"),
        tables.get("country_sovereignty"),
    )

    vsi = calculate_vsi_for_corridors(
        tables["corridor_prices"],
        tables.get("fx_rates"),
        tables.get("macro_country_panel"),
        trust,
        dollar_dep,
        mock_data_flag=mock_flag,
    )
    vsi = annotate_vsi_outputs(vsi, tables)

    out = {
        **tables,
        "currency_trust": trust,
        "dollar_dependency": dollar_dep,
        "value_survival_outputs": vsi,
    }
    out["_provenance_report"] = provenance_summary_df(tables)
    return out


def save_processed_dataset(dataset: dict[str, pd.DataFrame], out_dir: Path | None = None) -> dict[str, Path]:
    out_dir = out_dir or PROCESSED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, df in dataset.items():
        if name.startswith("_") or not isinstance(df, pd.DataFrame):
            continue
        p = out_dir / f"{name}.csv"
        df.to_csv(p, index=False)
        paths[name] = p
    return paths


def save_vsi_outputs(vsi: pd.DataFrame, out_dir: Path | None = None) -> Path:
    out_dir = out_dir or OUTPUTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "value_survival_outputs.csv"
    vsi.to_csv(p, index=False)
    return p


def build_and_validate() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    dataset = build_value_survival_dataset()
    validation = validate_all_tables(dataset)
    provenance = data_provenance_summary(
        {k: v for k, v in dataset.items() if isinstance(v, pd.DataFrame) and not k.startswith("_")}
    )
    dataset["_provenance"] = provenance
    dataset["_validation"] = validation
    return dataset, validation
