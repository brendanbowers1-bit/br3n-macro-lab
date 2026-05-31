"""
Sensitivity analysis for VSI — conservative, baseline, and severe assumptions.

Research-only. Ranks and value-loss estimates under alternative parameter weights.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import SENSITIVITY_CASES
from src.data.data_quality import annotate_quality
from src.indices.value_survival import calculate_vsi_for_corridors


def run_sensitivity_analysis(
    corridor_prices: pd.DataFrame,
    fx_rates: pd.DataFrame | None = None,
    macro: pd.DataFrame | None = None,
    trust_scores: pd.DataFrame | None = None,
    dollar_dependency: pd.DataFrame | None = None,
    mock_data_flag: bool = False,
) -> pd.DataFrame:
    """Run all sensitivity cases and return long-format results."""
    frames = []
    for case in SENSITIVITY_CASES:
        vsi = calculate_vsi_for_corridors(
            corridor_prices,
            fx_rates,
            macro,
            trust_scores,
            dollar_dependency,
            mock_data_flag=mock_data_flag,
            sensitivity_case=case,
        )
        vsi["sensitivity_case"] = case
        frames.append(vsi)

    combined = pd.concat(frames, ignore_index=True)
    tables = {
        "corridor_prices": corridor_prices,
        "fx_rates": fx_rates if fx_rates is not None and not fx_rates.empty else pd.DataFrame(),
        "macro_country_panel": macro if macro is not None and not macro.empty else pd.DataFrame(),
    }
    return annotate_quality(combined, tables)


def sensitivity_summary(vsi_long: pd.DataFrame) -> pd.DataFrame:
    """Corridor-level min/mean/max VSI across sensitivity cases."""
    if vsi_long.empty:
        return vsi_long

    agg = (
        vsi_long.groupby("corridor", as_index=False)
        .agg(
            vsi_core_min=("vsi_core", "min"),
            vsi_core_max=("vsi_core", "max"),
            vsi_core_mean=("vsi_core", "mean"),
            vsi_risk_min=("vsi_risk_adjusted", "min"),
            vsi_risk_max=("vsi_risk_adjusted", "max"),
            vsi_risk_mean=("vsi_risk_adjusted", "mean"),
            vsi_extended_min=("vsi_extended", "min"),
            vsi_extended_max=("vsi_extended", "max"),
            vsi_extended_mean=("vsi_extended", "mean"),
            value_loss_per_100_min=("value_loss_usd_per_100", "min"),
            value_loss_per_100_max=("value_loss_usd_per_100", "max"),
            data_quality_score=("data_quality_score", "mean"),
        )
        .assign(vsi_range=lambda d: d["vsi_risk_max"] - d["vsi_risk_min"])
        .sort_values("vsi_risk_mean")
    )
    return agg


def rank_stability_matrix(vsi_long: pd.DataFrame) -> pd.DataFrame:
    """Spearman-like rank correlation proxy across sensitivity cases."""
    if vsi_long.empty or "sensitivity_case" not in vsi_long.columns:
        return pd.DataFrame()

    ranks = {}
    for case in SENSITIVITY_CASES:
        sub = (
            vsi_long[vsi_long["sensitivity_case"] == case]
            .groupby("corridor", as_index=False)["vsi_risk_adjusted"]
            .mean()
            .sort_values("vsi_risk_adjusted")
            .reset_index(drop=True)
        )
        sub["rank"] = range(1, len(sub) + 1)
        ranks[case] = sub.set_index("corridor")["rank"]

    corridors = sorted(set().union(*[set(r.index) for r in ranks.values()]))
    mat = pd.DataFrame({case: ranks[case].reindex(corridors) for case in SENSITIVITY_CASES})
    mat.index.name = "corridor"
    return mat.reset_index()
