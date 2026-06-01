#!/usr/bin/env python3
"""Generate static dashboard visuals for reports/publication."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.dashboard.charts import (
    global_risk_heatmap,
    ranked_bar,
    sankey_value_survival,
    scatter_frontier,
)
from src.dashboard.data_loader import load_all_dashboard_data, load_value_survival_data
from src.visuals.vsi_charts import corridor_summary

OUT = ROOT / "reports" / "figures" / "dashboard"
OUT.mkdir(parents=True, exist_ok=True)


def _save_matplotlib_png(fig, png: Path) -> bool:
    """Fallback PNG export via matplotlib when Kaleido/Chrome unavailable."""
    try:
        import matplotlib.pyplot as plt
        from plotly.io import to_mpl

        mpl_fig = to_mpl(fig)
        mpl_fig.savefig(png, dpi=150, bbox_inches="tight", facecolor="#0B0F14")
        plt.close(mpl_fig)
        return True
    except Exception:
        return False


def _save(fig, name: str) -> Path:
    png = OUT / f"{name}.png"
    html = OUT / f"{name}.html"
    fig.write_html(str(html), include_plotlyjs="cdn")
    saved_png = False
    try:
        fig.write_image(str(png), width=1400, height=800, scale=2)
        saved_png = True
    except Exception:
        saved_png = _save_matplotlib_png(fig, png)
    if saved_png:
        print(f"  Saved: {png.relative_to(ROOT)}")
    else:
        print(f"  PNG skip {name} (HTML only)")
    print(f"  Saved: {html.relative_to(ROOT)}")
    return html


def main() -> int:
    print("BR3N Dashboard visuals")
    data = load_all_dashboard_data()
    vsi_lr = load_value_survival_data()["value_survival"]
    vsi = vsi_lr.df
    sdi = data.settlement.get("settlement_drag").df if data.settlement.get("settlement_drag") else pd.DataFrame()
    sfqi = data.stablecoin.get("finality_quality").df if data.stablecoin.get("finality_quality") else pd.DataFrame()

    if not vsi.empty:
        summary = corridor_summary(vsi)
        _save(ranked_bar(summary.head(12), "corridor", "value_survival_index", "Executive VSI — worst corridors", ascending=True), "executive_summary_grid")
        row = vsi.iloc[0]
        _save(sankey_value_survival(row), "value_survival_sankey")

    if not sdi.empty and "entity" in sdi.columns:
        top = sdi.nsmallest(15, "settlement_drag_index")
        _save(ranked_bar(top, "entity", "settlement_drag_index", "Settlement drag ranked", ascending=True), "settlement_drag_frontier")

    if not sfqi.empty:
        _save(scatter_frontier(sfqi, "ledger_finality_score", "economic_finality_score", "stablecoin", "Stablecoin finality matrix"), "stablecoin_finality_matrix")

    rows = []
    for mod, bundle in [("VSI", data.vsi), ("Settlement", data.settlement), ("Stablecoin", data.stablecoin)]:
        for name, lr in bundle.items():
            if lr.df.empty or "data_quality_score" not in lr.df.columns:
                continue
            rows.append({"Module": mod, "Dataset": name, "Quality": lr.df["data_quality_score"].mean()})
    if rows:
        d = pd.DataFrame(rows)
        import plotly.express as px
        from src.dashboard.styles import PLOTLY_LAYOUT
        fig = px.bar(d, x="Dataset", y="Quality", color="Module", barmode="group", template="plotly_dark")
        layout = dict(PLOTLY_LAYOUT)
        layout["title"] = {"text": "Data quality by dataset", "font": PLOTLY_LAYOUT["title"]["font"]}
        fig.update_layout(**layout)
        _save(fig, "data_quality_command_center")

    import plotly.graph_objects as go
    from src.dashboard.styles import COLORS, PLOTLY_LAYOUT
    fig = go.Figure()
    nodes = ["RPW / IMF / BIS", "VSI", "Settlement Lab", "Stablecoin Lab", "Audit / Quality", "Command Center"]
    for i, n in enumerate(nodes):
        fig.add_annotation(x=i / (len(nodes) - 1), y=0.5, text=n, showarrow=False, font=dict(color=COLORS["text_primary"]))
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_layout(title={"text": "Research framework diagram", "font": PLOTLY_LAYOUT["title"]["font"]}, xaxis=dict(visible=False), yaxis=dict(visible=False), height=400)
    _save(fig, "research_framework_diagram")

    print(f"Output directory: {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
