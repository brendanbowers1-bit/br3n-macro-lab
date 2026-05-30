#!/usr/bin/env python3
"""
Run the FX Lab model zoo — research only, no live trading.

Usage:
  python scripts/run_model_zoo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.data_loader import load_config
from src.model_evaluation import evaluate_all_models, save_run_log
from src.model_walk_forward import run_model_zoo_walk_forward
from src.model_zoo import run_model_zoo


def _load_features() -> pd.DataFrame:
    carry_path = ROOT / "data/processed/usdmxn_features_regimes_carry.csv"
    news_path = ROOT / "data/processed/usdmxn_features_regimes_news.csv"
    flow_path = ROOT / "data/processed/usdmxn_features_regimes_flow.csv"
    base_path = ROOT / "data/processed/usdmxn_features_regimes.csv"

    if carry_path.exists():
        path = carry_path
        print(f"Using carry-enhanced features: {path.name}")
    elif news_path.exists():
        path = news_path
        print(f"Using news-enhanced features: {path.name}")
    elif flow_path.exists():
        path = flow_path
    elif base_path.exists():
        path = base_path
    else:
        print("Missing processed data. Run first:")
        print("  python scripts/run_usdmxn_backtest.py")
        print("  python scripts/run_carry_layer.py  # optional carry features")
        sys.exit(1)

    df = pd.read_csv(path, parse_dates=["date"])
    df = df.sort_values("date").set_index("date")
    return df


def _print_summary(
    run_log: pd.DataFrame,
    fc_sc: pd.DataFrame,
    tr_sc: pd.DataFrame,
    hg_sc: pd.DataFrame,
    wf_sc: pd.DataFrame,
) -> None:
    attempted = len(run_log)
    success = int((run_log["status"] == "success").sum())
    skipped = int((run_log["status"] == "skipped").sum())

    print("\n" + "=" * 60)
    print("BR3N Macro Labs — Model Zoo Summary")
    print("Research only · Not investment advice · No live trading")
    print("=" * 60)
    print(f"Models attempted:  {attempted}")
    print(f"Models successful: {success}")
    print(f"Models skipped:    {skipped}")

    if not run_log[run_log["status"] == "skipped"].empty:
        print("\nSkipped models:")
        for _, row in run_log[run_log["status"] == "skipped"].iterrows():
            print(f"  - {row['model_name']}: {row['reason']} {row['required_columns_missing']}")

    if not fc_sc.empty:
        fc_sc = fc_sc.copy()
        fc_sc["rmse_improvement"] = fc_sc["rmse_random_walk"] - fc_sc["rmse_model"]
        best_fc = fc_sc.sort_values("rmse_improvement", ascending=False).iloc[0]
        beats_rmse = fc_sc["model_beats_rw_rmse"].sum()
        beats_mae = fc_sc["model_beats_rw_mae"].sum()
        print(f"\nBest forecast (RMSE improvement): {best_fc['model_name']} "
              f"(Δ={best_fc['rmse_improvement']:.6f})")
        print(f"Models beating random walk by RMSE: {beats_rmse}")
        print(f"Models beating random walk by MAE:  {beats_mae}")
        if beats_rmse == 0:
            print("WARNING: No model beats random walk by RMSE — conditional forecastability not supported.")

    if not tr_sc.empty and "sharpe_net" in tr_sc.columns:
        best_tr = tr_sc.sort_values("sharpe_net", ascending=False).iloc[0]
        print(f"\nBest trading model (Sharpe net): {best_tr['model_name']} "
              f"(Sharpe={best_tr['sharpe_net']})")

    if not hg_sc.empty and "cost_adjusted_risk_reduction" in hg_sc.columns:
        best_hg = hg_sc.sort_values("cost_adjusted_risk_reduction", ascending=False).iloc[0]
        print(f"\nBest hedge model (cost-adj risk reduction): {best_hg['model_name']} "
              f"({best_hg['cost_adjusted_risk_reduction']})")

    if wf_sc is not None and not wf_sc.empty:
        print(f"\nWalk-forward windows tested: {int(wf_sc['windows_tested'].max())} max per model")
        if "sharpe_net" in wf_sc.columns:
            wf_tr = wf_sc.dropna(subset=["sharpe_net"]).sort_values("sharpe_net", ascending=False)
            if not wf_tr.empty:
                print(f"Best walk-forward Sharpe: {wf_tr.iloc[0]['model_name']} "
                      f"({wf_tr.iloc[0]['sharpe_net']})")
    print("=" * 60 + "\n")


def main() -> None:
    cfg = load_config()
    if not cfg.get("model_zoo", {}).get("enabled", True):
        print("model_zoo.enabled is false in config.yaml")
        sys.exit(0)

    df = _load_features()
    print(f"Loaded {len(df)} rows ({df.index.min().date()} → {df.index.max().date()})")

    outputs, run_log = run_model_zoo(df, cfg)
    save_run_log(run_log, cfg)

    fc_sc, tr_sc, hg_sc = evaluate_all_models(df, outputs, cfg)

    wf_sc, wf_det = pd.DataFrame(), pd.DataFrame()
    if cfg.get("model_zoo", {}).get("walk_forward_enabled", True):
        wf_sc, wf_det = run_model_zoo_walk_forward(df, cfg)

    _print_summary(run_log, fc_sc, tr_sc, hg_sc, wf_sc)

    out = ROOT / "data/outputs"
    print("Outputs written to data/outputs/:")
    for name in [
        "model_zoo_forecast_scorecard.csv",
        "model_zoo_trading_scorecard.csv",
        "model_zoo_hedge_scorecard.csv",
        "model_zoo_run_log.csv",
        "model_zoo_walk_forward_scorecard.csv",
        "model_zoo_walk_forward_detail.csv",
    ]:
        p = out / name
        if p.exists():
            print(f"  {p.name}")


if __name__ == "__main__":
    main()
