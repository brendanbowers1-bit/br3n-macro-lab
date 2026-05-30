"""Research note — readable publication view."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import LAB_NAME

PUB = ROOT / "reports" / "publication"
LADDER = ROOT / "reports" / "research_ladder"

st.set_page_config(page_title=f"{LAB_NAME} · Research", layout="wide")
st.title("Research publication")
st.caption(f"{LAB_NAME} · Not investment advice")

tab1, tab2, tab3 = st.tabs(["One-pager", "Full memo", "Ladder data"])

with tab1:
    path = PUB / "ONE_PAGER.md"
    if path.exists():
        st.markdown(path.read_text(encoding="utf-8"))
    else:
        st.warning("Run: `python scripts/build_publication.py`")

with tab2:
    path = PUB / "FX_REGIME_RESEARCH_NOTE.md"
    if path.exists():
        st.markdown(path.read_text(encoding="utf-8"))
    else:
        st.warning("Run: `python scripts/build_publication.py`")

with tab3:
    st.markdown("#### OOS by pair")
    oos = LADDER / "level3_oos_by_pair.csv"
    if oos.exists():
        import pandas as pd

        st.dataframe(pd.read_csv(oos), width="stretch")
    st.markdown("#### White Reality Check")
    wrc = LADDER / "level6_white_reality_check.csv"
    if wrc.exists():
        import pandas as pd

        st.dataframe(pd.read_csv(wrc), width="stretch")

st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Static site**")
    st.code("python scripts/build_site.py --open", language="bash")
with col2:
    st.markdown("**Local server**")
    st.code("python scripts/serve_publication.py", language="bash")
with col3:
    st.markdown("**Files**")
    st.markdown(f"`{PUB}`")
