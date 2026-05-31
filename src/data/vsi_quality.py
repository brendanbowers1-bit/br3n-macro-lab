"""
Annotate VSI outputs with provenance, limitations, and data quality scores.

Integrates research-grade 0–100 rubric from data_quality.py with legacy 0–1 scores.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from src.config.research_settings import METHODOLOGY_VERSION, is_credible_mode
from src.data.data_quality import annotate_quality, grade_from_score
from src.utils.paths import RAW_DIR

DataMode = Literal["real", "mixed", "demo"]

VSI_LIMITATIONS = (
    "Measurement framework only — estimates cross-border value loss under stated assumptions. "
    "Does not prove causal welfare effects without identification. "
    "Not investment advice, not a trading signal, not a price forecast. "
    "Extended specification components (dollar drag, trust discount) are model-based adjustments."
)

TRACEABILITY_COLS = [
    "fee_source", "fx_margin_source", "inflation_source", "fx_volatility_source",
    "remittance_volume_source", "payout_friction_source", "dollar_dependency_source",
    "trust_score_source", "methodology_version", "data_quality_score", "data_quality_grade",
    "real_data_coverage_pct", "mock_data_flag", "manual_assumption_flag",
]


@dataclass(frozen=True)
class DataProvenanceReport:
    data_mode: DataMode
    mock_data_flag: bool
    tables_real: list[str]
    tables_demo: list[str]
    tables_mixed: list[str]
    overall_quality_score: float
    notes: list[str]


def _source_tier(source: str | None) -> str:
    s = str(source or "").lower()
    if "mock" in s or "synthetic" in s:
        return "mock"
    if "placeholder" in s or "manual_research" in s:
        return "placeholder"
    if "curated" in s or "historical_curated" in s:
        return "curated"
    if any(k in s for k in ("world_bank", "knomad", "imf", "fred", "bis", "rpw_bulk", "lab", "api")):
        return "real"
    return "curated"


def _table_is_mock(df: pd.DataFrame) -> bool:
    if df.empty:
        return True
    if "source" in df.columns and df["source"].notna().any():
        return _source_tier(str(df["source"].dropna().iloc[0])) == "mock"
    return False


def assess_dataset_provenance(tables: dict[str, pd.DataFrame]) -> DataProvenanceReport:
    real, demo, mixed = [], [], []
    notes = []
    for name, df in tables.items():
        if name.startswith("_") or not isinstance(df, pd.DataFrame):
            continue
        tier = _source_tier(str(df["source"].dropna().iloc[0])) if "source" in df.columns and df["source"].notna().any() else "curated"
        if tier == "mock":
            demo.append(name)
        elif tier == "real":
            real.append(name)
        else:
            mixed.append(name)

    if demo and not real and not mixed:
        mode: DataMode = "demo"
        notes.append("All canonical tables are synthetic demo data.")
    elif demo:
        mode = "mixed"
        notes.append(f"Demo tables present: {', '.join(demo)}")
    else:
        mode = "real"
        notes.append("Ingested public/curated files in use; formula placeholders remain.")

    if not (RAW_DIR / "world_bank_rpw" / "rpw_complete.xlsx").exists():
        notes.append("Full RPW Excel not loaded — using historical/curated corridor panel.")
    if is_credible_mode():
        notes.append("RESEARCH_MODE=credible: conservative language and source traceability enforced.")

    if mode == "real":
        overall = 0.72 if mixed else 0.78
    elif mode == "mixed":
        overall = 0.55
    else:
        overall = 0.25

    return DataProvenanceReport(
        data_mode=mode,
        mock_data_flag=mode == "demo",
        tables_real=real,
        tables_demo=demo,
        tables_mixed=mixed,
        overall_quality_score=overall,
        notes=notes,
    )


def annotate_vsi_outputs(vsi: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Add data_mode, limitations, traceability, and per-row quality scores."""
    prov = assess_dataset_provenance(tables)
    out = annotate_quality(vsi.copy(), tables)
    out["data_mode"] = prov.data_mode
    out["mock_data_flag"] = prov.mock_data_flag or out.get("mock_data_flag", False).astype(bool)
    out["methodology_version"] = out.get("methodology_version", METHODOLOGY_VERSION)
    out["limitations"] = VSI_LIMITATIONS

    for col in ("value_survival_index", "vsi_core", "vsi_risk_adjusted", "vsi_extended"):
        if col in out.columns:
            out[col] = out[col].clip(0, 100)
    if "real_usable_value_delivered_pct" in out.columns:
        out["real_usable_value_delivered_pct"] = out["real_usable_value_delivered_pct"].clip(0, 1)
    if "total_value_loss_pct" in out.columns:
        out["total_value_loss_pct"] = out["total_value_loss_pct"].clip(0, 0.5)

    # Legacy 0–1 score for backward compatibility in charts
    out["data_quality_score_normalized"] = (out["data_quality_score"] / 100.0).round(3)
    return out


def provenance_summary_df(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    prov = assess_dataset_provenance(tables)
    rows = [
        {"metric": "data_mode", "value": prov.data_mode},
        {"metric": "overall_quality_score", "value": prov.overall_quality_score},
        {"metric": "mock_data_flag", "value": prov.mock_data_flag},
        {"metric": "methodology_version", "value": METHODOLOGY_VERSION},
        {"metric": "tables_real", "value": ", ".join(prov.tables_real) or "none"},
        {"metric": "tables_demo", "value": ", ".join(prov.tables_demo) or "none"},
        {"metric": "tables_mixed", "value": ", ".join(prov.tables_mixed) or "none"},
    ]
    for i, note in enumerate(prov.notes):
        rows.append({"metric": f"note_{i+1}", "value": note})
    return pd.DataFrame(rows)
