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
from src.utils.paths import FIGURES_DIR
from src.visuals.vsi_charts import (
    chart_component_breakdown,
    chart_leakage_vs_volume,
    chart_loss_per_100,
    chart_ranked_vsi,
    corridor_summary,
    save_figure,
)


def main() -> None:
    print("BR3N Value Survival Index — make visuals")
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
    charts = [
        ("vsi_ranked_corridors.png", chart_ranked_vsi(summary)),
        ("vsi_loss_per_100.png", chart_loss_per_100(summary)),
        ("vsi_component_breakdown.png", chart_component_breakdown(vsi)),
        ("vsi_leakage_vs_volume.png", chart_leakage_vs_volume(vsi, flows)),
    ]

    saved = []
    for name, fig in charts:
        p = save_figure(fig, FIGURES_DIR / name)
        saved.append(p)
        print(f"  Saved: {p}")

    summary.to_csv(FIGURES_DIR / "vsi_corridor_summary.csv", index=False)
    print(f"  Saved: {FIGURES_DIR / 'vsi_corridor_summary.csv'}")
    print("\nResearch only — not investment advice.")


if __name__ == "__main__":
    main()
