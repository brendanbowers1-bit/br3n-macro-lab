#!/usr/bin/env python3
"""Generate stablecoin lab figures."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px

from src.data.build_dataset import build_stablecoin_dataset
from src.utils.paths import FIGURES_DIR, OUTPUTS_DIR

NOTE = "Research estimate · Not investment advice · Demo data unless Tier 1/2 sources loaded"


def _save(fig, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.update_layout(
        template="plotly_dark",
        annotations=[dict(text=NOTE, xref="paper", yref="paper", x=0, y=-0.18, showarrow=False, font=dict(size=10, color="#94a3b8"))],
        margin=dict(b=90),
    )
    p = FIGURES_DIR / name
    fig.write_html(str(p.with_suffix(".html")), include_plotlyjs="cdn")
    try:
        fig.write_image(str(p), width=1100, height=620, scale=2)
    except Exception:
        pass
    print(f"  Saved: {p.with_suffix('.html')}")


def main() -> None:
    print("Bowers Frontier Stablecoin Settlement Window Lab — make visuals")
    ds = build_stablecoin_dataset()
    sfqi = ds["stablecoin_finality_quality_outputs"]
    swc = ds["settlement_window_compression_outputs"]
    slt = ds["liquidity_transformation_outputs"]
    drv = ds["digital_run_velocity_outputs"]
    sdi = ds["stablecoin_dollarization_outputs"]
    sing = ds["tokenized_money_singleness_outputs"]
    csd = ds["compliance_settlement_drag_outputs"]
    svsi = ds["stablecoin_value_survival_outputs"]

    if not sfqi.empty:
        _save(px.bar(sfqi.sort_values("stablecoin_finality_quality_index"), x="entity", y="stablecoin_finality_quality_index",
                     title="Stablecoin Finality Quality Index"), "finality_quality_by_stablecoin.png")
        if "ledger_finality_score" in sfqi.columns and "economic_finality_score" in sfqi.columns:
            comp = sfqi.groupby("entity", as_index=False).agg(
                ledger_finality_score=("ledger_finality_score", "mean"),
                economic_finality_score=("economic_finality_score", "mean"),
            )
            comp = comp.melt(id_vars=["entity"], var_name="finality_type", value_name="score")
            _save(px.bar(comp, x="entity", y="score", color="finality_type", barmode="group",
                         title="Ledger vs Economic Finality"), "ledger_vs_economic_finality.png")

    if not swc.empty and "swc_extended" in swc.columns:
        _save(px.bar(swc, x="entity", y=["swc_core", "swc_risk_adjusted", "swc_extended"], barmode="group",
                     title="Settlement Window Compression"), "settlement_window_compression.png")

    if not slt.empty:
        _save(px.bar(slt, x="entity", y=["user_liquidity_benefit_score", "issuer_reserve_burden_score"],
                     barmode="group", title="Liquidity Transformation"), "liquidity_transformation_components.png")

    if not drv.empty:
        _save(px.bar(drv.sort_values("digital_run_velocity_score"), x="entity", y="digital_run_velocity_score",
                     title="Digital Run Velocity (risk conditions, not prediction)"), "digital_run_velocity_scores.png")

    if not sdi.empty:
        _save(px.bar(sdi.sort_values("stablecoin_dollarization_index"), x="entity", y="stablecoin_dollarization_index",
                     title="Stablecoin Dollarization Index"), "stablecoin_dollarization_scores.png")

    if not sing.empty:
        _save(px.bar(sing.sort_values("singleness_index"), x="entity", y="singleness_index",
                     title="Tokenized Money Singleness Index"), "tokenized_money_singleness.png")

    if not csd.empty:
        comp = csd.melt(id_vars=["entity"], value_vars=["ledger_finality_seconds", "effective_economic_finality_hours"],
                        var_name="metric", value_name="hours")
        _save(px.bar(comp, x="entity", y="hours", color="metric", barmode="group",
                     title="Compliance Settlement Drag"), "compliance_drag_breakdown.png")

    if not svsi.empty:
        _save(px.bar(svsi, x="entity", y=["stablecoin_vsi", "traditional_vsi"], barmode="group",
                     title="Stablecoin VSI vs Traditional Remittance VSI"), "stablecoin_vsi_vs_traditional_vsi.png")

    reserves = ds.get("stablecoin_reserves", pd.DataFrame())
    peg = ds.get("stablecoin_price_peg", pd.DataFrame())
    if not reserves.empty and not peg.empty:
        m = peg.groupby("stablecoin", as_index=False)["peg_deviation_bps"].mean().merge(
            reserves.groupby("stablecoin", as_index=False)["reserve_liquidity_score"].mean(), on="stablecoin")
        _save(px.scatter(m, x="reserve_liquidity_score", y="peg_deviation_bps", hover_name="stablecoin",
                         title="Depeg Risk vs Reserve Liquidity"), "depeg_risk_vs_reserve_liquidity.png")

    val = ds.get("_validation", pd.DataFrame())
    if not val.empty and "table" in val.columns:
        heat = val.set_index("table")[["valid"]].astype(int)
        _save(px.imshow(heat, title="Data Quality Validation Heatmap"), "data_quality_heatmap.png")

    rob = OUTPUTS_DIR / "stablecoin_robustness_results.csv"
    if rob.exists():
        rdf = pd.read_csv(rob)
        if "rank_stability_spearman" in rdf.columns:
            _save(px.bar(rdf, x="check_id", y="rank_stability_spearman", title="Robustness Rank Stability"),
                  "robustness_rank_stability.png")

    print("Visuals complete.")


if __name__ == "__main__":
    main()
