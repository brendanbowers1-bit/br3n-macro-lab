"""Plotly chart builders — Bowers Frontier institutional theme."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.dashboard.styles import COLORS, PLOTLY_LAYOUT
from src.visuals.vsi_charts import COMP_COLS, COMPONENT_LABELS, corridor_summary

RESEARCH_FOOTNOTE = "Research estimate under stated assumptions. Not investment advice."


def _base_layout(fig: go.Figure, title: str, subtitle: str = "", methodology: str = "") -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_layout(title={"text": f"<b>{title}</b><br><sup style='color:#94A3B8'>{subtitle}</sup>" if subtitle else f"<b>{title}</b>"})
    note = methodology or RESEARCH_FOOTNOTE
    fig.add_annotation(
        text=note, xref="paper", yref="paper", x=0, y=-0.18, showarrow=False,
        font=dict(size=9, color=COLORS["text_secondary"]),
    )
    fig.update_layout(margin=dict(b=100))
    return fig


def ranked_bar(df: pd.DataFrame, x: str, y: str, title: str, subtitle: str = "", ascending: bool = False, color_col: str | None = None) -> go.Figure:
    if df.empty or x not in df.columns or y not in df.columns:
        return _empty_fig(title, "No data available")
    d = df.sort_values(y, ascending=ascending)
    fig = px.bar(d, x=x, y=y, color=color_col or y, color_continuous_scale=[[0, COLORS["risk_red"]], [0.5, COLORS["warning_amber"]], [1, COLORS["accent_cyan"]]], template="plotly_dark")
    return _base_layout(fig, title, subtitle)


def stacked_component_breakdown(row: pd.Series, title: str = "Value loss components") -> go.Figure:
    labels, vals = [], []
    for col in COMP_COLS:
        if col in row.index and pd.notna(row[col]) and row[col] > 0:
            labels.append(COMPONENT_LABELS.get(col, col))
            vals.append(float(row[col]) * 100 if row[col] < 1 else float(row[col]))
    if not vals:
        return _empty_fig(title, "No component columns")
    fig = go.Figure(go.Bar(x=labels, y=vals, marker_color=COLORS["accent_cyan"]))
    fig.update_layout(barmode="stack")
    return _base_layout(fig, title, "Stacked loss components (% of sent value)")


def waterfall_value_loss(row: pd.Series, title: str = "Value waterfall ($100 sent)") -> go.Figure:
    parts = [
        ("Sent", 100),
        ("Fees", -float(row.get("explicit_fee_loss_pct", 0) or 0) * 100),
        ("FX spread", -float(row.get("fx_spread_loss_pct", 0) or 0) * 100),
        ("Timing", -float(row.get("timing_loss_pct", 0) or 0) * 100),
        ("Volatility", -float(row.get("volatility_loss_pct", 0) or 0) * 100),
        ("Inflation", -float(row.get("inflation_erosion_pct", 0) or 0) * 100),
        ("Payout friction", -float(row.get("payout_friction_pct", 0) or 0) * 100),
        ("Usable value", float(row.get("real_usable_value_delivered_pct", row.get("value_survival_index", 0) / 100 if "value_survival_index" in row.index else 0)) * (1 if row.get("real_usable_value_delivered_pct", 0) and row.get("real_usable_value_delivered_pct", 0) > 1 else 100)),
    ]
    measure = ["absolute"] + ["relative"] * (len(parts) - 2) + ["total"]
    fig = go.Figure(go.Waterfall(
        name="Value", orientation="v", measure=measure,
        x=[p[0] for p in parts], y=[p[1] for p in parts],
        connector={"line": {"color": COLORS["border"]}},
        increasing={"marker": {"color": COLORS["success_green"]}},
        decreasing={"marker": {"color": COLORS["risk_red"]}},
        totals={"marker": {"color": COLORS["accent_gold"]}},
    ))
    return _base_layout(fig, title, "Waterfall decomposition of $100 sent")


def sankey_value_survival(row: pd.Series, title: str = "Value survival flow") -> go.Figure:
    sent = 100.0
    fees = float(row.get("explicit_fee_loss_pct", 0) or 0) * 100
    fx = float(row.get("fx_spread_loss_pct", 0) or 0) * 100
    timing = float(row.get("timing_loss_pct", 0) or 0) * 100
    vol = float(row.get("volatility_loss_pct", 0) or 0) * 100
    infl = float(row.get("inflation_erosion_pct", 0) or 0) * 100
    payout = float(row.get("payout_friction_pct", 0) or 0) * 100
    usable = max(sent - fees - fx - timing - vol - infl - payout, 0)
    labels = ["$100 sent", "Fees", "FX spread", "Timing", "Volatility", "Inflation", "Payout friction", "Usable value"]
    fig = go.Figure(data=[go.Sankey(
        node=dict(pad=12, thickness=14, line=dict(color=COLORS["border"], width=0.5),
                  label=labels, color=[COLORS["accent_gold"], COLORS["risk_red"], COLORS["risk_red"], COLORS["warning_amber"], COLORS["warning_amber"], COLORS["muted_purple"], COLORS["muted_purple"], COLORS["success_green"]]),
        link=dict(source=[0, 0, 0, 0, 0, 0, 0], target=[1, 2, 3, 4, 5, 6, 7],
                  value=[max(fees, 0.01), max(fx, 0.01), max(timing, 0.01), max(vol, 0.01), max(infl, 0.01), max(payout, 0.01), max(usable, 0.01)],
                  color="rgba(56,189,248,0.35)"),
    )])
    return _base_layout(fig, title, "Sankey: value leakage channels")


def heatmap_quality(df: pd.DataFrame, x: str, y: str, z: str, title: str) -> go.Figure:
    if df.empty:
        return _empty_fig(title)
    pivot = df.pivot_table(index=y, columns=x, values=z, aggfunc="mean")
    fig = px.imshow(pivot, color_continuous_scale=[[0, COLORS["risk_red"]], [0.5, COLORS["warning_amber"]], [1, COLORS["success_green"]]], aspect="auto")
    return _base_layout(fig, title)


def scatter_frontier(df: pd.DataFrame, x: str, y: str, hover: str | None, title: str, subtitle: str = "") -> go.Figure:
    if df.empty:
        return _empty_fig(title)
    fig = px.scatter(df, x=x, y=y, hover_name=hover, color=y, color_continuous_scale=[[0, COLORS["accent_cyan"]], [1, COLORS["accent_gold"]]], template="plotly_dark")
    return _base_layout(fig, title, subtitle)


def finality_ladder(scores: dict[str, float], title: str = "Finality ladder") -> go.Figure:
    stages = list(scores.keys())
    vals = list(scores.values())
    fig = go.Figure(go.Bar(x=vals, y=stages, orientation="h", marker_color=COLORS["accent_cyan"]))
    fig.update_xaxis(range=[0, 100])
    return _base_layout(fig, title, "Settlement stage proximity scores")


def sensitivity_band_chart(df: pd.DataFrame, entity_col: str, value_col: str, case_col: str = "sensitivity_case", title: str = "Sensitivity bands") -> go.Figure:
    if df.empty or entity_col not in df.columns:
        return _empty_fig(title)
    fig = px.line(df.sort_values([entity_col, case_col]), x=case_col, y=value_col, color=entity_col, markers=True, template="plotly_dark")
    return _base_layout(fig, title)


def rank_stability_heatmap(df: pd.DataFrame, title: str = "Rank stability") -> go.Figure:
    if df.empty:
        return _empty_fig(title)
    if "entity" in df.columns and "metric" in df.columns and "rank_stability" in df.columns:
        pivot = df.pivot_table(index="entity", columns="metric", values="rank_stability", aggfunc="first")
    elif "corridor" in df.columns and "rank_stability_score" in df.columns:
        pivot = df.set_index("corridor")[["rank_stability_score"]]
    else:
        numeric = df.select_dtypes("number")
        pivot = numeric.head(20) if not numeric.empty else pd.DataFrame()
    if pivot.empty:
        return _empty_fig(title)
    fig = px.imshow(pivot, color_continuous_scale=[[0, COLORS["risk_red"]], [1, COLORS["success_green"]]], aspect="auto")
    return _base_layout(fig, title)


def gauge_card(value: float, title: str, max_val: float = 100) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        number={"suffix": "", "font": {"color": COLORS["text_primary"]}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": COLORS["text_secondary"]},
            "bar": {"color": COLORS["accent_gold"]},
            "bgcolor": COLORS["surface"],
            "bordercolor": COLORS["border"],
            "steps": [
                {"range": [0, 40], "color": "rgba(239,68,68,0.25)"},
                {"range": [40, 70], "color": "rgba(245,158,11,0.2)"},
                {"range": [70, max_val], "color": "rgba(34,197,94,0.2)"},
            ],
        },
        title={"text": title, "font": {"color": COLORS["text_secondary"], "size": 12}},
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=260)
    return fig


def radar_component_chart(row: pd.Series, cols: list[str], labels: list[str] | None = None, title: str = "Component radar") -> go.Figure:
    labels = labels or cols
    vals = [float(row.get(c, 0) or 0) for c in cols]
    vals_closed = vals + [vals[0]]
    labels_closed = labels + [labels[0]]
    fig = go.Figure(data=go.Scatterpolar(r=vals_closed, theta=labels_closed, fill="toself", line_color=COLORS["accent_cyan"]))
    fig.update_layout(polar=dict(bgcolor=COLORS["background"], radialaxis=dict(visible=True, gridcolor=COLORS["border"])))
    return _base_layout(fig, title)


def global_risk_heatmap(vsi: pd.DataFrame, settlement: pd.DataFrame, stablecoin: pd.DataFrame) -> go.Figure:
    rows = []
    if not vsi.empty and "corridor" in vsi.columns and "value_survival_index" in vsi.columns:
        s = corridor_summary(vsi)
        for _, r in s.head(10).iterrows():
            rows.append({"Domain": "VSI", "Entity": r["corridor"], "Score": 100 - float(r["value_survival_index"])})
    if not settlement.empty and "entity" in settlement.columns and "settlement_drag_index" in settlement.columns:
        top = settlement.nsmallest(5, "settlement_drag_index")
        for _, r in top.iterrows():
            rows.append({"Domain": "Settlement", "Entity": str(r["entity"])[:40], "Score": 100 - float(r.get("settlement_drag_index", 50))})
    if not stablecoin.empty and "stablecoin" in stablecoin.columns and "stablecoin_finality_quality_index" in stablecoin.columns:
        for _, r in stablecoin.iterrows():
            rows.append({"Domain": "Stablecoin", "Entity": r["stablecoin"], "Score": 100 - float(r.get("stablecoin_finality_quality_index", 50))})
    if not rows:
        return _empty_fig("Global risk heatmap", "Connect pipeline outputs")
    d = pd.DataFrame(rows)
    pivot = d.pivot_table(index="Entity", columns="Domain", values="Score", aggfunc="mean")
    fig = px.imshow(pivot.fillna(0), color_continuous_scale=[[0, COLORS["success_green"]], [0.5, COLORS["warning_amber"]], [1, COLORS["risk_red"]]], aspect="auto")
    return _base_layout(fig, "Global risk heatmap", "Higher = more leakage / fragility (inverted indices)")


def sankey_risk_relocation(row: pd.Series, title: str = "Risk relocation") -> go.Figure:
    labels = ["Counterparty risk ↓", "Issuer risk ↑", "Reserve risk ↑", "Off-ramp risk ↑", "Compliance risk ↑"]
    fig = go.Figure(data=[go.Sankey(
        node=dict(label=labels, pad=10, thickness=12, color=[COLORS["success_green"], COLORS["risk_red"], COLORS["risk_red"], COLORS["warning_amber"], COLORS["muted_purple"]]),
        link=dict(source=[0, 0, 0, 0], target=[1, 2, 3, 4],
                  value=[25, 25, 25, 25], color="rgba(212,175,55,0.35)"),
    )])
    return _base_layout(fig, title, "Conceptual risk relocation under SWC spec")


def tornado_assumptions(df: pd.DataFrame, entity_col: str, low_col: str, high_col: str, base_col: str, title: str) -> go.Figure:
    if df.empty or entity_col not in df.columns:
        return _empty_fig(title)
    d = df.head(12).copy()
    fig = go.Figure()
    if low_col in d.columns:
        fig.add_trace(go.Bar(y=d[entity_col], x=d[low_col], orientation="h", name="Conservative", marker_color=COLORS["accent_cyan"]))
    if high_col in d.columns:
        fig.add_trace(go.Bar(y=d[entity_col], x=d[high_col], orientation="h", name="Severe", marker_color=COLORS["risk_red"]))
    fig.update_layout(barmode="overlay")
    return _base_layout(fig, title)


def _empty_fig(title: str, subtitle: str = "Run reproduction scripts to generate outputs") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=subtitle, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(color=COLORS["text_secondary"]))
    return _base_layout(fig, title, subtitle)
