#!/usr/bin/env python3
"""Run under-tested research layer: flow proxies, hedge governance, RW validity."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.data_loader import load_config
from src.flow_pressure_tests import run_flow_pressure_tests, save_flow_pressure_results
from src.flow_proxies import add_calendar_flow_proxies
from src.hedge_governance import run_all_hedge_governance, save_governance_outputs
from src.random_walk_validity import build_random_walk_validity_map, save_validity_map
from src.research_runner import load_research_data


def main() -> None:
    cfg = load_config()
    processed = ROOT / "data" / "processed" / "usdmxn_features_regimes.csv"
    if not processed.exists():
        print("Missing data/processed/usdmxn_features_regimes.csv")
        print("Run: python scripts/run_usdmxn_backtest.py")
        sys.exit(1)

    df = load_research_data(cfg)
    df_flow = add_calendar_flow_proxies(df, corridor="USD_MXN")
    flow_path = ROOT / "data" / "processed" / "usdmxn_features_regimes_flow.csv"
    flow_path.parent.mkdir(parents=True, exist_ok=True)
    df_flow.to_csv(flow_path, index=False)
    print(f"Saved flow-enhanced data: {flow_path}")

    fp_results = run_flow_pressure_tests(df_flow)
    fp_path = save_flow_pressure_results(fp_results)

    gov_sc, gov_det = run_all_hedge_governance(
        df_flow,
        cfg,
        exposures=["us_entity_long_mxn", "mx_entity_usd_liabilities"],
    )
    gov_sc_path, gov_det_path = save_governance_outputs(gov_sc, gov_det, cfg=cfg)

    validity = build_random_walk_validity_map(df_flow)
    validity_path = save_validity_map(validity)

    # Summary — US entity long MXN exposure (primary treasury lens)
    us = gov_sc[gov_sc["exposure_type"] == "us_entity_long_mxn"].copy()
    best = us.loc[us["cost_adjusted_risk_reduction"].idxmax()]
    lowest_turn = us.loc[us["hedge_turnover"].idxmin()]

    rb = us[us["policy_name"] == "regime_based"].iloc[0]
    ncr = us[us["policy_name"] == "no_change_in_range"].iloc[0]
    turnover_reduced = ncr["hedge_turnover"] < rb["hedge_turnover"]

    fp = fp_results.iloc[0]
    vol_higher = fp["volatility_flow_window"] > fp["volatility_normal"]

    rw_like = validity.loc[
        validity["random_walk_validity_label"] == "Random-walk-like", "regime"
    ]
    structured = validity.loc[
        validity["random_walk_validity_label"] == "Potential structure", "regime"
    ]

    print("\n" + "=" * 60)
    print("Bowers Frontier Macro Labs — Under-Tested Research Summary")
    print("=" * 60)
    print(f"Best policy (cost-adj risk reduction): {best['policy_name']}")
    print(f"  Cost-adj risk reduction: {best['cost_adjusted_risk_reduction']}")
    print(f"Lowest turnover policy: {lowest_turn['policy_name']} ({lowest_turn['hedge_turnover']})")
    print(
        f"no_change_in_range vs regime_based turnover: "
        f"{ncr['hedge_turnover']} vs {rb['hedge_turnover']} "
        f"({'reduced' if turnover_reduced else 'not reduced'})"
    )
    print(
        f"Flow window vol vs normal: {fp['volatility_flow_window']:.4f}% vs "
        f"{fp['volatility_normal']:.4f}% ({'higher' if vol_higher else 'not higher'})"
    )
    print(f"Most random-walk-like regime(s): {', '.join(rw_like) or 'none'}")
    print(f"Most potential-structure regime(s): {', '.join(structured) or 'none'}")
    print("\nReminder: Exploratory research only. Not investment advice.")
    print("=" * 60)
    print("\nOutputs:")
    print(f"  flow data: {flow_path}")
    print(f"  flow pressure: {fp_path}")
    print(f"  hedge governance scorecard: {gov_sc_path}")
    print(f"  hedge governance detail: {gov_det_path}")
    print(f"  random walk validity: {validity_path}")


if __name__ == "__main__":
    main()
