"""
Validation engine — fails when required metadata missing (NO_UNLABELED_DATA=True).
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import NO_UNLABELED_DATA

REQUIRED_METADATA = [
    "source_id", "methodology_version", "mock_data_flag",
    "data_quality_score", "data_quality_grade",
]


def validate_table(
    df: pd.DataFrame,
    table_name: str,
    numeric_nonneg: dict[str, str] | None = None,
) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if df.empty:
        warnings.append(f"{table_name}: empty table")
        return {"valid": True, "errors": errors, "warnings": warnings, "table": table_name}

    if NO_UNLABELED_DATA:
        for col in REQUIRED_METADATA:
            if col not in df.columns:
                errors.append(f"{table_name}: missing required metadata column '{col}'")
            elif df[col].isna().all():
                errors.append(f"{table_name}: required metadata '{col}' all null")

    for col in ("date",):
        if col in df.columns:
            try:
                pd.to_datetime(df[col], errors="coerce")
                if df[col].notna().sum() == 0 and df[col].notna().any():
                    errors.append(f"{table_name}: date parsing failed")
            except Exception:
                errors.append(f"{table_name}: date parsing failed")

    checks = numeric_nonneg or {}
    for col, label in checks.items():
        if col in df.columns and (df[col] < 0).any():
            errors.append(f"{table_name}: negative {label} in '{col}'")

    if "data_quality_score" in df.columns:
        if df["data_quality_score"].isna().any():
            errors.append(f"{table_name}: data_quality_score missing on some rows")

    if "mock_data_flag" in df.columns and df["mock_data_flag"].any():
        warnings.append(f"{table_name}: mock_data_flag=True — demo data present")

    if "manual_assumption_flag" in df.columns and df.get("manual_assumption_flag", pd.Series([False])).any():
        warnings.append(f"{table_name}: manual_assumption_flag=True")

    if "missing_data_pct" in df.columns:
        high = df[df["missing_data_pct"] > 20]
        if len(high):
            warnings.append(f"{table_name}: {len(high)} rows with missing_data_pct > 20%")

    tier_col = "credibility_tier" if "credibility_tier" in df.columns else None
    if tier_col and (df[tier_col] > 3).any() and (df[tier_col] <= 3).any():
        low = df[df[tier_col] > 3]
        warnings.append(f"{table_name}: {len(low)} rows with source credibility below Tier 3")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "table": table_name,
        "n_rows": len(df),
    }


def validate_all_tables(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rules = {
        "payment_flow_observations": {
            "transaction_value_usd": "transaction value",
            "settlement_lag_days": "settlement lag",
        },
        "settlement_liquidity_table": {
            "average_daily_settlement_value_usd": "settlement value",
        },
    }
    skip = {"features", "settlement_drag_outputs", "operational_liquidity_outputs",
            "finality_quality_outputs", "payment_fragility_outputs", "friction_incidence_outputs"}
    rows = []
    for name, df in tables.items():
        if name.startswith("_") or name in skip:
            continue
        r = validate_table(df, name, rules.get(name))
        rows.append({
            "table": r["table"],
            "valid": r["valid"],
            "n_rows": r["n_rows"],
            "errors": "; ".join(r["errors"]) or "",
            "warnings": "; ".join(r["warnings"]) or "",
        })
    return pd.DataFrame(rows)
