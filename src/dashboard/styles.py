"""Bowers Frontier Macro Labs — institutional terminal design system."""

from __future__ import annotations

COLORS = {
    "background": "#050608",
    "surface": "#0B0F14",
    "surface_alt": "#111827",
    "border": "#1F2937",
    "border_subtle": "#161B22",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "accent_gold": "#D4AF37",
    "accent_cyan": "#38BDF8",
    "risk_red": "#EF4444",
    "warning_amber": "#F59E0B",
    "success_green": "#22C55E",
    "muted_purple": "#8B5CF6",
}

PLOTLY_LAYOUT = {
    "paper_bgcolor": "rgba(11,15,20,0)",
    "plot_bgcolor": COLORS["background"],
    "font": {"family": "JetBrains Mono, SF Mono, ui-monospace, monospace", "color": COLORS["text_primary"], "size": 10},
    "title": {"font": {"size": 13, "color": COLORS["text_primary"]}},
    "margin": {"l": 44, "r": 16, "t": 40, "b": 72},
    "colorway": [
        COLORS["accent_cyan"],
        COLORS["accent_gold"],
        COLORS["muted_purple"],
        COLORS["success_green"],
        COLORS["warning_amber"],
        COLORS["risk_red"],
    ],
    "xaxis": {
        "gridcolor": "rgba(31,41,55,0.8)",
        "linecolor": COLORS["border"],
        "zerolinecolor": COLORS["border"],
        "tickfont": {"color": COLORS["text_secondary"], "size": 9},
        "title_font": {"color": COLORS["text_muted"], "size": 10},
    },
    "yaxis": {
        "gridcolor": "rgba(31,41,55,0.8)",
        "linecolor": COLORS["border"],
        "zerolinecolor": COLORS["border"],
        "tickfont": {"color": COLORS["text_secondary"], "size": 9},
        "title_font": {"color": COLORS["text_muted"], "size": 10},
    },
    "legend": {
        "bgcolor": "rgba(11,15,20,0.92)",
        "bordercolor": COLORS["border"],
        "font": {"color": COLORS["text_secondary"], "size": 9},
    },
}


def inject_br3n_theme() -> str:
    c = COLORS
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {{
  --bg: {c['background']};
  --surface: {c['surface']};
  --surface-alt: {c['surface_alt']};
  --border: {c['border']};
  --border-subtle: {c['border_subtle']};
  --text: {c['text_primary']};
  --muted: {c['text_secondary']};
  --muted2: {c['text_muted']};
  --gold: {c['accent_gold']};
  --cyan: {c['accent_cyan']};
  --red: {c['risk_red']};
  --amber: {c['warning_amber']};
  --green: {c['success_green']};
  --purple: {c['muted_purple']};
  --glass: rgba(11, 15, 20, 0.72);
  --glass-border: rgba(212, 175, 55, 0.12);
}}

/* ── App shell ── */
.stApp {{
  background:
    radial-gradient(ellipse 120% 80% at 50% -20%, rgba(56,189,248,0.06) 0%, transparent 50%),
    radial-gradient(ellipse 80% 50% at 100% 0%, rgba(212,175,55,0.04) 0%, transparent 40%),
    linear-gradient(180deg, #07090d 0%, {c['background']} 100%);
  color: {c['text_primary']};
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}}
.stApp::before {{
  content: "";
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image:
    linear-gradient(rgba(56,189,248,0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(56,189,248,0.025) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: linear-gradient(180deg, black 0%, transparent 85%);
}}
.block-container {{
  padding: 1.5rem 2rem 2.5rem !important;
  max-width: 1480px !important;
  position: relative; z-index: 1;
}}
header[data-testid="stHeader"] {{
  background: rgba(5,6,8,0.94) !important;
  border-bottom: 1px solid {c['border']} !important;
  backdrop-filter: blur(12px);
}}
#MainMenu, footer {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}

/* ── Sidebar terminal nav ── */
section[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #0a0e14 0%, {c['background']} 100%) !important;
  border-right: 1px solid {c['border']} !important;
}}
section[data-testid="stSidebar"] > div {{
  padding-top: 1.25rem;
}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label {{
  background: transparent !important;
  border: 1px solid transparent !important;
  border-radius: 6px !important;
  padding: 0.45rem 0.65rem !important;
  margin: 2px 0 !important;
  font-size: 0.78rem !important;
  font-weight: 500 !important;
  color: {c['text_secondary']} !important;
  transition: all 0.15s ease;
}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
  border-color: {c['border']} !important;
  color: {c['text_primary']} !important;
  background: rgba(56,189,248,0.04) !important;
}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
section[data-testid="stSidebar"] [data-testid="stRadio"] div[aria-checked="true"] label {{
  background: rgba(56,189,248,0.1) !important;
  border-color: rgba(56,189,248,0.35) !important;
  color: {c['accent_cyan']} !important;
}}
.br3n-sidebar-brand {{
  padding: 0.25rem 0 1.25rem;
  border-bottom: 1px solid {c['border_subtle']};
  margin-bottom: 1rem;
}}
.br3n-sidebar-module {{
  font-size: 0.72rem; color: {c['text_muted']}; line-height: 1.8;
  font-family: 'JetBrains Mono', monospace;
}}
.br3n-sidebar-module .dot-on {{ color: {c['success_green']}; }}
.br3n-sidebar-module .dot-off {{ color: {c['text_muted']}; }}

/* ── Executive terminal header ── */
.br3n-terminal-header {{
  position: relative;
  margin: 0 0 1.75rem 0;
  padding: 1.35rem 1.5rem 1.25rem;
  background: linear-gradient(135deg, rgba(17,24,39,0.88) 0%, rgba(11,15,20,0.95) 100%);
  border: 1px solid {c['border']};
  border-radius: 14px;
  box-shadow: 0 16px 48px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.04);
  backdrop-filter: blur(16px);
  overflow: hidden;
}}
.br3n-terminal-header::before {{
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, {c['accent_gold']}, {c['accent_cyan']}, transparent);
}}
.br3n-terminal-eyebrow {{
  font-size: 0.62rem; letter-spacing: 0.22em; text-transform: uppercase;
  color: {c['accent_gold']}; font-weight: 600; margin-bottom: 0.5rem;
}}
.br3n-terminal-title-row {{
  display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;
}}
.br3n-terminal-header h1 {{
  margin: 0; font-size: 1.65rem; font-weight: 600; letter-spacing: -0.02em;
  color: {c['text_primary']}; line-height: 1.2;
}}
.br3n-live-pill {{
  font-size: 0.58rem; font-weight: 700; letter-spacing: 0.14em;
  padding: 0.2rem 0.55rem; border-radius: 999px;
  background: rgba(34,197,94,0.12); color: {c['success_green']};
  border: 1px solid rgba(34,197,94,0.35);
  animation: br3n-pulse 2.5s ease-in-out infinite;
}}
.br3n-page-tag {{
  font-size: 0.58rem; font-weight: 600; letter-spacing: 0.12em;
  padding: 0.2rem 0.55rem; border-radius: 4px;
  background: rgba(56,189,248,0.1); color: {c['accent_cyan']};
  border: 1px solid rgba(56,189,248,0.25);
}}
.br3n-terminal-sub {{
  margin: 0.5rem 0 0; color: {c['text_secondary']}; font-size: 0.88rem; max-width: 52rem;
}}
.br3n-terminal-meta {{
  display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.85rem;
}}

/* ── Compact KPI tiles ── */
.br3n-kpi-grid {{ margin-bottom: 1.25rem; }}
.br3n-kpi {{
  background: linear-gradient(160deg, rgba(17,24,39,0.75) 0%, rgba(11,15,20,0.92) 100%);
  border: 1px solid {c['border']};
  border-radius: 10px;
  padding: 0.7rem 0.85rem 0.75rem;
  backdrop-filter: blur(10px);
  min-height: 82px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}}
.br3n-kpi:hover {{
  border-color: rgba(56,189,248,0.25);
  box-shadow: 0 4px 20px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.04);
}}
.br3n-kpi-label {{
  font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase;
  color: {c['text_muted']}; font-weight: 600;
}}
.br3n-kpi-value {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.28rem; font-weight: 600;
  color: {c['text_primary']}; margin-top: 0.15rem; line-height: 1.2;
}}
.br3n-kpi-sub {{
  font-size: 0.68rem; color: {c['text_secondary']}; margin-top: 0.35rem;
  display: flex; align-items: center; gap: 0.35rem; flex-wrap: wrap;
}}

/* ── Glass panels ── */
.br3n-glass-panel-head {{
  background: linear-gradient(180deg, rgba(17,24,39,0.9) 0%, rgba(11,15,20,0.85) 100%);
  border: 1px solid {c['border']};
  border-bottom: none;
  border-radius: 12px 12px 0 0;
  padding: 0.85rem 1rem 0.65rem;
  backdrop-filter: blur(12px);
}}
.br3n-glass-panel-tail {{
  background: rgba(5,6,8,0.75);
  border: 1px solid {c['border']};
  border-top: 1px solid {c['border_subtle']};
  border-radius: 0 0 12px 12px;
  padding: 0.55rem 1rem 0.7rem;
  margin-bottom: 1.25rem;
}}
.br3n-panel-title {{
  font-size: 0.82rem; font-weight: 600; color: {c['text_primary']}; margin: 0;
}}
.br3n-panel-subtitle {{
  font-size: 0.72rem; color: {c['text_muted']}; margin: 0.2rem 0 0;
}}
.br3n-badge-row {{ display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.5rem; }}

/* Plotly chart sits in glass frame */
div[data-testid="stPlotlyChart"] {{
  background: rgba(5,6,8,0.85) !important;
  border-left: 1px solid {c['border']} !important;
  border-right: 1px solid {c['border']} !important;
  padding: 0.25rem 0.35rem !important;
}}
.js-plotly-plot .plotly .modebar {{ opacity: 0.35; }}
.js-plotly-plot .plotly .modebar:hover {{ opacity: 0.85; }}

/* ── Badges ── */
.br3n-badge {{
  display: inline-flex; align-items: center;
  padding: 0.12rem 0.45rem; border-radius: 4px;
  font-size: 0.58rem; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase;
  white-space: nowrap;
}}
.br3n-badge-gold {{ background: rgba(212,175,55,0.12); color: {c['accent_gold']}; border: 1px solid rgba(212,175,55,0.3); }}
.br3n-badge-cyan {{ background: rgba(56,189,248,0.1); color: {c['accent_cyan']}; border: 1px solid rgba(56,189,248,0.28); }}
.br3n-badge-red {{ background: rgba(239,68,68,0.1); color: {c['risk_red']}; border: 1px solid rgba(239,68,68,0.32); }}
.br3n-badge-green {{ background: rgba(34,197,94,0.1); color: {c['success_green']}; border: 1px solid rgba(34,197,94,0.28); }}
.br3n-badge-amber {{ background: rgba(245,158,11,0.1); color: {c['warning_amber']}; border: 1px solid rgba(245,158,11,0.28); }}
.br3n-badge-purple {{ background: rgba(139,92,246,0.1); color: {c['muted_purple']}; border: 1px solid rgba(139,92,246,0.28); }}

/* ── Warnings & credibility ── */
.br3n-warning {{
  display: flex; align-items: flex-start; gap: 0.65rem;
  border: 1px solid rgba(245,158,11,0.25);
  border-left: 3px solid {c['warning_amber']};
  background: linear-gradient(90deg, rgba(245,158,11,0.08) 0%, rgba(245,158,11,0.02) 100%);
  padding: 0.7rem 1rem; border-radius: 0 10px 10px 0;
  margin: 0 0 1.25rem 0; font-size: 0.8rem; line-height: 1.5; color: {c['text_secondary']};
}}
.br3n-warning-red {{
  border-color: rgba(239,68,68,0.25) !important;
  border-left-color: {c['risk_red']} !important;
  background: linear-gradient(90deg, rgba(239,68,68,0.08) 0%, rgba(239,68,68,0.02) 100%) !important;
}}
.br3n-warning-icon {{ color: {c['warning_amber']}; font-size: 0.9rem; flex-shrink: 0; }}
.br3n-credibility-strip {{
  font-size: 0.68rem; color: {c['text_muted']}; line-height: 1.5;
  font-family: 'JetBrains Mono', monospace;
  border-top: 1px dashed {c['border_subtle']};
  padding-top: 0.45rem; margin-top: 0.15rem;
}}
.br3n-caption {{ font-size: 0.68rem; color: {c['text_muted']}; line-height: 1.45; }}

/* ── Section headers ── */
.br3n-section {{
  display: flex; align-items: center; gap: 0.65rem;
  margin: 1.5rem 0 0.85rem; padding-bottom: 0.45rem;
  border-bottom: 1px solid {c['border_subtle']};
}}
.br3n-section h3 {{
  margin: 0; font-size: 0.72rem; font-weight: 700;
  letter-spacing: 0.14em; text-transform: uppercase; color: {c['text_secondary']};
}}
.br3n-section-line {{
  flex: 1; height: 1px; background: linear-gradient(90deg, {c['border']}, transparent);
}}

/* ── Loading skeleton ── */
.br3n-loading-wrap {{
  padding: 2rem 0;
}}
.br3n-skeleton {{
  background: linear-gradient(90deg, {c['surface_alt']} 25%, rgba(31,41,55,0.8) 50%, {c['surface_alt']} 75%);
  background-size: 200% 100%;
  animation: br3n-shimmer 1.4s ease-in-out infinite;
  border-radius: 8px; height: 14px; margin-bottom: 0.55rem;
}}
.br3n-skeleton-lg {{ height: 120px; border-radius: 12px; margin-bottom: 1rem; }}
.br3n-skeleton-kpi {{ height: 82px; border-radius: 10px; }}
.br3n-loading-label {{
  font-size: 0.65rem; letter-spacing: 0.16em; text-transform: uppercase;
  color: {c['accent_cyan']}; margin-bottom: 1rem;
  animation: br3n-pulse 1.8s ease-in-out infinite;
}}

@keyframes br3n-shimmer {{
  0% {{ background-position: 200% 0; }}
  100% {{ background-position: -200% 0; }}
}}
@keyframes br3n-pulse {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.55; }}
}}

/* ── Tables ── */
.br3n-table-wrap {{
  border: 1px solid {c['border']};
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 1rem;
  background: rgba(11,15,20,0.6);
}}
div[data-testid="stDataFrame"] {{
  border: 1px solid {c['border']} !important;
  border-radius: 10px !important;
  overflow: hidden !important;
  background: rgba(11,15,20,0.65) !important;
}}
div[data-testid="stDataFrame"] div[data-testid="stTable"] {{
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.72rem !important;
}}
div[data-testid="stDataFrame"] [data-testid="stHeader"] {{
  background: {c['surface_alt']} !important;
  font-size: 0.65rem !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
}}

/* ── Expanders (methodology popovers) ── */
div[data-testid="stExpander"] {{
  background: rgba(11,15,20,0.7) !important;
  border: 1px solid {c['border_subtle']} !important;
  border-radius: 8px !important;
  margin-bottom: 0.75rem !important;
}}
div[data-testid="stExpander"] summary {{
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.04em !important;
  color: {c['accent_cyan']} !important;
}}
div[data-testid="stExpander"] summary:hover {{
  color: {c['text_primary']} !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  gap: 4px; background: transparent; border-bottom: 1px solid {c['border_subtle']};
}}
.stTabs [data-baseweb="tab"] {{
  background: transparent !important;
  border: 1px solid transparent !important;
  border-radius: 6px 6px 0 0 !important;
  color: {c['text_muted']} !important;
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.04em !important;
  padding: 0.45rem 0.85rem !important;
}}
.stTabs [aria-selected="true"] {{
  background: rgba(56,189,248,0.08) !important;
  border-color: {c['border']} !important;
  border-bottom-color: transparent !important;
  color: {c['accent_cyan']} !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
  padding-top: 1rem !important;
}}

/* ── Buttons & inputs ── */
.stDownloadButton button, .stButton button {{
  background: rgba(56,189,248,0.1) !important;
  border: 1px solid rgba(56,189,248,0.3) !important;
  color: {c['accent_cyan']} !important;
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  border-radius: 6px !important;
}}
.stDownloadButton button:hover, .stButton button:hover {{
  background: rgba(56,189,248,0.18) !important;
  border-color: rgba(56,189,248,0.5) !important;
}}

/* ── Footer ── */
.br3n-footer {{
  margin-top: 2rem; padding-top: 1rem;
  border-top: 1px solid {c['border_subtle']};
  font-size: 0.65rem; color: {c['text_muted']};
  letter-spacing: 0.06em; text-align: center;
}}

/* ── Spacing utilities ── */
.br3n-spacer-sm {{ height: 0.75rem; }}
.br3n-spacer-md {{ height: 1.25rem; }}
</style>
"""
