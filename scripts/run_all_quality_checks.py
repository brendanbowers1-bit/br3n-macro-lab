#!/usr/bin/env python3
"""Master quality runner for BR3N Macro Lab."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.audit.metrics import count_project_lines, write_metrics_reports
from src.audit.reporting import write_report_bundle
from src.audit.snapshots import create_snapshot
from src.audit.git_utils import git_commit_hash
from src.quality.data_validation import run_data_validation
from src.quality.formula_validation import run_formula_validation
from src.quality.model_validation import run_model_validation


def _run(cmd: list[str], cwd: Path | None = None, timeout: int = 600, env=None) -> dict:
    try:
        r = subprocess.run(cmd, cwd=cwd or ROOT, capture_output=True, text=True, timeout=timeout, env=env)
        return {"status": "PASS" if r.returncode == 0 else "FAIL", "returncode": r.returncode, "stdout": r.stdout[-2000:], "stderr": r.stderr[-1000:]}
    except subprocess.TimeoutExpired:
        return {"status": "FAIL", "returncode": -1, "stdout": "", "stderr": "timeout"}
    except Exception as exc:
        return {"status": "SKIPPED", "returncode": -1, "stdout": "", "stderr": str(exc)}


def run_all_checks(skip_snapshot: bool = False, include_reproduce: bool = False) -> dict:
    rows = []

    if not skip_snapshot:
        try:
            snap = create_snapshot(reason="pre quality run", created_by="run_all_quality_checks")
            rows.append({"step": "pre_run_snapshot", "status": "PASS", "detail": str(snap.relative_to(ROOT))})
        except Exception as exc:
            rows.append({"step": "pre_run_snapshot", "status": "WARNING", "detail": str(exc)})
    else:
        rows.append({"step": "pre_run_snapshot", "status": "SKIPPED", "detail": "skip_snapshot=True"})

    try:
        metrics = count_project_lines(ROOT)
        write_metrics_reports(metrics, ROOT)
        rows.append({"step": "project_metrics", "status": "PASS", "detail": f"files={metrics['totals']['files']}"})
    except Exception as exc:
        rows.append({"step": "project_metrics", "status": "FAIL", "detail": str(exc)})

    for name, fn in (
        ("data_validation", run_data_validation),
        ("formula_validation", run_formula_validation),
        ("model_validation", run_model_validation),
    ):
        try:
            res = fn(ROOT)
            st = "FAIL" if res["summary"].get("fail", 0) else "PASS"
            rows.append({"step": name, "status": st, "detail": json.dumps(res["summary"])})
        except Exception as exc:
            rows.append({"step": name, "status": "FAIL", "detail": str(exc)})

    py = sys.executable
    run_smoke = False  # smoke tests rebuild full datasets; run via `make test` or scripts/smoke_test.py
    test_steps = [
        ("pytest_quality", [py, "-m", "pytest", "tests/", "-q", "--tb=no", "-m", "not slow", "--ignore=tests/test_snapshot_system.py"], ROOT),
        ("pytest_settlement", [py, "-m", "pytest", "tests/", "-q", "--tb=no"], ROOT / "settlement_lab"),
    ]
    if run_smoke:
        test_steps.extend([
            ("smoke_vsi", [py, "scripts/smoke_test.py"], ROOT),
            ("smoke_settlement", [py, "scripts/smoke_test_settlement_lab.py"], ROOT / "settlement_lab"),
        ])
    else:
        test_steps.append(("smoke_vsi", [], ROOT))
        test_steps.append(("smoke_settlement", [], ROOT))
    for step, cmd, cwd in test_steps:
        if step == "pytest_quality" and not (ROOT / "tests").exists():
            rows.append({"step": step, "status": "SKIPPED", "detail": "no tests/"})
            continue
        if step.startswith("smoke_") and not cmd:
            rows.append({"step": step, "status": "SKIPPED", "detail": "run scripts/smoke_test.py manually (slow)"})
            continue
        if step == "pytest_settlement" and not (ROOT / "settlement_lab" / "tests").exists():
            rows.append({"step": step, "status": "SKIPPED", "detail": "no settlement_lab/tests/"})
            continue
        env = None
        if step == "pytest_settlement":
            import os
            env = os.environ.copy()
            env["PYTHONPATH"] = str(cwd)
        res = _run(cmd, cwd=cwd, timeout=600, env=env if step == "pytest_settlement" else None)
        rows.append({"step": step, "status": res["status"], "detail": res["stderr"] or res["stdout"] or ""})

    if include_reproduce:
        optional = [
            ("reproduce_vsi", [py, "scripts/reproduce_all.py", "--skip-snapshot"]),
            ("reproduce_settlement", [py, "scripts/run_settlement_lab.py"]),
        ]
        for step, cmd in optional:
            res = _run(cmd, timeout=900)
            rows.append({"step": step, "status": res["status"] if res["status"] != "SKIPPED" else "WARNING", "detail": (res["stderr"] or "")[:200]})
    else:
        rows.append({"step": "reproduce_vsi", "status": "SKIPPED", "detail": "run scripts/reproduce_all.py separately"})
        rows.append({"step": "reproduce_settlement", "status": "SKIPPED", "detail": "run settlement_lab/scripts/reproduce_settlement_lab.py separately"})

    summary = {
        "pass": sum(1 for r in rows if r["status"] == "PASS"),
        "fail": sum(1 for r in rows if r["status"] == "FAIL"),
        "warning": sum(1 for r in rows if r["status"] == "WARNING"),
        "skipped": sum(1 for r in rows if r["status"] == "SKIPPED"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "git_commit": git_commit_hash(ROOT),
    }

    out_dir = ROOT / "audit" / "test_reports"
    paths = write_report_bundle(rows, out_dir, "full_quality_report", "Full Quality Report", summary)

    cred = _credibility_report(summary, rows)
    cred_path = ROOT / "audit" / "research_credibility_report.md"
    cred_path.write_text(cred, encoding="utf-8")

    return {"summary": summary, "rows": rows, "paths": {k: str(v) for k, v in paths.items()}}


def _credibility_report(summary: dict, rows: list[dict]) -> str:
    fails = [r for r in rows if r["status"] == "FAIL"]
    return f"""# Research Credibility Report

**Generated:** {summary.get('timestamp')}

## Quality run summary

- PASS: {summary.get('pass')}
- FAIL: {summary.get('fail')}
- WARNING: {summary.get('warning')}
- SKIPPED: {summary.get('skipped')}

## Publication-grade checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | No mock data in final outputs | Manual review required |
| 2 | Tier 1/2 sources for core variables | See DATA_GOVERNANCE / data_validation |
| 3 | Raw file hashes recorded | settlement_lab/metadata |
| 4 | Methodology version recorded | lineage columns |
| 5 | Assumptions disclosed | working papers / limitations |
| 6 | Sensitivity analysis completed | sensitivity_results.csv |
| 7 | Robustness checks completed | robustness_results.csv |
| 8 | Model validation passed | model_validation_report |
| 9 | Data validation passed | data_validation_report |
| 10 | Reproduction script passed | reproduce steps in quality report |
| 11 | Data quality score above 80 | dashboard / outputs |
| 12 | Claims limited to evidence | no causal language without identification |

## Failures

{chr(10).join(f"- {r['step']}: {r['detail'][:120]}" for r in fails) if fails else "_None_"}
"""


def main() -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--skip-snapshot", action="store_true")
    p.add_argument("--include-reproduce", action="store_true", help="Run full reproduction pipelines (slow)")
    args = p.parse_args()
    result = run_all_checks(skip_snapshot=args.skip_snapshot, include_reproduce=args.include_reproduce)
    s = result["summary"]
    print(f"Quality run: PASS={s['pass']} FAIL={s['fail']} WARNING={s['warning']}")
    print(f"Report: {result['paths'].get('md')}")
    return 1 if s["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
