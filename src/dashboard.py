"""Streamlit dashboard — streamlit run src/dashboard.py"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "data" / "outputs"

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


def _load_csv(name: str) -> pd.DataFrame | None:
    p = OUT / name
    if p.exists():
        return pd.read_csv(p)
    return None


try:
    df, sc, detail, curves = pipeline()
except Exception as e:
    st.error(str(e))
    st.stop()

tabs = st.tabs([
    "Overview",
    "Strategy Backtest",
    "Academic Tests",
    "ML Direction Models",
    "Hedge Policy Tests",
    "Hedge Governance",
    "Flow Pressure",
    "Random-Walk Validity",
    "Research Questions",
    "Data Quality",
    "Lab Health",
    "Corridor Roadmap",
])

with tabs[0]:
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

    st.subheader("Hedge guidance")
    st.markdown(format_guidance(recommend(last["regime"], exposure)))

with tabs[1]:
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

with tabs[2]:
    fc = _load_csv("forecast_scorecard.csv")
    ac = _load_csv("academic_test_results.csv")
    if fc is None and ac is None:
        st.info("Run: `python scripts/run_research_models.py`")
    else:
        if fc is not None:
            st.subheader("Forecast scorecard")
            st.dataframe(fc, width="stretch")
            if "model_beats_rw_rmse" in fc.columns:
                row = fc.iloc[0]
                st.markdown(
                    f"**Beats random walk by RMSE:** {'Yes' if row.get('model_beats_rw_rmse') else 'No'}  \n"
                    f"**Beats random walk by MAE:** {'Yes' if row.get('model_beats_rw_mae') else 'No'}"
                )
        if ac is not None:
            st.subheader("Academic tests")
            st.dataframe(ac, width="stretch")
            dm = ac[ac["test"] == "diebold_mariano_rmse"]
            if not dm.empty:
                p = dm.iloc[0].get("p_value", "n/a")
                sig = float(p) < 0.05 if p != "n/a" and pd.notna(p) else False
                st.markdown(
                    f"**Diebold-Mariano p-value:** {p}  \n"
                    f"**Statistically significant (5%):** {'Yes' if sig else 'No'}"
                )

with tabs[3]:
    ml = _load_csv("ml_direction_model_scorecard.csv")
    if ml is None:
        st.info("Run: `python scripts/run_research_models.py`")
    else:
        st.dataframe(ml, width="stretch")
        if "directional_accuracy" in ml.columns:
            valid = ml[ml["model_name"].str.contains("direction", na=False)]
            if not valid.empty:
                best = valid.loc[valid["directional_accuracy"].astype(float).idxmax()]
                st.markdown(f"**Best ML model:** {best['model_name']} ({best['directional_accuracy']}% directional accuracy)")

with tabs[4]:
    hp = _load_csv("hedge_policy_scorecard.csv")
    if hp is None:
        st.info("Run: `python scripts/run_hedge_policy_tests.py`")
    else:
        st.dataframe(hp, width="stretch")
        best = hp.loc[hp["cost_adjusted_risk_reduction"].idxmax()]
        st.markdown(
            f"**Best policy:** {best['policy']}  \n"
            f"**Volatility reduction:** {best['volatility_reduction']}%  \n"
            f"**Hedge turnover:** {best['hedge_turnover']}  \n"
            f"**Total hedge cost:** {best['total_hedge_cost_pct']}%"
        )

with tabs[5]:
    hg = _load_csv("hedge_governance_scorecard.csv")
    if hg is None:
        st.info("Run: `python scripts/run_under_tested_research.py`")
    else:
        st.warning(
            "Simplified hedge-governance research only — not ASC 815 / IFRS 9 hedge accounting."
        )
        exp_filter = hg[hg["exposure_type"] == exposure] if "exposure_type" in hg.columns else hg
        st.dataframe(exp_filter, width="stretch")
        if not exp_filter.empty:
            best_g = exp_filter.loc[exp_filter["cost_adjusted_risk_reduction"].idxmax()]
            low_t = exp_filter.loc[exp_filter["hedge_turnover"].idxmin()]
            ncr = exp_filter[exp_filter["policy_name"] == "no_change_in_range"]
            st.markdown(
                f"**Best policy (cost-adj risk reduction):** {best_g['policy_name']} "
                f"({best_g['cost_adjusted_risk_reduction']})  \n"
                f"**Lowest turnover:** {low_t['policy_name']} ({low_t['hedge_turnover']})"
            )
            if not ncr.empty:
                rb = exp_filter[exp_filter["policy_name"] == "regime_based"]
                if not rb.empty:
                    reduced = ncr.iloc[0]["hedge_turnover"] < rb.iloc[0]["hedge_turnover"]
                    st.markdown(
                        f"**no_change_in_range turnover:** {ncr.iloc[0]['hedge_turnover']} "
                        f"(vs regime_based {rb.iloc[0]['hedge_turnover']}) — "
                        f"{'reduced' if reduced else 'not reduced'}"
                    )

with tabs[6]:
    fp = _load_csv("flow_pressure_test_results.csv")
    if fp is None:
        st.info("Run: `python scripts/run_under_tested_research.py`")
    else:
        st.dataframe(fp, width="stretch")
        row = fp.iloc[0]
        higher = row["volatility_flow_window"] > row["volatility_normal"]
        st.markdown(
            f"**Flow window avg return:** {row['average_return_flow_window']}  \n"
            f"**Normal window avg return:** {row['average_return_normal']}  \n"
            f"**Flow window volatility:** {row['volatility_flow_window']}%  \n"
            f"**Normal volatility:** {row['volatility_normal']}%  \n"
            f"**Flow window vol higher:** {'Yes' if higher else 'No'}  \n"
            f"**Return diff p-value:** {row['p_value_return_difference']} (exploratory, not causal)"
        )

with tabs[7]:
    rw = _load_csv("random_walk_validity_map.csv")
    if rw is None:
        st.info("Run: `python scripts/run_under_tested_research.py`")
    else:
        st.dataframe(rw, width="stretch")
        if "random_walk_validity_label" in rw.columns:
            rw_like = rw[rw["random_walk_validity_label"] == "Random-walk-like"]["regime"].tolist()
            structured = rw[rw["random_walk_validity_label"] == "Potential structure"]["regime"].tolist()
            st.markdown(
                f"**Random-walk-like:** {', '.join(rw_like) or 'none'}  \n"
                f"**Potential structure:** {', '.join(structured) or 'none'}"
            )

with tabs[8]:
    rq_path = ROOT / "reports" / "research_questions.md"
    if rq_path.exists():
        st.markdown(rq_path.read_text(encoding="utf-8"))
    else:
        st.warning("Missing reports/research_questions.md")

with tabs[9]:
    dq = _load_csv("data_quality_report.csv")
    reg = _load_csv("data_source_registry.csv")
    if dq is None and reg is None:
        st.info("Run: `python scripts/run_data_quality.py` and `python scripts/export_data_sources.py`")
    else:
        st.info(
            "Prototype data is acceptable for early research and dashboard development, "
            "but academic claims should use official or institutionally recognized sources where possible. "
            "Trading and hedging claims require trading-grade data such as bid/ask, forwards, spreads, "
            "and transaction costs."
        )
        if dq is not None:
            st.subheader("Data quality report")
            st.dataframe(dq, width="stretch")
            row = dq.iloc[0]
            st.markdown(
                f"**Data source:** {row.get('source_name', 'n/a')}  \n"
                f"**Tier:** {row.get('tier_number', 'n/a')} — {row.get('tier_label', row.get('data_tier', 'n/a'))}  \n"
                f"**Observations:** {row.get('observation_count', 'n/a')}  \n"
                f"**Date range:** {row.get('start_date', 'n/a')} → {row.get('end_date', 'n/a')}  \n"
                f"**Missing prices:** {row.get('missing_price_count', 'n/a')}  \n"
                f"**Suspicious returns:** {row.get('suspicious_return_count', 'n/a')}  \n"
                f"**Quality flag:** {row.get('data_quality_flag', 'n/a')}"
            )
        if reg is not None:
            st.subheader("Data source registry")
            tier_filter = st.selectbox(
                "Filter by tier",
                [
                    "all",
                    "1 — Official / academic-grade",
                    "2 — Professional market data",
                    "3 — Proprietary data",
                    "4 — Prototype data",
                ],
                key="data_tier_filter",
            )
            if tier_filter == "all":
                show = reg
            else:
                tier_num = int(tier_filter.split("—")[0].strip())
                col = "tier_number" if "tier_number" in reg.columns else "tier"
                if col == "tier_number":
                    show = reg[reg["tier_number"] == tier_num]
                else:
                    slug_map = {1: "official", 2: "professional", 3: "proprietary", 4: "prototype"}
                    show = reg[reg["tier"] == slug_map[tier_num]]
            st.dataframe(show, width="stretch")
        ds_path = ROOT / "reports" / "DATA_STRATEGY.md"
        if ds_path.exists():
            with st.expander("Full data strategy"):
                st.markdown(ds_path.read_text(encoding="utf-8"))

with tabs[10]:
    latest = OUT.parent / "runs" / "latest" / "summary.json"
    prop_path = OUT.parent / "runs" / "latest" / "proposed_experiments.csv"
    scores_path = OUT.parent / "runs" / "latest" / "dimension_scores.csv"
    if not latest.exists():
        st.info("Run: `python scripts/run_self_improvement.py`")
    else:
        import json

        summary = json.loads(latest.read_text(encoding="utf-8"))
        st.warning("Research-only self-improvement. No auto-tuning on holdout. Not investment advice.")
        st.metric("Lab health", summary.get("health", "unknown"))
        st.caption(f"Last run: {summary.get('run_id', 'n/a')}")

        if scores_path.exists():
            st.subheader("Dimension scores")
            st.dataframe(pd.read_csv(scores_path), width="stretch")

        if prop_path.exists():
            st.subheader("Proposed next experiments")
            st.dataframe(pd.read_csv(prop_path), width="stretch")

        comp = summary.get("comparison", {})
        if comp.get("has_prior"):
            st.subheader("Changes vs prior run")
            deltas = comp.get("deltas", [])
            if deltas:
                for d in deltas:
                    st.markdown(f"- **{d['dimension']}:** {d['from']} → {d['to']}")
            else:
                st.markdown("No verdict changes since prior run.")

        si_path = ROOT / "reports" / "SELF_IMPROVEMENT.md"
        if si_path.exists():
            with st.expander("How self-improvement works"):
                st.markdown(si_path.read_text(encoding="utf-8"))

with tabs[11]:
    st.info(
        "The corridor roadmap expands BR3N Macro Labs from USD/MXN into major remittance "
        "and payment corridors. These tests are exploratory and depend heavily on data quality. "
        "Public calendar proxies are not actual order-flow data."
    )
    master = _load_csv("corridor_master_scorecard.csv")
    dl = _load_csv("corridor_download_log.csv")
    fp_sum = _load_csv("corridor_flow_pressure_summary.csv")
    hg_sum = _load_csv("corridor_hedge_governance_summary.csv")
    rw_sum = _load_csv("corridor_random_walk_validity.csv")

    if master is None and dl is None:
        st.warning("Run: `python scripts/run_corridor_roadmap.py`")
    else:
        if master is not None:
            st.subheader("Strategy scorecard by corridor")
            show = master[
                [
                    c
                    for c in [
                        "corridor_id",
                        "model_pair",
                        "official_pair_label",
                        "mode",
                        "total_return",
                        "sharpe",
                        "max_drawdown",
                        "number_of_trades",
                        "observations",
                    ]
                    if c in master.columns
                ]
            ]
            st.dataframe(show, width="stretch")

        if dl is not None:
            st.subheader("Data download log")
            st.dataframe(dl, width="stretch")
            failed = dl[dl["status"] != "success"] if "status" in dl.columns else pd.DataFrame()
            if not failed.empty:
                st.warning("Some corridors failed to download — see error_message column.")

        if fp_sum is not None:
            st.subheader("Flow-pressure window effects")
            st.dataframe(fp_sum, width="stretch")

        if hg_sum is not None:
            st.subheader("Hedge governance by corridor")
            if "cost_adjusted_risk_reduction" in hg_sum.columns and "corridor_id" in hg_sum.columns:
                best = (
                    hg_sum.sort_values("cost_adjusted_risk_reduction", ascending=False)
                    .groupby("corridor_id", as_index=False)
                    .first()
                )
                st.dataframe(best, width="stretch")
            else:
                st.dataframe(hg_sum, width="stretch")

        if rw_sum is not None:
            st.subheader("Random-walk validity by corridor")
            show_rw = rw_sum[
                [
                    c
                    for c in [
                        "corridor_id",
                        "regime",
                        "random_walk_validity_label",
                        "interpretation",
                    ]
                    if c in rw_sum.columns
                ]
            ]
            st.dataframe(show_rw, width="stretch")

    cr_path = ROOT / "reports" / "corridor_roadmap_report.md"
    if cr_path.exists():
        with st.expander("Full corridor roadmap report"):
            st.markdown(cr_path.read_text(encoding="utf-8"))
