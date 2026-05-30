"""
Level 5: Economic value after realistic frictions.
"""

from __future__ import annotations

import pandas as pd

from ..backtest import run_strategy_backtest
from ..metrics import performance_metrics


def apply_economic_costs(bt: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Extend turnover costs with spread, slippage, roll, optional carry."""
    econ = cfg.get("economic", {})
    out = bt.copy()
    turnover = out["turnover"]
    bps_trade = (
        float(cfg["backtest"]["transaction_cost_bps"])
        + float(econ.get("spread_bps", 0))
        + float(econ.get("slippage_bps", 0))
    )
    out["trade_cost"] = turnover * (bps_trade / 10_000.0)
    roll_daily = float(econ.get("roll_bps_monthly", 0)) / 10_000.0 / 21.0
    out["roll_cost"] = out["position"].abs() * roll_daily
    carry_daily = float(econ.get("carry_annual_bps", 0)) / 10_000.0 / 252.0
    out["carry_pnl"] = out["position"] * carry_daily
    out["gross_strategy_return"] = out["position"] * out["daily_return"] + out["carry_pnl"]
    out["total_cost"] = out["trade_cost"] + out["roll_cost"]
    out["net_strategy_return"] = out["gross_strategy_return"] - out["total_cost"]
    out["equity"] = (1.0 + out["net_strategy_return"]).cumprod()

    mdd_stop = econ.get("max_drawdown_stop")
    if mdd_stop:
        dd = out["equity"] / out["equity"].cummax() - 1
        out.loc[dd < -float(mdd_stop), "position"] = 0.0

    return out


def economic_scorecard(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    primary = cfg["backtest"].get("primary_strategy", "flat_range")
    ann = int(cfg["backtest"]["annualization_days"])
    rows = []
    for label, use_econ in [("base_costs_only", False), ("full_economic", True)]:
        if use_econ:
            bt = apply_economic_costs(run_strategy_backtest(df, cfg, primary), cfg)
        else:
            bt = run_strategy_backtest(df, cfg, primary)
        m = performance_metrics(bt["net_strategy_return"], bt["equity"], ann, primary)
        m["cost_layer"] = label
        m["total_cost_pct"] = round(float(bt.get("total_cost", bt["transaction_cost"]).sum()) * 100, 3)
        rows.append(m)
    return pd.DataFrame(rows)
