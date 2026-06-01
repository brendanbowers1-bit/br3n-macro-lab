"""
Bowers Frontier Value Survival Index — Streamlit dashboard (research-grade).

Run: streamlit run src/dashboard/app.py

Research and education only. Not investment advice. Not a trading signal.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.config.data_sources import sources_dataframe
from src.config.research_settings import RESEARCH_MODE, METHODOLOGY_VERSION, SENSITIVITY_CASES
from src.data.data_quality import quality_summary_by_corridor
from src.data.vsi_loader import load_vsi_dataset
from src.data.vsi_quality import VSI_LIMITATIONS, assess_dataset_provenance
from src.indices.currency_trust import calculate_currency_trust_table, CURRENCY_TRUST_LIMITATIONS
from src.indices.dollar_dependency import calculate_dollar_dependency_table, DOLLAR_DEPENDENCY_LIMITATIONS
from src.indices.hidden_fx_tax import calculate_hidden_fx_tax_table, rank_corridors_by_hidden_fx_tax, HIDDEN_FX_TAX_LIMITATIONS
from src.indices.remittance_welfare import calculate_remittance_welfare_table, rank_corridors_by_welfare_loss, REMITTANCE_WELFARE_LIMITATIONS
from src.models.correlation_analysis import corridor_correlation_matrix, test_hypothesis_associations
from src.models.robustness import run_robustness_checks
from src.models.sensitivity import rank_stability_matrix, sensitivity_summary
from src.research.hypotheses import HYPOTHESES, hypotheses_dataframe
from src.utils.paths import OUTPUTS_DIR
from src.visuals.vsi_charts import (
    chart_component_breakdown,
    chart_data_quality,
    chart_leakage_vs_volume,
    chart_loss_per_100,
    chart_official_vs_assumed,
    chart_rank_stability,
    chart_ranked_vsi,
    chart_ranked_vsi_by_col,
    chart_sensitivity_ranges,
    corridor_summary,
)

CSS = """
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0a0e14 !important; color: #e8edf4 !important;
    }
    [data-testid="stSidebar"] { background-color: #121a28 !important; }
    [data-testid="stSidebar"] * { color: #e8edf4 !important; }
    h1, h2, h3, h4, p, li, span, label { color: #e8edf4; }
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color: #e8edf4 !important; }
    .vsi-header { color: #5b9fd4; font-size: 2rem; font-weight: 600; }
    .vsi-sub { color: #94a3b8; font-size: 1.1rem; margin-bottom: 1rem; }
    .demo-banner {
        background: #3d1f1f; border: 1px solid #c44; padding: 0.75rem 1rem;
        border-radius: 4px; margin-bottom: 1rem; color: #fca5a5 !important;
    }
    .real-banner {
        background: #1a2e1a; border: 1px solid #3d9970; padding: 0.75rem 1rem;
        border-radius: 4px; margin-bottom: 1rem; color: #86efac !important;
    }
    .mixed-banner {
        background: #2a2416; border: 1px solid #ca8a04; padding: 0.75rem 1rem;
        border-radius: 4px; margin-bottom: 1rem; color: #fde047 !important;
    }
    .thesis-box {
        background: #121a28; border-left: 4px solid #5b9fd4;
        padding: 1rem 1.25rem; margin: 1rem 0; border-radius: 4px; color: #e8edf4 !important;
    }
    .limit-box {
        background: #121a28; border: 1px solid #2a3548;
        padding: 0.75rem 1rem; margin-top: 1rem; border-radius: 4px;
        font-size: 0.9rem; color: #94a3b8 !important;
    }
    .info-box {
        background: #1a2436; border: 1px solid #5b9fd4; padding: 0.75rem 1rem;
        border-radius: 4px; color: #e8edf4 !important; margin: 0.5rem 0;
    }
    .disclaimer { color: #64748b !important; font-size: 0.85rem; margin-top: 2rem; }
</style>
"""


@st.cache_data(show_spinner="Loading VSI dataset…")
def load_vsi_data() -> dict:
    return load_vsi_dataset(rebuild=False)


def _data_banner(ds: dict) -> None:
    prov = assess_dataset_provenance(ds)
    if prov.data_mode == "demo":
        st.markdown(
            '<div class="demo-banner">⚠️ <strong>Demo mode:</strong> synthetic seed data only. '
            "Do not use for research conclusions or policy decisions.</div>",
            unsafe_allow_html=True,
        )
    elif prov.data_mode == "mixed":
        st.markdown(
            f'<div class="mixed-banner">ℹ️ <strong>Mixed data mode</strong> (quality {prov.overall_quality_score:.0%}): '
            "some tables are demo/seed. Component formulas include placeholders.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="real-banner">✓ <strong>Public data mode</strong> (quality {prov.overall_quality_score:.0%}): '
            f"RESEARCH_MODE={RESEARCH_MODE}. RPW/KNOMAD/IMF/WB sources loaded.</div>",
            unsafe_allow_html=True,
        )


def _limitations(text: str) -> None:
    st.markdown(f'<div class="limit-box"><strong>Limitations:</strong> {text}</div>', unsafe_allow_html=True)


def _source_note() -> None:
    st.caption(f"Data sources: World Bank RPW, KNOMAD, IMF/WB macro · Methodology {METHODOLOGY_VERSION}")


def _footer() -> None:
    st.markdown(
        '<p class="disclaimer">Bowers Frontier Value Survival Index · Research and education only · '
        "Not investment advice · Not a trading signal · Not a price forecast</p>",
        unsafe_allow_html=True,
    )


def page_mission():
    st.markdown('<p class="vsi-header">Bowers Frontier Value Survival Index</p>', unsafe_allow_html=True)
    st.markdown('<p class="vsi-sub">Measuring how much value survives when money crosses borders.</p>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="thesis-box">
<p><strong>Core thesis:</strong> Foreign exchange is the daily auction of global trust.</p>
<p>The Value Survival Index <em>estimates</em> how much economic value survives that auction when money crosses
from one monetary trust system into another.</p>
<p><strong>Empirical question:</strong> For every $100 sent, how much survives as usable purchasing power after
fees, FX spread, transfer delay, volatility, inflation, payout friction, and (extended spec) dollar/trust adjustments?</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
**Master formula:** `VSI = 100 × Real Usable Value Delivered / Original Value Sent`

This framework **measures** value loss under stated assumptions. It does **not** prove causal welfare effects.
        """
    )
    _source_note()
    _limitations(VSI_LIMITATIONS)


def page_overview(ds):
    vsi = ds["value_survival_outputs"]
    summary = corridor_summary(vsi)
    st.markdown("### Value Survival Overview")
    st.markdown("Primary index: **VSI_RISK_ADJUSTED** (baseline empirical specification).")
    display_cols = [c for c in [
        "corridor", "vsi_risk_adjusted", "vsi_core", "vsi_extended",
        "total_value_loss_pct", "value_loss_usd_per_100", "interpretation",
        "data_quality_score", "data_quality_grade", "data_mode",
    ] if c in summary.columns]
    st.dataframe(summary[display_cols], hide_index=True, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_ranked_vsi(summary), use_container_width=True)
    with c2:
        st.plotly_chart(chart_loss_per_100(summary), use_container_width=True)
    _source_note()
    _limitations(VSI_LIMITATIONS)


def page_vsi_tiers(ds):
    st.markdown("### Core vs Risk-Adjusted vs Extended VSI")
    st.markdown(
        """
| Index | Components |
|-------|------------|
| **VSI_CORE** | Fee, spread, timing, inflation, payout |
| **VSI_RISK_ADJUSTED** | Core + volatility exposure |
| **VSI_EXTENDED** | Risk-adjusted + dollar drag + trust discount |
        """
    )
    summary = corridor_summary(ds["value_survival_outputs"])
    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(chart_ranked_vsi_by_col(summary, "vsi_core", "VSI Core"), use_container_width=True)
    with c2:
        st.plotly_chart(chart_ranked_vsi(summary), use_container_width=True)
    with c3:
        st.plotly_chart(chart_ranked_vsi_by_col(summary, "vsi_extended", "VSI Extended"), use_container_width=True)
    st.info("Extended components are model-based adjustments — not in baseline VSI_CORE.")
    _limitations("Trust and dollar drag are excluded from baseline index by design.")


def page_components(ds):
    vsi = ds["value_survival_outputs"]
    st.markdown("### Component Breakdown")
    st.plotly_chart(chart_component_breakdown(vsi), use_container_width=True)
    st.caption("Fee/spread from RPW when available. Timing/volatility use sensitivity weights.")
    _source_note()
    _limitations("Component weights are additive estimates; double-counting risk between timing and volatility.")


def page_data_quality(ds):
    st.markdown("### Data Quality & Credibility")
    vsi = ds["value_survival_outputs"]
    st.plotly_chart(chart_data_quality(vsi), use_container_width=True)
    st.plotly_chart(chart_official_vs_assumed(vsi), use_container_width=True)
    qsum = quality_summary_by_corridor(vsi)
    st.dataframe(qsum, hide_index=True, use_container_width=True)
    low = qsum[qsum["data_quality_score"] < 60] if not qsum.empty else qsum
    if not low.empty:
        st.warning(f"{len(low)} corridor(s) below Preliminary threshold (score < 60) — treat as exploratory.")
    _source_note()
    _limitations("Quality score reflects data availability, not forecast accuracy.")


def page_sensitivity(ds):
    st.markdown("### Sensitivity Analysis")
    st.markdown(f"Cases: {', '.join(SENSITIVITY_CASES)} — timing and volatility weights vary.")
    path = OUTPUTS_DIR / "vsi_sensitivity_results.csv"
    if path.exists():
        sens = pd.read_csv(path)
        summary = sensitivity_summary(sens)
        st.plotly_chart(chart_sensitivity_ranges(summary), use_container_width=True)
        rank_mat = rank_stability_matrix(sens)
        st.plotly_chart(chart_rank_stability(rank_mat), use_container_width=True)
        st.dataframe(summary.head(20), hide_index=True, use_container_width=True)
    else:
        st.info("Run `python scripts/run_sensitivity.py` to generate sensitivity outputs.")
    _limitations("Wide ranges indicate results depend heavily on assumed timing/volatility weights.")


def page_robustness(ds):
    st.markdown("### Robustness Checks")
    st.markdown("Results are **robust** if corridor rankings remain similar across specifications.")
    path = OUTPUTS_DIR / "robustness_results.csv"
    if path.exists():
        checks = pd.read_csv(path)
        st.dataframe(checks, hide_index=True, use_container_width=True)
    else:
        mock = ds["value_survival_outputs"]["mock_data_flag"].any()
        checks = run_robustness_checks(
            ds["corridor_prices"], ds.get("fx_rates"), ds.get("macro_country_panel"),
            ds.get("currency_trust"), ds.get("dollar_dependency"), mock_data_flag=bool(mock),
        )
        st.dataframe(checks, hide_index=True, use_container_width=True)
    _limitations("Rank stability (Spearman ≥ 0.85) is a descriptive check, not a statistical test.")


def page_leakage_volume(ds):
    vsi = ds["value_survival_outputs"]
    flows = ds.get("remittance_flows", pd.DataFrame())
    st.markdown("### Value Leakage vs Remittance Volume")
    st.plotly_chart(chart_leakage_vs_volume(vsi, flows), use_container_width=True)
    _source_note()
    _limitations(REMITTANCE_WELFARE_LIMITATIONS)


def page_hidden_fx_tax(ds):
    st.markdown("### Hidden FX Tax")
    hft = calculate_hidden_fx_tax_table(
        ds["corridor_prices"], ds.get("fx_rates"), ds.get("macro_country_panel")
    )
    ranked = rank_corridors_by_hidden_fx_tax(hft)
    st.dataframe(ranked, hide_index=True, use_container_width=True)
    _limitations(HIDDEN_FX_TAX_LIMITATIONS)


def page_welfare(ds):
    st.markdown("### Remittance Welfare Loss")
    hft = calculate_hidden_fx_tax_table(
        ds["corridor_prices"], ds.get("fx_rates"), ds.get("macro_country_panel")
    )
    welfare = calculate_remittance_welfare_table(hft, ds["remittance_flows"], ds["value_survival_outputs"])
    ranked = rank_corridors_by_welfare_loss(welfare)
    cols = [c for c in [
        "corridor", "year", "annual_remittance_usd", "aggregate_value_loss_usd",
        "real_value_delivered_usd", "vsi_score", "remittance_volume_source",
    ] if c in ranked.columns]
    st.dataframe(ranked[cols].head(20), hide_index=True, use_container_width=True)
    _limitations(REMITTANCE_WELFARE_LIMITATIONS)


def page_trust(ds):
    st.markdown("### Currency Trust (Extended Specification)")
    trust = calculate_currency_trust_table(ds["macro_country_panel"], ds.get("fx_rates"))
    st.dataframe(
        trust.sort_values("currency_trust_score", ascending=False),
        hide_index=True, use_container_width=True,
    )
    _limitations(CURRENCY_TRUST_LIMITATIONS)


def page_dollar(ds):
    st.markdown("### Dollar Dependency (Extended Specification)")
    dep = calculate_dollar_dependency_table(
        ds["macro_country_panel"], ds["currency_market_structure"],
        ds.get("remittance_flows"), ds.get("country_sovereignty"),
    )
    st.dataframe(dep.sort_values("dollar_dependency_score", ascending=False), hide_index=True, use_container_width=True)
    _limitations(DOLLAR_DEPENDENCY_LIMITATIONS)


def page_hypotheses(ds):
    st.markdown("### Research Hypotheses")
    st.dataframe(hypotheses_dataframe(), hide_index=True, use_container_width=True)
    mock = ds["value_survival_outputs"]["mock_data_flag"].any()
    assoc = test_hypothesis_associations(ds["value_survival_outputs"], mock_data_flag=bool(mock))
    if assoc.get("warning"):
        st.warning(assoc["warning"])
    if not assoc["associations"].empty:
        st.markdown("**Exploratory associations (not causal):**")
        st.dataframe(assoc["associations"], hide_index=True, use_container_width=True)
    for h in HYPOTHESES[:3]:
        with st.expander(f"{h.id}: {h.title}"):
            st.write(h.statement)
            st.write(f"**Limitation:** {h.identification_limitation}")
            st.write(f"**Credibility risk:** {h.credibility_risk}")


def page_methodology(ds):
    st.markdown("### Methodology & Assumptions")
    prov = assess_dataset_provenance(ds)
    st.metric("Data mode", prov.data_mode)
    st.metric("Methodology version", METHODOLOGY_VERSION)
    st.metric("Research mode", RESEARCH_MODE)
    for note in prov.notes:
        st.write(f"• {note}")
    st.markdown(
        """
| Component | Formula | Data status |
|-----------|---------|-------------|
| Explicit fee | `fee_pct` | RPW / curated |
| FX spread | `fx_margin_pct` | RPW / curated |
| Timing loss | `days × daily_vol × weight` | Modeled |
| Volatility loss | `vol × (1-hedge) × weight` | Modeled |
| Inflation erosion | `inflation × days/365` | WB API / IMF |
| Payout friction | Method defaults | Manual placeholder |
| Dollar drag | Extended spec only | BIS + sovereignty |
| Trust discount | Extended spec only | Trust sub-index |
        """
    )
    _limitations(VSI_LIMITATIONS)


def page_data_sources():
    st.markdown("### Data Sources")
    st.dataframe(sources_dataframe(), hide_index=True, use_container_width=True)
    st.markdown("See [DATA_SOURCES.md](../DATA_SOURCES.md) for methodology notes and traceability fields.")


def page_quality_command_center(ds):
    st.markdown("### Quality Command Center")
    root = Path(__file__).resolve().parents[2]
    reports = {
        "Full quality": root / "audit/test_reports/full_quality_report.md",
        "Data validation": root / "audit/data_quality_reports/data_validation_report.md",
        "Model validation": root / "audit/model_validation_reports/model_validation_report.md",
        "Line count": root / "audit/project_metrics/line_count_report.md",
        "Credibility": root / "audit/research_credibility_report.md",
    }
    for name, path in reports.items():
        if path.exists():
            with st.expander(name):
                st.markdown(path.read_text()[:8000])
        else:
            st.caption(f"{name}: not generated — run `python scripts/run_all_quality_checks.py`")

    snaps = root / "audit/change_logs/snapshot_log.csv"
    if snaps.exists():
        st.markdown("**Latest snapshots**")
        st.dataframe(pd.read_csv(snaps).tail(5), hide_index=True, use_container_width=True)

    checklist = [
        ("No mock data in final outputs", ds["value_survival_outputs"]["mock_data_flag"].any() == False),  # noqa: E712
        ("Sensitivity analysis completed", (root / "data/outputs/sensitivity_results.csv").exists()),
        ("Robustness checks completed", (root / "data/outputs/robustness_results.csv").exists()),
        ("Data quality scores present", "data_quality_score" in ds["value_survival_outputs"].columns),
    ]
    st.markdown("**Publication-grade checklist (auto-check partial)**")
    for label, ok in checklist:
        st.write(f"{'✅' if ok else '⚠️'} {label}")


def page_limitations():
    st.markdown("### Limitations")
    path = Path(__file__).resolve().parents[2] / "reports" / "working_paper" / "limitations_section.md"
    if path.exists():
        st.markdown(path.read_text())
    else:
        _limitations(VSI_LIMITATIONS)


def main():
    st.set_page_config(page_title="Bowers Frontier Value Survival Index", layout="wide", page_icon="📊")
    st.markdown(CSS, unsafe_allow_html=True)
    ds = load_vsi_data()
    _data_banner(ds)

    pages = {
        "Mission": page_mission,
        "VSI Overview": lambda: page_overview(ds),
        "Core vs Risk-Adjusted vs Extended": lambda: page_vsi_tiers(ds),
        "Component Breakdown": lambda: page_components(ds),
        "Data Quality & Credibility": lambda: page_data_quality(ds),
        "Sensitivity Analysis": lambda: page_sensitivity(ds),
        "Robustness Checks": lambda: page_robustness(ds),
        "Leakage vs Volume": lambda: page_leakage_volume(ds),
        "Hidden FX Tax": lambda: page_hidden_fx_tax(ds),
        "Remittance Welfare Loss": lambda: page_welfare(ds),
        "Currency Trust": lambda: page_trust(ds),
        "Dollar Dependency": lambda: page_dollar(ds),
        "Research Hypotheses": lambda: page_hypotheses(ds),
        "Methodology": lambda: page_methodology(ds),
        "Data Sources": page_data_sources,
        "Quality Command Center": lambda: page_quality_command_center(ds),
        "Limitations": page_limitations,
    }
    page = st.sidebar.radio("VSI Research Platform", list(pages.keys()))
    pages[page]()
    _footer()


if __name__ == "__main__":
    main()
