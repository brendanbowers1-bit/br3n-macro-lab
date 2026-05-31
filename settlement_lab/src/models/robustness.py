"""Robustness checks for settlement lab rankings."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _rank(df: pd.DataFrame, col: str) -> pd.Series:
    agg = df.groupby("entity", as_index=False)[col].mean().sort_values(col)
    agg["rank"] = range(1, len(agg) + 1)
    return agg.set_index("entity")["rank"]


def _spearman(r1: pd.Series, r2: pd.Series) -> float:
    common = r1.index.intersection(r2.index)
    if len(common) < 3:
        return float("nan")
    return float(r1.reindex(common).corr(r2.reindex(common), method="spearman"))


def run_robustness_checks(sdi: pd.DataFrame, olb: pd.DataFrame, fqi: pd.DataFrame) -> pd.DataFrame:
    checks = []
    if sdi.empty:
        return pd.DataFrame()

    base_rank = _rank(sdi, "settlement_drag_index")

    core = sdi.copy()
    if "sdi_core" in core.columns:
        core["settlement_drag_index"] = core["sdi_core"]
    checks.append(_check("core_only_sdi", base_rank, _rank(core, "settlement_drag_index")))

    if "sdi_risk_adjusted" in sdi.columns:
        risk = sdi.copy()
        risk["settlement_drag_index"] = risk["sdi_risk_adjusted"]
        checks.append(_check("risk_adjusted_sdi", base_rank, _rank(risk, "settlement_drag_index")))

    tier1 = sdi[sdi.get("credibility_tier", sdi.get("data_quality_score", 0)) <= 1] if "credibility_tier" in sdi.columns else sdi
    if len(tier1) >= 5:
        checks.append(_check("tier1_sources_only", base_rank, _rank(tier1, "settlement_drag_index")))

    hq = sdi[sdi["data_quality_score"] >= 70] if "data_quality_score" in sdi.columns else sdi
    if len(hq) >= 5:
        checks.append(_check("high_quality_rows_only", base_rank, _rank(hq, "settlement_drag_index")))

    wins = sdi.copy()
    if "settlement_drag_cost_per_100" in wins.columns:
        cap = wins["settlement_drag_cost_per_100"].quantile(0.95)
        wins["settlement_drag_index"] = 100 - wins["settlement_drag_cost_per_100"].clip(upper=cap)
        checks.append(_check("winsorized_outliers", base_rank, _rank(wins, "settlement_drag_index")))

    return pd.DataFrame(checks)


def _check(check_id: str, base: pd.Series, alt: pd.Series) -> dict:
    sp = _spearman(base, alt)
    return {
        "check_id": check_id,
        "rank_stability_spearman": round(sp, 3) if not np.isnan(sp) else None,
        "robust": sp >= 0.85 if not np.isnan(sp) else False,
        "notes": "Robust if Spearman rank correlation ≥ 0.85.",
    }
