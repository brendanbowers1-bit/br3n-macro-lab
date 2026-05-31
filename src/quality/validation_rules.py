"""Shared validation rules for VSI and Settlement Economics Lab."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

SCORE_COLS = [
    "value_survival_index", "vsi_core", "vsi_risk_adjusted", "vsi_extended",
    "settlement_drag_index", "finality_quality_index", "operational_liquidity_burden_score",
    "payment_network_fragility_score", "finality_quality_index",
]
METADATA_COLS = ["source_id", "data_quality_score", "mock_data_flag"]


def file_sha256(path: Path) -> str:
    if not path.exists():
        return "missing"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def check_bounded_scores(df: pd.DataFrame, prefix: str = "") -> list[str]:
    issues = []
    for col in df.columns:
        if "index" in col.lower() or col.endswith("_score") or col.startswith("vsi"):
            if not pd.api.types.is_numeric_dtype(df[col]):
                continue
            lo, hi = df[col].min(), df[col].max()
            if pd.notna(lo) and lo < 0:
                issues.append(f"{prefix}{col} has values below 0 (min={lo})")
            if pd.notna(hi) and hi > 100 and "pct" not in col and "percent" not in col:
                if col not in ("data_quality_score",):
                    issues.append(f"{prefix}{col} exceeds 100 (max={hi})")
    return issues


def check_mock_labeling(df: pd.DataFrame, prefix: str = "") -> list[str]:
    issues = []
    if "mock_data_flag" not in df.columns:
        return issues
    if df["mock_data_flag"].any() and "data_quality_score" in df.columns:
        mock_rows = df[df["mock_data_flag"] == True]  # noqa: E712
        bad = mock_rows[mock_rows["data_quality_score"] > 30]
        if not bad.empty:
            issues.append(f"{prefix}mock rows with data_quality_score > 30: {len(bad)}")
    unlabeled = df[df["mock_data_flag"].isna()]
    if not unlabeled.empty:
        issues.append(f"{prefix}rows with unlabeled mock_data_flag: {len(unlabeled)}")
    return issues


def check_metadata(df: pd.DataFrame, prefix: str = "", require_all: bool = False) -> list[str]:
    issues = []
    for col in METADATA_COLS:
        if col not in df.columns:
            if require_all:
                issues.append(f"{prefix}missing metadata column: {col}")
        elif df[col].isna().all():
            issues.append(f"{prefix}metadata column all NaN: {col}")
    return issues


def check_non_negative(df: pd.DataFrame, cols: list[str], prefix: str = "") -> list[str]:
    issues = []
    for col in cols:
        if col not in df.columns:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            neg = (df[col] < 0).sum()
            if neg > 0:
                issues.append(f"{prefix}{col} has {neg} negative values")
    return issues


def check_nan_inf(df: pd.DataFrame, prefix: str = "") -> list[str]:
    issues = []
    for col in df.select_dtypes(include=[np.number]).columns:
        if np.isinf(df[col]).any():
            issues.append(f"{prefix}{col} contains inf")
        if df[col].isna().sum() == len(df):
            issues.append(f"{prefix}{col} all NaN")
    return issues


def validate_vsi_outputs(df: pd.DataFrame) -> list[str]:
    issues = []
    issues += check_bounded_scores(df, "VSI ")
    issues += check_mock_labeling(df, "VSI ")
    issues += check_metadata(df, "VSI ")
    issues += check_non_negative(df, [
        "value_loss_usd_per_100", "fee_pct", "fx_margin_pct",
        "explicit_fee_loss_pct", "total_value_loss_pct",
    ], "VSI ")
    if "value_survival_index" in df.columns:
        if (df["value_survival_index"] > 100).any():
            issues.append("VSI value_survival_index > 100")
    if "real_usable_value_delivered_pct" in df.columns:
        mx = df["real_usable_value_delivered_pct"].max()
        if pd.notna(mx) and mx > 1.01:
            issues.append("VSI real_usable_value_delivered_pct > 1")
    if "total_value_loss_pct" in df.columns:
        mx = df["total_value_loss_pct"].max()
        if pd.notna(mx) and mx > 1.01:
            issues.append("VSI total_value_loss_pct > 1")
    return issues


def validate_settlement_outputs(df: pd.DataFrame, table: str) -> list[str]:
    issues = []
    prefix = f"Settlement/{table} "
    issues += check_bounded_scores(df, prefix)
    issues += check_mock_labeling(df, prefix)
    issues += check_metadata(df, prefix)
    issues += check_nan_inf(df, prefix)
    if table == "payment_flow_observations":
        issues += check_non_negative(df, ["transaction_value_usd", "settlement_lag_days"], prefix)
    if "settlement_drag_index" in df.columns:
        if (df["settlement_drag_index"] < 0).any() or (df["settlement_drag_index"] > 100).any():
            issues.append(f"{prefix}settlement_drag_index out of [0,100]")
    return issues
