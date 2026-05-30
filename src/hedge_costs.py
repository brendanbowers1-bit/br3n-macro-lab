"""Forward-aware hedge cost layers (turnover + spread/slippage + roll + carry drag)."""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .economic import economic_params_for


def hedge_cost_params(ticker: str, cfg: dict) -> Dict[str, Any]:
    """Resolve hedge friction parameters for a pair."""
    hg_cfg = cfg.get("hedge_governance", {})
    econ = economic_params_for(ticker, cfg)
    turnover_bps = float(
        hg_cfg.get("hedge_transaction_cost_bps")
        or cfg.get("research", {}).get("hedge_transaction_cost_bps", 2.0)
    )
    return {
        "turnover_bps": turnover_bps,
        "spread_bps": float(econ.get("spread_bps", 0)),
        "slippage_bps": float(econ.get("slippage_bps", 0)),
        "roll_bps_monthly": float(econ.get("roll_bps_monthly", 0)),
        "carry_annual_bps": float(econ.get("carry_annual_bps", 0)),
    }


def apply_hedge_costs(
    out: pd.DataFrame,
    ticker: str,
    cfg: dict,
    cost_layer: str = "base",
) -> pd.DataFrame:
    """
    Add hedge cost columns to a governance backtest frame.

    Layers:
    - base: turnover bps only (legacy)
    - forward_full: turnover + spread/slippage + forward roll + carry/forward-point drag
    """
    params = hedge_cost_params(ticker, cfg)
    turnover = out["hedge_turnover"]

    if cost_layer == "base":
        out["hedge_trade_cost"] = turnover * (params["turnover_bps"] / 10_000.0)
        out["forward_roll_cost"] = 0.0
        out["forward_carry_cost"] = 0.0
    elif cost_layer == "forward_full":
        bps_trade = params["turnover_bps"] + params["spread_bps"] + params["slippage_bps"]
        out["hedge_trade_cost"] = turnover * (bps_trade / 10_000.0)
        roll_daily = params["roll_bps_monthly"] / 10_000.0 / 21.0
        carry_daily = abs(params["carry_annual_bps"]) / 10_000.0 / 252.0
        out["forward_roll_cost"] = out["hedge_ratio"] * roll_daily
        out["forward_carry_cost"] = out["hedge_ratio"] * carry_daily
    else:
        raise ValueError(f"Unknown hedge cost_layer: {cost_layer}")

    out["hedge_cost"] = out["hedge_trade_cost"] + out["forward_roll_cost"] + out["forward_carry_cost"]
    out["cost_layer"] = cost_layer
    return out
