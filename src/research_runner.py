"""
Master research pipeline — forecast tests, academic tests, ML models, hedge policies.

Research only. Not investment advice.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

from .academic_tests import diebold_mariano_test, save_academic_test_results, simple_white_reality_check
from .backtest import run_strategy_backtest
from .data_loader import load_config, load_or_fetch
from .features import build_features
from .forecast_tests import (
    forecast_scorecard,
    make_random_walk_forecast,
    regime_conditioned_return_forecast,
    save_forecast_scorecard,
)
from .hedge_backtest import run_all_hedge_policies, save_hedge_outputs
from .regimes import classify_regimes
from .research_models import (
    regime_conditioned_trend_forecast,
    run_direction_models,
    save_ml_scorecard,
)

ROOT = Path(__file__).resolve().parents[1]


def load_research_data(cfg: dict) -> pd.DataFrame:
    """
    Load processed USD/MXN features + regimes.

    Priority:
      1. data/processed/usdmxn_features_regimes.csv
      2. data/outputs/usdmxn_labeled.csv
      3. Build from pipeline
    """
    proc = ROOT / "data" / "processed" / "usdmxn_features_regimes.csv"
    labeled = ROOT / cfg["reporting"]["output_dir"] / "usdmxn_labeled.csv"

    if proc.exists():
        df = pd.read_csv(proc, parse_dates=[0], index_col=0)
        df.index.name = "date"
        return df
    if labeled.exists():
        df = pd.read_csv(labeled, parse_dates=[0], index_col=0)
        df.index.name = "date"
        return df

    prices, _ = load_or_fetch(cfg)
    feat = build_features(prices, cfg)
    return classify_regimes(feat, cfg)


def _oos_forecast_test(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """OOS forecast scorecard on last 30% of sample."""
    train_ratio = float(cfg.get("research", {}).get("train_ratio", 0.7))
    cut = int(len(df) * train_ratio)
    train, test = df.iloc[:cut], df.iloc[cut:]
    if len(test) < 50:
        return pd.DataFrame([{"error": "insufficient test sample"}])

    test = test.copy()
    test["model_forecast"] = regime_conditioned_return_forecast(test, train)
    rw = make_random_walk_forecast(test, horizon=1, mode="return")
    test["rw_forecast"] = rw["rw_forecast"]
    test["target"] = rw["target"]

    sc = forecast_scorecard(test, "model_forecast", "target", "rw_forecast")
    sc["sample"] = "oos_last_30pct"
    sc["model"] = "regime_conditioned_mean_return"
    return sc


def run_full_research_pipeline(cfg: Optional[dict] = None) -> Dict[str, Path]:
    cfg = cfg or load_config()
    out_dir = ROOT / cfg["reporting"]["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    proc_path = ROOT / "data" / "processed" / "usdmxn_features_regimes.csv"
    if not proc_path.exists() and not (out_dir / "usdmxn_labeled.csv").exists():
        raise FileNotFoundError(
            "Processed data missing. Run first:\n  python scripts/run_usdmxn_backtest.py"
        )

    df = load_research_data(cfg)
    paths: Dict[str, Path] = {}

    # --- Forecast tests ---
    fc_sc = _oos_forecast_test(df, cfg)
    paths["forecast_scorecard"] = save_forecast_scorecard(fc_sc)

    # --- Academic tests ---
    train_ratio = float(cfg.get("research", {}).get("train_ratio", 0.7))
    cut = int(len(df) * train_ratio)
    train, test = df.iloc[:cut], df.iloc[cut:]
    test = test.copy()
    test["model_forecast"] = regime_conditioned_return_forecast(test, train)
    rw = make_random_walk_forecast(test, horizon=1, mode="return")
    actual = rw["target"].dropna()
    e_model = (actual - test.loc[actual.index, "model_forecast"]).values
    e_rw = (actual - rw.loc[actual.index, "rw_forecast"]).values
    dm = diebold_mariano_test(e_model, e_rw, power=2)

    # White RC on strategy returns if we can build them
    strat_rets = {}
    for s in ["legacy", "flat_range", "r2_only"]:
        bt = run_strategy_backtest(df, cfg, s)
        strat_rets[s] = bt["net_strategy_return"]
    rw_bt = run_strategy_backtest(df, cfg, "random_walk")
    wrc = simple_white_reality_check(strat_rets, rw_bt["net_strategy_return"])

    ac_rows = [
        {"test": "diebold_mariano_rmse", **dm},
        {"test": "white_reality_check", **{k: v for k, v in wrc.items() if k != "warning"}},
        {"test": "white_rc_warning", "interpretation": wrc.get("warning", "")},
    ]
    ac_df = pd.DataFrame(ac_rows)
    paths["academic_test_results"] = save_academic_test_results(ac_df)

    # --- ML direction models ---
    ml_sc = run_direction_models(df, cfg)
    paths["ml_direction_model_scorecard"] = save_ml_scorecard(ml_sc)

    # --- Hedge policy tests ---
    exposure = cfg.get("research", {}).get("default_exposure", "us_entity_long_mxn")
    h_sc, h_det = run_all_hedge_policies(df, cfg, exposure)
    paths["hedge_policy_scorecard"], paths["hedge_policy_detail"] = save_hedge_outputs(h_sc, h_det)

    # --- Terminal summary ---
    _print_summary(fc_sc, dm, ml_sc, h_sc, wrc)
    return paths


def _print_summary(fc_sc, dm, ml_sc, h_sc, wrc) -> None:
    print("\n" + "=" * 60)
    print("Bowers Frontier Macro Labs — Research Pipeline Summary")
    print("=" * 60)

    if not fc_sc.empty and "rmse_model" in fc_sc.columns:
        row = fc_sc.iloc[0]
        print(f"Beats random walk by RMSE: {row.get('model_beats_rw_rmse', 'n/a')}")
        print(f"Beats random walk by MAE:   {row.get('model_beats_rw_mae', 'n/a')}")
    print(f"Diebold-Mariano p-value:    {dm.get('p_value', 'n/a')}")
    print(f"DM interpretation:          {dm.get('interpretation', '')}")

    if not ml_sc.empty and "directional_accuracy" in ml_sc.columns:
        valid = ml_sc[ml_sc["model_name"].str.contains("direction", na=False)]
        if not valid.empty:
            best = valid.loc[valid["directional_accuracy"].astype(float).idxmax()]
            print(f"Best ML direction model:    {best['model_name']} ({best['directional_accuracy']}%)")

    if not h_sc.empty:
        best_h = h_sc.loc[h_sc["cost_adjusted_risk_reduction"].idxmax()]
        print(f"Best hedge policy (cost-adj risk reduction): {best_h['policy']}")
        print(f"  Vol reduction: {best_h['volatility_reduction']}% | Turnover: {best_h['hedge_turnover']}")

    static = h_sc[h_sc["policy"].isin(["never_hedged", "half_hedged", "mostly_hedged", "fully_hedged"])]
    regime = h_sc[h_sc["policy"] == "regime_based"]
    if not static.empty and not regime.empty:
        rb = regime.iloc[0]
        best_static = static.loc[static["cost_adjusted_risk_reduction"].idxmax()]
        beats = rb["cost_adjusted_risk_reduction"] > best_static["cost_adjusted_risk_reduction"]
        print(f"Regime-based hedging beats best static policy: {beats}")

    print(f"\nWhite RC p-value: {wrc.get('bootstrap_p_value', 'n/a')} — {wrc.get('warning', '')[:80]}...")
    print("\nReminder: Research and risk-framing only. Not investment advice.")
    print("=" * 60)
