#!/usr/bin/env python3
"""Full USD/MXN pipeline: load → features → regimes → backtest → walk-forward → charts."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import LAB_NAME
from src.backtest import build_output_frame, scorecard, walk_forward_scorecard
from src.data_loader import load_config, load_or_fetch
from src.features import build_features
from src.regimes import classify_regimes


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Re-download from yfinance")
    args = parser.parse_args()

    cfg = load_config()
    ticker = cfg["data"]["ticker"]
    years = cfg["data"]["history_years"]
    print(f"{LAB_NAME} — {ticker} ({years}y)\n" + "=" * 50)

    prices, path = load_or_fetch(cfg, force_refresh=args.refresh)
    print(f"Data: {len(prices)} rows from {path}")

    feat = build_features(prices, cfg)
    df = classify_regimes(feat, cfg)

    out_dir = ROOT / cfg["reporting"]["output_dir"]
    chart_dir = ROOT / cfg["reporting"]["chart_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    chart_dir.mkdir(parents=True, exist_ok=True)

    detail = build_output_frame(df, cfg, "flat_range")
    cols = [
        "price", "regime", "signal", "position", "daily_return",
        "gross_strategy_return", "transaction_cost", "net_strategy_return",
        "buy_hold_return", "random_walk_return",
        "equity_strategy_gross", "equity_strategy_net",
        "equity_buy_hold", "equity_random_walk",
    ]
    detail[cols].to_csv(out_dir / "usdmxn_backtest_detail.csv")
    df.to_csv(out_dir / "usdmxn_labeled.csv")

    proc_dir = ROOT / "data" / "processed"
    proc_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(proc_dir / "usdmxn_features_regimes.csv")

    sc = scorecard(df, cfg)
    sc.to_csv(out_dir / "strategy_scorecard.csv", index=False)
    print("\nScorecard:\n", sc.to_string(index=False))

    wf_is, wf_oos = walk_forward_scorecard(df, cfg)
    if not wf_oos.empty:
        wf_oos.to_csv(out_dir / "walkforward_oos.csv", index=False)
        wf_is.to_csv(out_dir / "walkforward_in_sample.csv", index=False)
        print("\nWalk-forward OOS:\n", wf_oos.to_string(index=False))
    else:
        print("\nWalk-forward: skipped (need more history for 5y train + 1y test)")

    latest = df.iloc[-1]
    legacy = sc[sc["strategy"] == "legacy"].iloc[0]
    flat = sc[sc["strategy"] == "flat_range"].iloc[0]
    print(f"\nLatest regime: {latest['regime']}")
    print(f"Latest price:  {latest['price']:.4f}")
    print(f"flat_range beats legacy (Sharpe): {flat['sharpe'] > legacy['sharpe']}")

    fig, ax = plt.subplots(figsize=(11, 4))
    for strat in ["buy_and_hold", "legacy", "flat_range", "r2_only"]:
        from src.backtest import run_strategy_backtest
        bt = run_strategy_backtest(df, cfg, strat)
        ax.plot(bt.index, bt["equity"], label=strat)
    ax.legend()
    ax.set_title(f"{ticker} equity (net, with costs)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(chart_dir / "equity_curves.png", dpi=150)
    plt.close(fig)
    print(f"\nChart: {chart_dir / 'equity_curves.png'}")
    print(f"Outputs: {out_dir}")


if __name__ == "__main__":
    main()
