#!/usr/bin/env python3
"""Run USD/MXN corridor intelligence pipeline: validate → score → brief → gold layer."""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.corridor_intelligence.brief import generate_corridor_brief, write_corridor_brief
from src.corridor_intelligence.dataset import load_us_mx_remittances
from src.corridor_intelligence.risk_score import compute_corridor_risk_score
from src.corridor_intelligence.validate import validate_us_mx_dataset
from src.lake.paths import CORRIDOR_DAILY_JSON, PROCESSED_CORRIDORS, REMITTANCES_CSV

OUT_DIR = ROOT / "data" / "outputs"
GOLD_DIR = ROOT / "data_lake" / "gold_research" / "us_mx_corridor"
BRIEF_DIR = ROOT / "model-lab" / "outputs" / "briefs"


def run(*, build_canonical: bool = True) -> dict:
    df = load_us_mx_remittances(REMITTANCES_CSV)
    validation = validate_us_mx_dataset(df)
    if not validation.passed:
        raise SystemExit(f"Corridor validation failed: {validation.errors}")

    score = compute_corridor_risk_score(df, data_quality_score=validation.data_quality_score)
    flows = df["remittance_usd_millions"].tolist()
    labels = df["month_label"].tolist()

    payload = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "lab": "Bowers Frontier Macro Labs",
            "product": "USD/MXN Corridor Intelligence System",
            "methodology_version": score.methodology_version,
            "raw_path": str(REMITTANCES_CSV.relative_to(ROOT)),
        },
        "validation": validation.to_dict(),
        "risk_score": score.to_dict(),
        "series": {
            "month_labels": labels,
            "remittance_usd_millions": flows,
        },
        "kpis": {
            "latest_flow": score.metrics["latest_flow_usd_millions"],
            "yoy_pct": score.metrics["yoy_pct"],
            "yoy_abs": round(flows[-1] - flows[-13], 1) if len(flows) >= 13 else None,
            "ytd_2025": round(sum(flows[12:23]), 1) if len(flows) >= 23 else None,
            "peak_flow": score.metrics["peak_flow_usd_millions"],
            "peak_month": labels[int(flows.index(max(flows)))],
            "latest_month": labels[-1],
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "us_mx_corridor_daily.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    PROCESSED_CORRIDORS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(json_path, CORRIDOR_DAILY_JSON)

    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(json_path, GOLD_DIR / "corridor_daily.json")
    df.to_csv(GOLD_DIR / "remittances_validated.csv", index=False)

    brief_md = generate_corridor_brief(df, score, validation.to_dict())
    brief_name = f"us_mx_corridor_{score.as_of_month.replace('-', '')}.md"
    brief_path = write_corridor_brief(BRIEF_DIR / brief_name, brief_md)
    shutil.copy2(brief_path, GOLD_DIR / "latest_brief.md")
    pub_brief = ROOT / "reports" / "publication" / "us-mx-corridor-brief.md"
    pub_brief.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(brief_path, pub_brief)

    if build_canonical:
        from src.lake.usd_mxn_canonical import build_usd_mxn_canonical

        build_usd_mxn_canonical(corridor_json_src=json_path)

    print(f"Validation: PASS (quality={validation.data_quality_score:.0f})")
    print(f"Corridor Risk Score: {score.score}/100 ({score.band})")
    print(f"JSON: {json_path}")
    print(f"Data-lake JSON: {CORRIDOR_DAILY_JSON}")
    print(f"Brief: {brief_path}")
    return payload


if __name__ == "__main__":
    run()
