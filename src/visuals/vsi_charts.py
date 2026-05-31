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
        "vsi_core": ("vsi_core", "mean"),
        "vsi_risk_adjusted": ("vsi_risk_adjusted", "mean"),
        "vsi_extended": ("vsi_extended", "mean"),
        "total_value_loss_pct": ("total_value_loss_pct", "mean"),
        "value_loss_usd_per_100": ("value_loss_usd_per_100", "mean"),
        "interpretation": ("interpretation", "first"),
        "data_quality_score": ("data_quality_score", "mean"),
        "data_quality_grade": ("data_quality_grade", "first"),
        "mock_data_flag": ("mock_data_flag", "first"),
    }
    if "data_mode" in vsi.columns:
        agg_dict["data_mode"] = ("data_mode", "first")
    cols_present = {k: v for k, v in agg_dict.items() if v[0] in vsi.columns}
    return (
        vsi.groupby("corridor", as_index=False)
        .agg(**cols_present)
        .sort_values("value_survival_index", ascending=False)
    )


CHART_FOOTNOTE = (
    "Research estimate under stated assumptions. Sources: World Bank RPW, KNOMAD, IMF/WB macro. "
    "Not investment advice."
)


def _add_chart_notes(fig: go.Figure, methodology: str = "") -> go.Figure:
    note = CHART_FOOTNOTE
    if methodology:
        note = f"{methodology} · {note}"
    fig.update_layout(
        annotations=[
            dict(
                text=note,
                xref="paper", yref="paper", x=0, y=-0.22, showarrow=False,
                font=dict(size=10, color="#94a3b8"),
            )
        ],
        margin=dict(b=100),
    )
    return fig


def chart_ranked_vsi_by_col(summary: pd.DataFrame, col: str, title: str) -> go.Figure:
    if col not in summary.columns:
        return go.Figure()
    df = summary.sort_values(col)
    fig = px.bar(
        df, x="corridor", y=col, color=col,
        color_continuous_scale="Teal",
        title=title, template="plotly_dark",
        text=df[col].round(1),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
    return _add_chart_notes(fig, f"Index: {col}")


def chart_ranked_vsi(summary: pd.DataFrame) -> go.Figure:
    col = "vsi_risk_adjusted" if "vsi_risk_adjusted" in summary.columns else "value_survival_index"
    return chart_ranked_vsi_by_col(
        summary, col,
        "Value Survival Index (risk-adjusted) by corridor — higher = more survives",
    )


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
    return _add_chart_notes(fig)


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
    return _add_chart_notes(fig, "Stacked loss components (% of sent value)")


def chart_aggregate_welfare(welfare: pd.DataFrame) -> go.Figure:
    if welfare.empty or "aggregate_value_loss_usd" not in welfare.columns:
        return go.Figure()
    df = welfare.groupby("corridor", as_index=False)["aggregate_value_loss_usd"].sum()
    df = df.sort_values("aggregate_value_loss_usd", ascending=False).head(20)
    fig = px.bar(
        df, x="corridor", y="aggregate_value_loss_usd",
        title="Estimated aggregate welfare loss by corridor (USD)",
        template="plotly_dark", color="aggregate_value_loss_usd",
        color_continuous_scale="Reds",
    )
    fig.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
    return _add_chart_notes(fig, "KNOMAD flows × VSI loss estimate")


def chart_data_quality(vsi: pd.DataFrame) -> go.Figure:
    if "data_quality_score" not in vsi.columns:
        return go.Figure()
    df = vsi.groupby("corridor", as_index=False).agg(
        data_quality_score=("data_quality_score", "mean"),
        data_quality_grade=("data_quality_grade", "first"),
    ).sort_values("data_quality_score")
    fig = px.bar(
        df, x="corridor", y="data_quality_score", color="data_quality_score",
        title="Data quality score by corridor (0–100)",
        template="plotly_dark", color_continuous_scale="Blues",
        text=df["data_quality_grade"],
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False, yaxis_range=[0, 100])
    return _add_chart_notes(fig, "Official data rubric — see DATA_SOURCES.md")


def chart_sensitivity_ranges(summary: pd.DataFrame) -> go.Figure:
    if summary.empty or "vsi_risk_min" not in summary.columns:
        return go.Figure()
    df = summary.sort_values("vsi_risk_mean").head(25)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Range", x=df["corridor"], y=df["vsi_risk_max"] - df["vsi_risk_min"],
        base=df["vsi_risk_min"], marker_color="#5b9fd4",
    ))
    fig.add_trace(go.Scatter(
        x=df["corridor"], y=df["vsi_risk_mean"], mode="markers",
        name="Baseline mean", marker=dict(color="#fbbf24", size=8),
    ))
    fig.update_layout(
        title="VSI risk-adjusted range across sensitivity cases",
        template="plotly_dark", barmode="overlay", xaxis_tickangle=-45,
    )
    return _add_chart_notes(fig, "Conservative / baseline / severe timing & volatility weights")


def chart_rank_stability(rank_mat: pd.DataFrame) -> go.Figure:
    if rank_mat.empty:
        return go.Figure()
    cases = [c for c in rank_mat.columns if c != "corridor"]
    if not cases:
        return go.Figure()
    z = rank_mat.set_index("corridor")[cases].astype(float)
    fig = px.imshow(
        z, aspect="auto", color_continuous_scale="RdYlGn_r",
        title="Corridor rank stability across sensitivity cases",
        labels=dict(color="Rank (1=best survival)"),
        template="plotly_dark",
    )
    fig.update_layout(xaxis_title="Sensitivity case", yaxis_title="Corridor")
    return _add_chart_notes(fig, "Lower rank number = higher VSI")


def chart_official_vs_assumed(vsi: pd.DataFrame) -> go.Figure:
    source_cols = [
        ("fee_source", "Fee"), ("fx_margin_source", "FX margin"),
        ("inflation_source", "Inflation"), ("fx_volatility_source", "Volatility"),
        ("payout_friction_source", "Payout"),
    ]
    rows = []
    for col, label in source_cols:
        if col not in vsi.columns:
            continue
        for src, cnt in vsi[col].value_counts().items():
            tier = "official" if any(k in str(src).lower() for k in ("world_bank", "rpw", "imf", "knomad", "api")) else "assumed"
            rows.append({"component": label, "source": str(src), "tier": tier, "count": int(cnt)})
    if not rows:
        return go.Figure()
    df = pd.DataFrame(rows)
    fig = px.bar(
        df, x="component", y="count", color="tier", barmode="stack",
        title="Official vs assumed data components",
        template="plotly_dark",
    )
    return _add_chart_notes(fig)


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
    fig.update_layout(xaxis_type="log")
    return _add_chart_notes(fig)


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
