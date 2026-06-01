#!/usr/bin/env python3
"""BR3N Macro Lab — unified research intelligence command center."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.dashboard.components import (
    loading_skeleton,
    render_filters_sidebar,
    sidebar_module_status,
    terminal_footer,
    warning_banner,
)
from src.dashboard.data_loader import load_all_dashboard_data
from src.dashboard.page_views import (
    render_audit,
    render_command_center,
    render_data_lake,
    render_gallery,
    render_hypotheses,
    render_methodology,
    render_sensitivity,
    render_settlement,
    render_stablecoin,
    render_value_survival,
)
from src.dashboard.styles import inject_br3n_theme

PAGES = [
    "Executive Command Center",
    "Value Survival Index",
    "Settlement Economics",
    "Stablecoin Settlement Windows",
    "Data Lake Command Center",
    "Data Quality & Audit",
    "Sensitivity & Robustness",
    "Research Hypotheses",
    "Working Paper / Methodology",
    "Visual Gallery",
]


@st.cache_data(ttl=120, show_spinner=False)
def _load_data():
    return load_all_dashboard_data()


def main() -> None:
    st.set_page_config(
        page_title="BR3N Command Center",
        page_icon="◆",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(inject_br3n_theme(), unsafe_allow_html=True)

    load_slot = st.empty()
    load_slot.markdown(loading_skeleton("Initializing research intelligence feed"), unsafe_allow_html=True)
    data = _load_data()
    load_slot.empty()

    flt = render_filters_sidebar(data)
    page = st.sidebar.radio("Navigation", PAGES, label_visibility="collapsed")
    sidebar_module_status(data.modules)

    warning_banner(
        "Research and education only. Not investment advice. Not operational payment or treasury guidance. "
        "Verify mock_data_flag and data_quality_score before citing any output.",
        "amber",
    )

    dispatch = {
        PAGES[0]: lambda: render_command_center(data, flt),
        PAGES[1]: lambda: render_value_survival(data, flt),
        PAGES[2]: lambda: render_settlement(data, flt),
        PAGES[3]: lambda: render_stablecoin(data, flt),
        PAGES[4]: lambda: render_data_lake(data),
        PAGES[5]: lambda: render_audit(data),
        PAGES[6]: lambda: render_sensitivity(data, flt),
        PAGES[7]: lambda: render_hypotheses(data),
        PAGES[8]: lambda: render_methodology(data),
        PAGES[9]: lambda: render_gallery(data),
    }
    dispatch[page]()
    terminal_footer()


if __name__ == "__main__":
    main()
