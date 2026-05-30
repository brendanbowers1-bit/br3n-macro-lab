"""
Score lab outputs across research dimensions.

Separates forecast accuracy, trading P&L, hedge usefulness, and data quality.
Does not auto-tune parameters or claim predictive edge.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "outputs"
LADDER = ROOT / "reports" / "research_ladder"


def _load(path: Path) -> pd.DataFrame | None:
    if path.exists():
        return pd.read_csv(path)
    return None


def _status(label: str, passed: bool | None, detail: str) -> dict:
    if passed is None:
        verdict = "insufficient_data"
    elif passed:
        verdict = "strong"
    else:
        verdict = "weak"
    return {"dimension": label, "verdict": verdict, "detail": detail}


def score_forecast(out_dir: Path = OUT) -> dict:
    fc = _load(out_dir / "forecast_scorecard.csv")
    ac = _load(out_dir / "academic_test_results.csv")
    if fc is None or fc.empty:
        return _status("forecast_vs_random_walk", None, "Run scripts/run_research_models.py")

    row = fc.iloc[0]
    beats_rmse = bool(row.get("model_beats_rw_rmse", False))
    beats_mae = bool(row.get("model_beats_rw_mae", False))
    dm_p = None
    if ac is not None and not ac.empty:
        dm = ac[ac["test"] == "diebold_mariano_rmse"]
        if not dm.empty:
            dm_p = float(dm.iloc[0]["p_value"])

    passed = beats_rmse and beats_mae and (dm_p is not None and dm_p < 0.05)
    detail = (
        f"RMSE beats RW: {beats_rmse}; MAE beats RW: {beats_mae}; "
        f"DM p-value: {dm_p if dm_p is not None else 'n/a'}"
    )
    return _status("forecast_vs_random_walk", passed if dm_p is not None else False, detail)


def score_ml_direction(out_dir: Path = OUT, min_acc: float = 0.53) -> dict:
    ml = _load(out_dir / "ml_direction_model_scorecard.csv")
    if ml is None or ml.empty:
        return _status("ml_direction", None, "Run scripts/run_research_models.py")

    models = ml[ml["model_name"].str.contains("direction", na=False)]
    if models.empty:
        return _status("ml_direction", None, "No direction models in scorecard")

    best = float(models["directional_accuracy"].astype(float).max())
    passed = best >= min_acc * 100 if best > 1 else best >= min_acc
    acc_pct = best if best > 1 else best * 100
    return _status(
        "ml_direction",
        passed,
        f"Best directional accuracy: {acc_pct:.2f}% (threshold {min_acc*100:.0f}%)",
    )


def score_hedge_governance(out_dir: Path = OUT) -> dict:
    hg = _load(out_dir / "hedge_governance_scorecard.csv")
    if hg is None or hg.empty:
        return _status("hedge_governance", None, "Run scripts/run_under_tested_research.py")

    us = hg[hg["exposure_type"] == "us_entity_long_mxn"]
    if us.empty:
        return _status("hedge_governance", None, "No US entity exposure rows")

    best = us.loc[us["cost_adjusted_risk_reduction"].idxmax()]
    regime = us[us["policy_name"] == "regime_based"]
    ncr = us[us["policy_name"] == "no_change_in_range"]
    static_best = us[us["policy_name"].isin(["fully_hedged", "mostly_hedged"])]

    regime_val = float(regime.iloc[0]["cost_adjusted_risk_reduction"]) if not regime.empty else 0
    static_val = float(static_best["cost_adjusted_risk_reduction"].max()) if not static_best.empty else 0
    ncr_turn = float(ncr.iloc[0]["hedge_turnover"]) if not ncr.empty else None
    regime_turn = float(regime.iloc[0]["hedge_turnover"]) if not regime.empty else None

    # Governance "wins" if dynamic policy reduces turnover vs regime_based with decent risk reduction
    turnover_win = (
        ncr_turn is not None
        and regime_turn is not None
        and ncr_turn < regime_turn
        and not ncr.empty
        and float(ncr.iloc[0]["cost_adjusted_risk_reduction"]) > regime_val * 0.9
    )
    passed = turnover_win or regime_val >= static_val * 0.85
    detail = (
        f"Best policy: {best['policy_name']} ({best['cost_adjusted_risk_reduction']}); "
        f"no_change_in_range turnover win vs regime_based: {turnover_win}"
    )
    return _status("hedge_governance", passed, detail)


def score_data_quality(out_dir: Path = OUT) -> dict:
    dq = _load(out_dir / "data_quality_report.csv")
    if dq is None or dq.empty:
        return _status("data_quality", None, "Run scripts/run_data_quality.py")

    row = dq.iloc[0]
    tier = row.get("tier_number", 4)
    flag = str(row.get("data_quality_flag", "UNKNOWN"))
    try:
        tier = int(tier)
    except (TypeError, ValueError):
        tier = 4

    passed = flag == "OK" and tier <= 2
    detail = f"Tier {tier}, flag {flag}, source {row.get('source_name', 'unknown')}"
    return _status("data_quality", passed, detail)


def score_white_rc(out_dir: Path = OUT, ladder_dir: Path = LADDER) -> dict:
    ac = _load(out_dir / "academic_test_results.csv")
    l6 = _load(ladder_dir / "level6_white_reality_check.csv")
    p_val = None
    if l6 is not None and not l6.empty and "bootstrap_p_value" in l6.columns:
        p_val = float(l6.iloc[0]["bootstrap_p_value"])
    elif ac is not None and not ac.empty:
        wrc = ac[ac["test"] == "white_reality_check"]
        if not wrc.empty:
            p_val = float(wrc.iloc[0]["bootstrap_p_value"])

    if p_val is None:
        return _status("data_snooping_control", None, "Run scripts/run_research_ladder.py")

    passed = p_val < 0.05
    return _status(
        "data_snooping_control",
        passed,
        f"White Reality Check p-value: {p_val:.4f} (need < 0.05 to reject data mining)",
    )


def score_trading_oos(out_dir: Path = OUT) -> dict:
    wf = _load(out_dir / "walkforward_oos.csv")
    if wf is None or wf.empty:
        return _status("trading_oos", None, "Run scripts/run_usdmxn_backtest.py")

    primary = wf[wf["strategy"] == "flat_range"]
    if primary.empty:
        return _status("trading_oos", None, "No flat_range walk-forward rows")

    positive = int((primary["sharpe"].astype(float) > 0).sum())
    total = len(primary)
    passed = positive > total / 2
    return _status(
        "trading_oos",
        passed,
        f"flat_range positive Sharpe OOS folds: {positive}/{total}",
    )


def score_all(cfg: dict) -> List[dict]:
    """Score all research dimensions from current outputs."""
    si = cfg.get("self_improvement", {})
    thresholds = si.get("weak_thresholds", {})
    min_ml = float(thresholds.get("ml_direction_min", 0.53))
    out_dir = Path(cfg.get("reporting", {}).get("output_dir", "data/outputs"))
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir

    return [
        score_data_quality(out_dir),
        score_forecast(out_dir),
        score_ml_direction(out_dir, min_acc=min_ml),
        score_trading_oos(out_dir),
        score_hedge_governance(out_dir),
        score_white_rc(out_dir),
    ]


def overall_health(scores: List[dict]) -> str:
    verdicts = [s["verdict"] for s in scores]
    if any(v == "weak" for v in verdicts):
        return "needs_work"
    if all(v in ("strong",) for v in verdicts if v != "insufficient_data"):
        return "healthy"
    if all(v == "insufficient_data" for v in verdicts):
        return "not_run"
    return "mixed"
