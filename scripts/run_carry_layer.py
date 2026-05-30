#!/usr/bin/env python3
"""
Run interest-rate carry feature layer for USD/MXN research.

Carry is a regime/risk feature — not a magic trading signal.
Policy-rate carry is a proxy; forward points required for true hedge economics.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.carry_features import add_carry_features, carry_data_available
from src.carry_hedge_governance import run_carry_hedge_governance_suite, save_carry_hedge_scorecard
from src.carry_tests import run_carry_regime_tests, save_carry_test_results
from src.data_loader import load_config
from src.forward_points import merge_forward_points


def _load_base_features() -> pd.DataFrame:
    for name in (
        "usdmxn_features_regimes_news.csv",
        "usdmxn_features_regimes_flow.csv",
        "usdmxn_features_regimes.csv",
    ):
        path = ROOT / "data" / "processed" / name
        if path.exists():
            print(f"Loading: {path.name}")
            return pd.read_csv(path, parse_dates=["date"])
    print("Missing processed features. Run: python scripts/run_usdmxn_backtest.py")
    sys.exit(1)


def main() -> None:
    cfg = load_config()
    df = _load_base_features()
    print(f"Rows: {len(df)} ({df['date'].min().date()} → {df['date'].max().date()})")

    df_carry, status = add_carry_features(df, cfg)
    df_carry, fwd_status = merge_forward_points(df_carry, cfg)
    status.update(fwd_status)

    out_path = ROOT / "data" / "processed" / "usdmxn_features_regimes_carry.csv"
    df_carry.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")

    work = df_carry.set_index("date") if "date" in df_carry.columns else df_carry
    tests = run_carry_regime_tests(work)
    test_path = save_carry_test_results(tests)
    print(f"Saved: {test_path}")

    if carry_data_available(work):
        hg_sc = run_carry_hedge_governance_suite(work, cfg)
        hg_path = save_carry_hedge_scorecard(hg_sc)
        print(f"Saved: {hg_path}")
    else:
        print("Skipping carry hedge governance — no carry data.")

    latest = df_carry.iloc[-1]
    print("\n" + "=" * 55)
    print("BR3N Macro Labs — Carry Layer Summary")
    print("Research only · Carry = regime/risk feature · Not price prediction")
    print("=" * 55)
    print(f"Carry data available:     {status.get('carry_data_available', False)}")
    print(f"Placeholders only:        {status.get('placeholders_only', False)}")
    print(f"Domestic rate source:     {status.get('domestic_rate_source', '—')}")
    print(f"Foreign rate source:      {status.get('foreign_rate_source', '—')}")

    if pd.notna(latest.get("carry_proxy")):
        print(f"Latest carry proxy:       {float(latest['carry_proxy']):.4f}")
    if pd.notna(latest.get("carry_percentile")):
        print(f"Latest carry percentile:  {float(latest['carry_percentile']):.3f}")
    print(f"High carry now:           {bool(latest.get('is_high_carry', False))}")
    print(f"Carry fragility active:   {bool(latest.get('carry_fragility_regime', False))}")
    print(f"Carry-adjusted regime:    {latest.get('carry_adjusted_regime', '—')}")
    print(f"Forward data loaded:    {status.get('forward_loaded', False)}")
    if status.get("forward_path"):
        print(f"  Forward CSV:          {status['forward_path']} ({status.get('forward_rows', 0)} rows)")
    elif status.get("forward_csv_hint"):
        print(f"  {status['forward_csv_hint']}")

    hi_lo = tests[tests["test_name"] == "high_carry_vs_low_carry"]
    if not hi_lo.empty:
        row = hi_lo.iloc[0]
        print(f"\nHigh-carry vol:           {row.get('volatility_high_carry')}")
        print(f"Low-carry vol:            {row.get('volatility_low_carry')}")

    r2 = tests[tests["test_name"] == "r2_high_carry_stable_vs_fragile"]
    if not r2.empty:
        row = r2.iloc[0]
        print(f"R2 stable Sharpe-like:    {row.get('sharpe_like_r2_stable')}")
        print(f"R2 fragile Sharpe-like:   {row.get('sharpe_like_r2_fragile')}")

    if status.get("placeholders_only"):
        print("\nWARNING: Policy-rate carry is a proxy. Forward points required for hedge economics.")

    if status.get("errors"):
        print("\nWarnings:")
        for e in status["errors"]:
            print(f"  - {e}")

    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
