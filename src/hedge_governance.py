"""
Hedge-governance backtests — when not to hedge, turnover discipline.

Simplified hedge-governance research only.
NOT accounting hedge-effectiveness testing under ASC 815 or IFRS 9.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd

from .regimes import R1, R2, R3, R4

ROOT = Path(__file__).resolve().parents[1]

REGIME_HEDGE_GRID = {R1: 0.70, R2: 0.60, R3: 0.40, R4: 0.30}
MAX_DAILY_HEDGE_STEP = 0.10


def _normalize_regime(regime: str) -> str:
    """Map alias regime names to canonical R1–R4."""
    aliases = {
        "R1_trend_highvol": R1,
        "R2_trend_lowvol": R2,
        "R3_range_highvol": R3,
        "R4_range_lowvol": R4,
    }
    return aliases.get(regime, regime)


def _exposure_return(daily_return: pd.Series, exposure: str) -> pd.Series:
    """
    Simplifying mark-to-market on unit exposure.

    receiver_currency_exposure / us_entity_long_mxn:
      Long receiver currency. USD/pair rising -> receiver weakens -> adverse.
      exposure_return = -daily_return

    usd_liability_exposure / mx_entity_usd_liabilities:
      USD liability stress. USD/pair rising -> adverse.
      exposure_return = +daily_return
    """
    if exposure in ("receiver_currency_exposure", "us_entity_long_mxn"):
        return -daily_return
    return daily_return


def _no_change_in_range_series(df: pd.DataFrame) -> pd.Series:
    """
    Start 50% hedged. Freeze in R3/R4; gradual moves in R1/R2.
    Max 0.10 hedge-ratio change per day.
    """
    ratios: List[float] = []
    prev = 0.50
    targets = {R1: 0.60, R2: 0.70, R3: None, R4: None}

    for regime in df["regime"].map(_normalize_regime):
        target = targets.get(regime)
        if target is None:
            # Range regimes: no change
            ratios.append(prev)
            continue
        delta = np.clip(target - prev, -MAX_DAILY_HEDGE_STEP, MAX_DAILY_HEDGE_STEP)
        prev = float(np.clip(prev + delta, 0.0, 1.0))
        ratios.append(prev)

    return pd.Series(ratios, index=df.index)


def get_policy_hedge_ratio(df: pd.DataFrame, policy_name: str) -> pd.Series:
    """Return daily hedge ratio in [0, 1] for a named governance policy."""
    n = len(df)
    if policy_name == "never_hedged":
        return pd.Series(0.0, index=df.index)
    if policy_name == "half_hedged":
        return pd.Series(0.50, index=df.index)
    if policy_name == "mostly_hedged":
        return pd.Series(0.75, index=df.index)
    if policy_name == "fully_hedged":
        return pd.Series(1.0, index=df.index)
    if policy_name == "regime_based":
        return df["regime"].map(_normalize_regime).map(REGIME_HEDGE_GRID).fillna(0.40)
    if policy_name == "r2_active_policy":
        norm = df["regime"].map(_normalize_regime)
        hr = pd.Series(0.40, index=df.index)
        hr.loc[norm == R2] = 0.70
        return hr
    if policy_name == "no_change_in_range":
        return _no_change_in_range_series(df)
    if policy_name == "volatility_triggered":
        high = df.get("high_vol_flag", pd.Series(False, index=df.index)).astype(bool)
        return high.map({True: 0.70, False: 0.40})
    raise ValueError(f"Unknown policy: {policy_name}")


def _max_drawdown(rets: pd.Series) -> float:
    eq = (1.0 + rets.fillna(0)).cumprod()
    return float((eq / eq.cummax() - 1.0).min()) * 100


def run_hedge_governance_backtest(
    df: pd.DataFrame,
    policy_name: str,
    exposure_type: str = "receiver_currency_exposure",
    config: Optional[dict] = None,
    corridor_id: Optional[str] = None,
) -> pd.DataFrame:
    """Compute hedged vs unhedged paths for one governance policy."""
    config = config or {}
    hg_cfg = config.get("hedge_governance", {})
    cost_bps = float(
        hg_cfg.get("hedge_transaction_cost_bps")
        or config.get("research", {}).get("hedge_transaction_cost_bps", 2.0)
    )
    out = df.copy()
    out["unhedged_exposure_return"] = _exposure_return(out["daily_return"], exposure_type)
    out["hedge_ratio"] = get_policy_hedge_ratio(out, policy_name)
    out["hedge_turnover"] = out["hedge_ratio"].diff().abs().fillna(out["hedge_ratio"].abs())
    out["hedge_cost"] = out["hedge_turnover"] * (cost_bps / 10_000.0)
    out["hedged_return"] = (
        out["unhedged_exposure_return"] * (1.0 - out["hedge_ratio"]) - out["hedge_cost"]
    )
    out["policy_name"] = policy_name
    out["exposure_type"] = exposure_type
    if corridor_id:
        out["corridor_id"] = corridor_id
    return out


def governance_metrics(detail: pd.DataFrame) -> dict:
    """Summary metrics for one hedge-governance run."""
    unh = detail["unhedged_exposure_return"]
    hed = detail["hedged_return"]
    ann = np.sqrt(252)
    vol_u = float(unh.std() * ann * 100)
    vol_h = float(hed.std() * ann * 100)
    vol_red = vol_u - vol_h
    total_cost_pct = float(detail["hedge_cost"].sum()) * 100
    cost_adj = vol_red - total_cost_pct

    # Perfect hedge = zero FX exposure daily return
    regret = float((hed - 0.0).abs().mean() * ann * 100)

    changes = int((detail["hedge_turnover"] > 0.001).sum())

    cum_ret = float((1.0 + hed.fillna(0)).prod() - 1.0) * 100

    return {
        "corridor_id": detail["corridor_id"].iloc[0] if "corridor_id" in detail.columns else None,
        "policy_name": detail["policy_name"].iloc[0],
        "exposure_type": detail["exposure_type"].iloc[0],
        "total_return_proxy": round(cum_ret, 3),
        "unhedged_volatility": round(vol_u, 3),
        "hedged_volatility": round(vol_h, 3),
        "volatility_reduction": round(vol_red, 3),
        "max_drawdown_unhedged": round(_max_drawdown(unh), 3),
        "max_drawdown_hedged": round(_max_drawdown(hed), 3),
        "hedge_turnover": round(float(detail["hedge_turnover"].sum()), 3),
        "total_hedge_cost": round(total_cost_pct, 4),
        "average_hedge_ratio": round(float(detail["hedge_ratio"].mean()), 3),
        "number_of_hedge_changes": changes,
        "cost_adjusted_risk_reduction": round(cost_adj, 3),
        "regret_proxy": round(regret, 3),
    }


GOVERNANCE_POLICIES = [
    "never_hedged",
    "half_hedged",
    "mostly_hedged",
    "fully_hedged",
    "regime_based",
    "r2_active_policy",
    "no_change_in_range",
    "volatility_triggered",
]


def run_all_hedge_governance(
    df: pd.DataFrame,
    config: dict,
    exposures: Optional[List[str]] = None,
    corridor_id: Optional[str] = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run all governance policies for each exposure type."""
    exposures = exposures or [
        "receiver_currency_exposure",
        "usd_liability_exposure",
    ]
    scorecard_rows: List[dict] = []
    detail_frames: List[pd.DataFrame] = []

    for exposure in exposures:
        for policy in GOVERNANCE_POLICIES:
            det = run_hedge_governance_backtest(
                df, policy, exposure, config, corridor_id=corridor_id
            )
            scorecard_rows.append(governance_metrics(det))
            detail_frames.append(det)

    return pd.DataFrame(scorecard_rows), pd.concat(detail_frames)


def save_governance_outputs(
    scorecard: pd.DataFrame,
    detail: pd.DataFrame,
    out_dir: Optional[Path] = None,
) -> tuple[Path, Path]:
    out_dir = out_dir or ROOT / "data" / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    sc_path = out_dir / "hedge_governance_scorecard.csv"
    det_path = out_dir / "hedge_governance_detail.csv"
    scorecard.to_csv(sc_path, index=False)
    detail.to_csv(det_path, index=False)
    return sc_path, det_path
