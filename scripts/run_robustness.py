#!/usr/bin/env python3
"""Run VSI robustness checks across alternative specifications."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.build_dataset import build_value_survival_dataset
from src.models.robustness import run_robustness_checks
from src.utils.paths import OUTPUTS_DIR


def main() -> None:
    print("BR3N Value Survival Index — Robustness Checks")
    print("=" * 60)
    print("Results are robust if corridor rankings remain similar across specifications.\n")

    dataset = build_value_survival_dataset()
    mock = dataset["value_survival_outputs"]["mock_data_flag"].any()
    checks = run_robustness_checks(
        dataset["corridor_prices"],
        dataset.get("fx_rates"),
        dataset.get("macro_country_panel"),
        dataset.get("currency_trust"),
        dataset.get("dollar_dependency"),
        mock_data_flag=bool(mock),
    )

    out_path = OUTPUTS_DIR / "robustness_results.csv"
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    checks.to_csv(out_path, index=False)
    print(f"Saved: {out_path}\n")
    print(checks.to_string(index=False))

    if mock:
        print("\n⚠️  Demo/mock data — robustness metrics are illustrative only.")


if __name__ == "__main__":
    main()
