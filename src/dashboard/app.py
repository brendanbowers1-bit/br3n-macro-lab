"""
BR3N Value Survival Index — Streamlit dashboard.

Run: streamlit run src/dashboard/app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config.data_sources import sources_dataframe
from src.data.build_dataset import build_value_survival_dataset
from src.data.mock_data import is_using_mock_data
from src.indices.currency_trust import calculate_currency_trust_table
from src.indices.dollar_dependency import calculate_dollar_dependency_table
from src.indices.hidden_fx_tax import calculate_hidden_fx_tax_table, rank_corridors_by_hidden_fx_tax
from src.indices.remittance_welfare import calculate_remittance_welfare_table, rank_corridors_by_welfare_loss
from src.research.questions import RESEARCH_QUESTIONS, questions_dataframe
from src.utils.paths import OUTPUTS_DIR

CSS = """
<style>
    .stApp { background-color: #0a0e14; color: #e8edf4; }
    .vsi-header { color: #5b9fd4; font-size: 2rem; font-weight: 600; }
    .vsi-sub { color: #94a3b8; font-size: 1.1rem; margin-bottom: 1rem; }
    .demo-banner {
        background: #3d1f1f; border: 1px solid #c44; padding: 0.75rem 1rem;
        border-radius: 4px; margin-bottom: 1rem;
    }
    .thesis-box {
        background: #121a28; border-left: 4px solid #5b9fd4;
        padding: 1rem 1.25rem; margin: 1rem 0; border-radius: 4px;
    }
</style>
"""


@st.cache_data(show_spinner="Computing Value Survival Index…")
def load_vsi_data() -> dict:
    out_path = OUTPUTS_DIR / "value_survival_outputs.csv"
    if out_path.exists():
        try:
            vsi = pd.read_csv(out_path, parse_dates=["date"] if "date" in pd.read_csv(out_path, nrows=1).columns else None)
            ds = build_value_survival_dataset()
            ds["value_survival_outputs"] = vsi
            return ds
        except Exception:
            pass
    return build_value_survival_dataset()


def _mock_banner(ds: dict) -> None:
    mock = is_using_mock_data(ds) or ds["value_survival_outputs"].get("mock_data_flag", pd.Series([False])).any()
    if mock:
        st.markdown(
            '<div class="demo-banner">⚠️ <strong>Demo mode:</strong> this dashboard is using synthetic mock data. '
            "Do not use for research conclusions.</div>",
            unsafe_allow_html=True,
        )


def _corridor_summary(vsi: pd.DataFrame) -> pd.DataFrame:
    return (
        vsi.groupby("corridor", as_index=False)
        .agg(
            value_survival_index=("value_survival_index", "mean"),
            total_value_loss_pct=("total_value_loss_pct", "mean"),
            real_usable_value_delivered_pct=("real_usable_value_delivered_pct", "mean"),
            value_loss_usd_per_100=("value_loss_usd_per_100", "mean"),
            interpretation=("interpretation", "first"),
            data_quality_score=("data_quality_score", "mean"),
            mock_data_flag=("mock_data_flag", "first"),
        )
        .sort_values("value_survival_index", ascending=False)
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
**Master formula:**

`VSI = 100 × Real Usable Value Delivered / Original Value Sent`

**Version 1 question:** For every $100 sent across a remittance corridor, how much survives as usable purchasing power for the recipient?

**Flagship paper:** *The Value Survival Index: Measuring How Much Value Survives When Money Crosses Borders*

*Research and education only. Not investment advice. Not a trading signal.*
        """
    )


def page_overview(ds):
    vsi = ds["value_survival_outputs"]
    summary = _corridor_summary(vsi)
    st.markdown("### Value Survival Overview")
    st.dataframe(
        summary[
            [
                "corridor",
                "value_survival_index",
                "total_value_loss_pct",
                "real_usable_value_delivered_pct",
                "value_loss_usd_per_100",
                "interpretation",
                "data_quality_score",
                "mock_data_flag",
            ]
        ],
        hide_index=True,
        use_container_width=True,
    )
    fig = px.bar(
        summary.sort_values("value_survival_index"),
        x="corridor",
        y="value_survival_index",
        color="value_survival_index",
        color_continuous_scale="Teal",
        title="Value Survival Index by corridor (higher = more value survives)",
        template="plotly_dark",
    )
    fig.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)


def page_components(ds):
    vsi = ds["value_survival_outputs"]
    summary = _corridor_summary(vsi)
    comp_cols = [
        "explicit_fee_loss_pct",
        "fx_spread_loss_pct",
        "timing_loss_pct",
        "volatility_loss_pct",
        "inflation_erosion_pct",
        "payout_friction_pct",
        "dollar_dependency_drag_pct",
        "trust_discount_pct",
    ]
    agg = vsi.groupby("corridor")[comp_cols].mean().reset_index()
    st.markdown("### Component Breakdown")
    melted = agg.melt(id_vars="corridor", var_name="component", value_name="loss_pct")
    melted["loss_pct"] = melted["loss_pct"] * 100
    fig = px.bar(
        melted,
        x="corridor",
        y="loss_pct",
        color="component",
        barmode="stack",
        title="Cross-border value loss components (% of sent value)",
        template="plotly_dark",
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Each component is a transparent starting assumption — refine with real corridor data.")


def page_hidden_fx_tax(ds):
    st.markdown("### Hidden FX Tax")
    hft = calculate_hidden_fx_tax_table(
        ds["corridor_prices"], ds.get("fx_rates"), ds.get("macro_country_panel")
    )
    ranked = rank_corridors_by_hidden_fx_tax(hft)
    st.dataframe(ranked, hide_index=True, use_container_width=True)
    if not ranked.empty:
        top = ranked.iloc[0]
        st.info(f"Highest hidden FX tax corridor: **{top['corridor']}** ({top['hidden_fx_tax_pct']*100:.2f}%)")


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
    if "aggregate_value_loss_usd" in ranked.columns and not ranked.empty:
        fig = px.bar(
            ranked.groupby("corridor", as_index=False)["aggregate_value_loss_usd"].sum().sort_values(
                "aggregate_value_loss_usd", ascending=False
            ).head(10),
            x="corridor",
            y="aggregate_value_loss_usd",
            title="Estimated aggregate annual value loss (top corridors)",
            template="plotly_dark",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


def page_trust(ds):
    st.markdown("### Currency Trust")
    trust = calculate_currency_trust_table(ds["macro_country_panel"], ds.get("fx_rates"))
    st.dataframe(
        trust[
            [
                c
                for c in [
                    "country", "currency", "currency_trust_score", "interpretation",
                    "inflation_stability_score", "fx_stability_score",
                    "reserve_adequacy_score", "current_account_score",
                    "external_debt_score", "institutional_trust_ph",
                ]
                if c in trust.columns
            ]
        ].sort_values("currency_trust_score", ascending=False),
        hide_index=True,
        use_container_width=True,
    )


def page_dollar(ds):
    st.markdown("### Dollar Dependency")
    dep = calculate_dollar_dependency_table(
        ds["macro_country_panel"],
        ds["currency_market_structure"],
        ds.get("remittance_flows"),
        ds.get("country_sovereignty"),
    )
    cols = [c for c in [
        "country", "currency", "dollar_dependency_score", "dollar_dependency_drag_pct",
        "interpretation", "dollar_debt_share", "usd_invoicing_share", "explanation",
    ] if c in dep.columns]
    st.dataframe(dep[cols].sort_values("dollar_dependency_score", ascending=False), hide_index=True, use_container_width=True)


def page_methodology():
    st.markdown("### Methodology")
    st.markdown(
        """
**VSI = 100 × Real Usable Value Delivered / Original Value Sent**

| Component | Starter formula | Status |
|-----------|-------------------|--------|
| Explicit fee | `fee_pct` | RPW / mock |
| FX spread | `fx_margin_pct` | RPW / mock |
| Timing loss | `days × daily_vol × 0.25` | Placeholder |
| Volatility loss | `vol_30d × (1-hedge) × 0.10` | Placeholder |
| Inflation erosion | `inflation × days/365` | Macro / mock |
| Payout friction | By payout method | Manual defaults |
| Dollar drag | `dep_score/100 × 0.75%` | Sovereignty + BIS |
| Trust discount | `(100-trust)/100 × 1%` | Currency trust score |

**Interpretation bands:**
- 95–100: High value survival
- 90–95: Moderate value leakage
- 80–90: High value leakage
- below 80: Severe value destruction

**Limitations:** Measurement framework, not a trading signal. Formulas are transparent starting assumptions.
        """
    )
    st.dataframe(sources_dataframe(), hide_index=True, use_container_width=True)


def page_research():
    st.markdown("### Research Lab")
    st.dataframe(questions_dataframe(), hide_index=True, use_container_width=True)
    st.markdown("#### Working paper outline")
    st.markdown(
        """
**The Value Survival Index: Measuring How Much Value Survives When Money Crosses Borders**

1. Introduction — cross-border value translation and trust
2. Literature — remittance costs, FX frictions, dollar dominance
3. Framework — VSI components and measurement
4. Data — RPW, KNOMAD, IMF, BIS, manual sovereignty layer
5. Results — corridor rankings and welfare aggregates
6. Discussion — who bears the cost when value crosses borders?
7. Limitations — placeholders, mock data, causal claims
        """
    )
    for q in RESEARCH_QUESTIONS[:3]:
        with st.expander(q.title):
            st.write(f"**Hypothesis:** {q.hypothesis}")
            st.write(f"**Regression idea:** {q.possible_regression}")


def main():
    st.set_page_config(page_title="BR3N Value Survival Index", layout="wide", page_icon="📊")
    st.markdown(CSS, unsafe_allow_html=True)
    ds = load_vsi_data()
    _mock_banner(ds)

    page = st.sidebar.radio(
        "VSI Research Platform",
        [
            "Mission",
            "Value Survival Overview",
            "Component Breakdown",
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
        "Hidden FX Tax": lambda: page_hidden_fx_tax(ds),
        "Remittance Welfare Loss": lambda: page_welfare(ds),
        "Currency Trust": lambda: page_trust(ds),
        "Dollar Dependency": lambda: page_dollar(ds),
        "Methodology": page_methodology,
        "Research Lab": page_research,
    }
    pages[page]()


if __name__ == "__main__":
    main()
