"""
BR3N Stablecoin Settlement Window Lab — Streamlit dashboard.

Run from stablecoin_lab/: streamlit run src/dashboard/app.py
Research and education only. Not financial advice.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.config.data_sources import sources_dataframe
from src.config.research_settings import LAB_LIMITATIONS, METHODOLOGY_VERSION, NO_UNLABELED_DATA
from src.data.build_dataset import build_stablecoin_dataset
from src.models.empirical_tests import run_empirical_tests
from src.models.robustness import run_robustness_checks
from src.models.sensitivity import run_sensitivity_analysis, sensitivity_summary
from src.research.hypotheses import FLAGSHIP_QUESTIONS, hypotheses_dataframe
from src.utils.paths import OUTPUTS_DIR

CSS = """
<style>
.stApp { background-color: #0a0e14 !important; color: #e8edf4 !important; }
.demo-banner { background:#3d1f1f; border:1px solid #c44; padding:0.75rem; color:#fca5a5; margin-bottom:1rem; }
.header { color:#5b9fd4; font-size:2rem; font-weight:600; }
.sub { color:#94a3b8; }
.limit { background:#121a28; border:1px solid #2a3548; padding:0.75rem; color:#94a3b8; font-size:0.9rem; }
</style>
"""


@st.cache_data
def load_data():
    return build_stablecoin_dataset()


def _banner(ds: dict) -> None:
    flags = ds["_mock_data_flag"].iloc[0]
    mock = bool(flags.get("mock_data_flag", True))
    mixed = bool(flags.get("mixed_mode", False))
    if mock:
        st.markdown(
            '<div class="demo-banner">⚠️ <strong>Demo mode:</strong> synthetic data. '
            "Do not use for research conclusions.</div>",
            unsafe_allow_html=True,
        )
    elif mixed:
        st.markdown(
            '<div class="demo-banner" style="background:#1f2d3d;border-color:#5b9fd4;color:#93c5fd;">'
            "ℹ️ <strong>Mixed mode:</strong> curated official/bridged data plus fallback tables. "
            "Associations only — not causal claims.</div>",
            unsafe_allow_html=True,
        )


def _limitations_caption(extra: str = "") -> None:
    text = LAB_LIMITATIONS
    if extra:
        text = f"{extra} · {LAB_LIMITATIONS}"
    st.caption(text)


def _show_table(df: pd.DataFrame, extra_limitation: str = "") -> None:
    if df.empty:
        st.info("No rows available for this view.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
    _limitations_caption(extra_limitation)


def page_mission() -> None:
    st.markdown('<p class="header">BR3N Stablecoin Settlement Window Lab</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub">When settlement windows collapse toward zero, where does risk go?</p>',
        unsafe_allow_html=True,
    )
    st.markdown("""
**Core thesis:** Stablecoins do not eliminate settlement risk; they change its location, speed, and legal form.

**Deeper thesis:** When money settles instantly, trust must settle somewhere else.

**Master question:** When settlement windows collapse toward zero, where does risk go?

Built from an institutional treasury perspective — ledger finality vs economic finality, reserve liquidity,
compliance drag, off-ramp frictions, and digital run conditions — not trading signals.
    """)
    st.markdown("#### Flagship research questions")
    for q in FLAGSHIP_QUESTIONS:
        st.markdown(f"- {q}")
    st.caption(f"NO_UNLABELED_DATA={NO_UNLABELED_DATA} · {METHODOLOGY_VERSION}")
    _limitations_caption()


def page_finality_quality(ds: dict) -> None:
    st.markdown("### Stablecoin Finality Quality Index (SFQI)")
    st.markdown(
        "Separates **ledger confirmation** from **economic finality** "
        "(redemption, compliance, off-ramp, legal enforceability)."
    )
    df = ds["stablecoin_finality_quality_outputs"]
    _show_table(df, "SFQI is a composite proxy — not a legal opinion on finality.")


def page_settlement_window_compression(ds: dict) -> None:
    st.markdown("### Settlement Window Compression (SWC)")
    st.markdown("Net compression benefit vs risk redistribution when traditional windows collapse to chain speed.")
    df = ds["settlement_window_compression_outputs"]
    _show_table(
        df,
        "Faster ledger settlement may increase liquidity pressure and run-speed fragility under this spec.",
    )


def page_liquidity_transformation(ds: dict) -> None:
    st.markdown("### Stablecoin Liquidity Transformation (SLT)")
    st.markdown("Whether stablecoins reduce user liquidity risk or relocate it to issuers and reserve markets.")
    df = ds["liquidity_transformation_outputs"]
    _show_table(df, "Reserve composition scores may lag attestations; not causal proof of risk transfer.")


def page_digital_run_velocity(ds: dict) -> None:
    st.markdown("### Digital Run Velocity (DRV)")
    st.warning("Run-velocity scores describe risk **conditions**, not run predictions or probabilities.")
    df = ds["digital_run_velocity_outputs"]
    _show_table(df, "Does not predict redemption timing, magnitude, or probability.")


def page_dollarization(ds: dict) -> None:
    st.markdown("### Stablecoin Dollarization Index")
    st.markdown("Retail digital dollar dependence outside traditional banking — macro pressure composite.")
    df = ds["stablecoin_dollarization_outputs"]
    _show_table(df, "Usage proxies are coarse; reverse causality from dollarization to adoption is possible.")


def page_singleness(ds: dict) -> None:
    st.markdown("### Tokenized Money Singleness Index")
    st.markdown("Parity across private tokenized dollars under stated stress assumptions.")
    df = ds["tokenized_money_singleness_outputs"]
    _show_table(df, "Does not prove parity holds in live market stress without observed depeg events.")


def page_compliance_drag(ds: dict) -> None:
    st.markdown("### Compliance Settlement Drag")
    st.markdown("Compliance, off-ramp, and redemption delay as the real settlement window beyond ledger time.")
    df = ds["compliance_settlement_drag_outputs"]
    _show_table(df, "Compliance delays are institution-specific; thin cross-section on official data.")


def page_value_survival(ds: dict) -> None:
    st.markdown("### Stablecoin Value Survival Index (SVSI)")
    st.markdown("Usable local purchasing power on stablecoin remittance rails vs traditional corridors.")
    df = ds["stablecoin_value_survival_outputs"]
    _show_table(df, "Does not assume stablecoins are cheaper — measures value survival under stated frictions.")


def page_quality(ds: dict) -> None:
    st.markdown("### Data Quality Command Center")
    val = ds["_validation"]
    _show_table(val, "Mock data capped at quality score 30 — demo only.")
    supply = ds.get("stablecoin_supply", pd.DataFrame())
    if not supply.empty and "data_quality_score" in supply.columns:
        st.metric("Mean supply data quality score", f"{supply['data_quality_score'].mean():.0f}")
        if "data_quality_grade" in supply.columns:
            st.metric("Supply grade mode", supply["data_quality_grade"].mode().iloc[0])


def page_sensitivity(ds: dict) -> None:
    st.markdown("### Sensitivity & Robustness")
    path = OUTPUTS_DIR / "sensitivity_results.csv"
    if path.exists():
        sens = pd.read_csv(path)
        st.dataframe(sens, use_container_width=True, hide_index=True)
    else:
        sens = run_sensitivity_analysis(ds)
        st.dataframe(sens, use_container_width=True, hide_index=True)
        summary = sensitivity_summary(sens)
        if not summary.empty:
            st.markdown("#### Score range by entity")
            st.dataframe(summary, use_container_width=True, hide_index=True)

    checks = run_robustness_checks(
        ds["stablecoin_finality_quality_outputs"],
        svsi=ds.get("stablecoin_value_survival_outputs"),
        csd=ds.get("compliance_settlement_drag_outputs"),
        swc=ds.get("settlement_window_compression_outputs"),
        dollarization=ds.get("stablecoin_dollarization_outputs"),
    )
    st.markdown("#### Robustness checks")
    st.dataframe(checks, use_container_width=True, hide_index=True)
    _limitations_caption("Sensitivity cases change assumptions — rankings may shift materially.")


def page_hypotheses(ds: dict) -> None:
    st.markdown("### Research Hypotheses")
    st.dataframe(hypotheses_dataframe(), use_container_width=True, hide_index=True)
    flags = ds["_mock_data_flag"].iloc[0]
    mock = bool(flags.get("mock_data_flag", True))
    emp = run_empirical_tests(ds.get("features", pd.DataFrame()), mock_flag=mock)
    if emp.get("warning"):
        st.warning(emp["warning"])
    if emp.get("limitations"):
        st.info(emp["limitations"])
    if not emp["tests"].empty:
        st.markdown("#### Exploratory association tests")
        st.dataframe(emp["tests"], use_container_width=True, hide_index=True)
    _limitations_caption("Hypotheses are associations only — not causal identification.")


def page_sources() -> None:
    st.markdown("### Data Sources")
    st.dataframe(sources_dataframe(), use_container_width=True, hide_index=True)
    _limitations_caption("Tier 5 (mock) sources must never support research conclusions.")


def page_working_paper() -> None:
    st.markdown("### Working Paper")
    st.markdown(
        "**When Settlement Windows Collapse: Stablecoins, Finality, and the Redistribution of Payment Risk**"
    )
    wp = Path(__file__).resolve().parents[2] / "reports" / "working_paper"
    sections = (
        "abstract",
        "introduction",
        "literature_map",
        "theory",
        "methodology",
        "data",
        "model_results",
        "limitations",
        "next_steps",
    )
    for name in sections:
        p = wp / f"{name}.md"
        if p.exists():
            with st.expander(name.replace("_", " ").title()):
                st.markdown(p.read_text())
    _limitations_caption("Working paper stubs — associations only, not causal claims.")


def main() -> None:
    st.set_page_config(page_title="Stablecoin Settlement Window Lab", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    ds = load_data()
    _banner(ds)
    pages = {
        "Mission": page_mission,
        "Finality Quality": lambda: page_finality_quality(ds),
        "Settlement Window Compression": lambda: page_settlement_window_compression(ds),
        "Liquidity Transformation": lambda: page_liquidity_transformation(ds),
        "Digital Run Velocity": lambda: page_digital_run_velocity(ds),
        "Stablecoin Dollarization": lambda: page_dollarization(ds),
        "Tokenized Money Singleness": lambda: page_singleness(ds),
        "Compliance Settlement Drag": lambda: page_compliance_drag(ds),
        "Stablecoin Value Survival": lambda: page_value_survival(ds),
        "Data Quality Command Center": lambda: page_quality(ds),
        "Sensitivity and Robustness": lambda: page_sensitivity(ds),
        "Research Hypotheses": lambda: page_hypotheses(ds),
        "Data Sources": page_sources,
        "Working Paper": page_working_paper,
    }
    choice = st.sidebar.radio("Navigation", list(pages.keys()))
    pages[choice]()
    st.caption("Research and education only · Not financial advice · Not investment recommendation")


if __name__ == "__main__":
    main()
