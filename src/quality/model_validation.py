"""Model validation for VSI and Settlement Economics Lab."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.audit.reporting import write_report_bundle
from src.audit.git_utils import project_root

CAUSAL_WORDS = ("proves", "causal", "causes", "proof that")


def _check_outputs(path: Path, module: str) -> list[str]:
    issues = []
    if not path.exists():
        return [f"missing output: {path.name}"]
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return [f"empty output file: {path.name}"]
    if df.empty:
        return [f"empty output file: {path.name}"]
    for col in df.select_dtypes(include="number").columns:
        if "score" in col.lower() or "index" in col.lower():
            if df[col].min() < 0 or df[col].max() > 100:
                if col != "data_quality_score" or df[col].max() > 100:
                    issues.append(f"{col} out of bounds [0,100]")
    if "limitations" in df.columns and df["limitations"].isna().all():
        issues.append("limitations column all empty")
    if "confidence_score" in df.columns and df["confidence_score"].isna().all():
        issues.append("confidence_score all empty")
    if "data_quality_score" in df.columns and df["data_quality_score"].isna().any():
        issues.append("missing data_quality_score values")
    for col in df.columns:
        if "interpretation" in col.lower() or col == "limitations":
            text = " ".join(df[col].dropna().astype(str).str.lower())
            for w in CAUSAL_WORDS:
                if w in text and "identification" not in text:
                    issues.append(f"possible causal language '{w}' in {col} without identification_strategy")
    return issues


def _check_sensitivity_robustness(root: Path, module: str) -> list[str]:
    issues = []
    if module == "VSI":
        sens = root / "data/outputs/sensitivity_results.csv"
        rob = root / "data/outputs/robustness_results.csv"
    else:
        sens = root / "settlement_lab/data/outputs/sensitivity_results.csv"
        rob = root / "settlement_lab/data/outputs/robustness_results.csv"
    if not sens.exists():
        issues.append(f"{module}: sensitivity_results.csv missing")
    if not rob.exists():
        issues.append(f"{module}: robustness_results.csv missing")
    return issues


def run_model_validation(root: Path | None = None) -> dict:
    root = root or project_root()
    rows = []

    checks = [
        ("VSI", root / "data/outputs/value_survival_outputs.csv"),
        ("VSI", root / "data/processed/value_survival_outputs.csv"),
        ("Settlement", root / "settlement_lab/data/outputs/settlement_drag_outputs.csv"),
        ("Settlement", root / "settlement_lab/data/outputs/finality_quality_outputs.csv"),
        ("Settlement", root / "settlement_lab/data/outputs/payment_fragility_outputs.csv"),
    ]

    for module, path in checks:
        if not path.exists():
            rows.append({"model": path.name, "module": module, "status": "SKIPPED", "issues": "file not found"})
            continue
        issues = _check_outputs(path, module)
        issues += _check_sensitivity_robustness(root, module) if path.name.endswith("value_survival_outputs.csv") or path.name == "settlement_drag_outputs.csv" else []
        rows.append({
            "model": path.name,
            "module": module,
            "status": "PASS" if not issues else "FAIL",
            "issues": "; ".join(dict.fromkeys(issues)),
        })

    summary = {
        "pass": sum(1 for r in rows if r["status"] == "PASS"),
        "fail": sum(1 for r in rows if r["status"] == "FAIL"),
        "skipped": sum(1 for r in rows if r["status"] == "SKIPPED"),
    }
    out_dir = root / "audit" / "model_validation_reports"
    paths = write_report_bundle(rows, out_dir, "model_validation_report", "Model Validation Report", summary)
    return {"summary": summary, "rows": rows, "paths": {k: str(v) for k, v in paths.items()}}


def main() -> int:
    result = run_model_validation()
    s = result["summary"]
    print(f"Model validation: PASS={s['pass']} FAIL={s['fail']} SKIPPED={s['skipped']}")
    return 1 if s["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
