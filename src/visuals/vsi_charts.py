"""Shared VSI chart builders for dashboard and publication visuals."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


COMPONENT_LABELS = {
    "explicit_fee_loss_pct": "Explicit fee",
    "fx_spread_loss_pct": "FX spread",
    "timing_loss_pct": "Timing loss",
    "volatility_loss_pct": "Volatility loss",
    "inflation_erosion_pct": "Inflation erosion",
    "payout_friction_pct": "Payout friction",
    "dollar_dependency_drag_pct": "Dollar drag",
    "trust_discount_pct": "Trust discount",
}

COMP_COLS = list(COMPONENT_LABELS.keys())


def corridor_summary(vsi: pd.DataFrame) -> pd.DataFrame:
    agg_dict = {
        "value_survival_index": ("value_survival_index", "mean"),
        "total_value_loss_pct": ("total_value_loss_pct", "mean"),
        "value_loss_usd_per_100": ("value_loss_usd_per_100", "mean"),
        "interpretation": ("interpretation", "first"),
        "data_quality_score": ("data_quality_score", "mean"),
        "mock_data_flag": ("mock_data_flag", "first"),
    }
    if "data_mode" in vsi.columns:
        agg_dict["data_mode"] = ("data_mode", "first")
    return (
        vsi.groupby("corridor", as_index=False)
        .agg(**agg_dict)
        .sort_values("value_survival_index", ascending=False)
    )


def chart_ranked_vsi(summary: pd.DataFrame) -> go.Figure:
    df = summary.sort_values("value_survival_index")
    fig = px.bar(
        df,
        x="corridor",
        y="value_survival_index",
        color="value_survival_index",
        color_continuous_scale="Teal",
        title="Value Survival Index by corridor (higher = more survives)",
        template="plotly_dark",
        text=df["value_survival_index"].round(1),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False, yaxis_range=[80, 100])
    return fig


def chart_loss_per_100(summary: pd.DataFrame) -> go.Figure:
    df = summary.sort_values("value_loss_usd_per_100", ascending=False)
    fig = px.bar(
        df,
        x="corridor",
        y="value_loss_usd_per_100",
        color="value_loss_usd_per_100",
        color_continuous_scale="Reds",
        title="Value lost per $100 sent (USD)",
        template="plotly_dark",
        text=df["value_loss_usd_per_100"].round(2),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
    return fig


def chart_component_breakdown(vsi: pd.DataFrame) -> go.Figure:
    agg = vsi.groupby("corridor")[COMP_COLS].mean().reset_index()
    melted = agg.melt(id_vars="corridor", var_name="component", value_name="loss_pct")
    melted["component"] = melted["component"].map(COMPONENT_LABELS)
    melted["loss_pct"] = melted["loss_pct"] * 100
    fig = px.bar(
        melted,
        x="corridor",
        y="loss_pct",
        color="component",
        barmode="stack",
        title="Cross-border value loss components (% of sent value)",
        template="plotly_dark",
    )
    fig.update_layout(xaxis_tickangle=-45, legend_title="Component")
    return fig


def chart_leakage_vs_volume(vsi: pd.DataFrame, remittance_flows: pd.DataFrame) -> go.Figure:
    vsi_c = corridor_summary(vsi)
    if remittance_flows.empty:
        fig = go.Figure()
        fig.update_layout(title="Remittance volume unavailable", template="plotly_dark")
        return fig
    flows = (
        remittance_flows.groupby("corridor", as_index=False)["remittance_usd"]
        .mean()
        .rename(columns={"remittance_usd": "avg_annual_remittance_usd"})
    )
    merged = vsi_c.merge(flows, on="corridor", how="left")
    merged["total_value_loss_pct"] = merged["total_value_loss_pct"] * 100
    fig = px.scatter(
        merged,
        x="avg_annual_remittance_usd",
        y="total_value_loss_pct",
        size="value_loss_usd_per_100",
        color="value_survival_index",
        hover_name="corridor",
        color_continuous_scale="Teal",
        title="Value leakage (%) vs average annual remittance volume",
        labels={
            "avg_annual_remittance_usd": "Avg annual remittance (USD)",
            "total_value_loss_pct": "Total value loss (%)",
        },
        template="plotly_dark",
    )
    fig.update_layout(
        xaxis_type="log",
        annotations=[
            dict(
                text="Research estimate — not investment advice",
                xref="paper", yref="paper", x=0, y=-0.18, showarrow=False,
                font=dict(size=11, color="#94a3b8"),
            )
        ],
    )
    return fig


def save_figure(fig: go.Figure, path: Path, width: int = 1100, height: int = 620) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    html_path = path.with_suffix(".html")
    fig.write_html(str(html_path), include_plotlyjs="cdn")
    try:
        fig.write_image(str(path), width=width, height=height, scale=2)
    except Exception:
        # kaleido optional — HTML always written
        path = html_path
    return path
