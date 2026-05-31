#!/usr/bin/env python3
"""
Run the FX research terminal pipeline (data → features → models → report).

Research-only. Not investment advice.

Usage:
  python scripts/run_fx_research_terminal.py
  python scripts/run_fx_research_terminal.py --pairs USDMXN=X EURUSD=X --horizon 10
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.backtesting.walk_forward import run_model_comparison
from src.data.constants import CORE_FX_PAIRS
from src.data.pipeline import build_terminal_data_bundle
from src.features.fx_terminal_features import build_multi_pair_feature_table
from src.risk.regime import classify_fx_regime
from src.utils.config import load_terminal_config
from src.utils.paths import FEATURES_DIR, OUTPUTS_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="BR3N FX Research Terminal pipeline")
    parser.add_argument("--pairs", nargs="*", default=CORE_FX_PAIRS[:4], help="Pairs to model")
    parser.add_argument("--horizon", type=int, default=5, choices=[5, 10, 20])
    parser.add_argument("--mock", action="store_true", help="Force mock data")
    args = parser.parse_args()

    cfg = load_terminal_config()
    print("Loading data bundle…")
    bundle = build_terminal_data_bundle(cfg, use_mock_on_failure=True)

    print("Building features…")
    features = build_multi_pair_feature_table(
        bundle.market,
        macro=bundle.macro,
        rates=bundle.rates,
        sentiment=bundle.sentiment,
        pairs=args.pairs,
    )
    feat_path = FEATURES_DIR / "terminal_feature_table.csv"
    features.to_csv(feat_path, index=False)
    print(f"  Saved {len(features)} rows → {feat_path}")

    print("Running walk-forward model comparison…")
    signals, comparison = run_model_comparison(
        features,
        pairs=args.pairs,
        horizon=args.horizon,
        train_years=cfg["fx_terminal"]["train_years"],
        test_years=cfg["fx_terminal"]["test_years"],
    )
    comp_path = OUTPUTS_DIR / "terminal_model_comparison.csv"
    sig_path = OUTPUTS_DIR / "terminal_model_signals.csv"
    comparison.to_csv(comp_path, index=False)
    if not signals.empty:
        signals.to_csv(sig_path, index=False)
    print(f"  Comparison → {comp_path}")
    print(comparison.to_string(index=False) if not comparison.empty else "  (no metrics)")

    # Latest regime from most recent macro row
    if not bundle.macro.empty:
        latest = bundle.macro.sort_values("date").iloc[-1]
        regime = classify_fx_regime(latest)
        print(f"\nCurrent regime: {regime.current_regime} ({regime.regime_confidence:.0%})")
        print(f"  {regime.regime_description}")

    print("\nDone. Launch dashboard: streamlit run src/fx_research_terminal.py")


if __name__ == "__main__":
    main()
