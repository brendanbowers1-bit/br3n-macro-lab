#!/usr/bin/env python3
"""Run Bowers Frontier Value Survival Index pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.data.build_dataset import build_value_survival_dataset, save_vsi_outputs
from src.data.vsi_quality import assess_dataset_provenance
from src.indices.hidden_fx_tax import calculate_hidden_fx_tax_table, rank_corridors_by_hidden_fx_tax
from src.indices.remittance_welfare import calculate_remittance_welfare_table, rank_corridors_by_welfare_loss


def main() -> None:
    print("Bowers Frontier Value Survival Index (VSI)")
    print("=" * 60)
    print("Question: For every $100 sent, how much survives as usable purchasing power?\n")

    dataset = build_value_survival_dataset()
    vsi = dataset["value_survival_outputs"]
    out_path = save_vsi_outputs(vsi)
    prov = assess_dataset_provenance(dataset)

    print(f"Data mode: {prov.data_mode} · quality score: {prov.overall_quality_score:.0%}")
    for note in prov.notes:
        print(f"  · {note}")
    print()

    hft = calculate_hidden_fx_tax_table(
        dataset["corridor_prices"],
        dataset.get("fx_rates"),
        dataset.get("macro_country_panel"),
    )
    welfare = calculate_remittance_welfare_table(hft, dataset["remittance_flows"], vsi)

    corridor_summary = (
        vsi.groupby("corridor", as_index=False)
        .agg(
            value_survival_index=("value_survival_index", "mean"),
            total_value_loss_pct=("total_value_loss_pct", "mean"),
            value_loss_usd_per_100=("value_loss_usd_per_100", "mean"),
            interpretation=("interpretation", "first"),
            mock_data_flag=("mock_data_flag", "first"),
        )
        .sort_values("value_survival_index")
    )

    print(f"Saved: {out_path} ({len(vsi)} corridor observations)\n")

    print("Top 10 highest value LEAKAGE corridors (lowest VSI):")
    print(corridor_summary.head(10).to_string(index=False))

    print("\nTop 10 highest value SURVIVAL corridors (highest VSI):")
    print(corridor_summary.sort_values("value_survival_index", ascending=False).head(10).to_string(index=False))

    if not welfare.empty:
        print("\nTop 5 aggregate welfare loss corridors (USD):")
        top_w = rank_corridors_by_welfare_loss(welfare).head(5)
        cols = [c for c in ["corridor", "year", "annual_remittance_usd", "aggregate_value_loss_usd", "vsi_score"] if c in top_w.columns]
        print(top_w[cols].to_string(index=False))

    mock = vsi["mock_data_flag"].any() if "mock_data_flag" in vsi.columns else False
    if mock:
        print("\n⚠️  Demo mode: synthetic mock data — not for research conclusions.")
    print("\nDashboard: streamlit run src/dashboard/app.py")


if __name__ == "__main__":
    main()
