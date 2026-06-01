#!/usr/bin/env python3
"""Generate settlement lab figures."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config.data_sources import DATA_SOURCES
from src.data.build_dataset import build_settlement_dataset
from src.models.stress_scenarios import run_stress_scenarios
from src.utils.paths import FIGURES_DIR, OUTPUTS_DIR

NOTE = "Research estimate · Not financial advice · See METHODOLOGY_SETTLEMENT_ECONOMICS.md"


def _save(fig, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.update_layout(
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
    print("Bowers Frontier Settlement Economics Lab — make visuals")
    ds = build_settlement_dataset()
    sdi = ds["settlement_drag_outputs"]
    olb = ds["operational_liquidity_outputs"]
    fqi = ds["finality_quality_outputs"]
    pnf = ds["payment_fragility_outputs"]
    pfi = ds["friction_incidence_outputs"]

    if not sdi.empty:
        fig = px.bar(sdi.sort_values("settlement_drag_index"), x="entity", y="settlement_drag_index",
                     title="Settlement Drag Index by rail (higher = less drag)", template="plotly_dark")
        fig.update_layout(xaxis_tickangle=-45)
        _save(fig, "settlement_drag_ranked.png")

        comp = sdi.melt(id_vars=["entity"], value_vars=["capital_cost_usd", "fx_exposure_cost_usd", "failure_cost_usd", "operational_cost_usd"],
                        var_name="component", value_name="usd")
        _save(px.bar(comp.head(120), x="entity", y="usd", color="component", barmode="stack", title="SDI components", template="plotly_dark"), "settlement_drag_components.png")

    if not olb.empty:
        _save(px.scatter(olb, x="liquidity_burden_ratio", y="operational_liquidity_burden_score",
                         hover_name="payment_system", title="Liquidity burden frontier", template="plotly_dark"), "liquidity_burden_frontier.png")
        _save(px.bar(olb.sort_values("liquidity_cost_per_100", ascending=False).head(20),
                      x="payment_system", y="liquidity_cost_per_100", title="OLB cost per $100 settled", template="plotly_dark"), "operational_liquidity_cost_per_100.png")

    if not fqi.empty:
        _save(px.bar(fqi.sort_values("finality_quality_index").head(30), x="entity", y="finality_quality_index",
                     title="Finality Quality Index by rail", template="plotly_dark"), "finality_quality_by_rail.png")
        comp_cols = [c for c in ["legal_finality_score", "funds_availability_score", "settlement_speed_score",
                                  "operational_finality_score", "reconciliation_quality_score"] if c in fqi.columns]
        if comp_cols:
            m = fqi.groupby("rail_type")[comp_cols].mean().reset_index().melt(id_vars="rail_type", var_name="component", value_name="score")
            _save(px.bar(m, x="rail_type", y="score", color="component", barmode="group", title="Finality component breakdown", template="plotly_dark"), "finality_component_breakdown.png")

    if not pnf.empty:
        _save(px.bar(pnf.sort_values("payment_network_fragility_score").head(30), x="entity", y="payment_network_fragility_score",
                     color="fragility_regime", title="Payment Network Fragility", template="plotly_dark"), "payment_fragility_scores.png")
        stress = run_stress_scenarios(pnf)
        if not stress.empty:
            _save(px.bar(stress.groupby("scenario_id")["delta_score"].mean().reset_index(),
                          x="scenario_id", y="delta_score", title="Fragility scenario impacts", template="plotly_dark"), "fragility_scenario_impacts.png")

    if not pfi.empty:
        cols = [c for c in pfi.columns if c.startswith("estimated_cost_borne")]
        if cols:
            m = pfi[cols].mean().reset_index()
            m.columns = ["party", "pct"]
            m["party"] = m["party"].str.replace("estimated_cost_borne_by_", "").str.replace("_pct", "")
            _save(px.bar(m, x="party", y="pct", title="Payment friction incidence (model-based)", template="plotly_dark"), "friction_incidence_stacked.png")

    if not sdi.empty and "data_quality_score" in sdi.columns:
        pivot = sdi.pivot_table(index="country", columns="rail_type", values="data_quality_score", aggfunc="mean")
        _save(px.imshow(pivot, title="Data quality heatmap", template="plotly_dark"), "data_quality_heatmap.png")

    tiers = pd.DataFrame([{"source_id": s.source_id, "tier": s.credibility_tier, "indices": len(s.indices_supported)} for s in DATA_SOURCES])
    _save(px.bar(tiers, x="source_id", y="tier", color="tier", title="Source credibility tier registry", template="plotly_dark"), "source_coverage_chart.png")

    rank_path = OUTPUTS_DIR / "rank_stability.csv"
    if rank_path.exists():
        rm = pd.read_csv(rank_path)
        if "entity" in rm.columns and len(rm.columns) > 2:
            cases = [c for c in rm.columns if c != "entity"]
            z = rm.set_index("entity")[cases]
            _save(px.imshow(z, title="SDI rank stability across sensitivity cases", template="plotly_dark"), "robustness_rank_stability.png")

    rob = OUTPUTS_DIR / "robustness_results.csv"
    if rob.exists():
        rdf = pd.read_csv(rob)
        if "rank_stability_spearman" in rdf.columns:
            _save(px.bar(rdf, x="check_id", y="rank_stability_spearman", title="Robustness rank stability", template="plotly_dark"), "robustness_rank_stability.png")

    print("Research only — not financial advice.")


if __name__ == "__main__":
    main()
