#!/usr/bin/env python3
"""Batch scorecard for pairs listed in config (optional extension)."""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.backtest import scorecard
from src.data_loader import fetch_prices, load_config
from src.features import build_features
from src.regimes import classify_regimes

def main():
    cfg = load_config()
    rows = []
    for ticker in cfg.get("pairs", [cfg["data"]["ticker"]]):
        try:
            px = fetch_prices(ticker, cfg["data"]["history_years"])
            df = classify_regimes(build_features(px, cfg), cfg)
            sc = scorecard(df, cfg)
            sc["ticker"] = ticker
            rows.append(sc)
        except Exception as e:
            print(f"SKIP {ticker}: {e}")
    if rows:
        out = pd.concat(rows, ignore_index=True)
        p = ROOT / cfg["reporting"]["output_dir"] / "multi_pair_scorecard.csv"
        out.to_csv(p, index=False)
        print(out)
        print(f"Saved {p}")

if __name__ == "__main__":
    main()
