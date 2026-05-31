"""
BR3N Settlement Economics Lab — Streamlit dashboard.

Run from settlement_lab/: streamlit run src/dashboard/app.py
Research and education only. Not financial advice.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.config.data_sources import sources_dataframe
from src.config.research_settings import LAB_LIMITATIONS, METHODOLOGY_VERSION, NO_UNLABELED_DATA
from src.data.build_dataset import build_settlement_dataset
from src.models.empirical_tests import run_empirical_tests
from src.models.robustness import run_robustness_checks
from src.models.sensitivity import run_sensitivity_analysis, sensitivity_summary
from src.models.stress_scenarios import run_stress_scenarios
from src.research.hypotheses import HYPOTHESES, hypotheses_dataframe
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
    return build_settlement_dataset()


def _banner(ds):
    flags = ds["_mock_data_flag"].iloc[0]
    mock = bool(flags.get("mock_data_flag", True))
    mixed = bool(flags.get("mixed_mode", False))
    if mock:
        st.markdown('<div class="demo-banner">⚠️ <strong>Demo mode:</strong> synthetic data. Do not use for research conclusions.</div>', unsafe_allow_html=True)
    elif mixed:
        st.markdown('<div class="demo-banner" style="background:#1f2d3d;border-color:#5b9fd4;color:#93c5fd;">ℹ️ <strong>Mixed mode:</strong> curated official/bridged data plus fallback tables. Associations only — not causal claims.</div>', unsafe_allow_html=True)


def page_mission():
    st.markdown('<p class="header">BR3N Settlement Economics Lab</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub">Measuring settlement drag, liquidity burden, finality quality, and payment-network fragility.</p>', unsafe_allow_html=True)
    st.markdown("""
**Thesis:** Modern economies do not run only on money; they run on **settlement**.

**Question:** How much value is lost, trapped, delayed, or redistributed because money does not settle instantly, universally, and with perfect finality?

Built from an institutional treasury perspective — liquidity, finality, operational flows — not trading signals.
    """)
    st.caption(f"NO_UNLABELED_DATA={NO_UNLABELED_DATA} · {METHODOLOGY_VERSION}")


def page_sdi(ds):
    st.markdown("### Settlement Drag Index")
    df = ds["settlement_drag_outputs"]
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption("SDI = 100 − min(100, drag cost per $100). Core / risk-adjusted / extended specs available.")


def page_olb(ds):
    st.markdown("### Operational Liquidity Burden")
    st.dataframe(ds["operational_liquidity_outputs"], use_container_width=True, hide_index=True)


def page_fqi(ds):
    st.markdown("### Finality Quality Index")
    st.dataframe(ds["finality_quality_outputs"], use_container_width=True, hide_index=True)


def page_pnf(ds):
    st.markdown("### Payment Network Fragility")
    st.dataframe(ds["payment_fragility_outputs"], use_container_width=True, hide_index=True)
    stress = run_stress_scenarios(ds["payment_fragility_outputs"])
    st.markdown("#### Stress scenarios")
    st.dataframe(stress, use_container_width=True, hide_index=True)


def page_pfi(ds):
    st.markdown("### Payment Friction Incidence")
    st.warning("Incidence estimates are model-based and require empirical validation.")
    st.dataframe(ds["friction_incidence_outputs"], use_container_width=True, hide_index=True)
    pfi_val = ds.get("_pfi_validation", pd.DataFrame())
    if isinstance(pfi_val, pd.DataFrame) and not pfi_val.empty:
        st.markdown("#### RPW corridor validation")
        st.dataframe(pfi_val, use_container_width=True, hide_index=True)
        within = (pfi_val["validation_status"] == "within_2pp").mean()
        st.metric("Corridors within 2pp of RPW", f"{within:.0%}")


def page_quality(ds):
    st.markdown("### Data Quality Command Center")
    val = ds["_validation"]
    st.dataframe(val, use_container_width=True, hide_index=True)
    flows = ds["payment_flow_observations"]
    st.metric("Mean data quality score", f"{flows['data_quality_score'].mean():.0f}")
    st.metric("Grade mode", flows["data_quality_grade"].mode().iloc[0] if not flows.empty else "N/A")


def page_sensitivity(ds):
    st.markdown("### Sensitivity & Robustness")
    path = OUTPUTS_DIR / "sensitivity_results.csv"
    if path.exists():
        st.dataframe(pd.read_csv(path), use_container_width=True, hide_index=True)
    else:
        st.dataframe(sensitivity_summary(run_sensitivity_analysis()), use_container_width=True, hide_index=True)
    checks = run_robustness_checks(ds["settlement_drag_outputs"], ds["operational_liquidity_outputs"], ds["finality_quality_outputs"])
    st.dataframe(checks, use_container_width=True, hide_index=True)


def page_hypotheses(ds):
    st.markdown("### Research Hypotheses")
    st.dataframe(hypotheses_dataframe(), use_container_width=True, hide_index=True)
    flags = ds["_mock_data_flag"].iloc[0]
    mock = bool(flags.get("mock_data_flag", True))
    pfi_val = ds.get("_pfi_validation", pd.DataFrame())
    emp = run_empirical_tests(ds.get("features", pd.DataFrame()), mock_flag=mock, pfi_validation=pfi_val if isinstance(pfi_val, pd.DataFrame) else None)
    if emp.get("warning"):
        st.warning(emp["warning"])
    if emp.get("pfi_validation_summary"):
        st.info(emp["pfi_validation_summary"])
    if isinstance(emp.get("pfi_validation"), pd.DataFrame) and not emp["pfi_validation"].empty:
        st.markdown("#### PFI vs RPW validation")
        st.dataframe(emp["pfi_validation"], use_container_width=True, hide_index=True)
    if not emp["tests"].empty:
        st.dataframe(emp["tests"], use_container_width=True, hide_index=True)


def page_limitations():
    st.markdown("### Limitations")
    st.markdown(f'<div class="limit">{LAB_LIMITATIONS}</div>', unsafe_allow_html=True)
    st.markdown("""
**Data limitations**
- Curated CPMI/ECB rows are public-report proxies until full BIS CPMI files are ingested.
- Finality scores map legal frameworks to ordinal research proxies — not legal opinions.
- PFI pass-through shares are model assumptions; RPW validation is descriptive only.

**Method limitations**
- Indices are associations, not causal estimates.
- Sensitivity cases change weights — rankings may shift materially.
- Mixed mode combines bridged official data with curated assumptions.
    """)


def page_glossary():
    st.markdown("### Data Glossary")
    glossary = [
        ("SDI", "Settlement Drag Index — economic cost of delayed settlement per $100 moved"),
        ("OLB", "Operational Liquidity Burden — capital trapped for settlement safety"),
        ("FQI", "Finality Quality Index — legal/operational irreversibility of settlement"),
        ("PNF", "Payment Network Fragility — stress sensitivity of payment rails"),
        ("PFI", "Payment Friction Incidence — modeled cost pass-through by actor type"),
        ("mock_data_flag", "True only for synthetic demo rows (tier 5)"),
        ("data_quality_score", "0–100 rubric; mock capped at 30"),
        ("observed_vs_estimated_flag", "Whether row is directly observed or derived"),
        ("credibility_tier", "1=official … 5=mock/demo"),
    ]
    st.dataframe(pd.DataFrame(glossary, columns=["Term", "Definition"]), use_container_width=True, hide_index=True)


def page_sources():
    st.markdown("### Data Sources")
    st.dataframe(sources_dataframe(), use_container_width=True, hide_index=True)


def page_methodology():
    st.markdown("### Methodology")
    st.markdown("See METHODOLOGY_SETTLEMENT_ECONOMICS.md and DATA_GOVERNANCE.md in repo root.")
    st.markdown(f'<div class="limit">{LAB_LIMITATIONS}</div>', unsafe_allow_html=True)


def page_working_paper():
    st.markdown("### Working Paper")
    wp = Path(__file__).resolve().parents[2] / "reports" / "working_paper"
    for name in ("abstract.md", "introduction.md", "methodology.md", "data.md", "model_results.md", "limitations.md", "next_steps.md"):
        p = wp / name
        if p.exists():
            with st.expander(name.replace(".md", "").replace("_", " ").title()):
                st.markdown(p.read_text())
    st.caption("Disciplined academic tone — associations only, not causal claims.")


def main():
    st.set_page_config(page_title="Settlement Economics Lab", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    ds = load_data()
    _banner(ds)
    pages = {
        "Mission": page_mission,
        "Settlement Drag Index": lambda: page_sdi(ds),
        "Operational Liquidity Burden": lambda: page_olb(ds),
        "Finality Quality Index": lambda: page_fqi(ds),
        "Payment Network Fragility": lambda: page_pnf(ds),
        "Payment Friction Incidence": lambda: page_pfi(ds),
        "Data Quality": lambda: page_quality(ds),
        "Sensitivity & Robustness": lambda: page_sensitivity(ds),
        "Research Hypotheses": lambda: page_hypotheses(ds),
        "Data Sources": page_sources,
        "Methodology": page_methodology,
        "Limitations": page_limitations,
        "Data Glossary": page_glossary,
        "Working Paper": page_working_paper,
    }
    choice = st.sidebar.radio("Navigation", list(pages.keys()))
    pages[choice]()
    st.caption("Research and education only · Not financial advice · Not operational payment guidance")


if __name__ == "__main__":
    main()
