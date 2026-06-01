#!/usr/bin/env python3
"""Run stablecoin lab flagship indices."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.build_dataset import build_stablecoin_dataset, save_outputs

INDEX_KEYS = (
    "stablecoin_finality_quality_outputs",
    "settlement_window_compression_outputs",
    "liquidity_transformation_outputs",
    "digital_run_velocity_outputs",
    "stablecoin_dollarization_outputs",
    "tokenized_money_singleness_outputs",
    "compliance_settlement_drag_outputs",
    "stablecoin_value_survival_outputs",
)


def main() -> None:
    print("Bowers Frontier Stablecoin Settlement Window Lab — run indices")
    ds = build_stablecoin_dataset()
    save_outputs(ds)
    for key in INDEX_KEYS:
        df = ds.get(key, None)
        if df is None or df.empty:
            print(f"\n{key}: empty")
            continue
        print(f"\n{key}: {len(df)} rows")
        score_col = next((c for c in df.columns if "index" in c.lower() or c.endswith("_score")), None)
        if score_col and "entity" in df.columns:
            print(df[["entity", score_col]].head(5).to_string(index=False))


if __name__ == "__main__":
    main()
