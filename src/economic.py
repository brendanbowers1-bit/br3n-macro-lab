"""Resolve per-pair economic friction parameters."""

from __future__ import annotations

from typing import Any, Dict


def economic_params_for(ticker: str, cfg: dict) -> Dict[str, Any]:
    econ = cfg.get("economic", {})
    params = {
        "spread_bps": float(econ.get("spread_bps", 0)),
        "slippage_bps": float(econ.get("slippage_bps", 0)),
        "roll_bps_monthly": float(econ.get("roll_bps_monthly", 0)),
        "carry_annual_bps": float(econ.get("carry_annual_bps", 0)),
        "max_drawdown_stop": econ.get("max_drawdown_stop"),
    }
    per_pair = econ.get("per_pair", {})
    if ticker in per_pair:
        params.update(per_pair[ticker])
    return params
