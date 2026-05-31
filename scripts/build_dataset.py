#!/usr/bin/env python3
"""Build processed VSI dataset from raw or mock data."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.build_dataset import build_and_validate, save_processed_dataset, save_vsi_outputs


def main() -> None:
    print("BR3N Value Survival Index — build dataset")
    print("=" * 60)
    dataset, validation = build_and_validate()
    paths = save_processed_dataset(dataset)
    vsi_path = save_vsi_outputs(dataset["value_survival_outputs"])
    print(f"\nSaved VSI outputs: {vsi_path} ({len(dataset['value_survival_outputs'])} rows)")
    print("\nProcessed tables:")
    for name, p in paths.items():
        print(f"  {name}: {p}")
    print("\nValidation:")
    print(validation.to_string(index=False))
    if "_provenance_report" in dataset:
        print("\nData provenance:")
        print(dataset["_provenance_report"].to_string(index=False))
    prov_mode = dataset["value_survival_outputs"]["data_mode"].iloc[0] if "data_mode" in dataset["value_survival_outputs"].columns else "unknown"
    mock = dataset["value_survival_outputs"]["mock_data_flag"].any()
    print(f"\nData mode: {prov_mode} · mock={mock}")
    if mock:
        print("⚠️  Demo mode: mock/synthetic data active.")


if __name__ == "__main__":
    main()
