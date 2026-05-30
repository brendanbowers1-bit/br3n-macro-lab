#!/usr/bin/env python3
"""Run flagship research lane: forecast failure vs hedge usefulness + R1/R2 quality."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_loader import load_config
from src.flagship_research_lane import build_turnover_adjusted_comparison, generate_flagship_report
from src.research_roadmap_reporting import generate_research_roadmap_report


def main() -> None:
    cfg = load_config()
    report_path, oos, r1r2 = generate_flagship_report(cfg)
    generate_research_roadmap_report(ROOT)

    print(f"Saved: {report_path}")
    print(f"Saved: {ROOT / 'data/outputs/flagship_hedge_oos_scorecard.csv'}")
    print(f"Saved: {ROOT / 'data/outputs/r1_r2_trend_quality_comparison.csv'}")
    print(f"Saved: {ROOT / 'data/outputs/flagship_turnover_adjusted_comparison.csv'}")
    print(f"Saved: {ROOT / 'data/outputs/r1_r2_trend_quality_oos.csv'}")
    print(f"Updated: {ROOT / 'reports/FX_RESEARCH_ROADMAP.md'}")

    turnover = build_turnover_adjusted_comparison(oos, cost_layer="forward_full")
    ok = oos[oos.get("status", "ok") == "ok"] if not oos.empty else oos
    ff = ok[ok.get("cost_layer", "base") == "forward_full"] if not ok.empty else ok
    print("\n" + "=" * 55)
    print("Flagship Lane Summary")
    print("=" * 55)
    if not ok.empty:
        best = ok.sort_values("cost_adjusted_risk_reduction", ascending=False).iloc[0]
        print(f"Best OOS policy (all):  {best['policy_name']} [{best.get('cost_layer')}] ({best.get('split')})")
        print(f"Cost-adj risk red.:     {best.get('cost_adjusted_risk_reduction')}")
        print(f"Hedge turnover:         {best.get('hedge_turnover')}")
    if not ff.empty:
        dyn = ff[ff.get("policy_class", "").isin(["dynamic", "carry_aware"])]
        if not dyn.empty:
            best_dyn = dyn.sort_values("turnover_efficiency", ascending=False).iloc[0]
            print(f"Best dynamic (forward_full, efficiency): {best_dyn['policy_name']} — eff {best_dyn.get('turnover_efficiency')}")
    if not turnover.empty:
        wins = int(turnover["dynamic_beats_static_efficiency"].sum())
        print(f"Dynamic beats static (efficiency): {wins}/{len(turnover)} OOS splits")
    if not r1r2.empty:
        r2 = r1r2[r1r2["regime"].str.contains("R2")].iloc[0]
        r1 = r1r2[r1r2["regime"].str.contains("R1")].iloc[0]
        print(f"R2 continuation:        {r2.get('continuation_probability')}")
        print(f"R1 continuation:        {r1.get('continuation_probability')}")
        print(f"R2 vol / R1 vol:        {r2.get('annualized_volatility')}% / {r1.get('annualized_volatility')}%")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
