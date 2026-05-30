#!/usr/bin/env python3
"""Run hedge-policy tests only."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_loader import load_config
from src.hedge_backtest import run_all_hedge_policies, save_hedge_outputs
from src.research_runner import load_research_data


def main() -> None:
    cfg = load_config()
    df = load_research_data(cfg)
    exposure = cfg.get("research", {}).get("default_exposure", "us_entity_long_mxn")
    sc, det = run_all_hedge_policies(df, cfg, exposure)
    sc_path, det_path = save_hedge_outputs(sc, det)

    best = sc.loc[sc["cost_adjusted_risk_reduction"].idxmax()]
    print(f"\nBest hedge policy: {best['policy']}")
    print(f"  Cost-adjusted risk reduction: {best['cost_adjusted_risk_reduction']}")
    print(f"  Volatility reduction: {best['volatility_reduction']}%")
    print(f"  Total hedge cost: {best['total_hedge_cost_pct']}%")
    print(f"\nScorecard: {sc_path}")
    print(f"Detail:    {det_path}")


if __name__ == "__main__":
    main()
