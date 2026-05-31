"""
BR3N Global FX & Remittance Research Lab — Streamlit Dashboard

Mission: Who bears the cost when value crosses borders?

Run: streamlit run src/global_fx_research_lab.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config.data_sources import sources_dataframe
from src.indices.pipeline import run_all_indices, save_index_outputs
from src.models.global_fx_models import full_model_lab_report, corridor_clustering_features
from src.research.questions import RESEARCH_QUESTIONS, questions_dataframe
from src.research.report_generator import WORKING_PAPER_ABSTRACT, WORKING_PAPER_TITLE
from src.utils.paths import OUTPUTS_DIR, REPORTS_DIR

DISCLAIMER = (
    "**Research and education only.** Not financial advice. "
    "Mock data is used when real World Bank/IMF/BIS files are absent — clearly labelled below."
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600&family=Source+Sans+3:wght@400;600&display=swap');
.gfx-header{background:linear-gradient(180deg,#0d1219,#121a28);border:1px solid #2a3548;border-radius:8px;padding:1.5rem;margin-bottom:1rem}
.gfx-title{font-family:'Cormorant Garamond',serif;color:#e8edf4;font-size:1.75rem;font-weight:600}
.gfx-sub{color:#5b9fd4;font-size:0.95rem;margin-top:0.35rem}
.gfx-q{color:#94a3b8;font-style:italic;margin-top:0.75rem;font-size:1rem}
.warn{background:#1a2436;border-left:4px solid #5b9fd4;padding:0.75rem 1rem;border-radius:4px;color:#94a3b8;margin:1rem 0}
</style>
"""


@st.cache_data(show_spinner="Computing flagship indices…")
def load_indices():
    idx = run_all_indices()
    save_index_outputs(idx)
    return idx


def page_mission():
    st.markdown(
        f'<div class="gfx-header"><div class="gfx-title">BR3N Global FX & Remittance Research Lab</div>'
        f'<div class="gfx-sub">Foreign exchange as the global translation layer of value</div>'
        f'<div class="gfx-q">Who bears the cost when value crosses borders?</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="warn">{DISCLAIMER}</div>', unsafe_allow_html=True)
    st.markdown(f"### Working Paper: *{WORKING_PAPER_TITLE}*")
    st.markdown(WORKING_PAPER_ABSTRACT)
    st.markdown("#### Flagship Indices")
    st.markdown(
        """
1. **Hidden FX Tax Index** — full cross-border conversion burden
2. **Remittance Welfare Loss Index** — purchasing power destroyed
3. **Currency Credibility Index** — national monetary credibility
4. **Dollar Dependency Index** — USD infrastructure reliance
5. **Labor Conversion Index** — global repricing of human labor
6. **Currency Stress Index** — crises of belief
"""
    )
    st.dataframe(questions_dataframe(), use_container_width=True, hide_index=True)


def page_hidden_fx_tax(idx):
    st.markdown("### Hidden FX Tax Index")
    df = idx["hidden_fx_tax"]
    if df.empty:
        st.warning("No data.")
        return
    latest = df.sort_values("date").groupby("corridor", as_index=False).tail(1)
    latest = latest.sort_values("hidden_fx_tax_pct", ascending=False)
    st.markdown("**Interpretation:** Higher index = greater hidden burden on cross-border value transfer.")
    st.dataframe(
        latest[["corridor", "hidden_fx_tax_pct", "hidden_fx_tax_index_0_100", "interpretation", "rank"]].head(10),
        hide_index=True,
        use_container_width=True,
    )
    top = latest.head(10)
    fig = go.Figure()
    for col, name, color in [
        ("fee_pct", "Fee", "#5b9fd4"),
        ("fx_margin_pct", "FX margin", "#94a3b8"),
        ("timing_risk_pct", "Timing", "#3d9970"),
        ("volatility_penalty_pct", "Volatility", "#c9a227"),
    ]:
        if col in top.columns:
            fig.add_trace(go.Bar(name=name, x=top["corridor"], y=top[col], marker_color=color))
    fig.update_layout(barmode="stack", template="plotly_dark", title="Component breakdown — top corridors", height=420)
    st.plotly_chart(fig, use_container_width=True)


def page_welfare(idx):
    st.markdown("### Remittance Welfare Loss")
    df = idx["remittance_welfare"]
    if df.empty:
        return
    agg = df.groupby("corridor", as_index=False).agg(
        remittance_usd=("remittance_usd", "sum"),
        aggregate_welfare_loss_usd=("aggregate_welfare_loss_usd", "sum"),
        welfare_loss_pct=("welfare_loss_pct", "mean"),
    ).sort_values("aggregate_welfare_loss_usd", ascending=False)
    st.dataframe(agg.head(10), hide_index=True, use_container_width=True)
    fig = px.bar(
        agg.head(8),
        x="corridor",
        y="aggregate_welfare_loss_usd",
        title="Estimated aggregate annual welfare loss (mock volumes)",
        template="plotly_dark",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Chart interpretation: corridors with high volume AND high hidden tax dominate aggregate welfare loss.")


def page_credibility(idx):
    st.markdown("### Currency Credibility")
    df = idx["currency_credibility"].sort_values("credibility_score", ascending=False)
    st.dataframe(
        df[["country", "currency", "credibility_score", "interpretation", "inflation_score", "reserve_score"]],
        hide_index=True,
        use_container_width=True,
    )


def page_dollar(idx):
    st.markdown("### Dollar Dependency")
    df = idx["dollar_dependency"].sort_values("dollar_dependency_score", ascending=False)
    st.dataframe(
        df[["country", "currency", "dollar_dependency_score", "interpretation", "remittance_dependence"]],
        hide_index=True,
        use_container_width=True,
    )
    st.caption("Dollar exposure uses `data/raw/manual/country_sovereignty.csv` research estimates where available.")


def page_labor(idx):
    st.markdown("### Labor Conversion")
    df = idx["labor_conversion"].sort_values("ppp_adjusted_labor_value", ascending=False)
    st.dataframe(
        df[["country", "local_hourly_wage", "global_labor_value_usd", "remittance_adjusted_labor_value", "interpretation"]],
        hide_index=True,
        use_container_width=True,
    )
    fig = px.bar(
        df,
        x="country",
        y=["global_labor_value_usd", "remittance_adjusted_labor_value"],
        barmode="group",
        title="Hourly labor value: global vs remittance-adjusted",
        template="plotly_dark",
    )
    st.plotly_chart(fig, use_container_width=True)


def page_stress(idx):
    st.markdown("### Currency Stress Monitor")
    df = idx["currency_stress"].sort_values("stress_score", ascending=False)
    st.dataframe(
        df[["country", "currency", "stress_score", "regime", "drivers", "explanation"]],
        hide_index=True,
        use_container_width=True,
    )
    crisis = df[df["regime"].isin(["stressed", "crisis"])]
    if not crisis.empty:
        st.warning(f"Watchlist: {', '.join(crisis['country'].tolist())}")


def page_model_lab(idx):
    st.markdown("### Research Model Lab")
    report = full_model_lab_report(idx)
    st.markdown("#### Panel regression (corridor + year FE)")
    st.json(report["panel_regression"])
    st.markdown("#### DXY surge event study")
    st.json(report["dxy_event_study"])
    st.markdown("#### Corridor / country clustering")
    cl = pd.DataFrame(report["clustering"])
    if not cl.empty:
        st.dataframe(cl, use_container_width=True, hide_index=True)
    st.markdown("#### Stress forecast (walk-forward OOS)")
    st.json(report["stress_forecast"])
    with st.expander("In-sample logistic (reference only)"):
        st.json(report["stress_forecast_in_sample"])
    st.markdown("**Limitations:** Mixed/curated data; in-sample models; not for trading or policy without validation.")


def page_data(idx):
    st.markdown("### Data Sources & Methods")
    st.dataframe(sources_dataframe(), use_container_width=True, hide_index=True)
    st.markdown(
        """
**Where to put real data:**
| Folder | Source |
|--------|--------|
| `data/raw/world_bank_rpw/` | Remittance Prices Worldwide CSV/Excel |
| `data/raw/world_bank_knomad/` | KNOMAD bilateral remittance matrix |
| `data/raw/imf/` | IMF exchange rates & IFS/WEO |
| `data/raw/bis/` | BIS triennial FX turnover |
| `data/raw/fred/` | FRED exports (optional) |
| `data/raw/manual/` | Wages, policy rates, sovereignty / dollar exposure |
"""
    )
    st.info("⚠️ Mock data active unless files found in folders above.")


def main():
    st.set_page_config(page_title="BR3N Global FX Lab", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    idx = load_indices()
    page = st.sidebar.radio(
        "Research Lab",
        [
            "Mission",
            "Hidden FX Tax",
            "Remittance Welfare",
            "Currency Credibility",
            "Dollar Dependency",
            "Labor Conversion",
            "Currency Stress",
            "Model Lab",
            "Data & Methods",
        ],
    )
    pages = {
        "Mission": page_mission,
        "Hidden FX Tax": lambda: page_hidden_fx_tax(idx),
        "Remittance Welfare": lambda: page_welfare(idx),
        "Currency Credibility": lambda: page_credibility(idx),
        "Dollar Dependency": lambda: page_dollar(idx),
        "Labor Conversion": lambda: page_labor(idx),
        "Currency Stress": lambda: page_stress(idx),
        "Model Lab": page_model_lab,
        "Data & Methods": lambda: page_data(idx),
    }
    if page == "Model Lab":
        page_model_lab(idx)
    else:
        pages[page]()


if __name__ == "__main__":
    main()
