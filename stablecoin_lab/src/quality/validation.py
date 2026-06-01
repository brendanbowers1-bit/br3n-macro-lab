"""
Validation engine — fails when required metadata missing (NO_UNLABELED_DATA=True).
Enforces data_quality_score in [0, 100] and mock rows <= MOCK_MAX_QUALITY_SCORE.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import MOCK_MAX_QUALITY_SCORE, NO_UNLABELED_DATA

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

    for col in ("date", "timestamp"):
        if col in df.columns:
            try:
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notna().sum() == 0 and df[col].notna().any():
                    errors.append(f"{table_name}: {col} parsing failed")
            except Exception:
                errors.append(f"{table_name}: {col} parsing failed")

    checks = numeric_nonneg or {}
    for col, label in checks.items():
        if col in df.columns and (df[col] < 0).any():
            errors.append(f"{table_name}: negative {label} in '{col}'")

    if "data_quality_score" in df.columns:
        if df["data_quality_score"].isna().any():
            errors.append(f"{table_name}: data_quality_score missing on some rows")
        invalid = df[
            (df["data_quality_score"] < 0) | (df["data_quality_score"] > 100)
        ]
        if len(invalid):
            errors.append(
                f"{table_name}: data_quality_score must be 0–100 ({len(invalid)} rows out of range)"
            )
        if "mock_data_flag" in df.columns:
            mock_rows = df[df["mock_data_flag"] == True]  # noqa: E712
            if len(mock_rows) and (mock_rows["data_quality_score"] > MOCK_MAX_QUALITY_SCORE).any():
                errors.append(
                    f"{table_name}: mock rows exceed MOCK_MAX_QUALITY_SCORE ({MOCK_MAX_QUALITY_SCORE})"
                )

    if "mock_data_flag" in df.columns and df["mock_data_flag"].any():
        warnings.append(f"{table_name}: mock_data_flag=True — demo data present")

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
        "stablecoin_supply": {
            "supply_usd": "supply",
            "market_cap_usd": "market cap",
        },
        "stablecoin_reserves": {
            "total_reserves_usd": "reserves",
        },
        "blockchain_settlement_characteristics": {
            "average_transaction_fee_usd": "transaction fee",
            "average_confirmation_time_seconds": "confirmation time",
        },
        "remittance_comparison": {
            "traditional_fee_pct": "traditional fee",
            "stablecoin_onramp_fee_pct": "on-ramp fee",
        },
    }
    skip = {"model_outputs", "features"}
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
