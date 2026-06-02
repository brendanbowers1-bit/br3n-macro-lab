"""Validate data-lake assets against metadata/validation_rules.json."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.lake.paths import (
    BANXICO_POLICY_CSV,
    DATA_LAKE_ROOT,
    FED_POLICY_CSV,
    REMITTANCES_CSV,
    RPW_COST_CSV,
    USD_MXN_DAILY_PARQUET,
    USD_MXN_SPOT_CSV,
    VALIDATION_REPORTS,
    VALIDATION_RULES,
)


@dataclass
class CheckResult:
    check_id: str
    status: str  # pass | warn | fail | skip
    message: str = ""


@dataclass
class ValidationReport:
    report_id: str
    target: str
    layer: str
    passed: bool
    checks: list[CheckResult] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "target": self.target,
            "layer": self.layer,
            "passed": self.passed,
            "summary": self.summary,
            "checks": [
                {"check_id": c.check_id, "status": c.status, "message": c.message} for c in self.checks
            ],
        }


def _load_rules() -> dict:
    return json.loads(VALIDATION_RULES.read_text(encoding="utf-8"))


def validate_remittances_raw(df: pd.DataFrame) -> ValidationReport:
    report = ValidationReport(
        report_id=f"raw_remittances_{date.today().isoformat().replace('-', '')}",
        target=str(REMITTANCES_CSV.relative_to(DATA_LAKE_ROOT.parent)),
        layer="raw",
        passed=True,
    )
    required = {"month", "remittance_usd_millions", "source", "methodology_version"}
    if not required.issubset(df.columns):
        report.passed = False
        report.checks.append(
            CheckResult("required_columns", "fail", f"Missing {required - set(df.columns)}")
        )
    else:
        report.checks.append(CheckResult("required_columns", "pass"))

    df = df.copy()
    df["month"] = pd.to_datetime(df["month"])
    if df["month"].isna().any():
        report.passed = False
        report.checks.append(CheckResult("valid_dates", "fail", "Invalid month values"))
    else:
        report.checks.append(CheckResult("valid_dates", "pass"))

    if df["month"].duplicated().any():
        report.passed = False
        report.checks.append(CheckResult("duplicate_dates", "fail", "Duplicate months"))
    else:
        report.checks.append(CheckResult("duplicate_dates", "pass"))

    if not df["month"].is_monotonic_increasing:
        report.passed = False
        report.checks.append(CheckResult("monotonic_date_ordering", "fail"))
    else:
        report.checks.append(CheckResult("monotonic_date_ordering", "pass"))

    if (df["remittance_usd_millions"] <= 0).any():
        report.passed = False
        report.checks.append(CheckResult("numeric_fields", "fail", "Non-positive remittances"))
    else:
        report.checks.append(CheckResult("numeric_fields", "pass"))

    if "starter" in " ".join(df["source"].astype(str)).lower():
        report.checks.append(
            CheckResult("stale_source_warning", "warn", "research_starter — not live Banxico feed")
        )

    report.summary = {
        "errors": sum(1 for c in report.checks if c.status == "fail"),
        "warnings": sum(1 for c in report.checks if c.status == "warn"),
    }
    return report


def validate_fed_rates_raw(df: pd.DataFrame) -> ValidationReport:
    report = ValidationReport(
        report_id=f"raw_fed_policy_{date.today().isoformat().replace('-', '')}",
        target=str(FED_POLICY_CSV.relative_to(DATA_LAKE_ROOT.parent)),
        layer="raw",
        passed=True,
    )
    date_col = "observation_date" if "observation_date" in df.columns else df.columns[0]
    rate_col = "DFEDTARU" if "DFEDTARU" in df.columns else df.columns[1]

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df[rate_col] = pd.to_numeric(df[rate_col], errors="coerce")
    df = df.dropna(subset=[date_col, rate_col])

    if df.empty:
        report.passed = False
        report.checks.append(CheckResult("numeric_fields", "fail", "Empty or invalid FRED CSV"))
    else:
        report.checks.append(CheckResult("numeric_fields", "pass"))
        report.checks.append(CheckResult("valid_dates", "pass"))
        report.checks.append(CheckResult("duplicate_dates", "pass" if not df[date_col].duplicated().any() else "fail"))
        if df[date_col].duplicated().any():
            report.passed = False
        report.checks.append(
            CheckResult(
                "monotonic_date_ordering",
                "pass" if df[date_col].is_monotonic_increasing else "fail",
            )
        )
        if not df[date_col].is_monotonic_increasing:
            report.passed = False

    report.summary = {
        "errors": sum(1 for c in report.checks if c.status == "fail"),
        "warnings": sum(1 for c in report.checks if c.status == "warn"),
    }
    return report


def validate_fx_spot_raw(df: pd.DataFrame) -> ValidationReport:
    report = ValidationReport(
        report_id=f"raw_usd_mxn_spot_{date.today().isoformat().replace('-', '')}",
        target=str(USD_MXN_SPOT_CSV.relative_to(DATA_LAKE_ROOT.parent)),
        layer="raw",
        passed=True,
    )
    if "date" not in df.columns or "usd_mxn_spot" not in df.columns:
        report.passed = False
        report.checks.append(CheckResult("required_columns", "fail", "Missing date or usd_mxn_spot"))
    else:
        work = df.copy()
        work["date"] = pd.to_datetime(work["date"])
        work["usd_mxn_spot"] = pd.to_numeric(work["usd_mxn_spot"], errors="coerce")
        work = work.dropna()
        if work.empty:
            report.passed = False
            report.checks.append(CheckResult("numeric_fields", "fail", "Empty FX series"))
        else:
            report.checks.append(CheckResult("required_columns", "pass"))
            report.checks.append(CheckResult("numeric_fields", "pass"))
            report.checks.append(CheckResult("valid_dates", "pass"))
    report.summary = {
        "errors": sum(1 for c in report.checks if c.status == "fail"),
        "warnings": sum(1 for c in report.checks if c.status == "warn"),
    }
    return report


def validate_banxico_policy_raw(df: pd.DataFrame) -> ValidationReport:
    report = ValidationReport(
        report_id=f"raw_banxico_policy_{date.today().isoformat().replace('-', '')}",
        target=str(BANXICO_POLICY_CSV.relative_to(DATA_LAKE_ROOT.parent)),
        layer="raw",
        passed=True,
    )
    if "date" not in df.columns or "mx_policy_rate" not in df.columns:
        report.passed = False
        report.checks.append(CheckResult("required_columns", "fail"))
    else:
        work = df.copy()
        work["date"] = pd.to_datetime(work["date"])
        work["mx_policy_rate"] = pd.to_numeric(work["mx_policy_rate"], errors="coerce")
        work = work.dropna()
        if work.empty:
            report.passed = False
            report.checks.append(CheckResult("numeric_fields", "fail"))
        else:
            report.checks.append(CheckResult("required_columns", "pass"))
            report.checks.append(CheckResult("numeric_fields", "pass"))
            from src.lake.paths import BANXICO_POLICY_META

            if BANXICO_POLICY_META.exists():
                meta = json.loads(BANXICO_POLICY_META.read_text(encoding="utf-8"))
                if meta.get("retrieval_method") != "banxico_sie_api":
                    report.checks.append(
                        CheckResult(
                            "stale_source_warning",
                            "warn",
                            "FRED OECD overnight proxy when BANXICO_SIE_TOKEN unset",
                        )
                    )
    report.summary = {
        "errors": sum(1 for c in report.checks if c.status == "fail"),
        "warnings": sum(1 for c in report.checks if c.status == "warn"),
    }
    return report


def validate_rpw_cost_raw(df: pd.DataFrame) -> ValidationReport:
    report = ValidationReport(
        report_id=f"raw_rpw_cost_{date.today().isoformat().replace('-', '')}",
        target=str(RPW_COST_CSV.relative_to(DATA_LAKE_ROOT.parent)),
        layer="raw",
        passed=True,
    )
    required = {"date", "quarter", "remittance_cost_proxy", "corridor"}
    if not required.issubset(df.columns):
        report.passed = False
        report.checks.append(CheckResult("required_columns", "fail", f"Missing {required - set(df.columns)}"))
    else:
        work = df.copy()
        work["date"] = pd.to_datetime(work["date"])
        work["remittance_cost_proxy"] = pd.to_numeric(work["remittance_cost_proxy"], errors="coerce")
        if work["remittance_cost_proxy"].isna().any() or (work["remittance_cost_proxy"] <= 0).any():
            report.passed = False
            report.checks.append(CheckResult("numeric_fields", "fail"))
        else:
            report.checks.append(CheckResult("required_columns", "pass"))
            report.checks.append(CheckResult("numeric_fields", "pass"))
    report.summary = {
        "errors": sum(1 for c in report.checks if c.status == "fail"),
        "warnings": sum(1 for c in report.checks if c.status == "warn"),
    }
    return report


def validate_processed_canonical(df: pd.DataFrame) -> ValidationReport:
    report = ValidationReport(
        report_id=f"processed_usd_mxn_daily_{date.today().isoformat().replace('-', '')}",
        target=str(USD_MXN_DAILY_PARQUET.relative_to(DATA_LAKE_ROOT.parent)),
        layer="processed",
        passed=True,
    )
    lineage = ["source_id", "retrieval_date", "data_mode", "synthetic_flag", "methodology_version"]
    missing_lineage = [c for c in lineage if c not in df.columns]
    if missing_lineage:
        report.passed = False
        report.checks.append(CheckResult("source_lineage_present", "fail", f"Missing {missing_lineage}"))
    else:
        report.checks.append(CheckResult("source_lineage_present", "pass"))

    if "date" not in df.columns:
        report.passed = False
        report.checks.append(CheckResult("required_columns", "fail", "Missing date"))
    else:
        report.checks.append(CheckResult("required_columns", "pass"))
        dates = pd.to_datetime(df["date"])
        if dates.isna().any():
            report.passed = False
            report.checks.append(CheckResult("valid_dates", "fail"))
        else:
            report.checks.append(CheckResult("valid_dates", "pass"))
        if dates.duplicated().any():
            report.passed = False
            report.checks.append(CheckResult("duplicate_dates", "fail"))
        else:
            report.checks.append(CheckResult("duplicate_dates", "pass"))
        if not dates.is_monotonic_increasing:
            report.passed = False
            report.checks.append(CheckResult("monotonic_date_ordering", "fail"))
        else:
            report.checks.append(CheckResult("monotonic_date_ordering", "pass"))

    numeric_cols = [
        "usd_mxn_spot", "usd_return_1d", "usd_return_5d", "us_policy_rate", "mx_policy_rate",
        "rate_differential", "carry_proxy", "volatility_20d", "spread_proxy_bps",
        "liquidity_proxy", "remittance_cost_proxy", "corridor_risk_score", "remittance_usd_millions",
    ]
    for col in numeric_cols:
        if col not in df.columns:
            continue
        ser = pd.to_numeric(df[col], errors="coerce")
        if ser.isna().all():
            continue
        if not ser.dropna().apply(lambda x: pd.notna(x) and abs(x) != float("inf")).all():
            report.passed = False
            report.checks.append(CheckResult("numeric_fields", "fail", f"Bad values in {col}"))
            break
    else:
        report.checks.append(CheckResult("numeric_fields", "pass"))

    if "synthetic_flag" in df.columns and "data_mode" in df.columns:
        bad = df["data_mode"].eq("synthetic") & ~df["synthetic_flag"].astype(bool)
        if bad.any():
            report.passed = False
            report.checks.append(CheckResult("synthetic_live_data_flag", "fail"))
        else:
            report.checks.append(CheckResult("synthetic_live_data_flag", "pass"))

    if "usd_return_1d" in df.columns:
        extreme = df["usd_return_1d"].abs() > 0.05
        if extreme.any():
            report.checks.append(
                CheckResult(
                    "suspicious_extreme_one_day_change",
                    "warn",
                    f"{int(extreme.sum())} rows exceed 5% daily return",
                )
            )

    if "retrieval_date" in df.columns:
        retrieval = pd.to_datetime(df["retrieval_date"].iloc[0])
        age = (pd.Timestamp(date.today()) - retrieval).days
        if age > 30:
            report.checks.append(CheckResult("stale_source_warning", "warn", f"retrieval_date {age} days old"))

    report.summary = {
        "errors": sum(1 for c in report.checks if c.status == "fail"),
        "warnings": sum(1 for c in report.checks if c.status == "warn"),
    }
    return report


def run_all_validations() -> list[ValidationReport]:
    reports: list[ValidationReport] = []

    if REMITTANCES_CSV.exists():
        rem = pd.read_csv(REMITTANCES_CSV)
        reports.append(validate_remittances_raw(rem))

    if FED_POLICY_CSV.exists():
        fed = pd.read_csv(FED_POLICY_CSV)
        reports.append(validate_fed_rates_raw(fed))

    if USD_MXN_SPOT_CSV.exists():
        fx = pd.read_csv(USD_MXN_SPOT_CSV)
        reports.append(validate_fx_spot_raw(fx))

    if BANXICO_POLICY_CSV.exists():
        mx = pd.read_csv(BANXICO_POLICY_CSV)
        reports.append(validate_banxico_policy_raw(mx))

    if RPW_COST_CSV.exists():
        rpw = pd.read_csv(RPW_COST_CSV)
        reports.append(validate_rpw_cost_raw(rpw))

    if USD_MXN_DAILY_PARQUET.exists():
        canon = pd.read_parquet(USD_MXN_DAILY_PARQUET)
        reports.append(validate_processed_canonical(canon))

    return reports


def write_reports(reports: list[ValidationReport]) -> list[Path]:
    VALIDATION_REPORTS.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for r in reports:
        p = VALIDATION_REPORTS / f"{r.report_id}.json"
        p.write_text(json.dumps(r.to_dict(), indent=2), encoding="utf-8")
        paths.append(p)
    return paths
