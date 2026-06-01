"""Validation rules for USD/MXN corridor dataset."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ValidationReport:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    row_count: int = 0
    data_quality_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "row_count": self.row_count,
            "data_quality_score": self.data_quality_score,
        }


def validate_us_mx_dataset(df: pd.DataFrame, *, min_rows: int = 12) -> ValidationReport:
    report = ValidationReport(passed=True, row_count=len(df))

    required = {"month", "remittance_usd_millions", "source", "methodology_version"}
    missing = required - set(df.columns)
    if missing:
        report.passed = False
        report.errors.append(f"Missing columns: {sorted(missing)}")
        return report

    if len(df) < min_rows:
        report.passed = False
        report.errors.append(f"Need at least {min_rows} rows; got {len(df)}")

    if df["remittance_usd_millions"].isna().any():
        report.passed = False
        report.errors.append("Null remittance values present")

    if (df["remittance_usd_millions"] <= 0).any():
        report.passed = False
        report.errors.append("Non-positive remittance values present")

    if not df["month"].is_monotonic_increasing:
        report.passed = False
        report.errors.append("Months are not strictly increasing")

    dupes = df["month"].duplicated().sum()
    if dupes:
        report.passed = False
        report.errors.append(f"Duplicate month rows: {dupes}")

    gaps = df["month"].diff().dt.days.dropna()
    if not gaps.empty and (gaps > 35).any():
        report.warnings.append("Gap larger than ~35 days detected between observations")

    if "starter" in " ".join(df["source"].astype(str)).lower():
        report.warnings.append("Source marked as starter/research series — not operational Banxico feed")

    score = 100.0
    score -= 15 * len(report.errors)
    score -= 5 * len(report.warnings)
    report.data_quality_score = max(0.0, min(100.0, score))
    return report
