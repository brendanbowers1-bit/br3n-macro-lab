"""
BR3N Value Survival Index — Streamlit dashboard.

Run: streamlit run src/dashboard/app.py

Research and education only. Not investment advice. Not a trading signal.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config.data_sources import sources_dataframe
from src.data.vsi_loader import load_vsi_dataset
from src.data.vsi_quality import VSI_LIMITATIONS, assess_dataset_provenance
from src.indices.currency_trust import calculate_currency_trust_table, CURRENCY_TRUST_LIMITATIONS
from src.indices.dollar_dependency import calculate_dollar_dependency_table, DOLLAR_DEPENDENCY_LIMITATIONS
from src.indices.hidden_fx_tax import calculate_hidden_fx_tax_table, rank_corridors_by_hidden_fx_tax, HIDDEN_FX_TAX_LIMITATIONS
from src.indices.remittance_welfare import calculate_remittance_welfare_table, rank_corridors_by_welfare_loss, REMITTANCE_WELFARE_LIMITATIONS
from src.research.questions import RESEARCH_QUESTIONS, questions_dataframe
from src.visuals.vsi_charts import (
    chart_component_breakdown,
    chart_leakage_vs_volume,
    chart_loss_per_100,
    chart_ranked_vsi,
    corridor_summary,
)

CSS = """
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0a0e14 !important;
        color: #e8edf4 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #121a28 !important;
    }
    [data-testid="stSidebar"] * {
        color: #e8edf4 !important;
    }
    h1, h2, h3, h4, h5, h6, p, li, span, label {
        color: #e8edf4;
    }
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        color: #e8edf4;
    }
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #e8edf4 !important;
    }
    [data-testid="stDataFrame"] {
        background: #121a28;
    }
    [data-testid="stExpander"] details summary p {
        color: #e8edf4 !important;
    }
    [data-testid="stAlert"] {
        background-color: #1a2436 !important;
        color: #e8edf4 !important;
        border: 1px solid #5b9fd4 !important;
    }
    .vsi-header { color: #5b9fd4; font-size: 2rem; font-weight: 600; }
    .vsi-sub { color: #94a3b8; font-size: 1.1rem; margin-bottom: 1rem; }
    .demo-banner {
        background: #3d1f1f; border: 1px solid #c44; padding: 0.75rem 1rem;
        border-radius: 4px; margin-bottom: 1rem; color: #fca5a5 !important;
    }
    .demo-banner strong { color: #fecaca !important; }
    .real-banner {
        background: #1a2e1a; border: 1px solid #3d9970; padding: 0.75rem 1rem;
        border-radius: 4px; margin-bottom: 1rem; color: #86efac !important;
    }
    .real-banner strong { color: #bbf7d0 !important; }
    .mixed-banner {
        background: #2a2416; border: 1px solid #ca8a04; padding: 0.75rem 1rem;
        border-radius: 4px; margin-bottom: 1rem; color: #fde047 !important;
    }
    .mixed-banner strong { color: #fef08a !important; }
    .thesis-box {
        background: #121a28; border-left: 4px solid #5b9fd4;
        padding: 1rem 1.25rem; margin: 1rem 0; border-radius: 4px;
        color: #e8edf4 !important;
    }
    .thesis-box p, .thesis-box strong { color: #e8edf4 !important; }
    .limit-box {
        background: #121a28; border: 1px solid #2a3548;
        padding: 0.75rem 1rem; margin-top: 1rem; border-radius: 4px;
        font-size: 0.9rem; color: #94a3b8 !important;
    }
    .limit-box strong { color: #cbd5e1 !important; }
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
            "RPW/KNOMAD/IMF/WB sources loaded. Timing, payout, trust formulas remain research placeholders.</div>",
            unsafe_allow_html=True,
        )


def _limitations(text: str) -> None:
    st.markdown(f'<div class="limit-box"><strong>Limitations:</strong> {text}</div>', unsafe_allow_html=True)


def _footer() -> None:
    st.markdown(
        '<p class="disclaimer">BR3N Value Survival Index · Research and education only · '
        "Not investment advice · Not a trading signal · Not a price forecast</p>",
        unsafe_allow_html=True,
    )


def page_mission():
    st.markdown('<p class="vsi-header">BR3N Value Survival Index</p>', unsafe_allow_html=True)
    st.markdown('<p class="vsi-sub">Measuring how much value survives when money crosses borders.</p>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="thesis-box">
<p><strong>Core thesis:</strong> Foreign exchange is the daily auction of global trust.</p>
<p>The Value Survival Index measures how much economic value survives that auction when it crosses
from one monetary trust system into another.</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
**Master formula:** `VSI = 100 × Real Usable Value Delivered / Original Value Sent`

**Version 1:** For every $100 sent across a remittance corridor, how much survives as usable purchasing power?

**Cross-border value loss** = fees + FX spread + timing + volatility + inflation + payout friction + dollar drag + trust discount
        """
    )
    _limitations(VSI_LIMITATIONS)
    _footer()


def page_overview(ds):
    vsi = ds["value_survival_outputs"]
    summary = corridor_summary(vsi)
    st.markdown("### Value Survival Overview")
    display_cols = [
        "corridor", "value_survival_index", "total_value_loss_pct",
        "value_loss_usd_per_100", "interpretation", "data_quality_score",
    ]
    if "data_mode" in summary.columns:
        display_cols.append("data_mode")
    st.dataframe(
        summary[display_cols],
        hide_index=True,
        use_container_width=True,
        column_config={
            "value_survival_index": st.column_config.NumberColumn(format="%.1f"),
            "total_value_loss_pct": st.column_config.NumberColumn(format="%.2%%"),
            "value_loss_usd_per_100": st.column_config.NumberColumn(format="$%.2f"),
            "data_quality_score": st.column_config.ProgressColumn(min_value=0, max_value=1),
        },
    )
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_ranked_vsi(summary), use_container_width=True)
    with c2:
        st.plotly_chart(chart_loss_per_100(summary), use_container_width=True)
    _limitations(VSI_LIMITATIONS)


def page_components(ds):
    vsi = ds["value_survival_outputs"]
    st.markdown("### Component Breakdown")
    st.plotly_chart(chart_component_breakdown(vsi), use_container_width=True)
    st.caption("Starter formulas — see Methodology page. Fee/spread from RPW when available.")
    _limitations("Component weights are additive estimates; double-counting risk exists between volatility and timing channels.")


def page_leakage_volume(ds):
    vsi = ds["value_survival_outputs"]
    flows = ds.get("remittance_flows", pd.DataFrame())
    st.markdown("### Value Leakage vs Remittance Volume")
    st.plotly_chart(chart_leakage_vs_volume(vsi, flows), use_container_width=True)
    st.caption("Bubble size = value lost per $100. Volume from KNOMAD-style bilateral flow estimates.")
    _limitations(REMITTANCE_WELFARE_LIMITATIONS)


def page_hidden_fx_tax(ds):
    st.markdown("### Hidden FX Tax")
    hft = calculate_hidden_fx_tax_table(
        ds["corridor_prices"], ds.get("fx_rates"), ds.get("macro_country_panel")
    )
    ranked = rank_corridors_by_hidden_fx_tax(hft)
    st.dataframe(ranked, hide_index=True, use_container_width=True)
    if not ranked.empty:
        top = ranked.iloc[0]
        st.markdown(
            f'<div class="info-box">Highest hidden FX tax: <strong>{top["corridor"]}</strong> '
            f'({top["hidden_fx_tax_pct"]*100:.2f}%)</div>',
            unsafe_allow_html=True,
        )
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
        "real_value_delivered_usd", "vsi_score", "total_value_loss_pct",
    ] if c in ranked.columns]
    st.dataframe(ranked[cols].head(20), hide_index=True, use_container_width=True)
    _limitations(REMITTANCE_WELFARE_LIMITATIONS)


def page_trust(ds):
    st.markdown("### Currency Trust")
    trust = calculate_currency_trust_table(ds["macro_country_panel"], ds.get("fx_rates"))
    st.dataframe(
        trust[[c for c in [
            "country", "currency", "currency_trust_score", "interpretation",
            "inflation_stability_score", "fx_stability_score", "institutional_trust_ph",
        ] if c in trust.columns]].sort_values("currency_trust_score", ascending=False),
        hide_index=True,
        use_container_width=True,
    )
    _limitations(CURRENCY_TRUST_LIMITATIONS)


def page_dollar(ds):
    st.markdown("### Dollar Dependency")
    dep = calculate_dollar_dependency_table(
        ds["macro_country_panel"], ds["currency_market_structure"],
        ds.get("remittance_flows"), ds.get("country_sovereignty"),
    )
    cols = [c for c in [
        "country", "currency", "dollar_dependency_score", "dollar_dependency_drag_pct",
        "interpretation", "explanation",
    ] if c in dep.columns]
    st.dataframe(dep[cols].sort_values("dollar_dependency_score", ascending=False), hide_index=True, use_container_width=True)
    _limitations(DOLLAR_DEPENDENCY_LIMITATIONS)


def page_methodology(ds):
    st.markdown("### Methodology & Data Quality")
    prov = assess_dataset_provenance(ds)
    st.metric("Data mode", prov.data_mode)
    st.metric("Overall quality score", f"{prov.overall_quality_score:.0%}")
    for note in prov.notes:
        st.write(f"• {note}")

    st.markdown(
        """
| Component | Formula | Data status |
|-----------|---------|-------------|
| Explicit fee | `fee_pct` | RPW / curated |
| FX spread | `fx_margin_pct` | RPW / curated |
| Timing loss | `days × daily_vol × 0.25` | **Placeholder** |
| Volatility loss | `vol × (1-hedge) × 0.10` | **Placeholder** |
| Inflation erosion | `inflation × days/365` | WB API / IMF |
| Payout friction | Method defaults | **Manual placeholder** |
| Dollar drag | `dep_score/100 × 0.75%` | BIS + sovereignty estimates |
| Trust discount | `(100-trust)/100 × 1%` | Trust sub-index |
        """
    )
    if "_provenance_report" in ds:
        st.dataframe(ds["_provenance_report"], hide_index=True, use_container_width=True)
    st.dataframe(sources_dataframe(), hide_index=True, use_container_width=True)
    _limitations(VSI_LIMITATIONS)


def page_research():
    st.markdown("### Research Lab")
    st.dataframe(questions_dataframe(), hide_index=True, use_container_width=True)
    for q in RESEARCH_QUESTIONS[:4]:
        with st.expander(q.title):
            st.write(f"**Hypothesis:** {q.hypothesis}")
            st.write(f"**Regression idea:** {q.possible_regression}")
    _limitations("Suggested regressions are hypotheses only — not validated causal models.")


def main():
    st.set_page_config(page_title="BR3N Value Survival Index", layout="wide", page_icon="📊")
    st.markdown(CSS, unsafe_allow_html=True)
    ds = load_vsi_data()
    _data_banner(ds)

    page = st.sidebar.radio(
        "VSI Research Platform",
        [
            "Mission",
            "Value Survival Overview",
            "Component Breakdown",
            "Leakage vs Volume",
            "Hidden FX Tax",
            "Remittance Welfare Loss",
            "Currency Trust",
            "Dollar Dependency",
            "Methodology",
            "Research Lab",
        ],
    )
    pages = {
        "Mission": page_mission,
        "Value Survival Overview": lambda: page_overview(ds),
        "Component Breakdown": lambda: page_components(ds),
        "Leakage vs Volume": lambda: page_leakage_volume(ds),
        "Hidden FX Tax": lambda: page_hidden_fx_tax(ds),
        "Remittance Welfare Loss": lambda: page_welfare(ds),
        "Currency Trust": lambda: page_trust(ds),
        "Dollar Dependency": lambda: page_dollar(ds),
        "Methodology": lambda: page_methodology(ds),
        "Research Lab": page_research,
    }
    pages[page]()
    _footer()


if __name__ == "__main__":
    main()
