"""
Strict Data Quality Score (0–100) for Settlement Economics Lab.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import MOCK_MAX_QUALITY_SCORE

GRADES = [
    (90, "Publication grade"),
    (80, "Research grade"),
    (70, "Strong preliminary"),
    (60, "Exploratory"),
    (40, "Demo/weak"),
    (0, "Do not use for inference"),
]

RUBRIC_WEIGHTS = {
    "source_credibility": 20,
    "completeness": 15,
    "timeliness": 10,
    "granularity": 10,
    "consistency": 10,
    "replicability": 15,
    "observability": 10,
    "external_validation": 10,
}

TIER_POINTS = {1: 20, 2: 16, 3: 12, 4: 6, 5: 0}


def grade_from_score(score: float) -> str:
    for threshold, label in GRADES:
        if score >= threshold:
            return label
    return "Do not use for inference"


def score_row(row: pd.Series, required_fields: list[str] | None = None) -> dict:
    req = required_fields or []
    pts = 0
    mock = bool(row.get("mock_data_flag", False))
    tier = int(row.get("credibility_tier", row.get("source_credibility_tier", 5)))

    if mock:
        score = min(MOCK_MAX_QUALITY_SCORE, 30)
        return {
            "data_quality_score": score,
            "data_quality_grade": "Demo only",
            "confidence_score": 0.1,
        }

    pts += TIER_POINTS.get(tier, 0)

    missing_pct = float(row.get("missing_data_pct", 0) or 0)
    present = sum(1 for f in req if pd.notna(row.get(f)))
    completeness = (present / len(req)) if req else 0.8
    pts += int(RUBRIC_WEIGHTS["completeness"] * completeness)

    if row.get("extraction_date"):
        pts += 8
    if row.get("vintage_date") or row.get("publication_date"):
        pts += 2

    if row.get("date_granularity") in ("daily", "transaction"):
        pts += RUBRIC_WEIGHTS["granularity"]
    elif row.get("rail_type") or row.get("payment_system"):
        pts += 6

    val = float(row.get("transaction_value_usd", row.get("average_daily_settlement_value_usd", 1)) or 0)
    lag = float(row.get("settlement_lag_days", row.get("settlement_lag_hours", 0)) or 0)
    if val >= 0 and lag >= 0:
        pts += RUBRIC_WEIGHTS["consistency"]

    if row.get("raw_file_hash_sha256") and row.get("raw_file_hash_sha256") != "missing":
        pts += 10
    if row.get("transformation_script"):
        pts += 5

    obs = str(row.get("observed_vs_estimated_flag", "")).lower()
    if obs == "observed":
        pts += RUBRIC_WEIGHTS["observability"]
    elif obs == "estimated":
        pts += 5
    else:
        pts += 2

    if tier <= 2:
        pts += 5

    if missing_pct > 20:
        pts = int(pts * 0.85)

    score = min(max(pts, 0), 100)
    return {
        "data_quality_score": score,
        "data_quality_grade": grade_from_score(score),
        "confidence_score": round(min(score / 100, 0.95), 2),
    }


def annotate_quality(df: pd.DataFrame, required_fields: list[str] | None = None) -> pd.DataFrame:
    if df.empty:
        return df
    scores = df.apply(lambda r: score_row(r, required_fields), axis=1, result_type="expand")
    out = df.copy()
    for col in scores.columns:
        out[col] = scores[col].values
    return out
