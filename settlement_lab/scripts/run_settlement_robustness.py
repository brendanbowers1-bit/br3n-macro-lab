#!/usr/bin/env python3
"""Run settlement robustness checks."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.build_dataset import build_settlement_dataset
from src.models.robustness import run_robustness_checks
from src.utils.paths import OUTPUTS_DIR


def main() -> None:
    print("Bowers Frontier Settlement Economics Lab — robustness")
    ds = build_settlement_dataset()
    checks = run_robustness_checks(
        ds["settlement_drag_outputs"],
        ds["operational_liquidity_outputs"],
        ds["finality_quality_outputs"],
    )
    path = OUTPUTS_DIR / "robustness_results.csv"
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    checks.to_csv(path, index=False)
    print(checks.to_string(index=False))
    print(f"\nSaved: {path}")

    report_path = ROOT / "reports" / "memos" / "assumption_impact_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Assumption Impact Report\n", "Results are robust if Spearman rank correlation ≥ 0.85.\n\n"]
    for _, row in checks.iterrows():
        lines.append(f"- **{row['check_id']}**: Spearman={row.get('rank_stability_spearman')} robust={row.get('robust')}\n")
    report_path.write_text("".join(lines))
    print(f"Saved: {report_path}")


if __name__ == "__main__":
    main()
