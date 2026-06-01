"""Data validation for Bowers Frontier Value Survival Index and shared outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.audit.reporting import write_report_bundle
from src.audit.git_utils import project_root
from src.quality.validation_rules import (
    check_metadata,
    check_mock_labeling,
    check_nan_inf,
    file_sha256,
    validate_settlement_outputs,
    validate_vsi_outputs,
)

VSI_OUTPUT_GLOBS = [
    "data/processed/value_survival_outputs.csv",
    "data/outputs/value_survival_outputs.csv",
    "data/outputs/vsi_*.csv",
]

SETTLEMENT_OUTPUT_GLOBS = [
    "settlement_lab/data/processed/*.csv",
    "settlement_lab/data/outputs/*.csv",
]

RAW_HASH_DIRS = [
    "data/raw",
    "settlement_lab/data/raw",
    "settlement_lab/data/metadata/file_checksums.csv",
]


def _discover_csvs(root: Path, patterns: list[str]) -> list[Path]:
    found = []
    for pat in patterns:
        if "*" in pat:
            found.extend(root.glob(pat))
        else:
            p = root / pat
            if p.exists():
                found.append(p)
    return sorted(set(found))


def validate_csv_file(path: Path, root: Path) -> dict:
    rel = str(path.relative_to(root))
    row = {"file": rel, "status": "PASS", "issues": "", "rows": 0, "module": "unknown"}
    if not path.exists():
        row["status"] = "FAIL"
        row["issues"] = "file missing"
        return row
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        row["status"] = "FAIL"
        row["issues"] = f"read error: {exc}"
        return row

    row["rows"] = len(df)
    issues = check_nan_inf(df, f"{rel}: ")
    issues += check_mock_labeling(df, f"{rel}: ")
    issues += check_metadata(df, f"{rel}: ")

    if "value_survival" in rel or "vsi" in rel.lower():
        row["module"] = "VSI"
        issues += validate_vsi_outputs(df)
    elif "settlement_lab" in rel:
        row["module"] = "Settlement"
        table = path.stem
        issues += validate_settlement_outputs(df, table)

    if issues:
        row["status"] = "FAIL"
        row["issues"] = "; ".join(issues[:10])
    return row


def validate_raw_hashes(root: Path) -> list[dict]:
    rows = []
    checksum_file = root / "settlement_lab/data/metadata/file_checksums.csv"
    if checksum_file.exists():
        df = pd.read_csv(checksum_file)
        for _, r in df.iterrows():
            fp = root / r["file_path"]
            if fp.exists():
                actual = file_sha256(fp)
                expected = str(r.get("sha256", ""))
                ok = actual == expected
                rows.append({
                    "file": r["file_path"],
                    "status": "PASS" if ok else "WARNING",
                    "issues": "" if ok else f"hash mismatch expected={expected[:12]} actual={actual[:12]}",
                    "module": "raw_hash",
                })
    return rows


def run_data_validation(root: Path | None = None) -> dict:
    root = root or project_root()
    patterns = VSI_OUTPUT_GLOBS + SETTLEMENT_OUTPUT_GLOBS
    files = _discover_csvs(root, patterns)
    rows = [validate_csv_file(p, root) for p in files]
    rows += validate_raw_hashes(root)

    if not rows:
        rows.append({"file": "none", "status": "WARNING", "issues": "no CSV outputs found", "module": "scan"})

    summary = {
        "pass": sum(1 for r in rows if r.get("status") == "PASS"),
        "fail": sum(1 for r in rows if r.get("status") == "FAIL"),
        "warning": sum(1 for r in rows if r.get("status") == "WARNING"),
        "total": len(rows),
    }
    out_dir = root / "audit" / "data_quality_reports"
    paths = write_report_bundle(rows, out_dir, "data_validation_report", "Data Validation Report", summary)
    return {"summary": summary, "rows": rows, "paths": {k: str(v) for k, v in paths.items()}}


def main() -> int:
    result = run_data_validation()
    s = result["summary"]
    print(f"Data validation: PASS={s['pass']} FAIL={s['fail']} WARNING={s['warning']}")
    return 1 if s["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
