"""Streamlit dashboard — streamlit run src/dashboard.py"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import LAB_NAME
from src.backtest import build_output_frame, run_strategy_backtest, scorecard
from src.data_loader import load_config, load_or_fetch
from src.features import build_features
from src.hedging import format_guidance, recommend
from src.models import predict_regimes
from src.regimes import classify_regimes

st.set_page_config(page_title=LAB_NAME, layout="wide")
st.title(LAB_NAME)
st.caption("Research only — not investment advice.")

cfg = load_config()
exposure = st.sidebar.selectbox(
    "Exposure",
    ["us_entity_long_mxn", "mx_entity_usd_liabilities"],
    format_func=lambda x: "US long MXN" if "us_entity" in x else "MX USD liabilities",
)


@st.cache_data(ttl=3600)
def pipeline():
    prices, _ = load_or_fetch(cfg)
    feat = build_features(prices, cfg)
    feat["regime"] = predict_regimes(feat, cfg)
    sc = scorecard(feat, cfg)
    out = build_output_frame(feat, cfg, "flat_range")
    curves = {}
    for s in ["buy_and_hold", "legacy", "flat_range", "r2_only", "random_walk"]:
        bt = run_strategy_backtest(feat, cfg, s)
        curves[s] = bt["equity"]
    return feat, sc, out, curves


try:
    df, sc, detail, curves = pipeline()
except Exception as e:
    st.error(str(e))
    st.stop()

last = df.iloc[-1]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Price", f"{last['price']:.4f}")
c2.metric("Regime", last["regime"])
c3.metric("MA20", f"{last['ma20']:.4f}")
c4.metric("MA60", f"{last['ma60']:.4f}")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df["price"], name="Price"))
fig.add_trace(go.Scatter(x=df.index, y=df["ma20"], name="MA20"))
fig.add_trace(go.Scatter(x=df.index, y=df["ma60"], name="MA60"))
fig.update_layout(title="Price & MAs", height=380)
st.plotly_chart(fig, width="stretch")

fig2 = go.Figure()
for name, eq in curves.items():
    fig2.add_trace(go.Scatter(x=eq.index, y=eq, name=name))
fig2.update_layout(title="Equity curves (net of costs)", height=380)
st.plotly_chart(fig2, width="stretch")

st.subheader("Scorecard")
st.dataframe(sc, width="stretch")

st.subheader("Return by regime (flat_range net, bps/day)")
attrib = detail.groupby("regime")["net_strategy_return"].mean().mul(10000).round(2)
st.dataframe(attrib.rename("bps").to_frame(), width="stretch")

st.subheader("Hedge guidance")
st.markdown(format_guidance(recommend(last["regime"], exposure)))
