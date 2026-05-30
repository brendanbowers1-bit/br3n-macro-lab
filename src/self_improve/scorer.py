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
    flag = str(row.get("quality_flag", row.get("data_quality_flag", "UNKNOWN")))
    source = str(row.get("source", row.get("source_name", "unknown")))
    try:
        tier = int(tier)
    except (TypeError, ValueError):
        tier = 4

    academic_sources = {"fred_h10", "fred", "fed_h10", "fed_h10_direct"}
    passed = flag == "OK" and (tier <= 1 or source in academic_sources)
    detail = f"Tier {tier}, flag {flag}, source {source}"
    return _status("data_quality", passed, detail)


def score_data_provenance(out_dir: Path = OUT) -> dict:
    sc = _load(out_dir / "strategy_scorecard.csv")
    if sc is None or sc.empty:
        return _status("data_provenance", None, "Run scripts/run_usdmxn_backtest.py")

    row = sc.iloc[0]
    source = str(row.get("source", "unknown"))
    tier = str(row.get("data_tier", "unknown"))
    academic = source in ("fred_h10", "fred", "fed_h10") or tier in ("official", "academic")
    has_prov = all(c in sc.columns for c in ("sample_start", "run_timestamp", "config_hash"))
    passed = academic and has_prov
    detail = f"source={source}, tier={tier}, provenance_cols={has_prov}"
    return _status("data_provenance", passed if has_prov else None, detail)


def score_model_zoo(out_dir: Path = OUT) -> dict:
    fc = _load(out_dir / "model_zoo_forecast_scorecard.csv")
    if fc is None or fc.empty:
        return _status("model_zoo_forecast", None, "Run scripts/run_model_zoo.py")

    beats = int(fc["model_beats_rw_rmse"].sum()) if "model_beats_rw_rmse" in fc.columns else 0
    n = len(fc)
    passed = beats > max(1, int(n * 0.25))
    src = fc["source"].iloc[0] if "source" in fc.columns else "unknown"
    detail = f"{beats}/{n} models beat RW by RMSE; scorecard source={src}"
    return _status("model_zoo_forecast", passed, detail)


def score_news_layer(out_dir: Path = OUT) -> dict:
    tests = _load(out_dir / "news_feature_test_results.csv")
    news_path = ROOT / "data" / "processed" / "usdmxn_features_regimes_news.csv"
    if not news_path.exists():
        return _status("news_layer", None, "Run scripts/run_news_layer.py")

    if tests is None or tests.empty:
        return _status("news_layer", None, "News features exist but tests missing")

    hi = tests[tests["test_name"] == "high_vs_normal_news_stress"]
    if hi.empty:
        return _status("news_layer", False, "News tests ran but high-vs-normal missing")

    row = hi.iloc[0]
    vol_h = row.get("volatility_high_news")
    vol_n = row.get("volatility_normal")
    discriminates = vol_h is not None and vol_n is not None and float(vol_h) > float(vol_n)
    detail = f"high-news vol={vol_h}%, normal={vol_n}% (stress discriminates: {discriminates})"
    return _status("news_layer", discriminates, detail)


def score_carry_layer(out_dir: Path = OUT) -> dict:
    carry_path = ROOT / "data" / "processed" / "usdmxn_features_regimes_carry.csv"
    tests = _load(out_dir / "carry_regime_test_results.csv")

    if not carry_path.exists():
        return _status("carry_layer", None, "Run scripts/run_carry_layer.py")

    cdf = pd.read_csv(carry_path, usecols=lambda c: c in ("carry_proxy", "date"))
    if cdf["carry_proxy"].notna().sum() < 10:
        return _status("carry_layer", None, "Carry placeholders only — add FRED rate series")

    if tests is None or tests.empty:
        return _status("carry_layer", False, "Carry data loaded but tests missing")

    hi = tests[tests["test_name"] == "high_carry_vs_low_carry"]
    if hi.empty:
        return _status("carry_layer", False, "Carry tests incomplete")

    row = hi.iloc[0]
    vol_h = row.get("volatility_high_carry")
    vol_n = row.get("volatility_low_carry")
    detail = f"carry proxy loaded; high-carry vol={vol_h}%, low-carry={vol_n}%"
    return _status("carry_layer", True, detail)


def score_carry_hedge(out_dir: Path = OUT) -> dict:
    chg = _load(out_dir / "carry_hedge_governance_scorecard.csv")
    if chg is None or chg.empty:
        return _status("carry_hedge_governance", None, "Run scripts/run_carry_layer.py")

    ok = chg[chg.get("status", "ok") != "error"] if "status" in chg.columns else chg
    if ok.empty or "cost_adjusted_risk_reduction" not in ok.columns:
        return _status("carry_hedge_governance", None, "Carry hedge scorecard empty")

    carry_adj = ok[ok["policy_name"] == "carry_adjusted_regime"]
    regime = ok[ok["policy_name"] == "regime_only"]
    if carry_adj.empty or regime.empty:
        best = ok.loc[ok["cost_adjusted_risk_reduction"].idxmax()]
        return _status(
            "carry_hedge_governance",
            True,
            f"Best carry policy: {best['policy_name']} ({best['cost_adjusted_risk_reduction']})",
        )

    c_val = float(carry_adj.iloc[0]["cost_adjusted_risk_reduction"])
    r_val = float(regime.iloc[0]["cost_adjusted_risk_reduction"])
    passed = c_val >= r_val * 0.95
    detail = f"carry_adjusted={c_val:.3f} vs regime_only={r_val:.3f}"
    return _status("carry_hedge_governance", passed, detail)


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
        score_data_provenance(out_dir),
        score_forecast(out_dir),
        score_model_zoo(out_dir),
        score_ml_direction(out_dir, min_acc=min_ml),
        score_trading_oos(out_dir),
        score_hedge_governance(out_dir),
        score_news_layer(out_dir),
        score_carry_layer(out_dir),
        score_carry_hedge(out_dir),
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
