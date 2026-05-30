"""
Hedge-policy backtests — separate from trading P&L.

Simplified hedge-effectiveness research only.
NOT accounting hedge-effectiveness under ASC 815 or IFRS 9.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Optional

import numpy as np
import pandas as pd

from .regimes import R1, R2, R3, R4

ROOT = Path(__file__).resolve().parents[1]

# Regime-based hedge ratio grid (research defaults)
REGIME_HEDGE_GRID = {
    R1: 0.70,
    R2: 0.60,
    R3: 0.40,
    R4: 0.30,
}


def _exposure_return(daily_return: pd.Series, exposure: str) -> pd.Series:
    """
    Simplifying assumption for mark-to-market on unit exposure:

    us_entity_long_mxn:
      Long economic MXN / short USD lens on USD/MXN.
      When USD/MXN rises, MXN weakens -> adverse for US entity long MXN.
      exposure_return = -daily_return (spot change)

    mx_entity_usd_liabilities:
      USD liability / MXN asset lens.
      When USD/MXN rises, USD liabilities grow in MXN terms -> adverse.
      exposure_return = +daily_return
    """
    if exposure == "us_entity_long_mxn":
        return -daily_return
    return daily_return


def hedge_ratio_series(df: pd.DataFrame, policy: str) -> pd.Series:
    """Return daily hedge ratio in [0, 1] for named policy."""
    n = len(df)
    if policy == "never_hedged":
        return pd.Series(0.0, index=df.index)
    if policy == "half_hedged":
        return pd.Series(0.50, index=df.index)
    if policy == "mostly_hedged":
        return pd.Series(0.75, index=df.index)
    if policy == "fully_hedged":
        return pd.Series(1.0, index=df.index)
    if policy == "regime_based":
        return df["regime"].map(REGIME_HEDGE_GRID).fillna(0.40)
    if policy == "r2_active_policy":
        hr = pd.Series(0.40, index=df.index)
        hr.loc[df["regime"] == R2] = 0.70
        return hr
    if policy == "volatility_based":
        # Higher vol -> higher hedge ratio (cap 0.85)
        pct = df.get("realized_vol_percentile", pd.Series(0.5, index=df.index))
        return (0.30 + 0.55 * pct).clip(0.30, 0.85)
    raise ValueError(f"Unknown policy: {policy}")


def run_hedge_policy(
    df: pd.DataFrame,
    policy: str,
    exposure: str,
    hedge_cost_bps: float = 2.0,
) -> pd.DataFrame:
    """Compute hedged vs unhedged paths for one policy."""
    out = df.copy()
    out["unhedged_exposure_return"] = _exposure_return(out["daily_return"], exposure)
    out["hedge_ratio"] = hedge_ratio_series(out, policy)
    out["hedge_turnover"] = out["hedge_ratio"].diff().abs().fillna(out["hedge_ratio"].abs())
    out["hedge_cost"] = out["hedge_turnover"] * (hedge_cost_bps / 10_000.0)
    # Residual exposure return after hedging
    out["hedged_return"] = out["unhedged_exposure_return"] * (1.0 - out["hedge_ratio"]) - out["hedge_cost"]
    out["policy"] = policy
    out["exposure"] = exposure
    return out


def _max_drawdown(rets: pd.Series) -> float:
    eq = (1.0 + rets.fillna(0)).cumprod()
    dd = eq / eq.cummax() - 1.0
    return float(dd.min()) * 100


def hedge_policy_metrics(detail: pd.DataFrame) -> dict:
    """Summary metrics for one hedge policy run."""
    unh = detail["unhedged_exposure_return"]
    hed = detail["hedged_return"]
    ann = np.sqrt(252)
    vol_u = float(unh.std() * ann * 100)
    vol_h = float(hed.std() * ann * 100)
    vol_red = vol_u - vol_h
    cost_adj = vol_red - float(detail["hedge_cost"].sum()) * 100  # rough cost penalty

    # Regret proxy: vs perfect hindsight hedge (not computed here — use unhedged vol as baseline)
    return {
        "policy": detail["policy"].iloc[0],
        "exposure": detail["exposure"].iloc[0],
        "total_unhedged_volatility": round(vol_u, 3),
        "hedged_volatility": round(vol_h, 3),
        "volatility_reduction": round(vol_red, 3),
        "max_drawdown_unhedged": round(_max_drawdown(unh), 3),
        "max_drawdown_hedged": round(_max_drawdown(hed), 3),
        "hedge_turnover": round(float(detail["hedge_turnover"].sum()), 3),
        "total_hedge_cost_pct": round(float(detail["hedge_cost"].sum()) * 100, 4),
        "regret_proxy": round(vol_u - vol_h, 3),
        "cost_adjusted_risk_reduction": round(cost_adj, 3),
    }


def run_all_hedge_policies(
    df: pd.DataFrame,
    config: dict,
    exposure: str = "us_entity_long_mxn",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run static and regime-based policies; return scorecard + detail."""
    cost_bps = float(config.get("research", {}).get("hedge_transaction_cost_bps", 2.0))
    policies = [
        "never_hedged",
        "half_hedged",
        "mostly_hedged",
        "fully_hedged",
        "regime_based",
        "r2_active_policy",
        "volatility_based",
    ]
    scorecard_rows: List[dict] = []
    detail_frames: List[pd.DataFrame] = []

    for pol in policies:
        det = run_hedge_policy(df, pol, exposure, cost_bps)
        scorecard_rows.append(hedge_policy_metrics(det))
        detail_frames.append(det)

    return pd.DataFrame(scorecard_rows), pd.concat(detail_frames)


def save_hedge_outputs(
    scorecard: pd.DataFrame,
    detail: pd.DataFrame,
    out_dir: Optional[Path] = None,
) -> tuple[Path, Path]:
    out_dir = out_dir or ROOT / "data" / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    sc_path = out_dir / "hedge_policy_scorecard.csv"
    det_path = out_dir / "hedge_policy_detail.csv"
    scorecard.to_csv(sc_path, index=False)
    detail.to_csv(det_path, index=False)
    return sc_path, det_path
