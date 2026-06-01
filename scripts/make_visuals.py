#!/usr/bin/env python3
"""Generate publication-quality VSI charts to reports/figures/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.data.vsi_loader import load_vsi_dataset
from src.data.vsi_quality import assess_dataset_provenance
from src.indices.remittance_welfare import calculate_remittance_welfare_table
from src.indices.hidden_fx_tax import calculate_hidden_fx_tax_table
from src.models.sensitivity import rank_stability_matrix, sensitivity_summary
from src.utils.paths import FIGURES_DIR, OUTPUTS_DIR
from src.visuals.vsi_charts import (
    chart_aggregate_welfare,
    chart_component_breakdown,
    chart_data_quality,
    chart_leakage_vs_volume,
    chart_loss_per_100,
    chart_official_vs_assumed,
    chart_rank_stability,
    chart_ranked_vsi,
    chart_ranked_vsi_by_col,
    chart_sensitivity_ranges,
    corridor_summary,
    save_figure,
)


def main() -> None:
    print("Bowers Frontier Value Survival Index — make visuals")
    print("=" * 60)

    ds = load_vsi_dataset(rebuild=False)
    vsi = ds["value_survival_outputs"]
    summary = corridor_summary(vsi)
    prov = assess_dataset_provenance(ds)

    print(f"Data mode: {prov.data_mode} · quality: {prov.overall_quality_score:.2f}")
    for note in prov.notes:
        print(f"  · {note}")

    flows = ds.get("remittance_flows")
    if flows is None:
        flows = pd.DataFrame()

    hft = calculate_hidden_fx_tax_table(
        ds["corridor_prices"], ds.get("fx_rates"), ds.get("macro_country_panel")
    )
    welfare = calculate_remittance_welfare_table(hft, flows, vsi)

    sens_path = OUTPUTS_DIR / "vsi_sensitivity_results.csv"
    if sens_path.exists():
        sens = pd.read_csv(sens_path)
        sens_summary = sensitivity_summary(sens)
        rank_mat = rank_stability_matrix(sens)
    else:
        sens_summary = pd.DataFrame()
        rank_mat = pd.DataFrame()

    charts = [
        ("vsi_core_ranked_bar.png", chart_ranked_vsi_by_col(summary, "vsi_core", "VSI Core by corridor")),
        ("vsi_risk_adjusted_ranked_bar.png", chart_ranked_vsi(summary)),
        ("vsi_extended_ranked_bar.png", chart_ranked_vsi_by_col(summary, "vsi_extended", "VSI Extended by corridor")),
        ("vsi_component_breakdown_stacked.png", chart_component_breakdown(vsi)),
        ("value_lost_per_100.png", chart_loss_per_100(summary)),
        ("aggregate_welfare_loss_by_corridor.png", chart_aggregate_welfare(welfare)),
        ("data_quality_score_by_corridor.png", chart_data_quality(vsi)),
        ("official_vs_assumed_components.png", chart_official_vs_assumed(vsi)),
        ("vsi_leakage_vs_volume.png", chart_leakage_vs_volume(vsi, flows)),
    ]
    if not sens_summary.empty:
        charts.extend([
            ("vsi_sensitivity_ranges.png", chart_sensitivity_ranges(sens_summary)),
            ("rank_stability_heatmap.png", chart_rank_stability(rank_mat)),
        ])

    saved = []
    for name, fig in charts:
        if fig is None or not fig.data:
            print(f"  Skip (empty): {name}")
            continue
        p = save_figure(fig, FIGURES_DIR / name)
        saved.append(p)
        print(f"  Saved: {p}")

    summary.to_csv(FIGURES_DIR / "vsi_corridor_summary.csv", index=False)
    print(f"  Saved: {FIGURES_DIR / 'vsi_corridor_summary.csv'}")
    print("\nResearch only — not investment advice.")


if __name__ == "__main__":
    main()
