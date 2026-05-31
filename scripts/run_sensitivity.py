#!/usr/bin/env python3
"""Run VSI sensitivity analysis across conservative, baseline, and severe cases."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.build_dataset import build_value_survival_dataset
from src.models.sensitivity import rank_stability_matrix, run_sensitivity_analysis, sensitivity_summary
from src.utils.paths import OUTPUTS_DIR, FIGURES_DIR


def main() -> None:
    print("BR3N Value Survival Index — Sensitivity Analysis")
    print("=" * 60)

    dataset = build_value_survival_dataset()
    mock = dataset["value_survival_outputs"]["mock_data_flag"].any()
    results = run_sensitivity_analysis(
        dataset["corridor_prices"],
        dataset.get("fx_rates"),
        dataset.get("macro_country_panel"),
        dataset.get("currency_trust"),
        dataset.get("dollar_dependency"),
        mock_data_flag=bool(mock),
    )

    out_path = OUTPUTS_DIR / "vsi_sensitivity_results.csv"
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(results)} rows)")

    summary = sensitivity_summary(results)
    print("\nCorridor VSI ranges (risk-adjusted):")
    print(summary[["corridor", "vsi_risk_min", "vsi_risk_max", "vsi_range"]].head(10).to_string(index=False))

    rank_mat = rank_stability_matrix(results)
    rank_path = OUTPUTS_DIR / "vsi_rank_stability.csv"
    rank_mat.to_csv(rank_path, index=False)
    print(f"\nSaved rank stability: {rank_path}")

    try:
        from src.visuals.vsi_charts import chart_sensitivity_ranges, chart_rank_stability, save_figure

        fig1 = chart_sensitivity_ranges(summary)
        fig2 = chart_rank_stability(rank_mat)
        save_figure(fig1, FIGURES_DIR / "vsi_sensitivity_ranges.png")
        save_figure(fig2, FIGURES_DIR / "vsi_rank_stability.png")
        print(f"Saved figures to {FIGURES_DIR}")
    except Exception as exc:
        print(f"Figure generation skipped: {exc}")

    if mock:
        print("\n⚠️  Demo/mock data — sensitivity ranges are illustrative only.")


if __name__ == "__main__":
    main()
