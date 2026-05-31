#!/usr/bin/env python3
"""Run all settlement lab flagship indices."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.build_dataset import build_settlement_dataset, save_outputs


def main() -> None:
    print("BR3N Settlement Economics Lab — run indices")
    ds = build_settlement_dataset()
    save_outputs(ds)
    for key in ("settlement_drag_outputs", "operational_liquidity_outputs",
                "finality_quality_outputs", "payment_fragility_outputs", "friction_incidence_outputs"):
        df = ds[key]
        print(f"\n{key}: {len(df)} rows")
        if not df.empty:
            score_col = next((c for c in df.columns if "index" in c or c.endswith("_score")), None)
            if score_col and "entity" in df.columns:
                print(df[["entity", score_col]].head(5).to_string(index=False))


if __name__ == "__main__":
    main()
