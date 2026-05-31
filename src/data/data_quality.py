"""
Data Quality Score (0–100) for VSI corridor observations.

Research-grade rubric — points awarded for official/observed data presence.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import is_credible_mode

RUBRIC = {
    "rpw_fee": 15,
    "rpw_fx_margin": 15,
    "transfer_speed": 10,
    "fx_volatility": 15,
    "inflation": 10,
    "remittance_flow": 10,
    "payout_verified": 5,
    "dollar_dependency_proxy": 5,
    "trust_macro": 10,
    "no_mock_manual": 5,
}

GRADES = [
    (90, "Research grade"),
    (75, "Strong"),
    (60, "Preliminary"),
    (40, "Exploratory"),
    (0, "Demo only"),
]


def grade_from_score(score: float) -> str:
    for threshold, label in GRADES:
        if score >= threshold:
            return label
    return "Demo only"


def _tier(source: str | None) -> str:
    s = str(source or "").lower()
    if "mock" in s or "synthetic" in s:
        return "mock"
    if "manual" in s or "placeholder" in s or "assumed" in s:
        return "manual"
    if "curated" in s or "historical" in s:
        return "curated"
    if any(k in s for k in ("world_bank", "rpw", "knomad", "imf", "fred", "bis", "api", "lab")):
        return "official"
    return "unknown"


def score_row(row: pd.Series, tables: dict | None = None) -> dict:
    """Compute 0–100 quality score and component flags for one VSI row."""
    pts = 0
    flags = {}

    fee_src = row.get("fee_source", row.get("source", ""))
    margin_src = row.get("fx_margin_source", row.get("source", ""))
    fee_t = _tier(fee_src)
    margin_t = _tier(margin_src)

    if fee_t in ("official", "curated") and pd.notna(row.get("fee_pct")):
        pts += RUBRIC["rpw_fee"]
        flags["rpw_fee"] = "official"
    else:
        flags["rpw_fee"] = "missing"

    if margin_t in ("official", "curated") and pd.notna(row.get("fx_margin_pct")):
        pts += RUBRIC["rpw_fx_margin"]
        flags["rpw_fx_margin"] = "official"
    else:
        flags["rpw_fx_margin"] = "missing"

    if pd.notna(row.get("transfer_speed_days")):
        pts += RUBRIC["transfer_speed"]
        flags["transfer_speed"] = "observed"
    else:
        flags["transfer_speed"] = "missing"

    vol_src = _tier(row.get("fx_volatility_source", ""))
    if vol_src in ("official", "curated") and pd.notna(row.get("volatility_30d")):
        pts += RUBRIC["fx_volatility"]
        flags["fx_volatility"] = "official"
    else:
        flags["fx_volatility"] = "assumed"

    infl_src = _tier(row.get("inflation_source", ""))
    if infl_src in ("official", "curated") and pd.notna(row.get("inflation_yoy")):
        pts += RUBRIC["inflation"]
        flags["inflation"] = "official"
    else:
        flags["inflation"] = "assumed"

    flow_src = _tier(row.get("remittance_volume_source", ""))
    if flow_src in ("official", "curated"):
        pts += RUBRIC["remittance_flow"]
        flags["remittance_flow"] = "official"
    else:
        flags["remittance_flow"] = "not_linked"

    payout_src = _tier(row.get("payout_friction_source", ""))
    if payout_src == "official":
        pts += RUBRIC["payout_verified"]
        flags["payout_friction"] = "verified"
    elif payout_src == "manual":
        flags["payout_friction"] = "manual_default"
    else:
        flags["payout_friction"] = "method_default"

    dd_src = _tier(row.get("dollar_dependency_source", ""))
    if dd_src in ("official", "curated", "manual") and row.get("dollar_dependency_drag_pct", 0):
        pts += RUBRIC["dollar_dependency_proxy"]
        flags["dollar_dependency"] = dd_src
    else:
        flags["dollar_dependency"] = "not_in_spec"

    trust_src = _tier(row.get("trust_score_source", ""))
    if trust_src in ("official", "curated", "manual"):
        pts += RUBRIC["trust_macro"]
        flags["trust_score"] = trust_src
    else:
        flags["trust_score"] = "not_in_spec"

    mock = bool(row.get("mock_data_flag", False))
    manual = bool(row.get("manual_assumption_flag", False))
    if not mock and not manual:
        pts += RUBRIC["no_mock_manual"]

    score = min(pts, 100)
    official_count = sum(1 for v in flags.values() if v in ("official", "observed", "verified"))
    total_components = len(flags)
    coverage = official_count / total_components if total_components else 0

    return {
        "data_quality_score": score,
        "data_quality_grade": grade_from_score(score),
        "real_data_coverage_pct": round(coverage * 100, 1),
        "quality_flags": flags,
    }


def annotate_quality(df: pd.DataFrame, tables: dict | None = None) -> pd.DataFrame:
    out = df.copy()
    scores = out.apply(lambda r: score_row(r, tables), axis=1, result_type="expand")
    for col in ("data_quality_score", "data_quality_grade", "real_data_coverage_pct"):
        if col in scores.columns:
            out[col] = scores[col]
    return out


def quality_summary_by_corridor(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return (
        df.groupby("corridor", as_index=False)
        .agg(
            data_quality_score=("data_quality_score", "mean"),
            data_quality_grade=("data_quality_grade", "first"),
            real_data_coverage_pct=("real_data_coverage_pct", "mean"),
            mock_data_flag=("mock_data_flag", "any"),
            manual_assumption_flag=("manual_assumption_flag", "any"),
        )
        .sort_values("data_quality_score", ascending=False)
    )
