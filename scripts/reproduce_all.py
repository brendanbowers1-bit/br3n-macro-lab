#!/usr/bin/env python3
"""Reproduce full BR3N Macro Lab pipelines with audit trail."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.audit.git_utils import git_commit_hash
from src.audit.metrics import count_project_lines, write_metrics_reports
from src.audit.snapshots import create_snapshot

VSI_STEPS = [
    ("build_dataset.py", "Build processed datasets"),
    ("run_vsi.py", "Compute Value Survival Index"),
    ("run_sensitivity.py", "Sensitivity analysis"),
    ("run_robustness.py", "Robustness checks"),
    ("make_visuals.py", "Generate figures"),
]

SETTLEMENT_STEPS = [
    ("build_settlement_dataset.py", "Build settlement dataset"),
    ("run_settlement_indices.py", "Settlement indices"),
    ("run_settlement_sensitivity.py", "Settlement sensitivity"),
    ("run_settlement_robustness.py", "Settlement robustness"),
    ("make_settlement_visuals.py", "Settlement visuals"),
]


def _run_script(script: str, cwd: Path) -> dict:
    r = subprocess.run([sys.executable, str(cwd / "scripts" / script)], cwd=cwd, capture_output=True, text=True)
    return {
        "script": script,
        "status": "PASS" if r.returncode == 0 else "FAIL",
        "returncode": r.returncode,
        "stderr": r.stderr[-500:] if r.stderr else "",
    }


def _package_versions() -> dict:
    try:
        import importlib.metadata as md

        pkgs = ["pandas", "numpy", "streamlit", "pytest", "requests"]
        return {p: md.version(p) for p in pkgs if _has_pkg(p)}
    except Exception:
        return {}


def _has_pkg(name: str) -> bool:
    try:
        import importlib.util
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


def reproduce(skip_snapshot: bool = False) -> dict:
    rows = []
    snap_path = None
    if not skip_snapshot:
        try:
            snap_path = create_snapshot(reason="before reproduce_all", created_by="reproduce_all")
            rows.append({"module": "snapshot", "step": "create_snapshot", "status": "PASS"})
        except Exception as exc:
            rows.append({"module": "snapshot", "step": "create_snapshot", "status": "WARNING", "detail": str(exc)})

    for script, desc in VSI_STEPS:
        res = _run_script(script, ROOT)
        rows.append({"module": "vsi", "step": script, "status": res["status"], "detail": desc})

    sl = ROOT / "settlement_lab"
    if sl.exists():
        for script, desc in SETTLEMENT_STEPS:
            if not (sl / "scripts" / script).exists():
                rows.append({"module": "settlement", "step": script, "status": "SKIPPED", "detail": "missing"})
                continue
            res = _run_script(script, sl)
            rows.append({"module": "settlement", "step": script, "status": res["status"], "detail": desc})
    else:
        rows.append({"module": "settlement", "step": "all", "status": "SKIPPED", "detail": "no settlement_lab"})

    validation_rows = []
    for name, mod_path, fn_name in (
        ("data", "src.quality.data_validation", "run_data_validation"),
        ("model", "src.quality.model_validation", "run_model_validation"),
    ):
        try:
            mod = __import__(mod_path, fromlist=[fn_name])
            res = getattr(mod, fn_name)(ROOT)
            st = "FAIL" if res["summary"].get("fail", 0) else "PASS"
            validation_rows.append({"check": name, "status": st, "summary": res["summary"]})
        except Exception as exc:
            validation_rows.append({"check": name, "status": "FAIL", "detail": str(exc)})

    test_r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=no"], cwd=ROOT, capture_output=True, text=True)
    metrics = count_project_lines(ROOT)
    write_metrics_reports(metrics, ROOT)

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "git_commit": git_commit_hash(ROOT),
        "packages": _package_versions(),
        "snapshot": str(snap_path) if snap_path else None,
        "steps_pass": sum(1 for r in rows if r["status"] == "PASS"),
        "steps_fail": sum(1 for r in rows if r["status"] == "FAIL"),
        "tests_returncode": test_r.returncode,
        "line_count": metrics["totals"],
        "validation": validation_rows,
    }

    out_dir = ROOT / "audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "reproducibility_report.json"
    json_path.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2), encoding="utf-8")

    md_lines = [
        "# Reproducibility Report",
        "",
        f"**Generated:** {summary['timestamp']}",
        "",
        f"- Python: `{summary['python'].split()[0]}`",
        f"- OS: {summary['platform']}",
        f"- Git commit: `{summary['git_commit'] or 'n/a'}`",
        f"- Snapshot: `{summary['snapshot'] or 'none'}`",
        "",
        "## Pipeline steps",
        "",
        "| Module | Step | Status |",
        "|--------|------|--------|",
    ]
    for r in rows:
        md_lines.append(f"| {r.get('module','')} | {r.get('step','')} | {r['status']} |")
    md_lines.extend([
        "",
        "## Validation",
        "",
        json.dumps(validation_rows, indent=2),
        "",
        "## Tests",
        "",
        f"pytest return code: {test_r.returncode}",
        "",
        "```",
        test_r.stdout[-1500:],
        "```",
        "",
        "## Line count",
        "",
        json.dumps(metrics["totals"], indent=2),
    ])
    (out_dir / "reproducibility_report.md").write_text("\n".join(md_lines), encoding="utf-8")
    return {"summary": summary, "rows": rows}


def main() -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--skip-snapshot", action="store_true")
    args = p.parse_args()
    result = reproduce(skip_snapshot=args.skip_snapshot)
    s = result["summary"]
    print(f"Reproduction: PASS={s['steps_pass']} FAIL={s['steps_fail']}")
    print(f"Report: {ROOT / 'audit/reproducibility_report.md'}")
    return 1 if s["steps_fail"] or s["tests_returncode"] != 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
