"""
BR3N Macro Labs — FX Research Terminal

Institutional-grade local-first FX research dashboard.
Research and education only. Not investment advice. No live trading.

Run: streamlit run src/fx_research_terminal.py
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

from src.backtesting.walk_forward import run_model_comparison
from src.data.constants import CORE_FX_PAIRS, PAIR_LABELS, TERMINAL_CORRIDORS, pair_label
from src.data.pipeline import build_terminal_data_bundle
from src.features.fx_terminal_features import FEATURE_COLUMNS, build_multi_pair_feature_table
from src.llm.classifiers import classify_central_bank_tone, classify_news_event, sanity_check_model_signal
from src.llm.memo_generator import generate_trade_memo
from src.llm.ollama_client import OllamaClient
from src.models.baselines import MomentumBaseline, get_baseline_models, signals_to_dataframe
from src.risk.position_risk import assess_trade_risk
from src.risk.regime import classify_fx_regime
from src.utils.config import load_terminal_config
from src.utils.paths import OUTPUTS_DIR, TRADE_MEMOS_DIR

DISCLAIMER = (
    "**Research and education only.** Not financial advice. FX trading involves substantial risk. "
    "Backtests are not guarantees. Models may be wrong, overfit, stale, or affected by missing data. "
    "Validate against real market data, transaction costs, liquidity, and risk limits."
)

TERMINAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&display=swap');
.terminal-header {
  background: linear-gradient(180deg, #0d1219 0%, #121a28 100%);
  border: 1px solid #2a3548;
  border-radius: 8px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1rem;
}
.terminal-title { color: #e8edf4; font-size: 1.6rem; font-weight: 600; }
.terminal-sub { color: #5b9fd4; font-size: 0.9rem; letter-spacing: 0.05em; }
.metric-card-t {
  background: #121a28;
  border: 1px solid #2a3548;
  border-radius: 6px;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
}
.metric-card-t .label { color: #94a3b8; font-size: 0.72rem; text-transform: uppercase; }
.metric-card-t .value { color: #e8edf4; font-size: 1.1rem; font-weight: 600; }
.warn-t { background: #1a2436; border-left: 4px solid #5b9fd4; padding: 0.75rem 1rem; border-radius: 4px; color: #94a3b8; }
</style>
"""


@st.cache_data(show_spinner="Loading FX data…")
def load_terminal_state(use_mock: bool = True):
    cfg = load_terminal_config()
    bundle = build_terminal_data_bundle(cfg, use_mock_on_failure=use_mock)
    features = build_multi_pair_feature_table(
        bundle.market, bundle.macro, bundle.rates, bundle.sentiment, pairs=CORE_FX_PAIRS
    )
    comparison_path = OUTPUTS_DIR / "terminal_model_comparison.csv"
    comparison = pd.read_csv(comparison_path) if comparison_path.exists() else pd.DataFrame()
    return cfg, bundle, features, comparison


def page_overview(features: pd.DataFrame, bundle) -> None:
    st.markdown("### FX Overview")
    latest = features.sort_values("date").groupby("pair").tail(1).copy()
    if latest.empty:
        st.warning("No feature data available.")
        return

    rows = []
    for _, r in latest.iterrows():
        pair = r["pair"]
        regime_row = r.copy()
        if not bundle.macro.empty:
            m = bundle.macro.sort_values("date").iloc[-1]
            for c in m.index:
                if c not in regime_row.index:
                    regime_row[c] = m[c]
        regime = classify_fx_regime(regime_row)
        mom = MomentumBaseline()
        X = r[FEATURE_COLUMNS].fillna(0).to_frame().T
        meta = pd.DataFrame([{"pair": pair, "date": r["date"]}])
        sig = mom.predict_signals(X, meta)[0]
        rows.append(
            {
                "Pair": pair_label(pair),
                "Spot": f"{r['spot']:.4f}",
                "5d Mom": f"{r.get('ret_5d', 0):.2%}",
                "20d Mom": f"{r.get('ret_20d', 0):.2%}",
                "60d Mom": f"{r.get('ret_60d', 0):.2%}",
                "Carry": f"{r.get('carry_score', 0):.2f}",
                "Vol 20d": f"{r.get('vol_20d', 0):.2%}",
                "Signal": sig.signal,
                "Conf": f"{sig.confidence:.0%}",
                "Regime": regime.current_regime,
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def page_pair_detail(features: pd.DataFrame, bundle, pair: str) -> None:
    st.markdown(f"### {pair_label(pair)}")
    sub = features[features["pair"] == pair].sort_values("date")
    if sub.empty:
        st.warning("No data for this pair.")
        return
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sub["date"], y=sub["spot"], name="Spot", line=dict(color="#5b9fd4")))
    if "ma20" in sub.columns:
        fig.add_trace(go.Scatter(x=sub["date"], y=sub["ma20"], name="MA20", line=dict(color="#94a3b8", dash="dot")))
    if "ma60" in sub.columns:
        fig.add_trace(go.Scatter(x=sub["date"], y=sub["ma60"], name="MA60", line=dict(color="#3d9970", dash="dot")))
    fig.update_layout(template="plotly_dark", height=380, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)

    latest = sub.iloc[-1]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vol 20d", f"{latest.get('vol_20d', 0):.2%}")
    c2.metric("Rate diff", f"{latest.get('rate_differential', 0):.2f}")
    c3.metric("Carry score", f"{latest.get('carry_score', 0):.2f}")
    c4.metric("Drawdown 60d", f"{latest.get('drawdown_60d', 0):.2%}")

    regime_row = latest.copy()
    if not bundle.macro.empty:
        m = bundle.macro.sort_values("date").iloc[-1]
        regime_row = pd.concat([regime_row, m])
    regime = classify_fx_regime(regime_row)

    model = get_baseline_models()[2]  # carry baseline quick signal
    X = latest[FEATURE_COLUMNS].fillna(0).to_frame().T
    meta = pd.DataFrame([{"pair": pair, "date": latest["date"]}])
    sig = model.predict_signals(X, meta)[0]
    risk = assess_trade_risk(
        entry=float(latest["spot"]),
        direction=sig.signal if sig.signal != "neutral" else "long",
        confidence=sig.confidence,
        expected_return=sig.expected_return,
        vol_20d=float(latest.get("vol_20d", 0.1) or 0.1),
        carry_score=float(latest.get("carry_score", 0) or 0),
        regime=regime,
    )
    st.markdown("**Risk parameters**")
    st.json(
        {
            "signal": sig.signal,
            "probability_up": sig.probability_up,
            "stop_loss": risk.stop_loss,
            "take_profit": risk.take_profit,
            "position_size": risk.suggested_position_size,
            "reward_risk": risk.reward_risk_ratio,
            "decision": risk.trade_decision,
            "notes": risk.risk_notes,
        }
    )

    if st.button("Generate trade memo (Ollama)", key=f"memo_{pair}"):
        memo = generate_trade_memo(
            {
                "pair": pair_label(pair),
                "direction": sig.signal,
                "horizon": 5,
                "model_name": sig.model_name,
                "probability_up": sig.probability_up,
                "expected_return": sig.expected_return,
                "confidence": sig.confidence,
                "regime": regime.current_regime,
                "regime_description": regime.regime_description,
                "carry_score": latest.get("carry_score", 0),
                "ret_20d": latest.get("ret_20d", 0),
                "vol_20d": latest.get("vol_20d", 0),
                "stop_loss": risk.stop_loss,
                "take_profit": risk.take_profit,
                "reward_risk": risk.reward_risk_ratio,
                "trade_decision": risk.trade_decision,
            }
        )
        st.markdown(memo)


def page_corridors(features: pd.DataFrame) -> None:
    st.markdown("### Remittance Corridors")
    rows = []
    for cid, c in TERMINAL_CORRIDORS.items():
        pair = c["model_pair"]
        sub = features[features["pair"] == pair]
        if sub.empty:
            trend = vol = carry = "N/A"
        else:
            last = sub.sort_values("date").iloc[-1]
            trend = f"{last.get('ret_20d', 0):.2%}"
            vol = f"{last.get('vol_20d', 0):.2%}"
            carry = f"{last.get('carry_score', 0):.2f}"
        rows.append(
            {
                "Corridor": c["label"],
                "Pair": pair_label(pair),
                "20d Trend": trend,
                "Volatility": vol,
                "Carry backdrop": carry,
                "Notes": c.get("data_warning", "Research proxy only."),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def page_model_lab(features: pd.DataFrame, comparison: pd.DataFrame) -> None:
    st.markdown("### Model Lab")
    if comparison.empty:
        if st.button("Run walk-forward comparison (may take a minute)"):
            with st.spinner("Running…"):
                _, comp = run_model_comparison(features, pairs=CORE_FX_PAIRS[:3], horizon=5)
                st.session_state["terminal_comparison"] = comp
                st.rerun()
        comp = st.session_state.get("terminal_comparison", pd.DataFrame())
    else:
        comp = comparison
    if not comp.empty:
        st.dataframe(comp, use_container_width=True, hide_index=True)
        fig = px.bar(
            comp,
            x="model",
            y="hit_rate",
            color="pair",
            barmode="group",
            title="Hit rate by model and pair (OOS walk-forward)",
            template="plotly_dark",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run `python scripts/run_fx_research_terminal.py` to generate comparison report.")


def page_news_lab() -> None:
    st.markdown("### News / Central Bank Lab")
    client = OllamaClient()
    ollama_ok = client.is_available()
    st.caption(f"Ollama: {'connected' if ollama_ok else 'offline — memos will show setup instructions'}")

    tab_cb, tab_news, tab_sanity = st.tabs(["Central Bank", "News", "Model Sanity Check"])
    with tab_cb:
        text = st.text_area("Central bank statement excerpt", height=120)
        if st.button("Classify tone") and text.strip():
            st.markdown(classify_central_bank_tone(text, client))
    with tab_news:
        headline = st.text_input("News headline")
        if st.button("Classify event") and headline.strip():
            st.markdown(classify_news_event(headline, client))
    with tab_sanity:
        pair = st.selectbox("Pair", CORE_FX_PAIRS, format_func=pair_label)
        signal = st.selectbox("Signal", ["long", "short", "neutral"])
        prob = st.slider("Probability up", 0.0, 1.0, 0.55)
        if st.button("Sanity check"):
            st.markdown(
                sanity_check_model_signal(
                    {"pair": pair_label(pair), "signal": signal, "probability_up": prob, "features": {"ret_20d": 0.01}},
                    client,
                )
            )


def main() -> None:
    st.set_page_config(page_title="BR3N FX Research Terminal", layout="wide", page_icon="📊")
    st.markdown(TERMINAL_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="terminal-header"><div class="terminal-title">BR3N FX Research Terminal</div>'
        '<div class="terminal-sub">Statistical models · Regime analysis · LLM research layer</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="warn-t">{DISCLAIMER}</div>', unsafe_allow_html=True)

    cfg, bundle, features, comparison = load_terminal_state()
    page = st.sidebar.radio(
        "Terminal",
        ["FX Overview", "Pair Detail", "Corridors", "Model Lab", "News / CB Lab"],
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Pairs: " + ", ".join(pair_label(p) for p in CORE_FX_PAIRS[:5]) + "…")
    if page == "FX Overview":
        page_overview(features, bundle)
    elif page == "Pair Detail":
        sel = st.selectbox("Select pair", CORE_FX_PAIRS, format_func=pair_label)
        page_pair_detail(features, bundle, sel)
    elif page == "Corridors":
        page_corridors(features)
    elif page == "Model Lab":
        page_model_lab(features, comparison)
    elif page == "News / CB Lab":
        page_news_lab()

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Trade memos: {TRADE_MEMOS_DIR}")


if __name__ == "__main__":
    main()
