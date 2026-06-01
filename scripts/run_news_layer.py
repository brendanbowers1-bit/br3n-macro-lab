#!/usr/bin/env python3
"""
Run news and uncertainty feature layer for USD/MXN research.

Research-only — news is a regime/risk feature, not a price prediction engine.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.data_loader import load_config
from src.news_features import add_news_features
from src.news_tests import run_news_feature_tests, save_news_test_results


def main() -> None:
    cfg = load_config()
    processed = ROOT / "data" / "processed" / "usdmxn_features_regimes.csv"
    if not processed.exists():
        print("Missing data/processed/usdmxn_features_regimes.csv")
        print("Run: python scripts/run_usdmxn_backtest.py")
        sys.exit(1)

    df = pd.read_csv(processed, parse_dates=["date"])
    print(f"Loaded {len(df)} rows ({df['date'].min().date()} → {df['date'].max().date()})")

    flow_path = ROOT / "data" / "processed" / "usdmxn_features_regimes_flow.csv"
    if flow_path.exists() and "is_flow_pressure_window" not in df.columns:
        flow = pd.read_csv(flow_path, parse_dates=["date"])
        if "is_flow_pressure_window" in flow.columns:
            df = df.merge(flow[["date", "is_flow_pressure_window"]], on="date", how="left")

    df_news, status = add_news_features(df, cfg)
    out_path = ROOT / "data" / "processed" / "usdmxn_features_regimes_news.csv"
    df_news.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")

    results = run_news_feature_tests(df_news.set_index("date") if "date" in df_news.columns else df_news)
    test_path = save_news_test_results(results)
    print(f"Saved: {test_path}")

    print("\n" + "=" * 55)
    print("Bowers Frontier Macro Labs — News Layer Summary")
    print("Research only · News = regime/risk feature · Not price prediction")
    print("=" * 55)
    print(f"FRED uncertainty loaded:  {status.get('fred_loaded', False)}")
    if status.get("fred_series_loaded"):
        print(f"  Series: {', '.join(status['fred_series_loaded'])}")
    print(f"GDELT loaded:             {status.get('gdelt_loaded', False)}")
    if not status.get("gdelt_loaded") and not cfg.get("news", {}).get("use_gdelt", False):
        print("  (skipped — news.use_gdelt is false)")
    print(f"Placeholders only:        {status.get('placeholders_only', False)}")
    print(f"News features added:      {len(status.get('features_added', []))}")

    high_row = results[results["test_name"] == "high_vs_normal_news_stress"]
    if not high_row.empty:
        hr = high_row.iloc[0]
        vol_h = hr.get("volatility_high_news")
        vol_n = hr.get("volatility_normal")
        print(f"\nHigh-news-stress volatility: {vol_h}")
        print(f"Normal-day volatility:       {vol_n}")
        if vol_h is not None and vol_n is not None:
            print(f"Higher vol on high-news days: {vol_h > vol_n}")

    r2_row = results[results["test_name"] == "r2_low_news_vs_r2_high_news"]
    if not r2_row.empty:
        rr = r2_row.iloc[0]
        print(f"\nR2 low-news Sharpe proxy:  {rr.get('sharpe_proxy_r2_low_news')}")
        print(f"R2 high-news Sharpe proxy: {rr.get('sharpe_proxy_r2_high_news')}")
        sl = rr.get("sharpe_proxy_r2_low_news")
        sh = rr.get("sharpe_proxy_r2_high_news")
        if sl is not None and sh is not None:
            print(f"R2 low-news performs better: {sl > sh}")

    if status.get("errors"):
        print("\nWarnings:")
        for e in status["errors"]:
            print(f"  - {e}")

    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
