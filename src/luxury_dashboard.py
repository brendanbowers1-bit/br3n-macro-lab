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

# ── Brand palette ─────────────────────────────────────────────────────────────
C = {
    "bg": "#080A0F",
    "panel": "#111827",
    "border": "#273244",
    "text": "#F8FAFC",
    "text2": "#94A3B8",
    "muted": "#64748B",
    "gold": "#D4AF37",
    "cyan": "#38BDF8",
    "green": "#22C55E",
    "amber": "#F59E0B",
    "red": "#EF4444",
    "purple": "#A78BFA",
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
    template="plotly_dark",
    paper_bgcolor=C["bg"],
    plot_bgcolor=C["panel"],
    font=dict(family="Inter, SF Pro Display, Helvetica Neue, Arial, sans-serif", color=C["text2"]),
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
    "Lab Portfolio",
    "Executive Overview",
    "FX Desk Command Center",
    "Random-Walk Lab",
    "Regime Intelligence",
    "Corridor Roadmap",
    "Hedge Governance",
    "Flow Pressure",
    "Academic Tests",
    "Data Quality",
    "Research Questions",
    "Publication Memo",
]

# ── CSS ───────────────────────────────────────────────────────────────────────
LUXURY_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{
    font-family: Inter, "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
}}
.stApp {{
    background-color: {C["bg"]};
    color: {C["text"]};
}}
section[data-testid="stSidebar"] {{
    background-color: {C["panel"]};
    border-right: 1px solid {C["border"]};
}}
section[data-testid="stSidebar"] .stRadio label {{
    color: {C["text2"]} !important;
}}
.hero-title {{
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: {C["gold"]};
    margin-bottom: 0.25rem;
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
    font-size: 1.35rem;
    font-weight: 600;
    color: {C["text"]};
    border-left: 3px solid {C["gold"]};
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
    background: linear-gradient(135deg, rgba(212,175,55,0.08), rgba(17,24,39,0.95));
    border: 1px solid {C["border"]};
    border-left: 3px solid {C["gold"]};
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
    color: {C["gold"]};
    margin: 0 0 0.5rem 0;
    font-size: 0.95rem;
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
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: {C["gold"]};
    margin-bottom: 0.25rem;
}}
.sidebar-tag {{
    font-size: 0.72rem;
    color: {C["muted"]};
    line-height: 1.4;
    margin-bottom: 1.5rem;
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
def page_lab_portfolio() -> None:
    """Umbrella lab portfolio — three verticals under BR3N Macro Labs."""
    st.markdown(
        '<div class="hero-title">BR3N MACRO LABS</div>'
        '<div class="hero-subtitle">Markets. Images. Materials. Systems.</div>'
        '<div class="hero-tagline">BR3N Macro Labs explores markets, images, and materials through '
        "AI-assisted experimentation, evidence, and design.</div>",
        unsafe_allow_html=True,
    )

    portfolio_md = safe_read_markdown(REPORTS / "LAB_PORTFOLIO.md")
    cover_md = safe_read_markdown(REPORTS / "publication" / "LAB_COVER_PAGE.md")

    public_base = "https://brendanbowers1-bit.github.io/br3n-macro-lab"

    verticals = [
        {
            "title": "FX Lab",
            "subtitle": "Conditional forecastability, payment-corridor risk, and hedge governance.",
            "description": (
                "The FX Lab studies when currency markets become less random by testing regime models "
                "against random-walk benchmarks, trading-cost realities, and hedge-governance scorecards."
            ),
            "outputs": [
                "FX regime dashboard",
                "random-walk tests",
                "corridor roadmap",
                "hedge governance scorecards",
                "FX desk command center",
                "data quality reports",
            ],
            "status": "Active prototype",
            "color": C["cyan"],
            "public_url": f"{public_base}/fx-lab.html",
        },
        {
            "title": "BR3N Photography",
            "subtitle": "Fine-art photography, visual systems, and luxury print research.",
            "description": (
                "BR3N Photography develops black-and-white fine-art photography, urban abstraction, "
                "AI-assisted concept work, and gallery-ready visual systems for prints and creative collections."
            ),
            "outputs": [
                "print collections",
                "black-and-white architectural series",
                "gallery-ready edits",
                "product mockups",
                "artist statements",
                "visual identity system",
            ],
            "status": "Creative studio vertical",
            "color": C["gold"],
            "public_url": f"{public_base}/photography.html",
        },
        {
            "title": "Metastable Hydride Superconductor Initiative",
            "subtitle": "Speculative materials research into metastable hydrides and ambient-pressure superconductivity pathways.",
            "description": (
                "A computational and experimental-roadmap project exploring whether hydrogen-deficient hydrides "
                "can be used as parent phases for hypothetical hydrogen-inserted metastable derivatives."
            ),
            "flagship": "Mg₂IrH₅ → Mg₂IrH₆",
            "outputs": [
                "technical brief",
                "literature map",
                "computational workflow",
                "experimental roadmap",
                "safety and replication plan",
                "outreach templates",
                "fundraising brief",
            ],
            "status": "Speculative research planning. No verified experimental result.",
            "color": C["purple"],
            "public_url": f"{public_base}/mhsi.html",
            "disclaimer": (
                "This initiative does not claim discovery of a superconductor or verified synthesis of Mg₂IrH₆. "
                "All candidate phases require computational validation, experimental safety review, "
                "and independent replication."
            ),
        },
    ]

    st.markdown(
        '<div class="callout">Locally, all three verticals live under this dashboard. '
        f'Publicly, each vertical has its own page at <a href="{public_base}/">{public_base}/</a>.</div>',
        unsafe_allow_html=True,
    )

    section_header("Lab Verticals", "Three disciplines under one umbrella")
    for v in verticals:
        outs = ", ".join(v["outputs"])
        flagship_html = ""
        if v.get("flagship"):
            flagship_html = f'<p><strong>Flagship system:</strong> {v["flagship"]}</p>'
        public_html = ""
        if v.get("public_url"):
            public_html = f'<p><strong>Public page:</strong> <a href="{v["public_url"]}">{v["public_url"]}</a></p>'
        disclaimer_html = ""
        if v.get("disclaimer"):
            disclaimer_html = (
                f'<p style="font-size:0.85rem;opacity:0.85;margin-top:0.5rem"><em>{v["disclaimer"]}</em></p>'
            )
        st.markdown(
            f'<div class="info-card" style="border-left:3px solid {v["color"]}">'
            f'<h4>{v["title"]}</h4>'
            f'<p><em>{v["subtitle"]}</em></p>'
            f'<p>{v["description"]}</p>'
            f'{flagship_html}'
            f'{public_html}'
            f'<p><strong>Outputs:</strong> {outs}</p>'
            f'<p>{status_badge(v["status"], "info")}</p>'
            f'{disclaimer_html}'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="callout"><strong>Shared theme:</strong> BR3N Macro Labs studies complex systems and '
        "turns them into structured research, visual intelligence, and experimental roadmaps.</div>",
        unsafe_allow_html=True,
    )

    if portfolio_md:
        with st.expander("Full lab portfolio"):
            st.markdown(portfolio_md)
    if cover_md:
        with st.expander("Public cover page"):
            st.markdown(cover_md)

    st.markdown(
        '<div class="warning-box">'
        "BR3N Macro Labs is an independent research and creative project — not affiliated with any "
        "employer, university, financial institution, payment company, data vendor, laboratory, or "
        "research institution unless explicitly stated.<br><br>"
        "FX Lab: education and risk-framing only — not investment advice.<br>"
        "Metastable Hydride Initiative: speculative planning — not verified experimental results.<br>"
        "BR3N Photography: creative works and visual research."
        "</div>",
        unsafe_allow_html=True,
    )


def page_executive_overview() -> None:
    st.markdown(
        '<div class="hero-title">BR3N MACRO LABS</div>'
        '<div class="hero-subtitle">FX Lab — Regime Intelligence for Conditional Forecastability and Hedge Governance</div>'
        '<div class="hero-tagline">An AI-assisted research lab testing when currency markets become less random — '
        "and when regime logic is useful for trading, hedging, and treasury decision-making.</div>",
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
    section_header("Data Quality", "Prototype vs academic-grade vs trading-grade data")

    dq = safe_read_csv(OUT / "data_quality_report.csv")
    reg = safe_read_csv(OUT / "data_source_registry.csv")
    dl = safe_read_csv(OUT / "corridor_download_log.csv")

    tier_badges = [
        ("Prototype", "Tier 4 — yfinance/Stooq", "warning"),
        ("Academic-grade", "Tier 1 — FRED/H.10/BIS", "success"),
        ("Trading-grade", "Tier 2 — Bloomberg/LSEG", "info"),
        ("Proprietary edge", "Tier 3 — payment flows", "gold"),
    ]
    cols = st.columns(4)
    for col, (label, desc, kind) in zip(cols, tier_badges):
        with col:
            st.markdown(
                f'<div class="info-card">{status_badge(label, kind)}<p style="margin-top:0.5rem">{desc}</p></div>',
                unsafe_allow_html=True,
            )

    if dq is not None:
        row = dq.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        cards = [
            ("Observations", str(row.get("observation_count", "—"))),
            ("Date Range", f"{row.get('start_date', '—')} → {row.get('end_date', '—')}"),
            ("Missing Prices", str(row.get("missing_price_count", "—"))),
            ("Quality Flag", str(row.get("data_quality_flag", "—"))),
        ]
        for col, (t, v) in zip([c1, c2, c3, c4], cards):
            with col:
                st.markdown(metric_card(t, v), unsafe_allow_html=True)
        st.dataframe(dq, width="stretch")
    else:
        missing_section("python scripts/run_data_quality.py")

    if reg is not None:
        section_header("Data Source Registry")
        st.dataframe(reg, width="stretch")
    else:
        missing_section("python scripts/export_data_sources.py")

    if dl is not None:
        section_header("Corridor Download Status")
        st.dataframe(dl, width="stretch")

    st.markdown(
        '<div class="info-card"><h4>Recommended Next Upgrade</h4>'
        "<p><strong>Current (yfinance):</strong> FRED / Fed H.10 / BIS / central bank data.<br>"
        "<strong>Hedge claims:</strong> forwards, forward points, bid/ask spreads, transaction costs.<br>"
        "<strong>Corridor-flow claims:</strong> official remittance data or legally usable payment-flow data.</p></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="warning-box">A model that works on prototype data is not publication-grade or '
        "trading-grade until retested on official or professional market data.</div>",
        unsafe_allow_html=True,
    )


def page_research_questions() -> None:
    st.markdown(
        '<div class="hero-subtitle">BR3N Macro Labs studies when markets become less random — '
        "not to claim certainty, but to improve evidence, discipline, and risk decisions.</div>",
        unsafe_allow_html=True,
    )

    md = safe_read_markdown(REPORTS / "research_questions.md")
    if md:
        st.markdown(md)
    else:
        questions = [
            "When does random walk fail in FX?",
            "What creates conditional forecastability?",
            "Can payment-flow proxies predict currency pressure?",
            "Can regime-based hedging beat static hedge policy?",
            "Is FX partly balance-sheet constrained?",
            "Can a model fail as a forecast but still help hedge governance?",
            "When should a treasury team intentionally not adjust the hedge?",
        ]
        for i, q in enumerate(questions, 1):
            st.markdown(f"**{i}.** {q}")


def page_publication_memo() -> None:
    section_header("Publication Memo", "Academic / pitch / publication workflow")

    st.markdown(
        "Refresh reports: `python scripts/generate_report.py` and "
        "`python scripts/generate_corridor_report.py`"
    )

    docs = [
        ("One-Pager", REPORTS / "publication" / "ONE_PAGER.md"),
        ("Corridor Roadmap Report", REPORTS / "corridor_roadmap_report.md"),
        ("USD/MXN Regime Report", REPORTS / "usdmxn_regime_report.md"),
        ("Data Strategy", REPORTS / "DATA_STRATEGY.md"),
    ]
    for label, path in docs:
        content = safe_read_markdown(path)
        with st.expander(label, expanded=(label == "One-Pager")):
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
        save_governance_outputs(hg_sc, hg_det)
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
        page_title="BR3N Macro Labs — FX Regime Intelligence",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(LUXURY_CSS, unsafe_allow_html=True)

    if not _key_outputs_present():
        ensure_dashboard_data()

    with st.sidebar:
        st.markdown('<div class="sidebar-brand">BR3N MACRO LABS</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sidebar-tag">Markets. Images. Materials. Systems.</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Navigation", PAGES, label_visibility="collapsed")
        st.markdown("---")
        st.markdown(
            f'<span class="pill pill-neutral">Research Only</span> '
            f'<span class="pill pill-gold">No Live Trading</span>',
            unsafe_allow_html=True,
        )

    renderers = {
        "Lab Portfolio": page_lab_portfolio,
        "Executive Overview": page_executive_overview,
        "FX Desk Command Center": page_fx_desk_command_center,
        "Random-Walk Lab": page_random_walk_lab,
        "Regime Intelligence": page_regime_intelligence,
        "Corridor Roadmap": page_corridor_roadmap,
        "Hedge Governance": page_hedge_governance,
        "Flow Pressure": page_flow_pressure,
        "Academic Tests": page_academic_tests,
        "Data Quality": page_data_quality,
        "Research Questions": page_research_questions,
        "Publication Memo": page_publication_memo,
    }

    renderers[page]()
    footer_disclaimer()


if __name__ == "__main__":
    main()
