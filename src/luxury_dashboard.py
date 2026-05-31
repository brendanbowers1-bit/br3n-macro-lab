"""
BR3N Macro Labs — Luxury Research Terminal Dashboard

Research-only. Not investment advice. No live trading.

Run: streamlit run src/luxury_dashboard.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data" / "outputs"
PROC = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
FX_LOGO = REPORTS / "publication" / "assets" / "br3n_macro_labs_logo.png"
BRAND_MOTTO = "Research. Regime. Risk."

# ── Brand palette (academic institutional) ────────────────────────────────────
C = {
    "bg": "#f7f5f0",
    "panel": "#ffffff",
    "sidebar": "#1e3a5f",
    "sidebar_text": "#e8edf4",
    "border": "#d4dce8",
    "text": "#1a2744",
    "text2": "#5c6578",
    "muted": "#7a8496",
    "navy": "#1e3a5f",
    "gold": "#1e3a5f",
    "bronze": "#7a6342",
    "cyan": "#2c5282",
    "green": "#1f6b4a",
    "amber": "#9a6700",
    "red": "#9b2c2c",
    "purple": "#4a5568",
}

REGIME_COLORS = {
    "R1_trend_high_vol": "#EF4444",
    "R2_trend_low_vol": "#D4AF37",
    "R3_range_high_vol": "#A78BFA",
    "R4_range_low_vol": "#64748B",
}

RW_COLORS = {
    "Random-walk-like": "#22C55E",
    "Potential structure": "#D4AF37",
    "High-risk noise": "#EF4444",
}

PLOTLY_LAYOUT = dict(
    template="simple_white",
    paper_bgcolor=C["bg"],
    plot_bgcolor=C["panel"],
    font=dict(family="Source Sans 3, Helvetica Neue, Arial, sans-serif", color=C["text2"]),
    margin=dict(l=40, r=20, t=50, b=40),
)

REGIME_INFO = {
    "R1_trend_high_vol": (
        "R1 — Trend + High Volatility",
        "Powerful but unstable trend. Useful for stress framing, not blind trend-following.",
    ),
    "R2_trend_low_vol": (
        "R2 — Trend + Low Volatility",
        "Orderly trend. Candidate regime for structured hedge adjustment or tactical signals.",
    ),
    "R3_range_high_vol": (
        "R3 — Range + High Volatility",
        "Choppy risk. High whipsaw risk. Avoid over-adjustment.",
    ),
    "R4_range_low_vol": (
        "R4 — Range + Low Volatility",
        "Quiet noise. Most random-walk-like candidate. Maintain discipline.",
    ),
}

PAGES = [
    "Executive Overview",
    "Random-Walk Lab",
    "Regime Intelligence",
    "Model Zoo",
    "Corridor Roadmap",
    "Hedge Governance",
    "Flow Pressure",
    "News & Macro Stress",
    "Carry & UIP Lab",
    "Unanswered FX Questions",
    "FX History",
    "Open Source FX AI Lab",
    "Academic Tests",
    "Data Quality",
    "FX Desk Command Center",
    "Publication Memo",
]

FX_LAB_TAGLINE = "Testing When Currency Markets Become Less Random"

# ── CSS ───────────────────────────────────────────────────────────────────────
LUXURY_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700&family=Source+Sans+3:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{
    font-family: "Source Sans 3", "Helvetica Neue", Arial, sans-serif;
}}
.stApp {{
    background-color: {C["bg"]};
    color: {C["text"]};
}}
section[data-testid="stSidebar"] {{
    background-color: {C["sidebar"]};
    border-right: 1px solid #152a45;
}}
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {{
    color: {C["sidebar_text"]} !important;
}}
section[data-testid="stSidebar"] .sidebar-brand {{
    color: #ffffff !important;
}}
section[data-testid="stSidebar"] .sidebar-tag,
section[data-testid="stSidebar"] .sidebar-motto {{
    color: rgba(232, 237, 244, 0.75) !important;
}}
.logo-frame {{
    background: #ffffff;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 6px;
    padding: 0.65rem 0.85rem;
    margin-bottom: 0.85rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}}
.hero-title {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: {C["navy"]};
    margin-bottom: 0.25rem;
}}
.tier-pill {{
    display: inline-block;
    padding: 0.2rem 0.55rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    margin-right: 0.35rem;
}}
.tier-1 {{ background: rgba(34,197,94,0.15); color: {C["green"]}; border: 1px solid rgba(34,197,94,0.35); }}
.tier-2 {{ background: rgba(56,189,248,0.12); color: {C["cyan"]}; border: 1px solid rgba(56,189,248,0.3); }}
.tier-3 {{ background: rgba(212,175,55,0.12); color: {C["gold"]}; border: 1px solid rgba(212,175,55,0.3); }}
.tier-4 {{ background: rgba(245,158,11,0.12); color: {C["amber"]}; border: 1px solid rgba(245,158,11,0.3); }}
.section-divider {{
    border: none;
    border-top: 1px solid {C["border"]};
    margin: 2rem 0 1.5rem;
}}
.hero-subtitle {{
    font-size: 1.15rem;
    font-weight: 500;
    color: {C["text"]};
    margin-bottom: 0.5rem;
}}
.hero-tagline {{
    font-size: 0.95rem;
    color: {C["text2"]};
    margin-bottom: 1.5rem;
}}
.section-header {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 1.45rem;
    font-weight: 700;
    color: {C["navy"]};
    border-left: 3px solid {C["navy"]};
    padding-left: 12px;
    margin: 1.5rem 0 0.75rem 0;
}}
.section-sub {{
    color: {C["muted"]};
    font-size: 0.9rem;
    margin-bottom: 1rem;
}}
.metric-card {{
    background: {C["panel"]};
    border: 1px solid {C["border"]};
    border-radius: 10px;
    padding: 1rem 1.15rem;
    min-height: 110px;
}}
.metric-card-title {{
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {C["muted"]};
    margin-bottom: 0.35rem;
}}
.metric-card-value {{
    font-size: 1.65rem;
    font-weight: 700;
    color: {C["text"]};
    line-height: 1.2;
}}
.metric-card-sub {{
    font-size: 0.8rem;
    color: {C["text2"]};
    margin-top: 0.35rem;
}}
.pill {{
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}}
.pill-success {{ background: rgba(34,197,94,0.15); color: {C["green"]}; border: 1px solid {C["green"]}; }}
.pill-warning {{ background: rgba(245,158,11,0.15); color: {C["amber"]}; border: 1px solid {C["amber"]}; }}
.pill-danger  {{ background: rgba(239,68,68,0.15); color: {C["red"]}; border: 1px solid {C["red"]}; }}
.pill-neutral {{ background: rgba(100,116,139,0.15); color: {C["text2"]}; border: 1px solid {C["border"]}; }}
.pill-info    {{ background: rgba(56,189,248,0.15); color: {C["cyan"]}; border: 1px solid {C["cyan"]}; }}
.pill-gold    {{ background: rgba(212,175,55,0.12); color: {C["gold"]}; border: 1px solid {C["gold"]}; }}
.callout {{
    background: {C["panel"]};
    border: 1px solid {C["border"]};
    border-left: 3px solid {C["navy"]};
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin: 1rem 0;
    color: {C["text2"]};
    font-size: 0.92rem;
}}
.warning-box {{
    background: rgba(245,158,11,0.08);
    border: 1px solid {C["amber"]};
    border-radius: 8px;
    padding: 1rem 1.25rem;
    color: {C["text2"]};
    margin: 1rem 0;
}}
.info-card {{
    background: {C["panel"]};
    border: 1px solid {C["border"]};
    border-radius: 10px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.75rem;
}}
.info-card h4 {{
    color: {C["navy"]};
    margin: 0 0 0.5rem 0;
    font-size: 0.95rem;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-weight: 700;
}}
.info-card p {{
    color: {C["text2"]};
    margin: 0;
    font-size: 0.88rem;
    line-height: 1.5;
}}
.footer-disclaimer {{
    border-top: 1px solid {C["border"]};
    margin-top: 2.5rem;
    padding-top: 1rem;
    color: {C["muted"]};
    font-size: 0.78rem;
    text-align: center;
}}
.sidebar-brand {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    color: #ffffff;
    margin-bottom: 0.15rem;
}}
.sidebar-tag {{
    font-size: 0.72rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: rgba(232, 237, 244, 0.8);
    line-height: 1.4;
    margin-bottom: 0.35rem;
}}
.sidebar-motto {{
    font-size: 0.65rem;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: rgba(232, 237, 244, 0.55);
    margin-bottom: 1.25rem;
}}
.missing-card {{
    background: {C["panel"]};
    border: 1px dashed {C["border"]};
    border-radius: 10px;
    padding: 1.5rem;
    text-align: center;
    color: {C["text2"]};
}}
.missing-card code {{
    color: {C["cyan"]};
    background: rgba(56,189,248,0.08);
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
}}
</style>
"""


# ── Helpers ───────────────────────────────────────────────────────────────────
def safe_read_csv(path: Path) -> Optional[pd.DataFrame]:
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            return None
    return None


def safe_read_markdown(path: Path) -> Optional[str]:
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return None
    return None


def format_pct(x: Any, digits: int = 2) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "—"
    return f"{float(x):.{digits}f}%"


def format_bps(x: Any, digits: int = 2) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "—"
    return f"{float(x) * 10000:.{digits}f} bps/day"


def format_float(x: Any, digits: int = 3) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "—"
    return f"{float(x):.{digits}f}"


def status_badge(label: str, kind: str = "neutral") -> str:
    return f'<span class="pill pill-{kind}">{label}</span>'


def metric_card(title: str, value: str, subtitle: Optional[str] = None, status: Optional[str] = None) -> str:
    sub = f'<div class="metric-card-sub">{subtitle}</div>' if subtitle else ""
    badge = f'<div style="margin-top:0.4rem">{status_badge(status, "info")}</div>' if status else ""
    return f"""
    <div class="metric-card">
        <div class="metric-card-title">{title}</div>
        <div class="metric-card-value">{value}</div>
        {sub}{badge}
    </div>
    """


def section_header(title: str, subtitle: Optional[str] = None) -> None:
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)


def missing_section(script_cmd: str, description: str = "") -> None:
    desc = f"<p style='margin-bottom:0.75rem'>{description}</p>" if description else ""
    st.markdown(
        f'<div class="missing-card">{desc}'
        f"<p>Data not available.</p>"
        f"<p>Run: <code>{script_cmd}</code></p></div>",
        unsafe_allow_html=True,
    )


def footer_disclaimer() -> None:
    st.markdown(
        '<div class="footer-disclaimer">'
        "BR3N Macro Labs is an independent research project — not affiliated with, endorsed by, "
        "or sponsored by any employer, financial institution, payment company, trading platform, "
        "or data vendor. Research and risk-framing only. Not investment advice. No live trading."
        "</div>",
        unsafe_allow_html=True,
    )


def load_latest_processed_pair() -> Optional[pd.DataFrame]:
    for name in ("usdmxn_features_regimes.csv", "US_MX_features_regimes.csv"):
        df = safe_read_csv(PROC / name)
        if df is not None:
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df = df.set_index("date")
            elif df.index.name != "date":
                df.index = pd.to_datetime(df.index)
            return df.sort_index()
    return None


def get_best_strategy(sc: pd.DataFrame, exclude: Tuple[str, ...] = ("buy_and_hold", "random_walk")) -> Optional[pd.Series]:
    if sc is None or sc.empty:
        return None
    col = "sharpe" if "sharpe" in sc.columns else "ann_vol_pct"
    mode_col = "strategy" if "strategy" in sc.columns else "mode"
    trade = sc[~sc[mode_col].isin(exclude)] if mode_col in sc.columns else sc
    if trade.empty:
        return None
    return trade.loc[trade[col].astype(float).idxmax()]


def get_lowest_drawdown(sc: pd.DataFrame) -> Optional[pd.Series]:
    if sc is None or sc.empty:
        return None
    dd_col = "max_drawdown_pct" if "max_drawdown_pct" in sc.columns else "max_drawdown"
    mode_col = "strategy" if "strategy" in sc.columns else "mode"
    trade = sc[~sc[mode_col].isin(("buy_and_hold", "random_walk"))]
    if trade.empty:
        return None
    return trade.loc[trade[dd_col].astype(float).idxmax()]


def get_latest_regime(df: pd.DataFrame) -> str:
    if df is None or df.empty or "regime" not in df.columns:
        return "—"
    return str(df["regime"].iloc[-1])


def rw_status_label(forecast: Optional[pd.DataFrame], academic: Optional[pd.DataFrame]) -> str:
    if forecast is not None and not forecast.empty:
        beats = forecast.iloc[0].get("model_beats_rw_rmse", False)
        if beats:
            return "Potential structure"
    if academic is not None and not academic.empty:
        dm = academic[academic["test"] == "diebold_mariano_rmse"]
        if not dm.empty:
            p = dm.iloc[0].get("p_value")
            if p is not None and float(p) < 0.05:
                return "Potential structure"
    if forecast is not None and not forecast.empty:
        if forecast.iloc[0].get("model_beats_rw_rmse") or forecast.iloc[0].get("model_beats_rw_mae"):
            return "Weak evidence"
    return "Not beaten"


def academic_claim_badge(forecast: Optional[pd.DataFrame], academic: Optional[pd.DataFrame]) -> Tuple[str, str]:
    if forecast is None or forecast.empty:
        return "Prototype only", "warning"
    beats_rmse = bool(forecast.iloc[0].get("model_beats_rw_rmse", False))
    p_val = None
    if academic is not None and not academic.empty:
        dm = academic[academic["test"] == "diebold_mariano_rmse"]
        if not dm.empty:
            p_val = dm.iloc[0].get("p_value")
    if beats_rmse and p_val is not None and float(p_val) < 0.05:
        return "Statistically significant", "success"
    if beats_rmse:
        return "Economically interesting but statistically weak", "warning"
    if p_val is not None and float(p_val) < 0.05:
        return "Requires better data", "info"
    return "Weak evidence", "neutral"


def apply_plotly_style(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, font=dict(color=C["text"], size=14)))
    fig.update_xaxes(gridcolor=C["border"], zerolinecolor=C["border"])
    fig.update_yaxes(gridcolor=C["border"], zerolinecolor=C["border"])
    return fig


# ── Charts ────────────────────────────────────────────────────────────────────
def price_with_moving_averages(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["price"], name="Price", line=dict(color=C["text"], width=1.2)))
    if "ma20" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["ma20"], name="MA20", line=dict(color=C["cyan"], width=1)))
    if "ma60" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["ma60"], name="MA60", line=dict(color=C["gold"], width=1)))
    return apply_plotly_style(fig, "Price & Moving Averages")


def regime_timeline_strip(df: pd.DataFrame) -> go.Figure:
    """Colored horizontal regime band."""
    regimes = df["regime"].astype(str)
    y_map = {r: i for i, r in enumerate(regimes.unique())}
    colors = [REGIME_COLORS.get(r, C["muted"]) for r in regimes]
    fig = go.Figure(
        go.Scatter(
            x=df.index,
            y=[0] * len(df),
            mode="markers",
            marker=dict(color=colors, size=3, symbol="square"),
            showlegend=False,
        )
    )
    fig.update_layout(height=80, yaxis=dict(visible=False, range=[-1, 1]))
    return apply_plotly_style(fig, "Regime Timeline")


def regime_distribution_chart(df: pd.DataFrame) -> go.Figure:
    counts = df["regime"].value_counts()
    colors = [REGIME_COLORS.get(r, C["muted"]) for r in counts.index]
    fig = go.Figure(go.Pie(labels=counts.index, values=counts.values, hole=0.55, marker=dict(colors=colors)))
    return apply_plotly_style(fig, "Regime Distribution")


def regime_return_bar(df: pd.DataFrame) -> go.Figure:
    bps = df.groupby("regime")["daily_return"].mean().mul(10000).round(2)
    colors = [REGIME_COLORS.get(r, C["muted"]) for r in bps.index]
    fig = go.Figure(go.Bar(x=bps.index, y=bps.values, marker_color=colors))
    fig.update_yaxes(title="bps/day")
    return apply_plotly_style(fig, "Average Return by Regime")


def regime_vol_bar(df: pd.DataFrame) -> go.Figure:
    vol_col = "realized_vol" if "realized_vol" in df.columns else "daily_return"
    if vol_col == "daily_return":
        vol = df.groupby("regime")["daily_return"].std().mul(252 ** 0.5 * 100).round(2)
    else:
        vol = df.groupby("regime")[vol_col].mean().round(2)
    colors = [REGIME_COLORS.get(r, C["muted"]) for r in vol.index]
    fig = go.Figure(go.Bar(x=vol.index, y=vol.values, marker_color=colors))
    fig.update_yaxes(title="Ann. vol %")
    return apply_plotly_style(fig, "Volatility by Regime")


def equity_curve_chart(out_dir: Path) -> Optional[go.Figure]:
    detail = safe_read_csv(out_dir / "usdmxn_backtest_detail.csv")
    if detail is None:
        return None
    if "date" in detail.columns:
        detail["date"] = pd.to_datetime(detail["date"])
        detail = detail.set_index("date")
    fig = go.Figure()
    if "equity" in detail.columns:
        fig.add_trace(go.Scatter(x=detail.index, y=detail["equity"], name="flat_range equity", line=dict(color=C["gold"])))
    return apply_plotly_style(fig, "Strategy Equity (flat_range)")


def scorecard_bar_chart(sc: pd.DataFrame, metric: str) -> go.Figure:
    mode_col = "strategy" if "strategy" in sc.columns else "mode"
    trade = sc[~sc[mode_col].isin(("buy_and_hold", "random_walk"))]
    fig = go.Figure(go.Bar(x=trade[mode_col], y=trade[metric], marker_color=C["gold"]))
    fig.update_yaxes(title=metric)
    return apply_plotly_style(fig, f"Strategy Comparison — {metric}")


def hedge_policy_scatter(hg: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        hg,
        x="hedge_turnover",
        y="volatility_reduction",
        size="total_hedge_cost",
        color="policy_name",
        hover_data=["cost_adjusted_risk_reduction"],
        color_discrete_sequence=[C["gold"], C["cyan"], C["green"], C["purple"], C["amber"]],
    )
    return apply_plotly_style(fig, "Hedge Turnover vs Volatility Reduction")


def random_walk_validity_heatmap(rw: pd.DataFrame) -> go.Figure:
    """Rows = corridor or USD/MXN, cols = regimes."""
    df = rw.copy()
    if "corridor_id" not in df.columns:
        df["corridor_id"] = "USD/MXN"
    pivot = df.pivot_table(
        index="corridor_id",
        columns="regime",
        values="random_walk_validity_label",
        aggfunc="first",
    )
    regime_order = ["R1_trend_high_vol", "R2_trend_low_vol", "R3_range_high_vol", "R4_range_low_vol"]
    pivot = pivot.reindex(columns=[c for c in regime_order if c in pivot.columns])

    z_text = pivot.values
    z_num = [[{"Random-walk-like": 0, "Potential structure": 1, "High-risk noise": 2}.get(v, 0.5)
              for v in row] for row in z_text]

    fig = go.Figure(
        go.Heatmap(
            z=z_num,
            x=pivot.columns,
            y=pivot.index,
            text=z_text,
            texttemplate="%{text}",
            colorscale=[[0, C["green"]], [0.5, C["gold"]], [1, C["red"]]],
            showscale=False,
        )
    )
    fig.update_layout(height=max(200, 60 * len(pivot)))
    return apply_plotly_style(fig, "Random-Walk Validity Heatmap")


def rmse_comparison_chart(forecast: pd.DataFrame) -> go.Figure:
    row = forecast.iloc[0]
    fig = go.Figure(
        go.Bar(
            x=["Model RMSE", "Random Walk RMSE"],
            y=[row["rmse_model"], row["rmse_random_walk"]],
            marker_color=[C["gold"], C["muted"]],
        )
    )
    return apply_plotly_style(fig, "RMSE vs Random Walk")


def flow_pressure_comparison(fp: pd.DataFrame) -> go.Figure:
    row = fp.iloc[0]
    fig = go.Figure(
        go.Bar(
            x=["Flow Window", "Normal Window"],
            y=[row["volatility_flow_window"], row["volatility_normal"]],
            marker_color=[C["amber"], C["cyan"]],
        )
    )
    fig.update_yaxes(title="Ann. Volatility %")
    return apply_plotly_style(fig, "Volatility: Flow Window vs Normal")


def news_vol_comparison(news_tests: pd.DataFrame) -> go.Figure:
    row = news_tests[news_tests["test_name"] == "high_vs_normal_news_stress"]
    if row.empty:
        row = news_tests.iloc[[0]]
    else:
        row = row.iloc[[0]]
    r = row.iloc[0]
    fig = go.Figure(
        go.Bar(
            x=["High News Stress", "Normal Days"],
            y=[r.get("volatility_high_news"), r.get("volatility_normal")],
            marker_color=[C["amber"], C["cyan"]],
        )
    )
    fig.update_yaxes(title="Ann. Volatility %")
    return apply_plotly_style(fig, "Volatility: High News Stress vs Normal")


def news_stress_timeline(df: pd.DataFrame) -> go.Figure:
    work = df.copy()
    if "date" not in work.columns:
        work = work.reset_index()
    work["date"] = pd.to_datetime(work["date"])
    fig = go.Figure()
    if "price" in work.columns:
        fig.add_trace(
            go.Scatter(x=work["date"], y=work["price"], name="USD/MXN", line=dict(color=C["cyan"], width=1))
        )
    if "news_stress_regime" in work.columns:
        stress = work[work["news_stress_regime"].astype(bool)]
        if not stress.empty and "price" in stress.columns:
            fig.add_trace(
                go.Scatter(
                    x=stress["date"],
                    y=stress["price"],
                    mode="markers",
                    name="News stress",
                    marker=dict(color=C["amber"], size=4, symbol="diamond"),
                )
            )
    return apply_plotly_style(fig, "USD/MXN with News-Stress Markers")


def corridor_heatmap(
    master: pd.DataFrame,
    dl: pd.DataFrame,
    fp: pd.DataFrame,
    hg: pd.DataFrame,
    rw: pd.DataFrame,
) -> pd.DataFrame:
    """Build summary matrix for corridor scorecard heatmap."""
    rows = []
    corridors = master["corridor_id"].unique() if master is not None else []
    for cid in corridors:
        row: Dict[str, Any] = {"corridor_id": cid}
        if master is not None:
            sub = master[(master["corridor_id"] == cid) & (~master["mode"].isin(["buy_and_hold", "random_walk"]))]
            if not sub.empty:
                row["best_sharpe"] = float(sub["sharpe"].max())
                row["max_drawdown"] = float(sub["max_drawdown"].min())
        if fp is not None and "corridor_id" in fp.columns:
            f = fp[fp["corridor_id"] == cid]
            if not f.empty:
                row["flow_p_value"] = f.iloc[0].get("p_value_return_difference")
        if hg is not None and "corridor_id" in hg.columns:
            h = hg[(hg["corridor_id"] == cid) & (hg["exposure_type"] == "receiver_currency_exposure")]
            if not h.empty:
                dyn = h[~h["policy_name"].isin(["fully_hedged", "never_hedged"])]
                if not dyn.empty:
                    row["hedge_score"] = float(dyn["cost_adjusted_risk_reduction"].max())
        if rw is not None and "corridor_id" in rw.columns:
            r = rw[rw["corridor_id"] == cid]
            rw_like = (r["random_walk_validity_label"] == "Random-walk-like").sum()
            struct = (r["random_walk_validity_label"] == "Potential structure").sum()
            row["rw_label"] = f"{rw_like} RW-like / {struct} structured"
        if dl is not None:
            d = dl[dl["corridor_id"] == cid]
            if not d.empty:
                row["observations"] = d.iloc[0].get("observations")
                row["status"] = d.iloc[0].get("status")
        rows.append(row)
    return pd.DataFrame(rows)


# ── Page renderers ────────────────────────────────────────────────────────────
def page_executive_overview() -> None:
    if FX_LOGO.exists():
        st.markdown('<div class="logo-frame">', unsafe_allow_html=True)
        st.image(str(FX_LOGO), width=280)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="hero-title">BR3N MACRO LABS</div>'
            '<div class="hero-subtitle">FX LAB</div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        f'<div class="hero-tagline">{FX_LAB_TAGLINE}<br>'
        "Conditional forecastability · Regime intelligence · Hedge governance · Corridor research</div>",
        unsafe_allow_html=True,
    )

    df = load_latest_processed_pair()
    sc = safe_read_csv(OUT / "strategy_scorecard.csv")
    forecast = safe_read_csv(OUT / "forecast_scorecard.csv")
    academic = safe_read_csv(OUT / "academic_test_results.csv")
    hg = safe_read_csv(OUT / "hedge_governance_scorecard.csv")
    dq = safe_read_csv(OUT / "data_quality_report.csv")

    best = get_best_strategy(sc) if sc is not None else None
    best_hg = None
    if hg is not None and not hg.empty:
        us = hg[hg["exposure_type"] == "us_entity_long_mxn"] if "exposure_type" in hg.columns else hg
        dyn = us[~us["policy_name"].isin(["fully_hedged", "never_hedged"])] if not us.empty else us
        if not dyn.empty:
            best_hg = dyn.loc[dyn["cost_adjusted_risk_reduction"].astype(float).idxmax()]

    tier = "prototype"
    if dq is not None and not dq.empty:
        tier = str(dq.iloc[0].get("tier_label", dq.iloc[0].get("data_tier", "prototype")))

    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)
    with c1:
        st.markdown(metric_card("Flagship Pair", "USD/MXN", "Primary research corridor"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Latest Regime", get_latest_regime(df) if df is not None else "—"), unsafe_allow_html=True)
    with c3:
        sharpe = format_float(best["sharpe"] if best is not None and "sharpe" in best.index else best.get("sharpe", "—") if best is not None else "—")
        mode = best["strategy"] if best is not None and "strategy" in best.index else (best.get("mode", "—") if best is not None else "—")
        st.markdown(metric_card("Best Strategy (Sharpe)", sharpe, str(mode)), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card("Random-Walk Status", rw_status_label(forecast, academic)), unsafe_allow_html=True)
    with c5:
        pol = best_hg["policy_name"] if best_hg is not None else "—"
        st.markdown(metric_card("Best Hedge Policy", str(pol), "Cost-adj risk reduction"), unsafe_allow_html=True)
    with c6:
        st.markdown(metric_card("Data Tier", tier.title(), "Current default source"), unsafe_allow_html=True)

    st.markdown(
        '<div class="callout"><strong>Academic honesty:</strong> This dashboard separates forecast accuracy, '
        "trading P&L, and hedge-governance usefulness. A model may fail to beat random walk as a forecast "
        "but still improve hedge discipline.</div>",
        unsafe_allow_html=True,
    )

    section_header("Three Research Objects")
    col1, col2, col3 = st.columns(3)
    cards = [
        ("Forecast Accuracy", "Does the model beat random walk by RMSE/MAE and statistical tests?"),
        ("Trading P&L", "Does the strategy survive costs, drawdowns, walk-forward, and data-snooping controls?"),
        ("Hedge Governance", "Can regime logic reduce hedge turnover, over-adjustment, and cost-adjusted exposure risk?"),
    ]
    for col, (title, q) in zip([col1, col2, col3], cards):
        with col:
            st.markdown(
                f'<div class="info-card"><h4>{title}</h4><p>{q}</p></div>',
                unsafe_allow_html=True,
            )


def page_fx_desk_command_center() -> None:
    """Cross-border payments FX desk decision framework visualization."""
    st.markdown(
        '<div class="hero-title">FX DESK COMMAND CENTER</div>'
        '<div class="hero-subtitle">Cross-border payments and treasury decisions</div>'
        '<div class="hero-tagline">Exposure, hedging, pricing, liquidity, settlement, and crisis-risk '
        "intelligence for payment-corridor and multi-currency treasury operations.</div>",
        unsafe_allow_html=True,
    )

    desk_sc = safe_read_csv(OUT / "fx_desk_scorecard.csv")
    framework_md = safe_read_markdown(REPORTS / "FX_DESK_DECISION_FRAMEWORK.md")

    if desk_sc is None:
        missing_section(
            "python scripts/run_fx_desk_framework.py",
            "FX desk scorecard and corridor memos",
        )
    else:
        # Default to US_MX or first row
        corridor_options = desk_sc["corridor_id"].tolist() if "corridor_id" in desk_sc.columns else []
        selected = st.selectbox("Corridor", corridor_options, index=0) if corridor_options else None
        row = desk_sc[desk_sc["corridor_id"] == selected].iloc[0] if selected else desk_sc.iloc[0]

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        kpis = [
            ("Latest Regime", str(row.get("latest_regime", "—"))),
            ("Desk Risk Level", str(row.get("overall_desk_risk_level", "—"))),
            ("Hedge Timing", str(row.get("hedge_timing_posture", "—"))[:40] + "…"),
            ("Pricing Posture", str(row.get("customer_pricing_posture", "—"))[:35] + "…"),
            ("Prefunding", str(row.get("prefunding_posture", "—"))[:35] + "…"),
            ("Data Quality", str(row.get("data_quality_warning", "—"))[:35] + "…"),
        ]
        for col, (title, val) in zip([c1, c2, c3, c4, c5, c6], kpis):
            with col:
                st.markdown(metric_card(title, val), unsafe_allow_html=True)

        st.markdown(
            f'<div class="callout">{row.get("plain_language_summary", "")}</div>',
            unsafe_allow_html=True,
        )

    section_header("Decision Modules", "Ten core FX desk decisions — research translation")
    try:
        from src.fx_desk_decisions import list_decision_modules

        modules = list_decision_modules()
        cols = st.columns(2)
        for i, mod in enumerate(modules):
            with cols[i % 2]:
                risks = ", ".join(mod["primary_risks"][:3])
                inputs = ", ".join(mod["inputs"][:4])
                st.markdown(
                    f'<div class="info-card">'
                    f'<h4>{mod["title"]}</h4>'
                    f'<p><strong>Q:</strong> {mod["question"]}</p>'
                    f'<p><strong>Inputs:</strong> {inputs}…</p>'
                    f'<p><strong>Risks:</strong> {risks}…</p>'
                    f'<p><strong>BR3N link:</strong> {mod["br3n_model_link"]}</p>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
    except ImportError:
        st.warning("Decision registry not loaded.")

    if desk_sc is not None:
        section_header("Corridor Risk Table")
        show_cols = [
            c
            for c in [
                "corridor_id",
                "pair_label",
                "latest_regime",
                "overall_desk_risk_level",
                "hedge_timing_posture",
                "customer_pricing_posture",
                "prefunding_posture",
                "data_quality_warning",
            ]
            if c in desk_sc.columns
        ]
        st.dataframe(desk_sc[show_cols], width="stretch")

    section_header("FX Desk Memo Viewer")
    memo_dir = REPORTS / "fx_desk_memos"
    if memo_dir.exists():
        memos = sorted(memo_dir.glob("*_fx_desk_memo.md"))
        if memos:
            memo_names = [m.name for m in memos]
            choice = st.selectbox("Select memo", memo_names)
            content = safe_read_markdown(memo_dir / choice)
            if content:
                st.markdown(content)
        else:
            missing_section("python scripts/run_fx_desk_framework.py", "Corridor FX desk memos")
    else:
        missing_section("python scripts/run_fx_desk_framework.py")

    if framework_md:
        with st.expander("Full FX Desk Decision Framework"):
            st.markdown(framework_md)

    st.markdown(
        '<div class="warning-box">Independent research only — not affiliated with any payment company '
        "or employer. This dashboard does not replace policy, approvals, exposure systems, "
        "compliance review, or human desk judgment.</div>",
        unsafe_allow_html=True,
    )


def page_random_walk_lab() -> None:
    section_header("Random-Walk Lab", "When does random walk fail, and when does it remain valid?")

    forecast = safe_read_csv(OUT / "forecast_scorecard.csv")
    rw_local = safe_read_csv(OUT / "random_walk_validity_map.csv")
    rw_corr = safe_read_csv(OUT / "corridor_random_walk_validity.csv")
    academic = safe_read_csv(OUT / "academic_test_results.csv")

    rw = None
    if rw_corr is not None and not rw_corr.empty:
        rw = rw_corr.copy()
        if rw_local is not None and not rw_local.empty:
            local = rw_local.copy()
            local["corridor_id"] = "USD/MXN"
            rw = pd.concat([local, rw_corr], ignore_index=True)
    elif rw_local is not None:
        rw = rw_local.copy()
        rw["corridor_id"] = "USD/MXN"

    if rw is not None and not rw.empty:
        st.plotly_chart(random_walk_validity_heatmap(rw), width="stretch")
    else:
        missing_section("python scripts/run_under_tested_research.py", "Random-walk validity map")

    col1, col2 = st.columns(2)
    with col1:
        if forecast is not None and not forecast.empty:
            st.plotly_chart(rmse_comparison_chart(forecast), width="stretch")
        else:
            missing_section("python scripts/run_research_models.py", "Forecast scorecard")
    with col2:
        if academic is not None and not academic.empty:
            dm = academic[academic["test"] == "diebold_mariano_rmse"]
            if not dm.empty:
                p = dm.iloc[0].get("p_value", "n/a")
                sig = float(p) < 0.05 if p != "n/a" and pd.notna(p) else False
                st.markdown(
                    f'<div class="info-card"><h4>Diebold-Mariano Test</h4>'
                    f"<p><strong>p-value:</strong> {p}<br>"
                    f"<strong>Statistically significant (5%):</strong> {'Yes' if sig else 'No'}<br>"
                    f"<strong>Interpretation:</strong> {dm.iloc[0].get('interpretation', '—')}</p></div>",
                    unsafe_allow_html=True,
                )
            st.dataframe(academic, width="stretch")
        else:
            missing_section("python scripts/run_research_models.py", "Academic test results")

    # Interpretation box
    beats = False
    p_val = None
    if forecast is not None and not forecast.empty:
        beats = bool(forecast.iloc[0].get("model_beats_rw_rmse", False))
    if academic is not None:
        dm = academic[academic["test"] == "diebold_mariano_rmse"]
        if not dm.empty:
            p_val = dm.iloc[0].get("p_value")

    if p_val is not None and float(p_val) >= 0.05:
        msg = "Current evidence does not reject the random-walk benchmark."
    elif beats and (p_val is None or float(p_val) >= 0.05):
        msg = "Possible structure, but not enough evidence for an academic claim."
    elif p_val is not None and float(p_val) < 0.05:
        msg = "Potential conditional forecastability; requires robustness testing."
    else:
        msg = "Insufficient data — run research models pipeline."

    st.markdown(f'<div class="callout"><strong>What this means:</strong> {msg}</div>', unsafe_allow_html=True)


def page_regime_intelligence() -> None:
    section_header("Regime Intelligence", "Market-state engine — trend × volatility")

    df = load_latest_processed_pair()
    sc = safe_read_csv(OUT / "strategy_scorecard.csv")

    if df is None:
        missing_section("python scripts/run_usdmxn_backtest.py", "Processed features with regime labels")
        return

    st.plotly_chart(price_with_moving_averages(df), width="stretch")
    st.plotly_chart(regime_timeline_strip(df), width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(regime_distribution_chart(df), width="stretch")
    with c2:
        st.plotly_chart(regime_return_bar(df), width="stretch")

    st.plotly_chart(regime_vol_bar(df), width="stretch")

    eq = equity_curve_chart(OUT)
    if eq is not None:
        st.plotly_chart(eq, width="stretch")

    section_header("Regime Interpretation")
    for regime in df["regime"].unique():
        title, text = REGIME_INFO.get(regime, (regime, "Review regime metrics."))
        color = REGIME_COLORS.get(regime, C["muted"])
        st.markdown(
            f'<div class="info-card" style="border-left:3px solid {color}">'
            f"<h4>{title}</h4><p>{text}</p></div>",
            unsafe_allow_html=True,
        )

    if sc is not None:
        section_header("Strategy Scorecard")
        st.dataframe(sc, width="stretch")


def page_model_zoo() -> None:
    section_header(
        "Model Zoo",
        "Tests conditional forecastability — not FX prediction",
    )

    run_log = safe_read_csv(OUT / "model_zoo_run_log.csv")
    fc = safe_read_csv(OUT / "model_zoo_forecast_scorecard.csv")
    tr = safe_read_csv(OUT / "model_zoo_trading_scorecard.csv")
    hg = safe_read_csv(OUT / "model_zoo_hedge_scorecard.csv")
    wf = safe_read_csv(OUT / "model_zoo_walk_forward_scorecard.csv")

    if run_log is None:
        missing_section("python scripts/run_model_zoo.py", "Model zoo scorecards")
        return

    attempted = len(run_log)
    success = int((run_log["status"] == "success").sum())
    skipped = int((run_log["status"] == "skipped").sum())

    section_header("Model Zoo Overview")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(metric_card("Attempted", str(attempted)), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Successful", str(success)), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("Skipped", str(skipped)), unsafe_allow_html=True)
    with c4:
        best_fc = fc.sort_values("rmse_model").iloc[0]["model_name"] if fc is not None and not fc.empty else "—"
        st.markdown(metric_card("Best forecast (lowest RMSE)", str(best_fc)), unsafe_allow_html=True)
    with c5:
        best_tr = tr.sort_values("sharpe_net", ascending=False).iloc[0]["model_name"] if tr is not None and not tr.empty else "—"
        st.markdown(metric_card("Best trading (Sharpe net)", str(best_tr)), unsafe_allow_html=True)

    if hg is not None and not hg.empty:
        best_hg = hg.sort_values("cost_adjusted_risk_reduction", ascending=False).iloc[0]
        st.markdown(
            metric_card(
                "Best hedge (cost-adj risk reduction)",
                f"{best_hg['model_name']} ({best_hg['cost_adjusted_risk_reduction']})",
            ),
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="warn-card"><strong>Research discipline:</strong> A model that performs well '
        "in-sample but fails walk-forward, random-walk tests, or cost-adjusted testing should "
        "<strong>not</strong> be treated as evidence of forecastability.</div>",
        unsafe_allow_html=True,
    )

    section_header("Forecast Model Scorecard")
    if fc is not None and not fc.empty:
        fc_cols = [
            c for c in [
                "model_name", "rmse_model", "rmse_random_walk", "mae_model", "mae_random_walk",
                "model_beats_rw_rmse", "model_beats_rw_mae", "directional_accuracy",
            ] if c in fc.columns
        ]
        st.dataframe(fc[fc_cols], width="stretch")
    else:
        st.info("No forecast scorecard.")

    section_header("Trading Model Scorecard")
    if tr is not None and not tr.empty:
        tr_cols = [
            c for c in [
                "model_name", "total_return_net", "sharpe_net", "max_drawdown_net",
                "number_of_trades", "total_transaction_cost", "percent_time_in_market",
            ] if c in tr.columns
        ]
        st.dataframe(tr[tr_cols], width="stretch")
    else:
        st.info("No trading scorecard.")

    section_header("Hedge Model Scorecard")
    if hg is not None and not hg.empty:
        hg_cols = [
            c for c in [
                "model_name", "volatility_reduction", "hedge_turnover", "total_hedge_cost",
                "cost_adjusted_risk_reduction", "average_hedge_ratio",
            ] if c in hg.columns
        ]
        st.dataframe(hg[hg_cols], width="stretch")
    else:
        st.info("No hedge scorecard.")

    section_header("Walk-Forward Scorecard")
    if wf is not None and not wf.empty:
        st.dataframe(wf, width="stretch")
    else:
        st.info("Walk-forward scorecard not available. Enable model_zoo.walk_forward_enabled in config.")

    section_header("Model Interpretation Cards")
    families = [
        ("Trend models", "MA crossover, regime trend, R2 only — test directional rules in trend regimes."),
        ("Risk-off models", "R1 risk-off, dollar stress — reduce exposure when volatility or USD stress is elevated."),
        ("Range models", "Mean reversion in range regimes — opposite logic to trend models."),
        ("Flow models", "Payment-flow proxy model — exploratory calendar windows, not causal flow data."),
        ("Hedge models", "Conservative hedge, no-change-in-range — governance when forecasts fail."),
    ]
    cols = st.columns(2)
    for i, (title, desc) in enumerate(families):
        with cols[i % 2]:
            st.markdown(
                f'<div class="info-card"><h4>{title}</h4><p>{desc}</p></div>',
                unsafe_allow_html=True,
            )

    if skipped > 0:
        section_header("Skipped Models")
        skip_df = run_log[run_log["status"] == "skipped"][["model_name", "reason", "required_columns_missing"]]
        st.dataframe(skip_df, width="stretch")


def page_corridor_roadmap() -> None:
    section_header("Corridor Roadmap", "Expansion from USD/MXN into major remittance corridors")

    master = safe_read_csv(OUT / "corridor_master_scorecard.csv")
    dl = safe_read_csv(OUT / "corridor_download_log.csv")
    fp = safe_read_csv(OUT / "corridor_flow_pressure_summary.csv")
    hg = safe_read_csv(OUT / "corridor_hedge_governance_summary.csv")
    rw = safe_read_csv(OUT / "corridor_random_walk_validity.csv")

    if dl is None and master is None:
        missing_section("python scripts/run_corridor_roadmap.py", "Multi-corridor research outputs")
        return

    if dl is not None:
        from src.corridors import get_corridor

        rows = []
        for _, r in dl.iterrows():
            cid = r["corridor_id"]
            try:
                meta = get_corridor(cid)
                rows.append({
                    "corridor_id": cid,
                    "sender": meta["sender_country"],
                    "receiver": meta["receiver_country"],
                    "model_pair": r["model_pair"],
                    "status": r["status"],
                    "observations": r["observations"],
                    "data_warning": meta.get("data_warning") or "—",
                })
            except KeyError:
                rows.append(dict(r))
        st.dataframe(pd.DataFrame(rows), width="stretch")

    if master is not None:
        heat = corridor_heatmap(master, dl or pd.DataFrame(), fp or pd.DataFrame(), hg or pd.DataFrame(), rw or pd.DataFrame())
        if not heat.empty:
            section_header("Corridor Scorecard Summary")
            st.dataframe(heat, width="stretch")

    # Leaderboard cards
    if master is not None and dl is not None:
        section_header("Corridor Leaderboard")
        best_data = dl.loc[dl["observations"].astype(float).idxmax(), "corridor_id"] if not dl.empty else "—"

        regime_spreads = {}
        for cid in master["corridor_id"].unique():
            p = PROC / f"{cid}_features_regimes_flow.csv"
            d = safe_read_csv(p)
            if d is not None and "regime" in d.columns and "daily_return" in d.columns:
                by = d.groupby("regime")["daily_return"].mean()
                regime_spreads[cid] = float(by.max() - by.min())

        strongest_regime = max(regime_spreads, key=regime_spreads.get) if regime_spreads else "—"

        most_rw = "—"
        if rw is not None and "corridor_id" in rw.columns:
            rw_counts = rw.groupby("corridor_id").apply(
                lambda x: (x["random_walk_validity_label"] == "Random-walk-like").sum()
            )
            if not rw_counts.empty:
                most_rw = rw_counts.idxmax()

        strongest_flow = "—"
        if fp is not None and "p_value_return_difference" in fp.columns:
            strongest_flow = fp.loc[fp["p_value_return_difference"].astype(float).idxmin(), "corridor_id"]

        best_hedge = "—"
        if hg is not None and "corridor_id" in hg.columns:
            dyn = hg[~hg["policy_name"].isin(["fully_hedged", "never_hedged"])]
            if not dyn.empty:
                best_hedge = dyn.loc[dyn["cost_adjusted_risk_reduction"].astype(float).idxmax(), "corridor_id"]

        cards = [
            ("Best Data Availability", best_data),
            ("Strongest Regime Effect", strongest_regime),
            ("Most Random-Walk-Like", most_rw),
            ("Strongest Flow-Pressure Signal", strongest_flow),
            ("Best Hedge Governance", best_hedge),
        ]
        cols = st.columns(len(cards))
        for col, (title, val) in zip(cols, cards):
            with col:
                st.markdown(metric_card(title, str(val)), unsafe_allow_html=True)

    st.markdown(
        '<div class="warning-box"><strong>Important:</strong> Public calendar proxies are not actual '
        "payment-flow data. They are exploratory proxies until validated with official remittance data "
        "or legally usable proprietary flow data.</div>",
        unsafe_allow_html=True,
    )

    if master is not None:
        section_header("Full Corridor Scorecard")
        st.dataframe(master, width="stretch")


def page_hedge_governance() -> None:
    section_header("Hedge Governance", "Forecast failure does not equal hedge uselessness")

    hg = safe_read_csv(OUT / "hedge_governance_scorecard.csv")
    hg_corr = safe_read_csv(OUT / "corridor_hedge_governance_summary.csv")

    if hg is None and hg_corr is None:
        missing_section("python scripts/run_under_tested_research.py", "Hedge governance scorecard")
        return

    exposure = st.selectbox(
        "Exposure lens",
        ["us_entity_long_mxn", "mx_entity_usd_liabilities", "receiver_currency_exposure"],
        format_func=lambda x: {
            "us_entity_long_mxn": "US entity long MXN",
            "mx_entity_usd_liabilities": "MX entity USD liabilities",
            "receiver_currency_exposure": "Receiver currency exposure",
        }.get(x, x),
    )

    data = hg if hg is not None else hg_corr
    if "exposure_type" in data.columns:
        data = data[data["exposure_type"] == exposure]
    if data.empty and hg_corr is not None:
        data = hg_corr[hg_corr["exposure_type"] == "receiver_currency_exposure"]

    if data.empty:
        st.warning("No data for selected exposure type.")
        return

    show_cols = [c for c in [
        "policy_name", "volatility_reduction", "hedge_turnover", "total_hedge_cost",
        "max_drawdown_hedged", "cost_adjusted_risk_reduction", "average_hedge_ratio",
    ] if c in data.columns]
    st.dataframe(data[show_cols], width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(go.Bar(
            x=data["policy_name"], y=data["cost_adjusted_risk_reduction"],
            marker_color=C["gold"],
        ))
        st.plotly_chart(apply_plotly_style(fig, "Cost-Adjusted Risk Reduction"), width="stretch")
    with c2:
        fig = go.Figure(go.Bar(x=data["policy_name"], y=data["hedge_turnover"], marker_color=C["cyan"]))
        st.plotly_chart(apply_plotly_style(fig, "Hedge Turnover"), width="stretch")

    st.plotly_chart(hedge_policy_scatter(data), width="stretch")

    st.markdown(
        '<div class="info-card"><h4>When Not to Hedge</h4>'
        "<p>The <strong>no_change_in_range</strong> policy tests whether avoiding hedge-ratio changes "
        "during R3/R4 range regimes reduces unnecessary turnover without materially increasing risk.</p></div>",
        unsafe_allow_html=True,
    )

    dyn = data[~data["policy_name"].isin(["fully_hedged", "never_hedged"])]
    if not dyn.empty:
        section_header("Policy Interpretation")
        interp = [
            ("Best risk reducer", dyn.loc[dyn["cost_adjusted_risk_reduction"].astype(float).idxmax(), "policy_name"]),
            ("Lowest turnover", dyn.loc[dyn["hedge_turnover"].astype(float).idxmin(), "policy_name"]),
            ("Most aggressive", dyn.loc[dyn["average_hedge_ratio"].astype(float).idxmax(), "policy_name"]),
            ("Most conservative", dyn.loc[dyn["average_hedge_ratio"].astype(float).idxmin(), "policy_name"]),
        ]
        cols = st.columns(len(interp))
        for col, (label, pol) in zip(cols, interp):
            with col:
                st.markdown(metric_card(label, str(pol)), unsafe_allow_html=True)


def page_flow_pressure() -> None:
    section_header("Flow Pressure", "Public payment-flow proxy research — exploratory, not causal")

    fp = safe_read_csv(OUT / "flow_pressure_test_results.csv")
    fp_corr = safe_read_csv(OUT / "corridor_flow_pressure_summary.csv")

    if fp is None and fp_corr is None:
        missing_section("python scripts/run_under_tested_research.py", "Flow pressure test results")
        return

    selected = st.radio("View", ["USD/MXN", "All Corridors"], horizontal=True)
    data = fp if selected == "USD/MXN" and fp is not None else fp_corr
    if data is None:
        missing_section("python scripts/run_corridor_roadmap.py")
        return

    row = data.iloc[0]
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        ("Flow Window Return", row.get("average_return_flow_window", "—")),
        ("Normal Window Return", row.get("average_return_normal", "—")),
        ("Flow Volatility", format_pct(row.get("volatility_flow_window"))),
        ("Normal Volatility", format_pct(row.get("volatility_normal"))),
        ("p-value", row.get("p_value_return_difference", "—")),
    ]
    for col, (title, val) in zip([c1, c2, c3, c4, c5], metrics):
        with col:
            st.markdown(metric_card(title, str(val)), unsafe_allow_html=True)

    if selected == "USD/MXN" and fp is not None:
        st.plotly_chart(flow_pressure_comparison(fp), width="stretch")

    if len(data) > 1:
        st.dataframe(data, width="stretch")

    section_header("Calendar Proxies Used")
    proxies = [
        "Payday windows (days 1, 15, 30/31 ±2 days)",
        "Month-end / month-start / quarter-end",
        "Christmas season",
        "US tax refund season (Feb–Apr)",
        "School-fee season (corridor-specific)",
        "Mother's Day window (Mexico)",
        "Semana Santa proxy (Mexico)",
        "Diwali proxy (India)",
    ]
    cols = st.columns(4)
    for i, p in enumerate(proxies):
        with cols[i % 4]:
            st.markdown(f'<div class="info-card"><p>{p}</p></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="warning-box">These are public calendar proxies, not actual order-flow data. '
        "Evidence is exploratory and not causal.</div>",
        unsafe_allow_html=True,
    )


def page_news_macro_stress() -> None:
    section_header("News & Macro Stress", "News as regime/risk feature — not price prediction")

    news_tests = safe_read_csv(OUT / "news_feature_test_results.csv")
    news_df_path = PROC / "usdmxn_features_regimes_news.csv"
    news_df = safe_read_csv(news_df_path) if news_df_path.exists() else None
    fc = safe_read_csv(OUT / "model_zoo_forecast_scorecard.csv")
    tr = safe_read_csv(OUT / "model_zoo_trading_scorecard.csv")
    hg = safe_read_csv(OUT / "model_zoo_hedge_scorecard.csv")
    strategy_md = safe_read_markdown(REPORTS / "NEWS_DATA_STRATEGY.md")

    fred_loaded = news_df is not None and "policy_uncertainty_index" in news_df.columns and news_df["policy_uncertainty_index"].notna().any()
    gdelt_loaded = news_df is not None and "total_usdmxn_news_intensity" in news_df.columns and news_df["total_usdmxn_news_intensity"].notna().any()
    placeholders = news_df is None or (
        "news_stress_regime" in news_df.columns and news_df.get("policy_uncertainty_index", pd.Series()).isna().all()
    )

    st.markdown(
        '<div class="callout">News features identify <strong>stress regimes</strong>, '
        "not guaranteed FX direction. Research and risk-framing only.</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    for col, (t, v, kind) in zip(
        [c1, c2, c3],
        [
            ("FRED uncertainty", "Loaded" if fred_loaded else "Not loaded", "success" if fred_loaded else "warning"),
            ("GDELT", "Loaded" if gdelt_loaded else "Skipped", "success" if gdelt_loaded else "info"),
            ("Placeholders only", "Yes" if placeholders and not fred_loaded else "No", "warning" if placeholders else "success"),
        ],
    ):
        with col:
            st.markdown(
                f'<div class="info-card">{status_badge(t, kind)}<p style="margin:0.4rem 0 0">{v}</p></div>',
                unsafe_allow_html=True,
            )

    if news_df is None:
        missing_section("python scripts/run_news_layer.py", "News-enhanced feature file")
    else:
        if "policy_uncertainty_index" in news_df.columns and news_df["policy_uncertainty_index"].notna().any():
            section_header("Policy Uncertainty (FRED)")
            nd = news_df.dropna(subset=["policy_uncertainty_index"])
            fig = go.Figure(
                go.Scatter(
                    x=pd.to_datetime(nd["date"]),
                    y=nd["policy_uncertainty_index"],
                    line=dict(color=C["gold"], width=1.5),
                )
            )
            fig.update_yaxes(title="USEPUINDXD")
            st.plotly_chart(apply_plotly_style(fig, "US Economic Policy Uncertainty"), width="stretch")

        if "news_stress_regime" in news_df.columns:
            section_header("News Stress Timeline")
            st.plotly_chart(news_stress_timeline(news_df), width="stretch")
            n_stress = int(news_df["news_stress_regime"].astype(bool).sum())
            st.markdown(
                f'<div class="info-card">News-stress days: <strong>{n_stress}</strong> '
                f"({round(n_stress / len(news_df) * 100, 1)}% of sample)</div>",
                unsafe_allow_html=True,
            )

    if news_tests is not None and not news_tests.empty:
        section_header("News Feature Tests")
        high = news_tests[news_tests["test_name"] == "high_vs_normal_news_stress"]
        if not high.empty:
            st.plotly_chart(news_vol_comparison(news_tests), width="stretch")
        st.dataframe(news_tests, width="stretch", hide_index=True)
    else:
        missing_section("python scripts/run_news_layer.py", "news_feature_test_results.csv")

    news_models = [
        "news_stress_risk_off_model",
        "r2_news_confirmed_model",
        "r1_news_escalation_model",
        "news_flow_pressure_model",
    ]
    section_header("News-Aware Model Zoo Results")
    for label, sc in [("Forecast", fc), ("Trading", tr), ("Hedge", hg)]:
        if sc is not None and "model_name" in sc.columns:
            sub = sc[sc["model_name"].isin(news_models)]
            if not sub.empty:
                st.markdown(f"**{label} scorecard (news models)**")
                st.dataframe(sub, width="stretch", hide_index=True)

    cols = st.columns(3)
    cards = [
        ("News as risk modifier", "News features identify stress regimes, not price prediction."),
        ("R2 quiet-trend hypothesis", "Orderly low-volatility trends may be cleaner when news stress is low."),
        ("R1 crisis hypothesis", "High-vol trend plus news stress may indicate escalation, not normal alpha."),
    ]
    for col, (title, body) in zip(cols, cards):
        with col:
            st.markdown(f'<div class="info-card"><h4>{title}</h4><p>{body}</p></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="warning-box">News data can be noisy, revised, biased by media coverage, '
        "and subject to look-ahead mistakes. All news features require out-of-sample testing.</div>",
        unsafe_allow_html=True,
    )

    if strategy_md:
        with st.expander("News data strategy"):
            st.markdown(strategy_md)


def carry_vol_comparison(tests: pd.DataFrame) -> go.Figure:
    row = tests[tests["test_name"] == "high_carry_vs_low_carry"]
    if row.empty:
        row = tests.iloc[[0]]
    else:
        row = row.iloc[[0]]
    r = row.iloc[0]
    fig = go.Figure(
        go.Bar(
            x=["High Carry", "Low Carry"],
            y=[r.get("volatility_high_carry"), r.get("volatility_low_carry")],
            marker_color=[C["gold"], C["cyan"]],
        )
    )
    fig.update_yaxes(title="Ann. Volatility %")
    return apply_plotly_style(fig, "Volatility: High Carry vs Low Carry")


def carry_fragility_timeline(df: pd.DataFrame) -> go.Figure:
    work = df.copy()
    if "date" not in work.columns:
        work = work.reset_index()
    work["date"] = pd.to_datetime(work["date"])
    fig = go.Figure()
    if "price" in work.columns:
        fig.add_trace(go.Scatter(x=work["date"], y=work["price"], name="USD/MXN", line=dict(color=C["cyan"], width=1)))
    if "carry_fragility_regime" in work.columns:
        frag = work[work["carry_fragility_regime"].astype(bool)]
        if not frag.empty:
            fig.add_trace(
                go.Scatter(
                    x=frag["date"], y=frag["price"], mode="markers",
                    name="Carry fragility", marker=dict(color=C["gold"], size=4, symbol="diamond"),
                )
            )
    return apply_plotly_style(fig, "USD/MXN with Carry-Fragility Markers")


def page_carry_uip_lab() -> None:
    section_header("Carry & UIP Lab", "When yield creates structure — and when it hides crash risk")

    carry_df_path = PROC / "usdmxn_features_regimes_carry.csv"
    carry_df = safe_read_csv(carry_df_path) if carry_df_path.exists() else None
    tests = safe_read_csv(OUT / "carry_regime_test_results.csv")
    hg = safe_read_csv(OUT / "carry_hedge_governance_scorecard.csv")
    fc = safe_read_csv(OUT / "model_zoo_forecast_scorecard.csv")
    tr = safe_read_csv(OUT / "model_zoo_trading_scorecard.csv")
    framework_md = safe_read_markdown(REPORTS / "CARRY_RESEARCH_FRAMEWORK.md")

    st.markdown(
        '<div class="hero-subtitle">Testing when yield creates structure and when yield hides crash risk. '
        "Carry is a regime/risk feature — not a magic trading signal.</div>",
        unsafe_allow_html=True,
    )

    if carry_df is None:
        missing_section("python scripts/run_carry_layer.py", "Carry-enhanced feature file")
        return

    latest = carry_df.iloc[-1]
    has_carry = pd.notna(latest.get("carry_proxy"))
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    cards = [
        ("Carry proxy", f"{float(latest['carry_proxy']):.3f}" if has_carry else "—"),
        ("Carry percentile", f"{float(latest['carry_percentile']):.2f}" if pd.notna(latest.get("carry_percentile")) else "—"),
        ("High carry?", "Yes" if latest.get("is_high_carry") else "No"),
        ("Fragility?", "Yes" if latest.get("carry_fragility_regime") else "No"),
        ("Forward data?", "Yes" if latest.get("forward_data_available") else "No"),
        ("Carry regime", str(latest.get("carry_adjusted_regime", "—"))),
    ]
    for col, (t, v) in zip([c1, c2, c3, c4, c5, c6], cards):
        with col:
            st.markdown(metric_card(t, v), unsafe_allow_html=True)

    if has_carry and "carry_proxy" in carry_df.columns:
        section_header("Carry Proxy Over Time")
        cd = carry_df.dropna(subset=["carry_proxy"])
        fig = go.Figure(go.Scatter(x=pd.to_datetime(cd["date"]), y=cd["carry_proxy"], line=dict(color=C["gold"], width=1.5)))
        fig.update_yaxes(title="Foreign − Domestic policy rate (proxy)")
        st.plotly_chart(apply_plotly_style(fig, "Policy-Rate Carry Proxy (USD/MXN)"), width="stretch")

    if "carry_zscore" in carry_df.columns:
        section_header("Carry Z-Score")
        cz = carry_df.dropna(subset=["carry_zscore"])
        fig = go.Figure(go.Scatter(x=pd.to_datetime(cz["date"]), y=cz["carry_zscore"], line=dict(color=C["amber"], width=1)))
        st.plotly_chart(apply_plotly_style(fig, "Carry Z-Score"), width="stretch")

    if "carry_fragility_regime" in carry_df.columns:
        section_header("Price with Carry-Fragility Markers")
        st.plotly_chart(carry_fragility_timeline(carry_df), width="stretch")

    if tests is not None and not tests.empty:
        section_header("Carry Regime Tests")
        hi = tests[tests["test_name"] == "high_carry_vs_low_carry"]
        if not hi.empty:
            st.plotly_chart(carry_vol_comparison(tests), width="stretch")
        st.dataframe(tests, width="stretch", hide_index=True)

    if hg is not None:
        section_header("Carry Hedge Governance")
        st.dataframe(hg, width="stretch", hide_index=True)

    carry_models = [
        "carry_proxy_model", "carry_regime_model", "carry_fragility_risk_off_model",
        "r2_carry_confirmed_model", "carry_adjusted_hedge_model",
    ]
    section_header("Carry-Aware Model Zoo")
    for label, sc in [("Forecast", fc), ("Trading", tr)]:
        if sc is not None and "model_name" in sc.columns:
            sub = sc[sc["model_name"].isin(carry_models)]
            if not sub.empty:
                st.markdown(f"**{label}**")
                st.dataframe(sub, width="stretch", hide_index=True)

    cols = st.columns(2)
    cards_interp = [
        ("Carry is not free yield", "Carry may compensate investors for crash, liquidity, or dollar-stress risk."),
        ("UIP question", "High-yield currencies should theoretically depreciate to offset yield — empirically this often fails or appears regime-dependent."),
        ("Carry fragility", "High carry plus rising vol/news/dollar stress may indicate carry is becoming dangerous."),
        ("Hedge governance", "Forward/carry costs matter. Spot hedges may still be expensive after forward points and carry drag."),
    ]
    for i, (title, body) in enumerate(cards_interp):
        with cols[i % 2]:
            st.markdown(f'<div class="info-card"><h4>{title}</h4><p>{body}</p></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="warning-box">Policy-rate carry is a proxy. Trading-grade hedge economics require '
        "actual forward points, bid/ask spreads, and transaction costs.</div>",
        unsafe_allow_html=True,
    )

    if framework_md:
        with st.expander("Carry research framework"):
            st.markdown(framework_md)


def page_academic_tests() -> None:
    section_header("Academic Tests", "Journal-grade framing — prototype data until Tier 1 rerun")

    forecast = safe_read_csv(OUT / "forecast_scorecard.csv")
    academic = safe_read_csv(OUT / "academic_test_results.csv")
    ml = safe_read_csv(OUT / "ml_direction_model_scorecard.csv")
    wf = safe_read_csv(OUT / "walkforward_oos.csv")

    if all(x is None for x in (forecast, academic, ml)):
        missing_section("python scripts/run_research_models.py", "Academic research layer")
        return

    badge_label, badge_kind = academic_claim_badge(forecast, academic)
    st.markdown(
        f'<div style="margin-bottom:1rem">Academic claim status: {status_badge(badge_label, badge_kind)}</div>',
        unsafe_allow_html=True,
    )

    # Summary cards
    c1, c2, c3 = st.columns(3)
    with c1:
        rmse_beats = forecast.iloc[0]["model_beats_rw_rmse"] if forecast is not None else "—"
        mae_beats = forecast.iloc[0]["model_beats_rw_mae"] if forecast is not None else "—"
        st.markdown(metric_card("RMSE beats RW?", str(rmse_beats)), unsafe_allow_html=True)
        st.markdown(metric_card("MAE beats RW?", str(mae_beats)), unsafe_allow_html=True)
    with c2:
        p_val = "—"
        if academic is not None:
            dm = academic[academic["test"] == "diebold_mariano_rmse"]
            if not dm.empty:
                p_val = dm.iloc[0]["p_value"]
        st.markdown(metric_card("DM p-value", str(p_val)), unsafe_allow_html=True)
        wrc = "—"
        if academic is not None:
            w = academic[academic["test"] == "white_reality_check"]
            if not w.empty:
                wrc = w.iloc[0].get("bootstrap_p_value", "—")
        st.markdown(metric_card("White RC p-value", str(wrc)), unsafe_allow_html=True)
    with c3:
        wf_result = "Available" if wf is not None else "Missing"
        st.markdown(metric_card("Walk-forward OOS", wf_result), unsafe_allow_html=True)
        st.markdown(metric_card("Data-snooping", "Use White RC + holdout"), unsafe_allow_html=True)

    if forecast is not None:
        section_header("Forecast Scorecard")
        st.dataframe(forecast, width="stretch")

    if ml is not None:
        section_header("ML Direction Models")
        st.dataframe(ml, width="stretch")

    if wf is not None:
        section_header("Walk-Forward OOS")
        st.dataframe(wf, width="stretch")

    st.markdown(
        '<div class="callout">BR3N Macro Labs does not treat backtest performance as proof. Models must be '
        "tested against random-walk benchmarks, transaction costs, walk-forward validation, "
        "and data-snooping controls.</div>",
        unsafe_allow_html=True,
    )


def page_data_quality() -> None:
    section_header("Data Quality Layer", "Explicit source tiers · manifest · publication standards")

    manifest = safe_read_csv(OUT / "data_quality_manifest.csv")
    dq = safe_read_csv(OUT / "data_quality_report.csv")
    reg = safe_read_csv(OUT / "data_source_registry.csv")
    cmp_df = safe_read_csv(OUT / "data_source_comparison_usdmxn.csv")
    dl = safe_read_csv(OUT / "corridor_download_log.csv")
    layer_md = safe_read_markdown(REPORTS / "DATA_QUALITY_LAYER.md")
    upgrade_md = safe_read_markdown(REPORTS / "DATA_UPGRADE_REPORT.md")

    st.markdown(
        '<div class="callout">Every FX claim in this lab must record <strong>source</strong>, '
        "<strong>data tier</strong>, and <strong>quality flag</strong>. "
        "Prototype ≠ academic-grade ≠ trading-grade.</div>",
        unsafe_allow_html=True,
    )

    arch_badges = [
        ("Prototype", "yfinance / Stooq", "warning", "tier-4"),
        ("Academic-grade", "FRED / Fed H.10 / BIS", "success", "tier-1"),
        ("Trading-grade", "Bloomberg / LSEG / EBS", "info", "tier-2"),
        ("Proprietary edge", "Payment flows (authorized)", "gold", "tier-3"),
    ]
    cols = st.columns(4)
    for col, (label, desc, kind, css) in zip(cols, arch_badges):
        with col:
            st.markdown(
                f'<div class="info-card">'
                f'<span class="tier-pill {css}">{label}</span>'
                f'{status_badge(desc, kind)}'
                f"</div>",
                unsafe_allow_html=True,
            )

    current_source = "unknown"
    current_tier = "prototype"
    if dq is not None and not dq.empty:
        row0 = dq.iloc[0]
        current_source = str(row0.get("source", row0.get("source_name", "unknown")))
        current_tier = str(row0.get("architecture_tier", row0.get("data_tier", "prototype")))

    if current_source in ("yfinance", "stooq", "fallback_cache", "download"):
        st.markdown(
            '<div class="warning-box"><strong>Prototype data.</strong> Good for development, '
            "not enough for academic claims without rerunning on FRED/Fed H.10.</div>",
            unsafe_allow_html=True,
        )
    elif current_source in ("fred_h10", "fred", "fed_h10", "fed_h10_direct"):
        st.markdown(
            '<div class="callout"><strong>Academic-grade public source.</strong> '
            "Good for public research, but not executable trading data.</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="warning-box">Hedge economics remain incomplete until forward points '
        "and bid/ask data are added (trading-grade tier).</div>",
        unsafe_allow_html=True,
    )

    if cmp_df is not None and not cmp_df.empty:
        section_header("Source Comparison (USD/MXN)", "FRED H.10 vs yfinance")
        cr = cmp_df.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        cards = [
            ("FRED loaded", str(cr.get("fred_loaded", "—"))),
            ("yfinance loaded", str(cr.get("yfinance_loaded", "—"))),
            ("Return correlation", str(cr.get("daily_return_correlation", "—"))),
            ("Agree closely", str(cr.get("agree_closely", "—"))),
        ]
        for col, (t, v) in zip([c1, c2, c3, c4], cards):
            with col:
                st.markdown(metric_card(t, v), unsafe_allow_html=True)
        st.dataframe(cmp_df, width="stretch", hide_index=True)

    if manifest is not None:
        section_header("Quality Manifest", "All series in the research stack")
        ok = int((manifest["data_quality_flag"] == "OK").sum()) if "data_quality_flag" in manifest.columns else 0
        warn = int((manifest["data_quality_flag"] == "WARNING").sum()) if "data_quality_flag" in manifest.columns else 0
        fail = int((manifest["data_quality_flag"].isin(["FAIL", "MISSING"])).sum()) if "data_quality_flag" in manifest.columns else 0
        c1, c2, c3, c4 = st.columns(4)
        for col, (t, v) in zip([c1, c2, c3, c4], [("OK", ok), ("Warning", warn), ("Fail/Missing", fail), ("Series", len(manifest))]):
            with col:
                st.markdown(metric_card(t, str(v)), unsafe_allow_html=True)
        show_cols = [c for c in [
            "role", "label", "source_name", "tier_label", "data_quality_flag",
            "observation_count", "start_date", "end_date", "missing_price_pct",
        ] if c in manifest.columns]
        st.dataframe(manifest[show_cols], width="stretch", hide_index=True)
    elif dq is not None:
        section_header("Primary Series (USD/MXN)")
        row = dq.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        qflag = row.get("quality_flag", row.get("data_quality_flag", "—"))
        cards = [
            ("Source", str(row.get("source", row.get("source_name", "—")))),
            ("Data tier", str(row.get("architecture_tier", row.get("tier_label", row.get("data_tier", "—"))))),
            ("Observations", str(row.get("observation_count", "—"))),
            ("Quality flag", str(qflag)),
        ]
        for col, (t, v) in zip([c1, c2, c3, c4], cards):
            with col:
                st.markdown(metric_card(t, v), unsafe_allow_html=True)
        c5, c6, c7, c8 = st.columns(4)
        extra = [
            ("Date range", f"{row.get('start_date', '—')} → {row.get('end_date', '—')}"),
            ("Missing prices", str(row.get("missing_price_count", "—"))),
            ("Suspicious returns", str(row.get("suspicious_return_count_abs_gt_10pct", row.get("suspicious_return_count", "—")))),
            ("Stale price flags", str(row.get("stale_price_count", "—"))),
        ]
        for col, (t, v) in zip([c5, c6, c7, c8], extra):
            with col:
                st.markdown(metric_card(t, v), unsafe_allow_html=True)
        if qflag == "OK" and current_source in ("fred_h10", "fred", "fed_h10"):
            st.markdown(
                '<div class="callout">Recommendation: Use FRED H.10 as source of truth for '
                "public research; document limitations (no bid/ask, no forwards).</div>",
                unsafe_allow_html=True,
            )
        elif qflag in ("WARNING", "FAIL") or current_source in ("yfinance", "stooq"):
            st.markdown(
                '<div class="warning-box">Recommendation: Rerun pipelines with '
                "<code>preferred_source: fred_h10</code> before academic publication.</div>",
                unsafe_allow_html=True,
            )
        st.dataframe(dq, width="stretch")
    else:
        missing_section("python scripts/run_data_quality.py")

    if upgrade_md:
        with st.expander("Data upgrade report (FRED vs yfinance)"):
            st.markdown(upgrade_md)

    if layer_md:
        with st.expander("Data quality layer summary"):
            st.markdown(layer_md)

    arch_md = safe_read_markdown(REPORTS / "DATA_ARCHITECTURE.md")
    if arch_md:
        with st.expander("Data architecture (tiers and rules)"):
            st.markdown(arch_md)

    if reg is not None:
        section_header("Source Registry", f"{len(reg)} registered sources")
        tier_col = "tier_number" if "tier_number" in reg.columns else None
        if tier_col:
            st.dataframe(
                reg[["key", "name", "tier_number", "tier_label", "official_status", "cost_tier"]].head(20),
                width="stretch",
                hide_index=True,
            )
        else:
            st.dataframe(reg.head(20), width="stretch")

    if dl is not None:
        section_header("Corridor Download Log")
        st.dataframe(dl, width="stretch", hide_index=True)

    st.markdown(
        '<div class="warning-box">Prototype data (Tier 4) supports development. '
        "Publication-grade claims require Tier 1 reruns on FRED H.10 / BIS / official macro.</div>",
        unsafe_allow_html=True,
    )


def page_unanswered_fx_questions() -> None:
    from src.research_questions import (
        FLAGSHIP_QUESTION_ID,
        PRIORITY_LANES,
        get_research_question,
        research_questions_dataframe,
    )

    st.markdown(
        '<div class="hero-title">Major Unanswered Questions in FX</div>'
        '<div class="hero-subtitle">Testing whether currency decisions can improve even when currency forecasts fail.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="info-card"><h4>Highest-Level Thesis</h4>'
        "<p>FX markets may be mostly random-walk-like as price processes, but not all FX decisions are price forecasts. "
        "Regime, carry, news, flow, and stress variables may fail to predict exchange rates directly while still "
        "improving hedge governance, risk escalation, and decision discipline.</p></div>",
        unsafe_allow_html=True,
    )

    flagship = get_research_question(FLAGSHIP_QUESTION_ID)
    st.markdown(
        f'<div class="info-card" style="border-color:{C["gold"]}">'
        f'<h4>Flagship Research Lane — {flagship["title"]}</h4>'
        f'<p><strong>{flagship["core_question"]}</strong></p>'
        f'<p>{flagship["current_status"]}</p></div>',
        unsafe_allow_html=True,
    )

    section_header("Priority Research Lanes", "Five unresolved questions driving current lab work")
    cols = st.columns(min(5, len(PRIORITY_LANES)))
    for col, qid in zip(cols, PRIORITY_LANES):
        q = get_research_question(qid)
        badge = "Flagship" if qid == FLAGSHIP_QUESTION_ID else f"P{q['priority']}"
        with col:
            st.markdown(
                metric_card(
                    q["title"],
                    q["core_question"][:80] + ("…" if len(q["core_question"]) > 80 else ""),
                    subtitle=q["current_status"],
                    status=badge if qid == FLAGSHIP_QUESTION_ID else None,
                ),
                unsafe_allow_html=True,
            )
            st.caption(q["why_it_matters"][:120] + "…")
            st.markdown(f"**Modules:** `{', '.join(q['model_modules'][:3])}`")
            outs = q["output_files"][:2]
            if outs:
                st.markdown("**Outputs:** " + ", ".join(f"`{Path(o).name}`" for o in outs))

    section_header("Flagship Lane Results", "OOS hedge governance vs forecast failure")
    flagship_oos = safe_read_csv(OUT / "flagship_hedge_oos_scorecard.csv")
    fc = safe_read_csv(OUT / "model_zoo_forecast_scorecard.csv")
    if fc is not None and "model_beats_rw_rmse" in fc.columns and not fc.empty:
        beats = int(fc["model_beats_rw_rmse"].sum())
        st.markdown(
            f'<div class="info-card"><p><strong>Forecast layer:</strong> {beats}/{len(fc)} models beat random walk on RMSE '
            f"({100*beats/len(fc):.0f}%). Hedge usefulness evaluated separately.</p></div>",
            unsafe_allow_html=True,
        )
    if flagship_oos is not None and not flagship_oos.empty:
        ok = flagship_oos[flagship_oos.get("status", "ok") == "ok"]
        ff = ok[ok.get("cost_layer", "base") == "forward_full"] if not ok.empty else ok
        if not ff.empty:
            st.dataframe(
                ff.sort_values(["split", "cost_adjusted_risk_reduction"], ascending=[True, False])[
                    [
                        c
                        for c in [
                            "split",
                            "policy_name",
                            "policy_class",
                            "cost_adjusted_risk_reduction",
                            "hedge_turnover",
                            "turnover_efficiency",
                        ]
                        if c in ff.columns
                    ]
                ],
                width="stretch",
                hide_index=True,
            )
        turnover_cmp = safe_read_csv(OUT / "flagship_turnover_adjusted_comparison.csv")
        if turnover_cmp is not None and not turnover_cmp.empty:
            st.markdown("**Turnover-adjusted (forward_full)**")
            st.dataframe(turnover_cmp, width="stretch", hide_index=True)
    else:
        missing_section("python scripts/run_flagship_research_lane.py", "Flagship OOS hedge scorecard")

    r1r2 = safe_read_csv(OUT / "r1_r2_trend_quality_comparison.csv")
    r1r2_oos = safe_read_csv(OUT / "r1_r2_trend_quality_oos.csv")
    if r1r2 is not None and not r1r2.empty:
        section_header("R1 vs R2 Trend Quality")
        st.caption("Full sample")
        st.dataframe(r1r2, width="stretch", hide_index=True)
        if r1r2_oos is not None and not r1r2_oos.empty:
            st.caption("OOS test windows only")
            st.dataframe(r1r2_oos, width="stretch", hide_index=True)
    else:
        missing_section("python scripts/run_flagship_research_lane.py", "R1 vs R2 trend quality comparison")

    section_header("Full Research Question Registry")
    df = research_questions_dataframe()
    show = df[["question_id", "title", "priority", "current_status", "model_modules", "output_files"]]
    st.dataframe(show, width="stretch", hide_index=True)

    tab_roadmap, tab_flagship, tab_full = st.tabs(["Research Roadmap", "Flagship Lane", "Full Question Document"])
    with tab_roadmap:
        roadmap = safe_read_markdown(REPORTS / "FX_RESEARCH_ROADMAP.md")
        if roadmap:
            st.markdown(roadmap)
        else:
            missing_section(
                "python -c \"from pathlib import Path; from src.research_roadmap_reporting import generate_research_roadmap_report; generate_research_roadmap_report(Path('.'))\"",
                "FX research roadmap report",
            )
    with tab_flagship:
        flagship_md = safe_read_markdown(REPORTS / "FLAGSHIP_RESEARCH_LANE.md")
        if flagship_md:
            st.markdown(flagship_md)
        else:
            missing_section("python scripts/run_flagship_research_lane.py", "Flagship research lane report")
    with tab_full:
        unanswered = safe_read_markdown(REPORTS / "UNANSWERED_FX_QUESTIONS.md")
        if unanswered:
            st.markdown(unanswered)
        else:
            st.warning("Missing reports/UNANSWERED_FX_QUESTIONS.md")

    st.markdown(
        '<div class="warning-box"><strong>Interpretation:</strong> The lab should not chase endless models. '
        "Each model should answer one of the major research questions. The strongest current question is whether "
        "hedge decisions can improve when price forecasts fail.</div>",
        unsafe_allow_html=True,
    )


def page_fx_history() -> None:
    st.markdown(
        '<div class="hero-title">FX History & Academic Foundations</div>'
        '<div class="hero-subtitle">The 300-year road from gold flows and parity conditions to random-walk benchmarks, '
        "carry puzzles, order flow, and hedge-governance research.</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="info-card"><h4>Why This History Matters</h4>'
        "<p>BR3N Macro Labs does not claim to ignore prior research. FX Lab builds on major exchange-rate theories "
        "and puzzles. Random walk remains the benchmark. The strongest current thesis is not that FX can be predicted — "
        "it is that <strong>FX decisions may improve when prediction fails</strong>.</p></div>",
        unsafe_allow_html=True,
    )

    section_header("Timeline", "Major milestones in exchange-rate thought")
    timeline = [
        ("1700s", "Hume & specie-flow adjustment", "Trade imbalances, gold flows, and international adjustment"),
        ("1800s", "Gold standard", "Fixed rates with adjustment through prices, flows, and stress"),
        ("Early 1900s", "Purchasing Power Parity", "Gustav Cassel — long-run relative price alignment"),
        ("1940s–1970s", "Bretton Woods", "Managed FX; collapse ushered in modern floating rates"),
        ("1960s", "Mundell-Fleming", "Policy works differently under fixed vs floating regimes"),
        ("1976", "Dornbusch overshooting", "FX can overshoot when asset markets move faster than goods prices"),
        ("1983", "Meese-Rogoff", "Random walk is extremely hard to beat out of sample"),
        ("1980s onward", "UIP / carry puzzle", "High-yield currencies and crash-risk compensation"),
        ("1990s–2000s", "Microstructure & order flow", "Lyons, Evans — trades reveal pressure and information"),
        ("2008 onward", "Funding stress & CIP breakdown", "Forwards reflect balance-sheet scarcity"),
        ("2010s–present", "Machine learning & FX", "Complex models still struggle OOS after costs"),
    ]
    cols = st.columns(3)
    for i, (era, title, desc) in enumerate(timeline):
        with cols[i % 3]:
            st.markdown(
                f'<div class="info-card"><div class="metric-card-title">{era}</div>'
                f"<strong>{title}</strong><p style='margin-top:0.4rem;font-size:0.85rem'>{desc}</p></div>",
                unsafe_allow_html=True,
            )

    section_header("Nobel Connections")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f'<div class="info-card" style="border-color:{C["gold"]}">'
            "<h4>Robert Mundell — 1999</h4>"
            "<p>Nobel for monetary and fiscal policy under different exchange-rate regimes and optimum currency areas.</p>"
            "<p><em>Clearest Nobel link to exchange-rate regimes. FX Lab extends regime thinking to market regimes.</em></p></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="info-card"><h4>Paul Krugman — 2008</h4>'
            "<p>Nobel for international trade and economic geography — not FX forecasting directly.</p>"
            "<p><em>Important for trade, geography, production, and crisis context around currencies.</em></p></div>",
            unsafe_allow_html=True,
        )

    section_header("What Every FX Person Should Know")
    essentials = [
        ("Random walk is the benchmark", "If a model does not beat random walk OOS, be humble."),
        ("Spot and forwards are different", "Hedge economics require forward points, not spot charts alone."),
        ("Carry is not free money", "Carry may compensate investors for crash and liquidity risk."),
        ("UIP often fails", "One of the largest unresolved puzzles in FX."),
        ("PPP is long-run", "PPP matters for valuation — not usually as a daily trading rule."),
        ("Regime matters", "Fixed vs floating, calm vs stress, trend vs range change the problem."),
        ("Order flow matters", "FX is not only macro — trades and flows move prices."),
        ("Liquidity disappears in stress", "Hedging can become harder and more expensive when needed most."),
        ("Hedging is not trading", "Judged by risk reduction, cost, and policy discipline — not alpha."),
        ("Forecast failure ≠ decision failure", "The central FX Lab thesis."),
    ]
    cols = st.columns(2)
    for i, (title, desc) in enumerate(essentials):
        with cols[i % 2]:
            st.markdown(
                metric_card(title, desc),
                unsafe_allow_html=True,
            )

    st.markdown(
        f'<div class="info-card" style="border-color:{C["gold"]};margin-top:1rem">'
        "<h4>How FX Lab Fits</h4>"
        "<p>FX Lab accepts the history of exchange-rate research and the difficulty of beating random walk. "
        "The lab asks whether regime information can improve <strong>hedge-governance decisions</strong> even when "
        "it fails to improve price forecasts.</p></div>",
        unsafe_allow_html=True,
    )

    tab_public, tab_full = st.tabs(["Public Page", "Full Foundations Document"])
    with tab_public:
        md = safe_read_markdown(REPORTS / "publication" / "FX_HISTORY_PAGE.md")
        if md:
            st.markdown(md)
        else:
            missing_section("python scripts/build_site.py", "FX history public page")
    with tab_full:
        md_full = safe_read_markdown(REPORTS / "FX_HISTORY_AND_ACADEMIC_FOUNDATIONS.md")
        if md_full:
            st.markdown(md_full)
        else:
            st.warning("Missing reports/FX_HISTORY_AND_ACADEMIC_FOUNDATIONS.md")


def page_open_source_fx_ai_lab() -> None:
    """Open Source FX AI Model Lab — borrow, benchmark, improve, explain."""
    from src.models.model_registry import CATEGORY_LABELS, MODEL_REGISTRY, models_dataframe

    OS = {
        "bg": "#0a0e14",
        "surface": "#121a28",
        "border": "#2a3548",
        "text": "#e8edf4",
        "muted": "#94a3b8",
        "blue": "#5b9fd4",
        "green": "#3d9970",
    }

    st.markdown(
        f'<div style="background:{OS["bg"]};border:1px solid {OS["border"]};border-radius:8px;'
        f'padding:1.5rem 1.75rem;margin-bottom:1.25rem">'
        f'<div style="font-family:Cormorant Garamond,serif;font-size:1.85rem;color:{OS["text"]};'
        f'font-weight:600">Open Source FX AI Model Lab</div>'
        f'<div style="color:{OS["blue"]};font-size:1rem;margin-top:0.35rem;letter-spacing:0.06em">'
        f'Borrow. Benchmark. Improve. Explain.</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div style="background:{OS["surface"]};border-left:4px solid {OS["blue"]};'
        f'border:1px solid {OS["border"]};padding:1rem 1.25rem;border-radius:4px;margin-bottom:1rem">'
        "<strong>Warning:</strong> These models are not trading systems by themselves. They are research baselines. "
        "Every model must be tested out-of-sample with realistic transaction costs, drawdown controls, and "
        "no look-ahead bias before any trading use.</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div style="background:{OS["surface"]};border-left:4px solid {OS["green"]};'
        f'border:1px solid {OS["border"]};padding:1rem 1.25rem;border-radius:4px;margin-bottom:1.25rem">'
        "<strong>Core thesis:</strong> Most open-source FX AI models only predict the next candle from OHLC. "
        "BR3N FX Lab adds carry, macro, volatility regimes, news sentiment, better labels, transaction costs, "
        "and walk-forward backtesting.<br/><br/>"
        "<strong>Conclusion:</strong> The edge is not copying an open-source FX model. The edge is building a "
        "disciplined research pipeline that proves when a model works, when it fails, and why.</div>",
        unsafe_allow_html=True,
    )

    section_header("Model Registry", "Open-source baselines and experiment candidates")
    for cat_key, cat_label in CATEGORY_LABELS.items():
        st.markdown(f"**{cat_label}**")
        cols = st.columns(3)
        idx = 0
        for mid, meta in MODEL_REGISTRY.items():
            if meta.get("category") != cat_key:
                continue
            with cols[idx % 3]:
                imps = meta.get("br3n_improvement", [])
                imp_list = "".join(f"<li>{i}</li>" for i in imps[:4])
                st.markdown(
                    f'<div style="background:{OS["surface"]};border:1px solid {OS["border"]};'
                    f'border-radius:6px;padding:0.9rem 1rem;margin-bottom:0.75rem;min-height:11rem">'
                    f'<div style="font-size:0.7rem;color:{OS["muted"]};text-transform:uppercase">'
                    f'{meta.get("type", "")} · {meta.get("status", "")}</div>'
                    f'<div style="color:{OS["blue"]};font-weight:600;margin:0.35rem 0">{meta.get("title", mid)}</div>'
                    f'<div style="font-size:0.82rem;color:{OS["muted"]}">{meta.get("description", "")}</div>'
                    f'<ul style="font-size:0.75rem;color:{OS["muted"]};margin:0.5rem 0 0 1rem">{imp_list}</ul>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            idx += 1

    section_header("Architecture — BR3N FX Lab v1")
    st.code(
        """BR3N FX Lab v1
├── Baselines (LSTM, Transformer, TimesFM, Lag-Llama, FinRL/TensorTrade)
├── Data Layer (OHLCV, carry, macro, DXY/VIX, news)
├── Signal Engine (direction, return, vol, carry, confidence)
├── Trading Layer (long/short/flat, sizing, costs, drawdown)
└── Research Dashboard (Sharpe, drawdown, regime performance)""",
        language=None,
    )

    section_header("Research Questions")
    questions = [
        "Do time-series foundation models outperform LSTM and Transformer in FX?",
        "Does interest-rate carry improve directional accuracy?",
        "Does news sentiment help after central bank events?",
        "Trend continuation vs mean reversion — which is more predictable?",
        "Most predictable pair: EUR/USD, USD/JPY, GBP/USD, AUD/USD, USD/MXN, USD/INR?",
        "Does edge survive transaction costs?",
        "Can a model know when not to trade?",
        "Can BR3N explain why a trade works?",
    ]
    for q in questions:
        st.markdown(f"- {q}")

    section_header("Benchmarking Standard")
    st.markdown(
        "Same pair · timeframe · train/test split · costs · dates · risk limits · walk-forward method.\n\n"
        "**Metrics:** directional accuracy, precision/recall on signals, Sharpe, Sortino, max drawdown, "
        "win rate, profit factor, turnover, cost drag, performance by regime."
    )

    section_header("Build Roadmap")
    roadmap = [
        ("Phase 1", "Model registry + documentation (this page)"),
        ("Phase 2", "LSTM + Transformer wrappers"),
        ("Phase 3", "TimesFM + Lag-Llama adapters"),
        ("Phase 4", "Macro / carry / news feature pipeline"),
        ("Phase 5", "Walk-forward backtesting engine"),
        ("Phase 6", "Model comparison dashboard"),
        ("Phase 7", "Trade explanation engine"),
        ("Phase 8", "Publish research notes"),
    ]
    for phase, desc in roadmap:
        st.markdown(f"**{phase}:** {desc}")

    section_header("Registry Table")
    st.dataframe(models_dataframe(), use_container_width=True, hide_index=True)

    tab_pub, tab_full = st.tabs(["Public Page", "Full Lab Document"])
    with tab_pub:
        md = safe_read_markdown(REPORTS / "publication" / "OPEN_SOURCE_FX_AI_MODEL_LAB_PAGE.md")
        if md:
            st.markdown(md)
        else:
            missing_section("python scripts/build_site.py", "Open Source FX AI Model Lab page")
    with tab_full:
        md_full = safe_read_markdown(REPORTS / "OPEN_SOURCE_FX_AI_MODEL_LAB.md")
        if md_full:
            st.markdown(md_full)
        else:
            st.warning("Missing reports/OPEN_SOURCE_FX_AI_MODEL_LAB.md")


def page_research_questions() -> None:
    page_unanswered_fx_questions()


def page_publication_memo() -> None:
    section_header("Publication Memo", "Academic / pitch / publication workflow")

    st.markdown(
        "Refresh reports: `python scripts/generate_report.py` and "
        "`python scripts/generate_corridor_report.py`"
    )

    docs = [
        ("FX Lab Cover Page", REPORTS / "publication" / "FX_LAB_COVER_PAGE.md"),
        ("FX Lab One-Pager", REPORTS / "publication" / "FX_LAB_ONE_PAGER.md"),
        ("USD/MXN Flagship Memo", REPORTS / "USDMXN_FLAGSHIP_MEMO.md"),
        ("USD/MXN Regime Report", REPORTS / "usdmxn_regime_report.md"),
        ("Corridor Roadmap Report", REPORTS / "corridor_roadmap_report.md"),
        ("Unanswered FX Questions", REPORTS / "UNANSWERED_FX_QUESTIONS.md"),
        ("FX History & Foundations", REPORTS / "publication" / "FX_HISTORY_PAGE.md"),
        ("FX Research Roadmap", REPORTS / "FX_RESEARCH_ROADMAP.md"),
        ("Data Quality Layer", REPORTS / "DATA_QUALITY_LAYER.md"),
    ]
    for label, path in docs:
        content = safe_read_markdown(path)
        with st.expander(label, expanded=(label == "FX Lab One-Pager")):
            if content:
                st.markdown(content)
            else:
                st.markdown(f'<div class="missing-card">Missing: {path.name}</div>', unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
def _key_outputs_present() -> bool:
    required = [
        OUT / "strategy_scorecard.csv",
        OUT / "hedge_governance_scorecard.csv",
        PROC / "usdmxn_features_regimes.csv",
    ]
    return all(p.exists() for p in required)


@st.cache_resource(show_spinner="First load: fetching FX data and building research outputs…")
def ensure_dashboard_data() -> bool:
    """
    Streamlit Cloud has no local CSV cache — bootstrap pipelines when outputs are missing.
    """
    if _key_outputs_present():
        return True
    try:
        from src.data_loader import load_config, load_or_fetch
        from src.features import build_features
        from src.regimes import classify_regimes
        from src.backtest import scorecard, walk_forward_scorecard
        from src.flow_proxies import add_calendar_flow_proxies
        from src.flow_pressure_tests import run_flow_pressure_tests, save_flow_pressure_results
        from src.hedge_governance import run_all_hedge_governance, save_governance_outputs
        from src.random_walk_validity import build_random_walk_validity_map, save_validity_map
        from src.corridor_runner import run_corridor_roadmap

        cfg = load_config()
        OUT.mkdir(parents=True, exist_ok=True)
        PROC.mkdir(parents=True, exist_ok=True)

        prices, _ = load_or_fetch(cfg)
        feat = classify_regimes(build_features(prices, cfg), cfg)
        feat.to_csv(PROC / "usdmxn_features_regimes.csv")
        scorecard(feat, cfg).to_csv(OUT / "strategy_scorecard.csv", index=False)
        wf_is, wf_oos = walk_forward_scorecard(feat, cfg)
        wf_oos.to_csv(OUT / "walkforward_oos.csv", index=False)

        flow = add_calendar_flow_proxies(feat, corridor="USD_MXN")
        flow.to_csv(PROC / "usdmxn_features_regimes_flow.csv", index=False)
        save_flow_pressure_results(run_flow_pressure_tests(flow))
        hg_sc, hg_det = run_all_hedge_governance(
            flow, cfg, exposures=["us_entity_long_mxn", "mx_entity_usd_liabilities"]
        )
        save_governance_outputs(hg_sc, hg_det, cfg=cfg)
        save_validity_map(build_random_walk_validity_map(flow))

        try:
            from src.research_runner import run_full_research_pipeline
            run_full_research_pipeline(cfg)
        except Exception:
            pass

        try:
            run_corridor_roadmap(cfg)
        except Exception:
            pass

        return True
    except Exception as exc:
        st.error(f"Could not build research data: {exc}")
        return False


def main() -> None:
    st.set_page_config(
        page_title="BR3N Macro Labs — FX Lab",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(LUXURY_CSS, unsafe_allow_html=True)

    if not _key_outputs_present():
        ensure_dashboard_data()

    with st.sidebar:
        if FX_LOGO.exists():
            st.markdown('<div class="logo-frame">', unsafe_allow_html=True)
            st.image(str(FX_LOGO), width="stretch")
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="sidebar-brand">BR3N MACRO LABS</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-tag">FX LAB</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-motto">{BRAND_MOTTO}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="color:rgba(232,237,244,0.65);font-size:0.76rem;margin-bottom:1rem;line-height:1.45">'
            f"{FX_LAB_TAGLINE}</div>",
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", PAGES, label_visibility="collapsed")
        st.markdown("---")
        st.markdown(
            f'<span class="pill pill-neutral">Research Only</span> '
            f'<span class="pill pill-gold">Not Investment Advice</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p style="font-size:0.72rem;color:{C["muted"]};margin-top:0.75rem">'
            "Risk-framing only. Does not place trades.</p>",
            unsafe_allow_html=True,
        )

    renderers = {
        "Executive Overview": page_executive_overview,
        "Random-Walk Lab": page_random_walk_lab,
        "Regime Intelligence": page_regime_intelligence,
        "Model Zoo": page_model_zoo,
        "Corridor Roadmap": page_corridor_roadmap,
        "Hedge Governance": page_hedge_governance,
        "Flow Pressure": page_flow_pressure,
        "News & Macro Stress": page_news_macro_stress,
        "Carry & UIP Lab": page_carry_uip_lab,
        "Unanswered FX Questions": page_unanswered_fx_questions,
        "FX History": page_fx_history,
        "Open Source FX AI Lab": page_open_source_fx_ai_lab,
        "Academic Tests": page_academic_tests,
        "Data Quality": page_data_quality,
        "FX Desk Command Center": page_fx_desk_command_center,
        "Publication Memo": page_publication_memo,
    }

    renderers[page]()
    footer_disclaimer()


if __name__ == "__main__":
    main()
