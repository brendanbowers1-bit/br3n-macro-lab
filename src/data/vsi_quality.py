"""
Data quality and provenance scoring for the BR3N Value Survival Index.

Separates real ingested data from demo/seed data and formula placeholders.
Research-only — scores reflect data availability, not forecast accuracy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from src.utils.paths import RAW_DIR

DataMode = Literal["real", "mixed", "demo"]

# Component-level max quality when source is fully real
COMPONENT_QUALITY = {
    "explicit_fee_loss_pct": {"real": 0.95, "curated": 0.75, "placeholder": 0.35, "mock": 0.15},
    "fx_spread_loss_pct": {"real": 0.95, "curated": 0.75, "placeholder": 0.35, "mock": 0.15},
    "timing_loss_pct": {"real": 0.50, "curated": 0.45, "placeholder": 0.40, "mock": 0.20},
    "volatility_loss_pct": {"real": 0.80, "curated": 0.70, "placeholder": 0.45, "mock": 0.25},
    "inflation_erosion_pct": {"real": 0.85, "curated": 0.65, "placeholder": 0.40, "mock": 0.20},
    "payout_friction_pct": {"real": 0.70, "curated": 0.50, "placeholder": 0.35, "mock": 0.15},
    "dollar_dependency_drag_pct": {"real": 0.60, "curated": 0.55, "placeholder": 0.40, "mock": 0.20},
    "trust_discount_pct": {"real": 0.55, "curated": 0.50, "placeholder": 0.35, "mock": 0.20},
}

VSI_LIMITATIONS = (
    "Measurement framework only — not investment advice, not a trading signal, "
    "not a price forecast. Timing, volatility, payout, trust, and dollar-drag "
    "components use transparent starter formulas pending corridor validation. "
    "Causal claims require panel instruments or natural experiments."
)


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


def score_vsi_row(row: pd.Series, provenance: DataProvenanceReport) -> float:
    """Row-level quality 0–1 from component source tiers."""
    cp_tier = "mock" if provenance.mock_data_flag else _source_tier(row.get("source"))
    if cp_tier == "mock":
        cp_tier = "mock"
    elif cp_tier == "real" and "curated" in str(row.get("source", "")).lower():
        cp_tier = "curated"

    weights = {
        "explicit_fee_loss_pct": 0.20,
        "fx_spread_loss_pct": 0.20,
        "timing_loss_pct": 0.10,
        "volatility_loss_pct": 0.15,
        "inflation_erosion_pct": 0.10,
        "payout_friction_pct": 0.08,
        "dollar_dependency_drag_pct": 0.09,
        "trust_discount_pct": 0.08,
    }
    score = 0.0
    for comp, w in weights.items():
        val = float(row.get(comp, 0) or 0)
        if val <= 0:
            tier = cp_tier
        elif comp in ("timing_loss_pct", "payout_friction_pct", "trust_discount_pct", "dollar_dependency_drag_pct"):
            tier = "placeholder"
        elif comp in ("explicit_fee_loss_pct", "fx_spread_loss_pct"):
            tier = cp_tier if cp_tier != "mock" else "mock"
        else:
            tier = "real" if provenance.data_mode == "real" and not provenance.mock_data_flag else cp_tier
        score += w * COMPONENT_QUALITY[comp].get(tier, 0.4)
    return round(min(max(score, 0.0), 1.0), 3)


def annotate_vsi_outputs(vsi: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Add data_mode, limitations, and per-row quality scores."""
    prov = assess_dataset_provenance(tables)
    out = vsi.copy()
    out["data_mode"] = prov.data_mode
    out["mock_data_flag"] = prov.mock_data_flag or out.get("mock_data_flag", False)
    out["data_quality_score"] = out.apply(lambda r: score_vsi_row(r, prov), axis=1)
    out["limitations"] = VSI_LIMITATIONS
    out["value_survival_index"] = out["value_survival_index"].clip(0, 100)
    out["real_usable_value_delivered_pct"] = out["real_usable_value_delivered_pct"].clip(0, 1)
    out["total_value_loss_pct"] = out["total_value_loss_pct"].clip(0, 0.5)
    return out


def provenance_summary_df(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    prov = assess_dataset_provenance(tables)
    rows = [
        {"metric": "data_mode", "value": prov.data_mode},
        {"metric": "overall_quality_score", "value": prov.overall_quality_score},
        {"metric": "mock_data_flag", "value": prov.mock_data_flag},
        {"metric": "tables_real", "value": ", ".join(prov.tables_real) or "none"},
        {"metric": "tables_demo", "value": ", ".join(prov.tables_demo) or "none"},
        {"metric": "tables_mixed", "value": ", ".join(prov.tables_mixed) or "none"},
    ]
    for i, note in enumerate(prov.notes):
        rows.append({"metric": f"note_{i+1}", "value": note})
    return pd.DataFrame(rows)
