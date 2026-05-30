"""
Level 5: Economic value after realistic frictions (per-pair aware).
"""

from __future__ import annotations

import pandas as pd

from ..backtest import run_strategy_backtest
from ..economic import economic_params_for
from ..metrics import performance_metrics


def apply_economic_costs(bt: pd.DataFrame, cfg: dict, ticker: str | None = None) -> pd.DataFrame:
    """Extend turnover costs with spread, slippage, roll, optional carry."""
    ticker = ticker or cfg["data"]["ticker"]
    econ = economic_params_for(ticker, cfg)
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


def economic_scorecard(df: pd.DataFrame, cfg: dict, ticker: str | None = None) -> pd.DataFrame:
    primary = cfg["backtest"].get("primary_strategy", "flat_range")
    ticker = ticker or cfg["data"]["ticker"]
    ann = int(cfg["backtest"]["annualization_days"])
    rows = []
    for label, use_econ in [("base_costs_only", False), ("full_economic", True)]:
        if use_econ:
            bt = apply_economic_costs(run_strategy_backtest(df, cfg, primary), cfg, ticker)
        else:
            bt = run_strategy_backtest(df, cfg, primary)
        m = performance_metrics(bt["net_strategy_return"], bt["equity"], ann, primary)
        m["cost_layer"] = label
        m["ticker"] = ticker
        cost_col = bt.get("total_cost", bt["transaction_cost"])
        m["total_cost_pct"] = round(float(cost_col.sum()) * 100, 3)
        rows.append(m)
    return pd.DataFrame(rows)


def multipair_economic_scorecard(cfg: dict, tickers: list[str] | None = None) -> pd.DataFrame:
    """Full economic layer for each pair in the ladder list."""
    from ..data_loader import load_pair_prices
    from ..features import build_features
    from ..regimes import classify_regimes

    tickers = tickers or cfg.get("research_ladder", {}).get("pairs", [])
    years = int(cfg["data"]["history_years"])
    primary = cfg["backtest"].get("primary_strategy", "flat_range")
    rows = []
    for ticker in tickers:
        try:
            px, _ = load_pair_prices(ticker, years)
            df = classify_regimes(build_features(px, cfg), cfg)
            sub = economic_scorecard(df, cfg, ticker)
            sub = sub[sub["cost_layer"] == "full_economic"]
            rows.append(sub)
        except Exception as exc:
            rows.append(pd.DataFrame([{"ticker": ticker, "error": str(exc)[:100]}]))
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)
