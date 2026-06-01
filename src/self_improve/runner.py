"""
Self-improvement runner — snapshot runs, compare, propose next experiments.

Research-only. Does not auto-tune on holdout or place trades.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml

from .scorer import overall_health, score_all

ROOT = Path(__file__).resolve().parents[2]

SNAPSHOT_FILES = [
    "forecast_scorecard.csv",
    "academic_test_results.csv",
    "ml_direction_model_scorecard.csv",
    "hedge_policy_scorecard.csv",
    "hedge_governance_scorecard.csv",
    "flow_pressure_test_results.csv",
    "random_walk_validity_map.csv",
    "data_quality_report.csv",
    "data_source_comparison_usdmxn.csv",
    "strategy_scorecard.csv",
    "usdmxn_scorecard.csv",
    "walkforward_oos.csv",
    "model_zoo_forecast_scorecard.csv",
    "model_zoo_trading_scorecard.csv",
    "model_zoo_hedge_scorecard.csv",
    "model_zoo_run_log.csv",
    "news_feature_test_results.csv",
    "carry_regime_test_results.csv",
    "carry_hedge_governance_scorecard.csv",
]

EXPERIMENT_CATALOG = {
    "forecast_vs_random_walk": {
        "priority": 2,
        "action": "Test conditional forecastability by regime (Level 4 ladder); do not claim FX prediction.",
        "script": "python scripts/run_research_ladder.py",
    },
    "ml_direction": {
        "priority": 3,
        "action": "Deprioritize ML direction; focus hedge-governance path (forecast failure vs hedge usefulness).",
        "script": "python scripts/run_under_tested_research.py",
    },
    "trading_oos": {
        "priority": 2,
        "action": "Review transaction costs and flat_range rule; run level5 economic friction tests.",
        "script": "python scripts/run_research_ladder.py",
    },
    "hedge_governance": {
        "priority": 1,
        "action": "Expand no_change_in_range and calendar-flow tests; compare Tier 1 vs Tier 4 spot.",
        "script": "python scripts/run_under_tested_research.py",
    },
    "data_quality": {
        "priority": 1,
        "action": "Upgrade to Tier 1 official spot: python scripts/fetch_tier1_official.py (or set FRED_API_KEY).",
        "script": "python scripts/fetch_tier1_official.py",
    },
    "data_snooping_control": {
        "priority": 2,
        "action": "Pre-register next experiment before testing; avoid tuning on holdout 2025–2026.",
        "script": "python scripts/run_research_ladder.py",
    },
    "data_provenance": {
        "priority": 1,
        "action": "Rerun backtest with preferred_source fred_h10; verify scorecard provenance columns.",
        "script": "python scripts/run_usdmxn_backtest.py",
    },
    "model_zoo_forecast": {
        "priority": 2,
        "action": "Focus hedge-governance path; do not claim forecast alpha until RW beaten OOS.",
        "script": "python scripts/run_model_zoo.py",
    },
    "news_layer": {
        "priority": 3,
        "action": "Validate news stress splits on holdout; optional GDELT with look-ahead checks.",
        "script": "python scripts/run_news_layer.py",
    },
    "carry_layer": {
        "priority": 2,
        "action": "Add forward points CSV; compare policy-rate proxy vs executable carry.",
        "script": "python scripts/run_carry_layer.py",
    },
    "carry_hedge_governance": {
        "priority": 1,
        "action": "Test carry_adjusted_regime under forward_full costs on multi-pair OOS.",
        "script": "python scripts/run_carry_layer.py",
    },
}


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_config(cfg_path: Optional[Path] = None) -> dict:
    path = cfg_path or ROOT / "config.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _snapshot_outputs(run_dir: Path, out_dir: Path) -> List[str]:
    copied = []
    run_dir.mkdir(parents=True, exist_ok=True)
    for name in SNAPSHOT_FILES:
        src = out_dir / name
        if src.exists():
            shutil.copy2(src, run_dir / name)
            copied.append(name)
    ladder = ROOT / "reports" / "research_ladder"
    if ladder.exists():
        ladder_snap = run_dir / "research_ladder"
        ladder_snap.mkdir(exist_ok=True)
        for csv in ladder.glob("*.csv"):
            shutil.copy2(csv, ladder_snap / csv.name)
            copied.append(f"research_ladder/{csv.name}")
    return copied


def _prior_runs(runs_dir: Path, limit: int = 10) -> List[Path]:
    if not runs_dir.exists():
        return []
    dirs = sorted([d for d in runs_dir.iterdir() if d.is_dir()], reverse=True)
    return dirs[:limit]


def _load_prior_summary(run_dir: Path) -> dict | None:
    p = run_dir / "summary.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def propose_experiments(scores: List[dict]) -> List[dict]:
    """Map weak/insufficient dimensions to next experiments (fixed catalog)."""
    proposals = []
    for s in scores:
        if s["verdict"] not in ("weak", "insufficient_data"):
            continue
        cat = EXPERIMENT_CATALOG.get(s["dimension"])
        if not cat:
            continue
        proposals.append(
            {
                "dimension": s["dimension"],
                "verdict": s["verdict"],
                "current_detail": s["detail"],
                "priority": cat["priority"],
                "proposed_action": cat["action"],
                "suggested_script": cat["script"],
            }
        )
    proposals.sort(key=lambda x: x["priority"])
    return proposals


def compare_to_prior(current: dict, prior: dict | None) -> dict:
    if prior is None:
        return {"has_prior": False, "deltas": []}

    deltas = []
    cur_map = {s["dimension"]: s for s in current.get("scores", [])}
    pri_map = {s["dimension"]: s for s in prior.get("scores", [])}
    for dim in cur_map:
        if dim not in pri_map:
            continue
        if cur_map[dim]["verdict"] != pri_map[dim]["verdict"]:
            deltas.append(
                {
                    "dimension": dim,
                    "from": pri_map[dim]["verdict"],
                    "to": cur_map[dim]["verdict"],
                }
            )
    return {"has_prior": True, "prior_run_id": prior.get("run_id"), "deltas": deltas}


def _subprocess_run(script: str) -> bool:
    parts = script.split()
    py = sys.executable
    if parts[0] in ("python", "python3"):
        parts = parts[1:]
    try:
        r = subprocess.run([py] + parts, cwd=ROOT, timeout=600)
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def rerun_pipelines(cfg: dict) -> dict:
    """Run configured research stages (research-only)."""
    si = cfg.get("self_improvement", {})
    stages = si.get("auto_rerun", ["backtest", "research", "under_tested", "data_quality"])
    results: Dict[str, bool] = {}

    stage_scripts = {
        "full_pipeline": ["scripts/run_full_lab_pipeline.sh"],
        "backtest": ["scripts/run_usdmxn_backtest.py"],
        "data_upgrade": ["scripts/run_data_upgrade_report.py"],
        "news": ["scripts/run_news_layer.py"],
        "carry": ["scripts/run_carry_layer.py"],
        "model_zoo": ["scripts/run_model_zoo.py", "scripts/generate_model_zoo_report.py"],
        "research": ["scripts/run_research_models.py"],
        "under_tested": ["scripts/run_under_tested_research.py"],
        "flagship_lane": ["scripts/run_flagship_research_lane.py"],
        "data_quality": [
            "scripts/run_data_quality.py",
            "scripts/export_data_sources.py",
        ],
        "ladder": ["scripts/run_research_ladder.py"],
        "lab_status": ["scripts/generate_lab_status.py"],
    }

    for stage in stages:
        ok = True
        for script in stage_scripts.get(stage, []):
            if script.endswith(".sh"):
                try:
                    r = subprocess.run(
                        ["bash", str(ROOT / script)],
                        cwd=ROOT,
                        timeout=1800,
                    )
                    if r.returncode != 0:
                        ok = False
                except subprocess.TimeoutExpired:
                    ok = False
            elif not _subprocess_run(f"python {script}"):
                ok = False
        results[stage] = ok
    return results


def run_self_improvement(
    cfg: Optional[dict] = None,
    rerun: bool = False,
) -> dict:
    """
    Score current lab state, snapshot outputs, compare to prior run, propose experiments.
    """
    cfg = cfg or _load_config()
    si = cfg.get("self_improvement", {})
    runs_dir = ROOT / si.get("runs_dir", "data/runs")
    out_dir = ROOT / cfg.get("reporting", {}).get("output_dir", "data/outputs")

    rerun_results = {}
    if rerun:
        rerun_results = rerun_pipelines(cfg)

    scores = score_all(cfg)
    health = overall_health(scores)
    proposals = propose_experiments(scores)

    run_id = _run_id()
    run_dir = runs_dir / run_id
    copied = _snapshot_outputs(run_dir, out_dir)

    priors = _prior_runs(runs_dir, limit=si.get("compare_last_n", 10) + 1)
    prior_summary = None
    for p in priors:
        if p.name != run_id:
            prior_summary = _load_prior_summary(p)
            break

    summary = {
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "health": health,
        "scores": scores,
        "proposals": proposals,
        "rerun": rerun,
        "rerun_results": rerun_results,
        "files_snapshotted": copied,
        "disclaimer": "Research-only self-improvement. Not investment advice. No auto-tuning on holdout.",
    }
    summary["comparison"] = compare_to_prior(summary, prior_summary)

    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.DataFrame(scores).to_csv(run_dir / "dimension_scores.csv", index=False)
    if proposals:
        pd.DataFrame(proposals).to_csv(run_dir / "proposed_experiments.csv", index=False)

    # Latest symlink-style copy for dashboard
    latest = runs_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(run_dir / "summary.json", latest / "summary.json")
    if proposals:
        shutil.copy2(run_dir / "proposed_experiments.csv", latest / "proposed_experiments.csv")
    pd.DataFrame(scores).to_csv(latest / "dimension_scores.csv", index=False)

    try:
        from src.lab_status import write_lab_status

        status_path = write_lab_status(cfg)
        summary["lab_status_path"] = str(status_path.relative_to(ROOT))
        shutil.copy2(status_path, run_dir / "LAB_STATUS.md")
        shutil.copy2(status_path, latest / "LAB_STATUS.md")
    except Exception as exc:
        summary["lab_status_error"] = str(exc)[:200]

    return summary


def print_summary(summary: dict) -> None:
    print("\n" + "=" * 60)
    print("Bowers Frontier Macro Labs — Self-Improvement Loop")
    print("=" * 60)
    print(f"Run ID:   {summary['run_id']}")
    print(f"Health:   {summary['health']}")
    print("\nDimension scores:")
    for s in summary["scores"]:
        print(f"  [{s['verdict']:18}] {s['dimension']}: {s['detail']}")

    comp = summary.get("comparison", {})
    if comp.get("has_prior"):
        print(f"\nVs prior run {comp.get('prior_run_id')}:")
        for d in comp.get("deltas", []):
            print(f"  {d['dimension']}: {d['from']} → {d['to']}")
        if not comp.get("deltas"):
            print("  No verdict changes.")

    if summary.get("proposals"):
        print("\nProposed next experiments (research-only):")
        for i, p in enumerate(summary["proposals"][:5], 1):
            print(f"  {i}. [{p['dimension']}] {p['proposed_action']}")
            print(f"     → {p['suggested_script']}")

    print(f"\nSnapshot: data/runs/{summary['run_id']}/")
    if summary.get("lab_status_path"):
        print(f"Lab status: {summary['lab_status_path']}")
    print("Reminder: Research-only. No auto-tuning on holdout. Not investment advice.")
    print("=" * 60)
