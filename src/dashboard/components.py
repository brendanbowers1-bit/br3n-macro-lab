"""Premium Streamlit UI components — BR3N research intelligence terminal."""

from __future__ import annotations

import html as html_lib
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src.dashboard.data_loader import LoadResult, ROOT
from src.dashboard.styles import COLORS

PLOTLY_CONFIG = {
    "displayModeBar": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
    "displaylogo": False,
}


def _esc(text: str) -> str:
    return html_lib.escape(str(text))


def loading_skeleton(label: str = "Loading intelligence feed") -> str:
    return f"""
<div class="br3n-loading-wrap">
  <div class="br3n-loading-label">◆ {_esc(label)}</div>
  <div class="br3n-skeleton br3n-skeleton-lg"></div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.65rem;">
    <div class="br3n-skeleton br3n-skeleton-kpi"></div>
    <div class="br3n-skeleton br3n-skeleton-kpi"></div>
    <div class="br3n-skeleton br3n-skeleton-kpi"></div>
    <div class="br3n-skeleton br3n-skeleton-kpi"></div>
  </div>
  <div class="br3n-skeleton br3n-skeleton-lg" style="margin-top:1rem;height:280px;"></div>
</div>"""


def page_header(
    title: str,
    subtitle: str,
    *,
    tag: str = "INTELLIGENCE",
    live: bool = True,
    meta_badges: list[tuple[str, str]] | None = None,
) -> None:
    live_pill = '<span class="br3n-live-pill">● LIVE</span>' if live else ""
    tag_html = f'<span class="br3n-page-tag">{_esc(tag)}</span>' if tag else ""
    badges = meta_badges or []
    meta_html = "".join(f'<span class="br3n-badge br3n-badge-{tone}">{_esc(lbl)}</span>' for lbl, tone in badges)
    st.markdown(
        f"""<div class="br3n-terminal-header">
        <div class="br3n-terminal-eyebrow">BR3N Macro Lab · Research Intelligence Terminal</div>
        <div class="br3n-terminal-title-row">
          <h1>{_esc(title)}</h1>
          {tag_html}{live_pill}
        </div>
        <p class="br3n-terminal-sub">{_esc(subtitle)}</p>
        {"<div class='br3n-terminal-meta'>" + meta_html + "</div>" if meta_html else ""}
        </div>""",
        unsafe_allow_html=True,
    )


def section_header(title: str) -> None:
    st.markdown(
        f"""<div class="br3n-section">
        <h3>{_esc(title)}</h3>
        <div class="br3n-section-line"></div>
        </div>""",
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, sub: str = "", tone: str = "cyan") -> None:
    tone_map = {
        "cyan": "br3n-badge-cyan",
        "gold": "br3n-badge-gold",
        "red": "br3n-badge-red",
        "green": "br3n-badge-green",
        "amber": "br3n-badge-amber",
        "purple": "br3n-badge-purple",
    }
    badge = tone_map.get(tone, "br3n-badge-cyan")
    sub_html = f'<span class="br3n-badge {badge}">{tone}</span>' if tone else ""
    if sub:
        sub_html += f' <span>{_esc(sub)}</span>'
    st.markdown(
        f"""<div class="br3n-kpi">
        <div class="br3n-kpi-label">{_esc(label)}</div>
        <div class="br3n-kpi-value">{_esc(value)}</div>
        <div class="br3n-kpi-sub">{sub_html}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def kpi_row(items: list[tuple[str, str, str, str]], cols: int = 4) -> None:
    columns = st.columns(cols)
    for col, (label, value, sub, tone) in zip(columns, items):
        with col:
            kpi_card(label, value, sub, tone)


def badge_html(label: str, tone: str = "cyan") -> str:
    return f'<span class="br3n-badge br3n-badge-{tone}">{_esc(label)}</span>'


def badge_row(badges: list[tuple[str, str]]) -> None:
    row = "".join(badge_html(lbl, tone) for lbl, tone in badges)
    st.markdown(f'<div class="br3n-badge-row">{row}</div>', unsafe_allow_html=True)


def data_quality_badge(score: float | None, grade: str | None = None, mock: bool | None = None) -> str:
    if mock:
        return badge_html("MOCK DATA", "red")
    if score is None:
        return badge_html("QUALITY UNKNOWN", "amber")
    tone = "green" if score >= 80 else "amber" if score >= 50 else "red"
    label = grade or ("STRONG" if score >= 80 else "PRELIMINARY" if score >= 50 else "DEMO")
    return badge_html(f"{label} · {score:.0f}", tone)


def source_badge(source_id: str | None = None, tier: int | None = None) -> str:
    sid = source_id or "unknown"
    tier_txt = f"T{tier}" if tier else "SRC"
    return badge_html(f"{tier_txt} · {sid}", "cyan")


def warning_banner(text: str, level: str = "amber") -> None:
    cls = "br3n-warning br3n-warning-red" if level == "red" else "br3n-warning"
    icon = "⚠" if level == "amber" else "⛔"
    st.markdown(
        f"""<div class="{cls}">
        <span class="br3n-warning-icon">{icon}</span>
        <span>{_esc(text)}</span>
        </div>""",
        unsafe_allow_html=True,
    )


def credibility_strip(*parts: str) -> None:
    text = " · ".join(p for p in parts if p)
    if text:
        st.markdown(f'<div class="br3n-credibility-strip">{_esc(text)}</div>', unsafe_allow_html=True)


def methodology_note(text: str) -> None:
    st.markdown(f'<p class="br3n-caption">{_esc(text)}</p>', unsafe_allow_html=True)


def methodology_popover(
    title: str,
    body: str,
    *,
    source: str = "",
    limitations: str = "",
    expanded: bool = False,
) -> None:
    content = body
    if source:
        content += f"\n\n**Source:** {source}"
    if limitations:
        content += f"\n\n**Limitations:** {limitations}"
    with st.expander(f"◈ {_esc(title)} — methodology & lineage", expanded=expanded):
        st.markdown(content)


def chart_card(
    fig,
    title: str,
    subtitle: str = "",
    caption: str = "",
    source: str = "",
    methodology: str = "",
    quality_note: str = "",
    quality_score: float | None = None,
    mock_warning: bool = False,
    source_id: str | None = None,
    tier: int | None = None,
    limitations: str = "",
) -> None:
    badges: list[tuple[str, str]] = []
    if source_id or tier:
        badges.append((f"T{tier} · {source_id}" if tier else str(source_id), "cyan"))
    if quality_score is not None:
        tone = "green" if quality_score >= 80 else "amber" if quality_score >= 50 else "red"
        badges.append((f"DQ {quality_score:.0f}", tone))
    if mock_warning:
        badges.append(("MOCK / MIXED", "red"))

    badge_row_html = "".join(badge_html(l, t) for l, t in badges)
    st.markdown(
        f"""<div class="br3n-glass-panel-head">
        <p class="br3n-panel-title">{_esc(title)}</p>
        {"<p class='br3n-panel-subtitle'>" + _esc(subtitle) + "</p>" if subtitle else ""}
        {"<div class='br3n-badge-row'>" + badge_row_html + "</div>" if badge_row_html else ""}
        </div>""",
        unsafe_allow_html=True,
    )

    if mock_warning:
        warning_banner(
            "Mock or manual-assumption data present in this visualization. "
            "Do not use for research conclusions, investment decisions, or operational guidance.",
            "red",
        )

    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    footer_parts = [p for p in (caption, source, quality_note) if p]
    footer = " · ".join(footer_parts)
    st.markdown(
        f"""<div class="br3n-glass-panel-tail">
        {"<div class='br3n-caption'>" + _esc(footer) + "</div>" if footer else ""}
        </div>""",
        unsafe_allow_html=True,
    )

    if methodology or limitations:
        methodology_popover(
            title,
            methodology or "Research estimate under stated assumptions.",
            source=source,
            limitations=limitations or "Not investment advice. Verify mock_data_flag and data_quality_score before citation.",
        )


def premium_table(
    df: pd.DataFrame,
    *,
    title: str = "",
    max_rows: int = 50,
    numeric_cols: list[str] | None = None,
    hide_cols: list[str] | None = None,
) -> None:
    if df.empty:
        st.markdown('<div class="br3n-caption">No rows to display.</div>', unsafe_allow_html=True)
        return
    show = df.head(max_rows).copy()
    if hide_cols:
        show = show.drop(columns=[c for c in hide_cols if c in show.columns], errors="ignore")

    if title:
        st.markdown(f'<p class="br3n-panel-title" style="margin-bottom:0.5rem;">{_esc(title)}</p>', unsafe_allow_html=True)

    col_config = {}
    if numeric_cols:
        for c in numeric_cols:
            if c in show.columns:
                col_config[c] = st.column_config.NumberColumn(format="%.2f")
    for c in show.columns:
        if c.endswith("_index") or c.endswith("_score") or "vsi" in c.lower():
            if c not in col_config and pd.api.types.is_numeric_dtype(show[c]):
                col_config[c] = st.column_config.NumberColumn(format="%.1f")

    st.dataframe(show, use_container_width=True, hide_index=True, column_config=col_config or None)


def missing_data_panel(result: LoadResult, generate_cmd: str = "") -> None:
    st.markdown(
        f"""<div class="br3n-glass-panel-head">
        <p class="br3n-panel-title">Data unavailable · {_esc(result.name)}</p>
        <p class="br3n-panel-subtitle">{_esc(result.message or result.status)}</p>
        </div>""",
        unsafe_allow_html=True,
    )
    if generate_cmd:
        st.code(generate_cmd, language="bash")
    methodology_note("Pipeline outputs are required. Do not infer values from missing tables.")


def publication_checklist(items: list[tuple[str, str, str]]) -> None:
    section_header("Publication-grade checklist")
    rows = []
    for criterion, status, note in items:
        icon = "✓" if status == "PASS" else "⚠" if status == "WARN" else "✗"
        tone = "green" if status == "PASS" else "amber" if status == "WARN" else "red"
        rows.append({"": icon, "Criterion": criterion, "Status": status, "Note": note, "_tone": tone})
    premium_table(pd.DataFrame(rows).drop(columns=["_tone"], errors="ignore"), title="")


def export_csv_button(df: pd.DataFrame, filename: str, label: str = "↓ Export CSV") -> None:
    if df.empty:
        return
    st.download_button(label, df.to_csv(index=False), file_name=filename, mime="text/csv")


def module_status_panel(modules: Any) -> None:
    flags = [
        ("VSI", modules.vsi, "Value Survival Index"),
        ("Settlement", modules.settlement, "SDI · OLB · FQI"),
        ("Stablecoin", modules.stablecoin, "SFQI · SWC · SVSI"),
        ("Data Lake", modules.data_lake, "Medallion · DuckDB"),
        ("Audit", modules.audit, "Quality · Validation"),
    ]
    cols = st.columns(5)
    for col, (name, ok, desc) in zip(cols, flags):
        with col:
            kpi_card(name, "ONLINE" if ok else "OFFLINE", desc, "green" if ok else "amber")


def render_filters_sidebar(data: Any) -> dict[str, Any]:
    st.sidebar.markdown(
        """<div class="br3n-sidebar-brand">
        <span class="br3n-badge br3n-badge-gold">BR3N MACRO LAB</span>
        <div style="margin-top:0.65rem;font-size:1rem;font-weight:600;color:#F8FAFC;">Command Center</div>
        <div style="font-size:0.72rem;color:#64748B;margin-top:0.2rem;">Research intelligence terminal</div>
        </div>""",
        unsafe_allow_html=True,
    )

    section_header_sidebar = '<div style="font-size:0.62rem;letter-spacing:0.14em;text-transform:uppercase;color:#64748B;font-weight:700;margin:1rem 0 0.5rem;">Global filters</div>'
    st.sidebar.markdown(section_header_sidebar, unsafe_allow_html=True)

    vsi_df = data.vsi.get("value_survival", LoadResult("", None, pd.DataFrame(), "")).df
    corridors = sorted(vsi_df["corridor"].dropna().unique()) if not vsi_df.empty and "corridor" in vsi_df.columns else []
    senders = sorted(vsi_df["sender_country"].dropna().unique()) if not vsi_df.empty and "sender_country" in vsi_df.columns else []
    receivers = sorted(vsi_df["receiver_country"].dropna().unique()) if not vsi_df.empty and "receiver_country" in vsi_df.columns else []

    sensitivity = st.sidebar.selectbox("Sensitivity case", ["baseline", "conservative", "severe"], index=0)
    official_only = st.sidebar.toggle("Official data only", value=False)
    include_mock = st.sidebar.toggle("Include mock data", value=True)
    min_quality = st.sidebar.slider("Min data quality score", 0, 100, 0, 5)
    corridor = st.sidebar.selectbox("Corridor", ["All"] + list(corridors))
    sender = st.sidebar.selectbox("Sender country", ["All"] + list(senders)) if senders else "All"
    receiver = st.sidebar.selectbox("Receiver country", ["All"] + list(receivers)) if receivers else "All"

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """<div class="br3n-caption" style="padding:0 0.25rem;">
        Research &amp; education only.<br>Not investment advice.<br>Verify lineage before citation.
        </div>""",
        unsafe_allow_html=True,
    )
    return {
        "sensitivity": sensitivity,
        "official_only": official_only,
        "include_mock": include_mock,
        "min_quality": float(min_quality),
        "corridor": None if corridor == "All" else corridor,
        "sender": None if sender == "All" else sender,
        "receiver": None if receiver == "All" else receiver,
    }


def sidebar_module_status(modules: Any) -> None:
    dots = [
        ("VSI", modules.vsi),
        ("Settlement", modules.settlement),
        ("Stablecoin", modules.stablecoin),
        ("Audit", modules.audit),
    ]
    lines = []
    for name, ok in dots:
        cls = "dot-on" if ok else "dot-off"
        sym = "●" if ok else "○"
        lines.append(f'<span class="{cls}">{sym} {name}</span>')
    st.sidebar.markdown(
        f"""<div style="font-size:0.62rem;letter-spacing:0.12em;text-transform:uppercase;color:#64748B;font-weight:700;margin-bottom:0.5rem;">Module status</div>
        <div class="br3n-sidebar-module">{"<br>".join(lines)}</div>""",
        unsafe_allow_html=True,
    )


def terminal_footer() -> None:
    st.markdown(
        """<div class="br3n-footer">
        BR3N MACRO LAB · Value Survival Index · Settlement Economics · Stablecoin Settlement Window Lab<br>
        Research intelligence only · Not investment advice · Verify mock_data_flag before citation
        </div>""",
        unsafe_allow_html=True,
    )


def read_markdown_snippet(path: Path, max_chars: int = 4000) -> str:
    if not path.exists():
        return f"_Missing: `{path.relative_to(ROOT)}`_"
    text = path.read_text(encoding="utf-8")
    return text[:max_chars] + ("…" if len(text) > max_chars else "")
