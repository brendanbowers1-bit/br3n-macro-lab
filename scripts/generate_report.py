#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.backtest import scorecard, walk_forward_scorecard
from src.data_loader import load_config, load_or_fetch
from src.features import build_features
from src.regimes import classify_regimes
from src.reporting import generate_report


def main() -> None:
    cfg = load_config()
    prices, _ = load_or_fetch(cfg)
    df = classify_regimes(build_features(prices, cfg), cfg)
    sc = scorecard(df, cfg)
    wf_is, wf_oos = walk_forward_scorecard(df, cfg)
    path = generate_report(df, sc, wf_is, wf_oos, cfg, cfg["data"]["ticker"])
    print(f"Report: {path}")


if __name__ == "__main__":
    main()
