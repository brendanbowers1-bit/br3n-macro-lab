"""
Build a styled static HTML site from publication markdown.
"""

from __future__ import annotations

import html
import re
from datetime import datetime
from pathlib import Path
from typing import Dict

from . import LAB_NAME, LAB_NAME_DISPLAY
from .bfi_site import (
    BFI_LOGO_HORIZONTAL,
    BFI_LOGO_HORIZONTAL_INVERSE,
    ROOT_BRAND,
    bfi_favicon_tags,
    bfi_header_logo,
    build_bfi_pages,
)

ROOT = Path(__file__).resolve().parents[1]
PUB_DIR = ROOT / "reports" / "publication"
VERTICALS_DIR = PUB_DIR / "verticals"

PUBLIC_SITE_BASE = "https://brendanbowers1-bit.github.io/br3n-macro-lab"

FX_LAB_TAGLINE = "Testing When Currency Markets Become Less Random"
FX_LAB_LOGO = "assets/br3n_macro_labs_logo.png"
BRAND_MOTTO = "Research. Regime. Risk."

# (href, title, description, tag)
HOME_RESEARCH_LINKS: list[tuple[str, str, str, str]] = [
    ("fx-lab.html", "FX Lab Overview", "Mission, modules, and research outputs", "Start here"),
    ("usdmxn-research.html", "USD/MXN Regime Research", "2-minute summary and key stats", "Research"),
    ("hedge-governance.html", "Hedge Governance Memo", "Forecast failure, hedge usefulness", "Flagship"),
    ("model-zoo.html", "Model Zoo", "Conditional forecastability tests", "Models"),
    ("lab-status.html", "Lab Status", "Nightly health snapshot and pipeline gaps", "Ops"),
    ("unanswered-fx.html", "Unanswered FX Questions", "Major research questions and flagship lane", "Research"),
    ("history.html", "FX History & Foundations", "300 years of exchange-rate research", "Foundations"),
    ("open-source-ai.html", "Open Source FX AI Model Lab", "Borrow, benchmark, and improve OSS FX models", "Models"),
    ("global-fx-lab.html", "Global FX Research Lab", "Who bears the cost when value crosses borders?", "Research"),
    ("value-survival-index.html", "Value Survival Index", "How much value survives when money crosses borders?", "Flagship"),
    ("settlement-economics-lab.html", "Settlement Economics Lab", "Settlement drag, liquidity burden, and finality", "Flagship"),
    ("stablecoin-settlement-lab.html", "Stablecoin Settlement Lab", "Finality, window compression, and digital run conditions", "Flagship"),
    ("dashboard/index.html", "Interactive Web Dashboard", "Cinematic command center — Sankey, value flow map, finality matrix", "Dashboard"),
    ("ladder.html", "Evidence Ladder", "Eight-level evidence framework", "Methods"),
    ("memo.html", "Full Research Note", "Methods, tables, limitations", "Deep dive"),
    ("corridor.html", "Corridor Roadmap", "Multi-corridor payment research", "Corridors"),
    ("fx_desk.html", "FX Desk Framework", "Cross-border payments and treasury decisions", "Desk"),
]

FX_LAB_RESEARCH_LINKS: list[tuple[str, str, str, str]] = [
    link for link in HOME_RESEARCH_LINKS if link[0] != "fx-lab.html"
]


def _css() -> str:
    return """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Source+Sans+3:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');
:root {
  --bg: #f7f5f0;
  --surface: #ffffff;
  --surface-alt: #f0ede6;
  --border: #d4dce8;
  --border-strong: #b8c4d4;
  --text: #1a2744;
  --muted: #5c6578;
  --accent: #1e3a5f;
  --accent-dim: #152a45;
  --good: #1f6b4a;
  --warn: #9a6700;
  --font: "Source Sans 3", "Helvetica Neue", Arial, sans-serif;
  --serif: "Cormorant Garamond", "Times New Roman", Georgia, serif;
  --mono: "SF Mono", ui-monospace, Menlo, monospace;
  --max: 720px;
  --wide: 960px;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
  font-size: 17px;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--accent-dim); text-decoration: underline; }
header {
  border-bottom: 2px solid var(--border-strong);
  background: linear-gradient(180deg, #ffffff 0%, var(--surface-alt) 100%);
  padding: 2rem 1.5rem 1.75rem;
}
.header-inner { max-width: var(--wide); margin: 0 auto; }
.brand {
  font-family: var(--serif);
  font-size: 0.85rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 0.35rem;
}
h1.title {
  font-family: var(--serif);
  font-size: 2.15rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
  line-height: 1.15;
  color: var(--text);
  letter-spacing: 0.02em;
}
.subtitle { color: var(--muted); font-size: 1.02rem; max-width: 42rem; line-height: 1.55; }
nav.top {
  max-width: var(--wide);
  margin: 1.25rem auto 0;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
nav.top a {
  padding: 0.4rem 0.85rem;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  background: var(--surface);
  color: var(--accent);
}
nav.top a:hover { background: var(--surface-alt); text-decoration: none; }
nav.top a.primary {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}
main { max-width: var(--max); margin: 0 auto; padding: 2rem 1.5rem 4rem; }
main.wide { max-width: var(--wide); }
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1.25rem 1.5rem;
  margin: 1.5rem 0;
  box-shadow: 0 1px 3px rgba(26, 39, 68, 0.04);
}
.card h3 { margin-top: 0; font-size: 1rem; color: var(--accent); font-family: var(--serif); }
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin: 1.5rem 0;
}
.stat {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1rem;
}
.stat .label { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; }
.stat .value { font-family: var(--serif); font-size: 1.45rem; font-weight: 700; margin-top: 0.25rem; color: var(--text); }
.stat .value.good { color: var(--good); }
.stat .value.warn { color: var(--warn); }
blockquote {
  margin: 1.5rem 0;
  padding: 1rem 1.35rem;
  border-left: 3px solid var(--accent);
  background: var(--surface-alt);
  border-radius: 0 4px 4px 0;
  color: var(--muted);
  font-family: var(--serif);
  font-size: 1.08rem;
  font-style: italic;
}
h2 {
  font-family: var(--serif);
  font-size: 1.55rem;
  font-weight: 700;
  margin: 2.25rem 0 1rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--border-strong);
  color: var(--text);
  letter-spacing: 0.01em;
}
h3 { font-family: var(--serif); font-size: 1.15rem; font-weight: 600; margin: 1.5rem 0 0.75rem; color: var(--accent); }
p { margin: 0.75rem 0; }
ul, ol { padding-left: 1.25rem; }
li { margin: 0.35rem 0; }
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92rem;
  margin: 1rem 0;
}
th, td {
  border: 1px solid var(--border);
  padding: 0.55rem 0.75rem;
  text-align: left;
}
th { background: var(--surface-alt); color: var(--accent); font-weight: 600; font-size: 0.82rem; letter-spacing: 0.04em; text-transform: uppercase; }
table.data-table th.num,
table.data-table td.num {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.table-wrap {
  overflow-x: auto;
  margin: 1rem 0;
  -webkit-overflow-scrolling: touch;
}
.table-wrap table { margin: 0; }
.conclusion-box {
  background: var(--surface);
  border: 1px solid var(--accent);
  border-left: 4px solid var(--accent);
  border-radius: 4px;
  padding: 1.25rem 1.5rem;
  margin: 1.5rem 0;
}
.claim-discipline {
  background: var(--surface-alt);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1.25rem 1.5rem;
  margin: 1.5rem 0;
  color: var(--text);
}
code, pre {
  font-family: var(--mono);
  font-size: 0.85rem;
  background: var(--surface-alt);
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text);
}
code { padding: 0.15rem 0.4rem; }
pre { padding: 1rem; overflow-x: auto; }
pre code { border: none; padding: 0; background: none; }
footer {
  max-width: var(--wide);
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
  border-top: 2px solid var(--border-strong);
  color: var(--muted);
  font-size: 0.85rem;
  background: var(--surface-alt);
}
.disclaimer {
  background: #fff8ee;
  border: 1px solid #e8d5b0;
  color: #6b5344;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  font-size: 0.88rem;
  margin-top: 1rem;
}
/* Cover page */
body.cover-page {
  background: var(--bg);
}
body.cover-page header.hero-cover {
  border-bottom: 2px solid var(--border-strong);
  padding: 3rem 1.5rem 2.5rem;
  text-align: center;
  background:
    radial-gradient(ellipse 70% 50% at 50% 0%, rgba(30, 58, 95, 0.06) 0%, transparent 60%),
    linear-gradient(180deg, #ffffff 0%, var(--bg) 100%);
}
.hero-cover .lab-title {
  font-family: var(--serif);
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 700;
  letter-spacing: 0.08em;
  margin: 0 0 0.5rem;
  line-height: 1.1;
  color: var(--text);
}
.hero-cover .tagline {
  color: var(--muted);
  font-size: clamp(1rem, 2.2vw, 1.15rem);
  max-width: 40rem;
  margin: 0 auto 0.5rem;
  line-height: 1.55;
}
.hero-cover .motto {
  font-size: 0.78rem;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0.75rem auto 1.5rem;
  font-weight: 600;
}
.hero-cover .author {
  color: var(--accent);
  font-size: 0.92rem;
  letter-spacing: 0.06em;
  margin-bottom: 1.5rem;
}
.logo-frame {
  display: inline-block;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1rem 1.5rem;
  margin: 0 auto 1rem;
  box-shadow: 0 4px 24px rgba(26, 39, 68, 0.08);
}
.fx-lab-logo {
  display: block;
  max-width: min(340px, 88vw);
  width: 100%;
  height: auto;
  margin: 0 auto;
}
.fx-lab-logo-sm {
  display: block;
  max-width: 220px;
  width: 100%;
  height: auto;
  margin: 0 0 1rem;
}
.institute-brand-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}
.institute-brand-link {
  display: inline-flex;
  align-items: center;
  line-height: 0;
  text-decoration: none;
}
.institute-brand-link:hover { opacity: 0.9; text-decoration: none; }
.institute-brand-sep {
  color: var(--muted);
  font-size: 0.85rem;
  opacity: 0.5;
  user-select: none;
}
.bfi-logo-header-sm,
.bfi-logo-header-sm-inv {
  height: 32px;
  width: auto;
  display: block;
  background: transparent;
  border: none;
  box-shadow: none;
}
.bfi-logo-header-sm-inv { height: 30px; }
.institute-brand-link img {
  background: transparent;
  border: none;
  box-shadow: none;
}
.cta-row {
  display: flex;
  gap: 0.65rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 1.25rem;
}
.cta-row a {
  padding: 0.6rem 1.15rem;
  border-radius: 4px;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  text-decoration: none;
}
.cta-row a.primary {
  background: var(--accent);
  border: 1px solid var(--accent);
  color: #fff;
}
.cta-row a.secondary {
  background: var(--surface);
  border: 1px solid var(--border-strong);
  color: var(--accent);
}
.principle-box {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent);
  border-radius: 4px;
  padding: 1.5rem 1.75rem;
  margin: 2rem 0;
  font-size: 1.02rem;
  box-shadow: 0 1px 3px rgba(26, 39, 68, 0.04);
}
.principle-box p { margin: 0.5rem 0; color: var(--text); }
.cover-main { max-width: var(--wide); }
.cover-main h2:first-child { margin-top: 0; }
.vertical-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.25rem;
  margin: 2rem 0;
}
.vertical-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1.5rem;
  text-align: left;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  box-shadow: 0 1px 3px rgba(26, 39, 68, 0.04);
}
.vertical-card:hover { border-color: var(--accent); box-shadow: 0 4px 12px rgba(26, 39, 68, 0.08); }
.vertical-card .tag {
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.5rem;
}
.vertical-card h3 {
  margin: 0 0 0.5rem;
  font-family: var(--serif);
  font-size: 1.15rem;
  color: var(--text);
  border: none;
  padding: 0;
}
.vertical-card p {
  color: var(--muted);
  font-size: 0.95rem;
  margin: 0 0 1rem;
}
.vertical-card a.btn {
  display: inline-block;
  padding: 0.5rem 0.95rem;
  border-radius: 4px;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  text-decoration: none;
  color: #fff;
  background: var(--accent);
}
.vertical-card a.btn:hover { text-decoration: none; opacity: 0.92; }
.research-link-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin: 1.25rem 0 2rem;
}
.research-link-card {
  display: block;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1.25rem 1.35rem;
  text-decoration: none;
  color: inherit;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  box-shadow: 0 1px 3px rgba(26, 39, 68, 0.04);
}
.research-link-card:hover {
  border-color: var(--accent);
  text-decoration: none;
  box-shadow: 0 4px 12px rgba(26, 39, 68, 0.08);
}
.research-link-card .tag {
  font-size: 0.68rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 0.4rem;
  display: block;
  font-weight: 600;
}
.research-link-card h3 {
  margin: 0 0 0.35rem;
  font-family: var(--serif);
  font-size: 1.08rem;
  color: var(--text);
  border: none;
  padding: 0;
}
.research-link-card p {
  margin: 0;
  font-size: 0.92rem;
  color: var(--muted);
  line-height: 1.5;
}
.back-link {
  display: inline-block;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: var(--muted);
}
@media (max-width: 600px) {
  h1.title { font-size: 1.55rem; }
  body { font-size: 16px; }
  .hero-cover .lab-title { letter-spacing: 0.05em; }
}
"""


def _css_home() -> str:
    """Dark institutional theme for the BR3N Macro Labs homepage."""
    return (
        _css()
        + """
body.home-page {
  --bg: #050608;
  --surface: #0b0f14;
  --surface-alt: #111827;
  --border: #1f2937;
  --border-strong: #374151;
  --text: #f8fafc;
  --muted: #94a3b8;
  --accent: #38bdf8;
  --accent-dim: #7dd3fc;
  --gold: #d4af37;
  --good: #22c55e;
  --warn: #f59e0b;
  background:
    linear-gradient(rgba(56, 189, 248, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(56, 189, 248, 0.025) 1px, transparent 1px),
    var(--bg);
  background-size: 48px 48px, 48px 48px, auto;
}
body.home-page header.hero-cover {
  background:
    radial-gradient(ellipse 80% 55% at 50% -10%, rgba(56, 189, 248, 0.09) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 85% 20%, rgba(212, 175, 55, 0.06) 0%, transparent 50%),
    linear-gradient(180deg, #0b0f14 0%, var(--bg) 100%);
  border-bottom: 1px solid var(--border);
}
body.home-page .logo-frame {
  background: transparent;
  border-color: var(--border);
  box-shadow: none;
}
body.home-page .hero-cover .lab-title {
  letter-spacing: 0.06em;
  text-transform: none;
  font-size: clamp(1.85rem, 4.5vw, 2.85rem);
  color: var(--text);
}
body.home-page .hero-cover .home-subtitle {
  font-family: var(--serif);
  font-size: clamp(1.05rem, 2.4vw, 1.35rem);
  color: var(--gold);
  letter-spacing: 0.04em;
  margin: 0.35rem auto 0.75rem;
  font-weight: 500;
}
body.home-page .hero-cover .home-hero-line {
  font-family: var(--serif);
  font-size: clamp(1.05rem, 2.2vw, 1.25rem);
  font-style: italic;
  color: var(--muted);
  max-width: 44rem;
  margin: 0.75rem auto 0;
  line-height: 1.55;
}
body.home-page .hero-cover .motto { color: var(--muted); opacity: 0.85; }
body.home-page .hero-cover .author { color: var(--accent); }
body.home-page .cta-row a.primary {
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.35);
  color: var(--accent);
}
body.home-page .cta-row a.secondary {
  background: rgba(17, 24, 39, 0.6);
  border: 1px solid var(--border);
  color: var(--muted);
}
body.home-page .cta-row a:hover { opacity: 0.92; text-decoration: none; }
body.home-page nav.top a {
  background: rgba(11, 15, 20, 0.7);
  border-color: var(--border);
  color: var(--muted);
}
body.home-page nav.top a:hover {
  border-color: rgba(56, 189, 248, 0.35);
  color: var(--accent);
}
body.home-page nav.top a.primary {
  background: rgba(56, 189, 248, 0.12);
  border-color: rgba(56, 189, 248, 0.35);
  color: var(--accent);
}
body.home-page main.cover-main {
  padding: 2.5rem 1.5rem 3rem;
  margin: 0 auto;
}
body.home-page .home-section {
  margin: 2.75rem 0;
}
body.home-page .home-section h2 {
  font-family: var(--serif);
  font-size: 1.35rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text);
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.5rem;
  margin: 0 0 1.25rem;
}
body.home-page .home-mission {
  font-size: 1.02rem;
  line-height: 1.75;
  color: var(--muted);
  max-width: 52rem;
  margin: 0;
}
body.home-page .flagship-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}
body.home-page .flagship-card {
  display: block;
  background: linear-gradient(145deg, rgba(11, 15, 20, 0.95) 0%, rgba(17, 24, 39, 0.55) 100%);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1.35rem 1.4rem;
  text-decoration: none;
  color: inherit;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
}
body.home-page .flagship-card:hover {
  border-color: rgba(56, 189, 248, 0.35);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.04);
  text-decoration: none;
  transform: translateY(-1px);
}
body.home-page .flagship-card .card-tag {
  font-size: 0.62rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gold);
  font-weight: 600;
  margin-bottom: 0.45rem;
}
body.home-page .flagship-card h3 {
  margin: 0 0 0.55rem;
  font-family: var(--serif);
  font-size: 1.12rem;
  color: var(--text);
  border: none;
  padding: 0;
}
body.home-page .flagship-card p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.6;
  color: var(--muted);
}
body.home-page .discipline-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin: 0;
  padding: 0;
  list-style: none;
}
body.home-page .discipline-badge {
  display: inline-block;
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 600;
  padding: 0.35rem 0.65rem;
  border-radius: 3px;
  border: 1px solid var(--border);
  background: rgba(17, 24, 39, 0.55);
  color: var(--muted);
}
body.home-page .discipline-badge.emphasis {
  border-color: rgba(212, 175, 55, 0.35);
  color: var(--gold);
}
body.home-page .focus-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.65rem;
  list-style: none;
  margin: 0;
  padding: 0;
}
body.home-page .focus-grid li {
  font-size: 0.9rem;
  color: var(--muted);
  padding: 0.55rem 0.75rem;
  border-left: 2px solid rgba(56, 189, 248, 0.35);
  background: rgba(11, 15, 20, 0.5);
}
body.home-page .questions-list {
  margin: 0;
  padding: 0;
  list-style: none;
  counter-reset: rq;
}
body.home-page .questions-list li {
  counter-increment: rq;
  position: relative;
  padding: 0.85rem 0 0.85rem 2.5rem;
  border-bottom: 1px solid var(--border);
  font-family: var(--serif);
  font-size: 1.05rem;
  color: var(--text);
  line-height: 1.45;
}
body.home-page .questions-list li:last-child { border-bottom: none; }
body.home-page .questions-list li::before {
  content: counter(rq, decimal-leading-zero);
  position: absolute;
  left: 0;
  top: 0.85rem;
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.06em;
  color: var(--gold);
}
body.home-page .fx-spotlight {
  background: linear-gradient(135deg, rgba(11, 15, 20, 0.95) 0%, rgba(30, 58, 95, 0.15) 100%);
  border: 1px solid var(--border);
  border-left: 3px solid var(--gold);
  border-radius: 6px;
  padding: 1.5rem 1.65rem;
}
body.home-page .fx-spotlight h3 {
  margin: 0 0 0.35rem;
  font-family: var(--serif);
  font-size: 1.2rem;
  color: var(--text);
  border: none;
  padding: 0;
}
body.home-page .fx-spotlight .fx-tagline {
  font-size: 0.95rem;
  color: var(--gold);
  font-style: italic;
  margin-bottom: 0.75rem;
}
body.home-page .fx-spotlight p {
  margin: 0 0 1rem;
  font-size: 0.92rem;
  color: var(--muted);
  line-height: 1.65;
}
body.home-page .fx-spotlight a.btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--gold);
  border: 1px solid rgba(212, 175, 55, 0.35);
  background: rgba(212, 175, 55, 0.08);
}
body.home-page footer {
  background: var(--bg);
  border-top: 1px solid var(--border);
  color: var(--muted);
}
body.home-page .disclaimer {
  background: rgba(245, 158, 11, 0.06);
  border: 1px solid rgba(245, 158, 11, 0.25);
  color: var(--muted);
}
"""
    )


FLAGSHIP_HOME_CARDS: list[tuple[str, str, str, str]] = [
    (
        "global-fx-lab.html",
        "Global FX Lab",
        "Tests when currency markets become less random by studying trend, volatility, carry, liquidity stress, and payment-flow pressure. Separates forecast accuracy, trading P&L, and hedge-governance usefulness.",
        "FX · Regimes",
    ),
    (
        "value-survival-index.html",
        "Value Survival Index",
        "Measures how much usable purchasing power survives when money crosses borders after fees, FX spreads, transfer timing, volatility, inflation erosion, payout friction, dollar dependency, and currency trust adjustments.",
        "Remittance · VSI",
    ),
    (
        "settlement-economics-lab.html",
        "Settlement Economics Lab",
        "Measures settlement drag, operational liquidity burden, finality quality, and payment-network fragility. Core thesis: the economy is not complete when money is promised; it is complete when value settles.",
        "Settlement",
    ),
    (
        "stablecoin-settlement-lab.html",
        "Stablecoin Settlement Window Lab",
        "Studies what happens when settlement windows collapse toward zero. Core thesis: stablecoins do not eliminate settlement risk; they change its location, speed, and legal form.",
        "Stablecoin · SWC",
    ),
    (
        "lab-status.html",
        "Data Lake & Audit Layer",
        "Preserves raw data, cleaned tables, model outputs, source lineage, file hashes, data quality scores, methodology versions, snapshots, and reproducibility reports.",
        "Data · Audit",
    ),
]

HOME_DISCIPLINE_BADGES: list[tuple[str, bool]] = [
    ("Research only", True),
    ("Not investment advice", True),
    ("No live trading", True),
    ("Mock data labeled", False),
    ("Source lineage required", False),
    ("Data quality scored", False),
    ("Sensitivity tested", False),
    ("Replication first", False),
]

HOME_CURRENT_FOCUS: list[str] = [
    "Conditional FX forecastability",
    "Cross-border value survival",
    "Settlement drag and liquidity burden",
    "Ledger finality vs economic finality",
    "Stablecoin risk relocation",
    "Data quality and reproducibility",
]

HOME_CORE_QUESTIONS: list[str] = [
    "When do FX markets become less random?",
    "When value crosses borders, how much survives?",
    "How much economic value is lost to settlement delay?",
    "When money settles instantly, where does trust go?",
    "Can payment infrastructure become a new form of monetary power?",
]


def _looks_numeric(s: str) -> bool:
    s = s.strip().replace(",", "")
    if s in ("—", "True", "False", "None", "", "nan"):
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def _numeric_col_flags(headers: list[str], rows: list[list[str]]) -> list[bool]:
    text_cols = {"strategy", "regime", "ticker", "sample", "split", "question", "level", "policy_name", "exposure_type"}
    flags: list[bool] = []
    for j, header in enumerate(headers):
        if header.lower().replace(" ", "_") in text_cols or header in text_cols:
            flags.append(False)
            continue
        vals = [r[j] for r in rows if j < len(r)]
        nums = sum(1 for v in vals if _looks_numeric(v))
        flags.append(bool(vals) and nums >= max(1, int(len(vals) * 0.55)))
    return flags


def _research_links_grid(links: list[tuple[str, str, str, str]]) -> str:
    cards = []
    for href, title, desc, tag in links:
        cards.append(
            f'<a href="{html.escape(href, quote=True)}" class="research-link-card">'
            f'<span class="tag">{html.escape(tag)}</span>'
            f"<h3>{html.escape(title)}</h3>"
            f"<p>{html.escape(desc)}</p>"
            f"</a>"
        )
    return '<div class="research-link-grid">' + "".join(cards) + "</div>"


def _skip_research_link_bullets(lines: list[str], i: int) -> int:
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("## ") or stripped == "---":
            break
        if re.match(r"^[-*] ", lines[i]):
            i += 1
            continue
        if not stripped:
            i += 1
            continue
        break
    return i


def _md_to_html(text: str, *, research_links: list[tuple[str, str, str, str]] | None = None) -> str:
    """Minimal markdown → HTML (headings, lists, tables, bold, code, blockquote)."""
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    in_pre = False

    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("```"):
            if not in_pre:
                lang = line.strip()[3:].strip()
                out.append(f'<pre><code class="{html.escape(lang)}">')
                in_pre = True
            else:
                out.append("</code></pre>")
                in_pre = False
            i += 1
            continue

        if in_pre:
            out.append(html.escape(line))
            i += 1
            continue

        if line.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            if len(rows) >= 2:
                num_flags = _numeric_col_flags(rows[0], rows[2:])
                def _th(c: str, j: int) -> str:
                    cls = ' class="num"' if num_flags[j] else ""
                    return f"<th{cls}>{_inline(c)}</th>"

                def _td(c: str, j: int) -> str:
                    cls = ' class="num"' if num_flags[j] else ""
                    return f"<td{cls}>{_inline(c)}</td>"

                out.append('<div class="table-wrap"><table class="data-table">')
                out.append("<thead><tr>" + "".join(_th(c, j) for j, c in enumerate(rows[0])) + "</tr></thead>")
                out.append("<tbody>")
                for row in rows[2:]:
                    out.append("<tr>" + "".join(_td(c, j) for j, c in enumerate(row)) + "</tr>")
                out.append("</tbody></table></div>")
            continue

        if line.startswith("# "):
            out.append(f"<h1>{_inline(line[2:])}</h1>")
        elif line.startswith("## Claim discipline"):
            out.append(f"<h2>{_inline(line[3:])}</h2>")
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            para_lines = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("#") and not lines[i].startswith("|"):
                para_lines.append(lines[i].strip())
                i += 1
            inner = " ".join(_inline(p) for p in para_lines)
            out.append(f'<div class="claim-discipline"><p>{inner}</p></div>')
            continue
        elif line.startswith("## Main conclusion"):
            out.append(f"<h2>{_inline(line[3:])}</h2>")
            i += 1
            continue
        elif line.startswith("## Explore FX Lab Research"):
            out.append("<h2>Explore FX Lab Research</h2>")
            if research_links:
                out.append(_research_links_grid(research_links))
            i += 1
            i = _skip_research_link_bullets(lines, i)
            continue
        elif line.startswith("## "):
            out.append(_h2(line[3:]))
        elif line.startswith("### "):
            out.append(f"<h3>{_inline(line[4:])}</h3>")
        elif line.startswith(">") or line.startswith("> "):
            quote_lines = []
            while i < len(lines) and (lines[i].startswith(">") or lines[i].strip() == ""):
                if lines[i].startswith(">"):
                    q = lines[i].lstrip(">").strip()
                    if q:
                        quote_lines.append(q)
                elif quote_lines:
                    break
                i += 1
            inner = " ".join(_inline(q) for q in quote_lines)
            out.append(f'<div class="principle-box"><p>{inner}</p></div>')
            continue
        elif re.match(r"^[-*] ", line):
            items = []
            while i < len(lines) and re.match(r"^[-*] ", lines[i]):
                items.append(f"<li>{_inline(lines[i][2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif re.match(r"^\d+\. ", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                text = re.sub(r"^\d+\.\s*", "", lines[i])
                items.append(f"<li>{_inline(text)}</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        elif line.strip() == "---":
            out.append("<hr/>")
        elif line.strip():
            out.append(f"<p>{_inline(line)}</p>")
        i += 1

    return "\n".join(out)


def _heading_id(title: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    return re.sub(r"\s+", "-", slug.strip())


def _h2(title: str, *, with_id: bool = True) -> str:
    inner = _inline(title)
    if with_id:
        return f'<h2 id="{html.escape(_heading_id(title), quote=True)}">{inner}</h2>'
    return f"<h2>{inner}</h2>"


def _inline(s: str) -> str:
    def _link(m: re.Match[str]) -> str:
        return f'<a href="{html.escape(m.group(2), quote=True)}">{html.escape(m.group(1))}</a>'

    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s


def _os_model_cards_html() -> str:
    """Render model registry entries as dark-theme cards."""
    from .models.model_registry import CATEGORY_LABELS, MODEL_REGISTRY

    parts: list[str] = []
    for cat_key, cat_label in CATEGORY_LABELS.items():
        parts.append(f"<h3>{html.escape(cat_label)}</h3>")
        parts.append('<div class="os-card-grid">')
        for mid, meta in MODEL_REGISTRY.items():
            if meta.get("category") != cat_key:
                continue
            improvements = meta.get("br3n_improvement", [])
            imp_html = (
                "<ul>"
                + "".join(f"<li>{html.escape(i)}</li>" for i in improvements)
                + "</ul>"
                if improvements
                else ""
            )
            parts.append(
                f"""<div class="os-card">
  <div class="meta">{html.escape(meta.get("type", ""))} · {html.escape(meta.get("status", ""))}</div>
  <h4>{html.escape(meta.get("title", mid))}</h4>
  <p>{html.escape(meta.get("description", ""))}</p>
  <p><span class="label">Use case:</span> {html.escape(meta.get("use_case", ""))}</p>
  <p><span class="label">Source:</span> {html.escape(meta.get("source", ""))}</p>
  <p><span class="label">BR3N improvements:</span></p>{imp_html}
</div>"""
            )
        parts.append("</div>")
    return "\n".join(parts)


def _open_source_ai_body(out_dir: Path) -> str:
    page_md = _read_md(out_dir / "OPEN_SOURCE_FX_AI_MODEL_LAB_PAGE.md") or _read_md(
        ROOT / "reports/publication/OPEN_SOURCE_FX_AI_MODEL_LAB_PAGE.md"
    )
    full_md = _read_md(ROOT / "reports/OPEN_SOURCE_FX_AI_MODEL_LAB.md")
    arch = """BR3N FX Lab v1
├── Baselines
│   ├── EUR/USD LSTM
│   ├── EUR/USD TimeSeriesTransformer
│   ├── TimesFM
│   ├── Lag-Llama
│   └── FinRL / TensorTrade
│
├── Data Layer
│   ├── OHLCV
│   ├── interest-rate differentials
│   ├── forward points / carry
│   ├── DXY / VIX / yields
│   ├── macro indicators
│   └── news sentiment
│
├── Signal Engine
│   ├── direction probability
│   ├── expected return
│   ├── volatility forecast
│   ├── carry score
│   └── confidence score
│
├── Trading Layer
│   ├── long / short / flat
│   ├── position sizing
│   ├── stop-loss logic
│   ├── drawdown controls
│   └── transaction costs
│
└── Research Dashboard
    ├── accuracy · Sharpe · Sortino · max drawdown
    ├── win rate · avg win/loss · profit factor
    └── regime performance"""
    return f"""
<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>
<div class="warning-box">
  <p><strong>Warning:</strong> These models are not trading systems by themselves. They are research baselines.
  Every model must be tested out-of-sample with realistic transaction costs, drawdown controls, and no look-ahead bias
  before any trading use.</p>
</div>
<div class="conclusion-box">
  <p><strong>Conclusion:</strong> The edge is not copying an open-source FX model. The edge is building a disciplined
  research pipeline that proves when a model works, when it fails, and why.</p>
</div>
{_md_to_html(page_md) if page_md else ""}
<h2>Model Registry</h2>
{_os_model_cards_html()}
<h2>Architecture</h2>
<pre class="arch-tree">{html.escape(arch)}</pre>
<hr/>
<h2>Full Documentation</h2>
{_md_to_html(full_md) if full_md else "<p><em>Missing reports/OPEN_SOURCE_FX_AI_MODEL_LAB.md</em></p>"}
"""


def _global_fx_lab_body(out_dir: Path) -> str:
    page_md = _read_md(out_dir / "GLOBAL_FX_RESEARCH_LAB_PAGE.md") or _read_md(
        ROOT / "reports/publication/GLOBAL_FX_RESEARCH_LAB_PAGE.md"
    )
    indices = [
        ("Hidden FX Tax Index", "Full cross-border conversion burden beyond visible fees"),
        ("Remittance Welfare Loss Index", "Purchasing power destroyed between sender and recipient"),
        ("Currency Credibility Index", "FX as market price of national credibility"),
        ("Dollar Dependency Index", "Reliance on USD financial infrastructure"),
        ("Labor Conversion Index", "How FX reprices human labor globally"),
        ("Currency Stress Index", "Early warning when currency belief is under stress"),
    ]
    cards = "".join(
        f'<div class="os-card"><h4>{html.escape(t)}</h4><p>{html.escape(d)}</p></div>'
        for t, d in indices
    )
    return f"""
<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>
<div class="warning-box">
  <p><strong>Research only.</strong> Not investment advice. Stage 3 wires World Bank API macro, multi-quarter RPW panel, sovereignty research layer, and walk-forward stress models. Drop full RPW Excel in <code>data/raw/world_bank_rpw/</code> for bulk parse.</p>
</div>
<div class="conclusion-box">
  <p><strong>Core question:</strong> Who bears the cost when value crosses borders?</p>
</div>
{_md_to_html(page_md) if page_md else ""}
<h2>Flagship Indices</h2>
<div class="os-card-grid">{cards}</div>
<p><em>Interactive dashboard runs locally: <code>streamlit run src/global_fx_research_lab.py</code></em></p>
"""


def _vsi_corridor_table_html() -> str:
    """Build live corridor VSI summary table from pipeline outputs."""
    import pandas as pd

    vsi_path = ROOT / "data" / "outputs" / "value_survival_outputs.csv"
    if not vsi_path.exists():
        return "<p><em>Run <code>python scripts/run_vsi.py</code> to generate corridor rankings.</em></p>"
    try:
        df = pd.read_csv(vsi_path)
        summary = (
            df.groupby("corridor", as_index=False)
            .agg(
                vsi=("value_survival_index", "mean"),
                loss_pct=("total_value_loss_pct", "mean"),
                loss_per_100=("value_loss_usd_per_100", "mean"),
                interpretation=("interpretation", "first"),
                mock=("mock_data_flag", "first"),
            )
            .sort_values("vsi", ascending=False)
        )
        rows = []
        for _, r in summary.iterrows():
            mock_badge = ' <span class="tag">mock</span>' if r.get("mock") else ""
            rows.append(
                f"<tr><td>{html.escape(str(r['corridor']))}{mock_badge}</td>"
                f'<td class="num">{r["vsi"]:.1f}</td>'
                f'<td class="num">{r["loss_pct"]*100:.2f}%</td>'
                f'<td class="num">${r["loss_per_100"]:.2f}</td>'
                f"<td>{html.escape(str(r['interpretation']))}</td></tr>"
            )
        return f"""
<h2>Corridor Rankings (live pipeline)</h2>
<table>
<thead><tr><th>Corridor</th><th>VSI</th><th>Total loss</th><th>Lost per $100</th><th>Classification</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table>
<p class="meta">Source: <code>data/outputs/value_survival_outputs.csv</code> · {len(df)} observations · {len(summary)} corridors</p>
"""
    except Exception as exc:
        return f"<p><em>Could not load VSI outputs: {html.escape(str(exc))}</em></p>"


def _value_survival_index_body(out_dir: Path) -> str:
    page_md = _read_md(out_dir / "VALUE_SURVIVAL_INDEX_PAGE.md") or _read_md(
        ROOT / "reports/publication/VALUE_SURVIVAL_INDEX_PAGE.md"
    )
    components = [
        ("Explicit Fee", "Visible remittance transfer fee"),
        ("FX Spread", "Exchange-rate margin on corridor"),
        ("Timing Loss", "FX exposure during transfer delay"),
        ("Volatility Loss", "Unhedged household FX risk"),
        ("Inflation Erosion", "Purchasing power while in transit"),
        ("Payout Friction", "Last-mile cash-out costs"),
        ("Dollar Dependency Drag", "USD infrastructure burden"),
        ("Trust Discount", "Lower currency trust → higher discount"),
    ]
    cards = "".join(
        f'<div class="os-card"><h4>{html.escape(t)}</h4><p>{html.escape(d)}</p></div>'
        for t, d in components
    )
    return f"""
<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>
<div class="warning-box">
  <p><strong>Research only.</strong> Not investment advice. VSI Stage 1 uses World Bank RPW historical panel, KNOMAD flows, IMF FX cache, WB API macro, and transparent formula placeholders. Not a trading signal.</p>
</div>
<div class="conclusion-box">
  <p><strong>Core thesis:</strong> Foreign exchange is the daily auction of global trust. The Value Survival Index measures how much economic value survives when it crosses borders.</p>
</div>
{_md_to_html(page_md) if page_md else ""}
<h2>Loss Components</h2>
<div class="os-card-grid">{cards}</div>
{_vsi_corridor_table_html()}
<p><em>Interactive dashboard: <code>streamlit run src/dashboard/app.py</code></em></p>
"""


def _settlement_sdi_table_html() -> str:
    import pandas as pd

    path = ROOT / "settlement_lab" / "data" / "outputs" / "settlement_drag_outputs.csv"
    if not path.exists():
        return "<p><em>Run <code>cd settlement_lab && python scripts/reproduce_settlement_lab.py</code> to generate SDI rankings.</em></p>"
    try:
        df = pd.read_csv(path)
        summary = (
            df.groupby("entity", as_index=False)
            .agg(
                sdi=("settlement_drag_index", "mean"),
                drag_per_100=("settlement_drag_cost_per_100", "mean"),
                interpretation=("interpretation", "first"),
                mock=("mock_data_flag", "first"),
            )
            .sort_values("sdi", ascending=False)
            .head(15)
        )
        rows = []
        for _, r in summary.iterrows():
            badge = ' <span class="tag">demo</span>' if r.get("mock") else ""
            rows.append(
                f"<tr><td>{html.escape(str(r['entity']))}{badge}</td>"
                f'<td class="num">{r["sdi"]:.1f}</td>'
                f'<td class="num">{r["drag_per_100"]:.2f}</td>'
                f"<td>{html.escape(str(r['interpretation']))}</td></tr>"
            )
        return f"""
<h2>Settlement Drag Rankings (live pipeline)</h2>
<table>
<thead><tr><th>Rail / Entity</th><th>SDI</th><th>Drag per $100</th><th>Classification</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table>
<p class="meta">Source: settlement_lab/data/outputs/settlement_drag_outputs.csv</p>
"""
    except Exception as exc:
        return f"<p><em>Could not load SDI outputs: {html.escape(str(exc))}</em></p>"


def _settlement_lab_body(out_dir: Path) -> str:
    page_md = _read_md(out_dir / "SETTLEMENT_ECONOMICS_LAB_PAGE.md") or _read_md(
        ROOT / "reports/publication/SETTLEMENT_ECONOMICS_LAB_PAGE.md"
    )
    models = [
        ("Settlement Drag Index (SDI)", "Economic cost of delayed settlement"),
        ("Operational Liquidity Burden (OLB)", "Capital trapped for settlement safety"),
        ("Finality Quality Index (FQI)", "Proximity to final usable value"),
        ("Payment Network Fragility (PNF)", "Settlement stress → disruption risk"),
        ("Payment Friction Incidence (PFI)", "Who bears payment-system costs (model-based)"),
    ]
    cards = "".join(
        f'<div class="os-card"><h4>{html.escape(t)}</h4><p>{html.escape(d)}</p></div>'
        for t, d in models
    )
    return f"""
<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>
<div class="warning-box">
  <p><strong>Research only.</strong> Not financial advice. Not operational payment guidance. Stage 1 uses strict data lineage (NO_UNLABELED_DATA). Demo settlement tables with bridged IMF/FRED/RPW where available.</p>
</div>
<div class="conclusion-box">
  <p><strong>Core thesis:</strong> Modern economies do not run only on money; they run on settlement.</p>
</div>
{_md_to_html(page_md) if page_md else ""}
<h2>Flagship Models</h2>
<div class="os-card-grid">{cards}</div>
{_settlement_sdi_table_html()}
<p><em>Interactive dashboard: <code>cd settlement_lab && streamlit run src/dashboard/app.py</code></em></p>
"""


def _stablecoin_swc_table_html() -> str:
    import pandas as pd

    path = ROOT / "stablecoin_lab" / "data" / "outputs" / "settlement_window_compression_outputs.csv"
    if not path.exists():
        return "<p><em>Run <code>cd stablecoin_lab && python scripts/reproduce_stablecoin_lab.py</code> to generate SWC rankings.</em></p>"
    try:
        df = pd.read_csv(path)
        summary = (
            df.groupby("entity", as_index=False)
            .agg(
                swc=("swc_core", "mean"),
                risk_adj=("swc_risk_adjusted", "mean"),
                interpretation=("interpretation", "first"),
                mock=("mock_data_flag", "first"),
            )
            .sort_values("swc", ascending=False)
            .head(15)
        )
        rows = []
        for _, r in summary.iterrows():
            badge = ' <span class="tag">demo</span>' if r.get("mock") else ""
            rows.append(
                f"<tr><td>{html.escape(str(r['entity']))}{badge}</td>"
                f'<td class="num">{r["swc"]:.1f}</td>'
                f'<td class="num">{r["risk_adj"]:.1f}</td>'
                f"<td>{html.escape(str(r['interpretation']))}</td></tr>"
            )
        return f"""
<h2>Settlement Window Compression Rankings (live pipeline)</h2>
<table>
<thead><tr><th>Corridor</th><th>SWC</th><th>Risk-adj.</th><th>Interpretation</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table>
"""
    except Exception as exc:
        return f"<p><em>Could not load SWC table: {html.escape(str(exc))}</em></p>"


def _stablecoin_lab_body(out_dir: Path) -> str:
    page_md = _read_md(out_dir / "STABLECOIN_SETTLEMENT_LAB_PAGE.md") or _read_md(
        ROOT / "reports/publication/STABLECOIN_SETTLEMENT_LAB_PAGE.md"
    )
    models = [
        ("Stablecoin Finality Quality (SFQI)", "Ledger vs economic finality"),
        ("Settlement Window Compression (SWC)", "Net benefit vs risk redistribution"),
        ("Stablecoin Liquidity Transformation (SLT)", "User benefit vs reserve burden"),
        ("Digital Run Velocity (DRV)", "Run-conditions composite — not run prediction"),
        ("Stablecoin Value Survival (SVSI)", "Usable value on remittance rails"),
    ]
    cards = "".join(
        f'<div class="os-card"><h4>{html.escape(t)}</h4><p>{html.escape(d)}</p></div>'
        for t, d in models
    )
    return f"""
<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>
<div class="warning-box">
  <p><strong>Research only.</strong> Not financial advice. Mixed-mode data: DeFiLlama supply/prices, issuer attestations, World Bank RPW baselines, BIS/Fed references. Off-ramp tables remain Tier 4 manual until exchange data is added.</p>
</div>
<div class="conclusion-box">
  <p><strong>Core thesis:</strong> Stablecoins do not eliminate settlement risk; they change its location, speed, and legal form.</p>
</div>
{_md_to_html(page_md) if page_md else ""}
<h2>Flagship Models</h2>
<div class="os-card-grid">{cards}</div>
{_stablecoin_swc_table_html()}
<p><em>Interactive dashboard: <code>cd stablecoin_lab && streamlit run src/dashboard/app.py</code></em></p>
"""


def _css_os_lab() -> str:
    """Dark institutional theme for the Open Source FX AI Model Lab page."""
    return (
        _css()
        + """
body.os-lab-page {
  --bg: #0a0e14;
  --surface: #121a28;
  --surface-alt: #1a2436;
  --surface2: #1a2436;
  --border: #2a3548;
  --border-strong: #3d4f66;
  --text: #e8edf4;
  --muted: #94a3b8;
  --text2: #94a3b8;
  --accent: #5b9fd4;
  --accent-dim: #7eb8e0;
  --accent2: #3d9970;
  --good: #3d9970;
  --warn: #ca8a04;
  --warn-bg: #1a2436;
  --warn-border: #5b9fd4;
}
body.os-lab-page {
  background: var(--bg);
  background-image:
    linear-gradient(rgba(91, 159, 212, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(91, 159, 212, 0.03) 1px, transparent 1px);
  background-size: 48px 48px;
  color: var(--text);
}
body.os-lab-page header {
  background: linear-gradient(180deg, #0d1219 0%, #121a28 100%);
  border-bottom: 1px solid var(--border);
}
body.os-lab-page header .brand,
body.os-lab-page header .title { color: var(--text); }
body.os-lab-page header .subtitle { color: var(--text2); }
body.os-lab-page footer {
  background: #0d1219;
  border-top: 1px solid var(--border);
  color: var(--text2);
}
body.os-lab-page h2, body.os-lab-page h3 { color: var(--text); border-color: var(--border); }
body.os-lab-page a { color: var(--accent); }
body.os-lab-page .principle-box,
body.os-lab-page .warning-box {
  background: var(--warn-bg);
  border: 1px solid var(--warn-border);
  border-left: 4px solid var(--accent);
  padding: 1rem 1.25rem;
  margin: 1.25rem 0;
  border-radius: 4px;
  color: var(--text);
}
body.os-lab-page .principle-box p,
body.os-lab-page .warning-box p,
body.os-lab-page .conclusion-box p {
  color: var(--text);
  margin: 0.35rem 0;
}
body.os-lab-page .conclusion-box {
  background: var(--surface2);
  border: 1px solid var(--accent2);
  border-left: 4px solid var(--accent2);
  padding: 1rem 1.25rem;
  margin: 1.25rem 0;
  border-radius: 4px;
  color: var(--text);
}
body.os-lab-page h1 { color: var(--text); }
body.os-lab-page p,
body.os-lab-page li,
body.os-lab-page td,
body.os-lab-page th {
  color: var(--text);
}
body.os-lab-page blockquote {
  background: var(--surface-alt);
  border-left: 3px solid var(--accent);
  color: var(--text2);
}
body.os-lab-page code,
body.os-lab-page pre {
  background: var(--surface-alt);
  border: 1px solid var(--border);
  color: var(--text);
}
body.os-lab-page pre code {
  background: transparent;
  color: var(--text);
}
body.os-lab-page .data-table th,
body.os-lab-page .table-wrap th {
  background: var(--surface2);
  color: var(--accent);
}
body.os-lab-page .data-table td,
body.os-lab-page .table-wrap td {
  background: var(--surface);
  color: var(--text2);
}
body.os-lab-page .disclaimer {
  background: #1a2436;
  border: 1px solid var(--border);
  color: var(--text2);
}
body.os-lab-page .meta {
  color: var(--text2);
  font-size: 0.85rem;
}
body.os-lab-page nav.top a {
  background: var(--surface);
  border-color: var(--border);
  color: var(--text);
}
body.os-lab-page nav.top a:hover {
  background: var(--surface-alt);
  color: var(--accent);
}
body.os-lab-page nav.top a.primary {
  background: var(--accent);
  color: #0a0e14;
}
body.os-lab-page hr {
  border-color: var(--border);
}
body.os-lab-page .os-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin: 1.5rem 0;
}
body.os-lab-page .os-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1.1rem 1.25rem;
}
body.os-lab-page .os-card h4 {
  margin: 0 0 0.5rem;
  color: var(--accent);
  font-size: 1rem;
}
body.os-lab-page .os-card .meta {
  font-size: 0.78rem;
  color: var(--text2);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.5rem;
}
body.os-lab-page .os-card p { margin: 0.35rem 0; font-size: 0.92rem; color: var(--text2); }
body.os-lab-page .os-card .label { color: var(--text); font-weight: 600; font-size: 0.85rem; }
body.os-lab-page pre.arch-tree {
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 1.25rem;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.82rem;
  line-height: 1.5;
  color: var(--accent);
}
body.os-lab-page table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.88rem;
}
body.os-lab-page th, body.os-lab-page td {
  border: 1px solid var(--border);
  padding: 0.5rem 0.75rem;
  text-align: left;
}
body.os-lab-page th { background: var(--surface2); color: var(--accent); }
body.os-lab-page td { color: var(--text2); }
body.os-lab-page .roadmap-phase { color: var(--accent2); font-weight: 600; }
"""
    )


def _shell_os_lab(
    title: str,
    body: str,
    *,
    wide: bool = True,
    nav_active: str = "open_source_ai",
    subtitle: str = "Borrow. Benchmark. Improve. Explain.",
    nav_html: str | None = None,
) -> str:
    main_class = "wide" if wide else ""
    nav = nav_html if nav_html is not None else _nav_fx(nav_active)
    foot_disclaimer = (
        "These models are not trading systems by themselves. They are research baselines. "
        "Every model must be tested out-of-sample with realistic transaction costs, "
        "drawdown controls, and no look-ahead bias before any trading use."
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <meta name="description" content="{html.escape(LAB_NAME)} — Open Source FX AI Model Lab"/>
  <title>{html.escape(title)} — {html.escape(LAB_NAME)}</title>
  {bfi_favicon_tags()}
  <style>{_css_os_lab()}</style>
</head>
<body class="os-lab-page">
  <header>
    <div class="header-inner">
      {_division_header_row()}
      <div class="brand">{html.escape(LAB_NAME_DISPLAY)} · Division of {html.escape(ROOT_BRAND)}</div>
      <h1 class="title">{html.escape(title)}</h1>
      <p class="subtitle">{html.escape(subtitle)} · Research only · Not investment advice</p>
      {nav}
    </div>
  </header>
  <main class="{main_class}">
    {body}
  </main>
  <footer>
    <p>{html.escape(LAB_NAME)} · Prepared by Brendan Bowers · {datetime.now():%Y-%m-%d}</p>
    <div class="disclaimer">{html.escape(foot_disclaimer)}</div>
  </footer>
</body>
</html>"""


def _division_header_row(*, dark: bool = False) -> str:
    """Parent BFI logo + BR3N Macro Lab division mark."""
    bfi_src = BFI_LOGO_HORIZONTAL_INVERSE if dark else BFI_LOGO_HORIZONTAL
    bfi_cls = "bfi-logo-header-sm-inv" if dark else "bfi-logo-header-sm"
    return f"""
<div class="institute-brand-row">
  <a href="index.html" class="institute-brand-link" title="{html.escape(ROOT_BRAND)}">
    <img src="{bfi_src}" alt="{html.escape(ROOT_BRAND)}" class="{bfi_cls}"/>
  </a>
  <span class="institute-brand-sep" aria-hidden="true">/</span>
  <a href="macro-lab.html" class="institute-brand-link" title="{html.escape(LAB_NAME)}">
    <img src="{FX_LAB_LOGO}" alt="{html.escape(LAB_NAME_DISPLAY)}" class="fx-lab-logo-sm" style="max-width:140px;margin:0"/>
  </a>
</div>"""


def _nav_fx(active: str = "home") -> str:
    links = [
        ("index.html", "Institute", "institute"),
        ("macro-lab.html", "Macro Lab", "home"),
        ("fx-lab.html", "FX Lab", "fx"),
        ("usdmxn-research.html", "USD/MXN", "research"),
        ("corridor.html", "Corridor", "corridor"),
        ("fx_desk.html", "FX Desk", "fx_desk"),
        ("memo.html", "Memo", "memo"),
        ("ladder.html", "Ladder", "ladder"),
        ("hedge-governance.html", "Hedge Gov", "hedge"),
        ("model-zoo.html", "Model Zoo", "model_zoo"),
        ("lab-status.html", "Lab Status", "lab_status"),
        ("unanswered-fx.html", "Unanswered FX", "unanswered_fx"),
        ("history.html", "History", "history"),
        ("open-source-ai.html", "OSS AI Lab", "open_source_ai"),
        ("global-fx-lab.html", "Global FX", "global_fx_lab"),
        ("value-survival-index.html", "VSI", "value_survival_index"),
        ("settlement-economics-lab.html", "Settlement", "settlement_lab"),
        ("stablecoin-settlement-lab.html", "Stablecoin", "stablecoin_lab"),
        ("dashboard/index.html", "Dashboard", "web_dashboard"),
    ]
    parts = ['<nav class="top">']
    for href, label, key in links:
        cls = ' class="primary"' if key == active else ""
        parts.append(f'  <a href="{href}"{cls}>{html.escape(label)}</a>')
    parts.append("</nav>")
    return "\n".join(parts)


def _nav(active: str = "") -> str:
    return _nav_fx(active)


def _read_md(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _shell(
    title: str,
    body: str,
    *,
    wide: bool = False,
    nav_active: str = "research",
    subtitle: str = "USD/MXN regime research · Research only · Not investment advice",
    nav_html: str | None = None,
    disclaimer: str | None = None,
) -> str:
    main_class = "wide" if wide else ""
    nav = nav_html if nav_html is not None else _nav_fx(nav_active)
    foot_disclaimer = disclaimer or (
        "This site is for research and education only. It is not investment advice, "
        "does not guarantee returns, and is not intended for automated live trading."
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <meta name="description" content="{html.escape(LAB_NAME)} — {html.escape(subtitle)}"/>
  <title>{html.escape(title)} — {html.escape(LAB_NAME)}</title>
  {bfi_favicon_tags()}
  <style>{_css()}</style>
</head>
<body>
  <header>
    <div class="header-inner">
      {_division_header_row()}
      <div class="brand">{html.escape(LAB_NAME_DISPLAY)} · Division of {html.escape(ROOT_BRAND)}</div>
      <h1 class="title">{html.escape(title)}</h1>
      <p class="subtitle">{html.escape(subtitle)}</p>
      {nav}
    </div>
  </header>
  <main class="{main_class}">
    {body}
  </main>
  <footer>
    <p>{html.escape(LAB_NAME)} · Prepared by Brendan Bowers · {datetime.now():%Y-%m-%d}</p>
    <div class="disclaimer">{html.escape(foot_disclaimer)}</div>
  </footer>
</body>
</html>"""


def _home_body() -> str:
    cards = "".join(
        f'<a href="{html.escape(href, quote=True)}" class="flagship-card">'
        f'<div class="card-tag">{html.escape(tag)}</div>'
        f"<h3>{html.escape(title)}</h3>"
        f"<p>{html.escape(desc)}</p>"
        f"</a>"
        for href, title, desc, tag in FLAGSHIP_HOME_CARDS
    )
    badges = "".join(
        f'<li class="discipline-badge{" emphasis" if emph else ""}">{html.escape(label)}</li>'
        for label, emph in HOME_DISCIPLINE_BADGES
    )
    focus = "".join(f"<li>{html.escape(item)}</li>" for item in HOME_CURRENT_FOCUS)
    questions = "".join(f"<li>{html.escape(q)}</li>" for q in HOME_CORE_QUESTIONS)
    return f"""
<section class="home-section">
  <p class="home-mission">BR3N Macro Labs studies how currencies, payment rails, liquidity systems, and settlement windows determine how value survives when it crosses borders. The lab combines FX research, remittance economics, settlement infrastructure, stablecoin finality analysis, and data-quality governance into one research platform.</p>
</section>

<section class="home-section">
  <h2>Flagship Research</h2>
  <div class="flagship-grid">{cards}</div>
</section>

<section class="home-section">
  <h2>Flagship Vertical — FX Lab</h2>
  <div class="fx-spotlight">
    <h3>FX Lab</h3>
    <p class="fx-tagline">Testing When Currency Markets Become Less Random</p>
    <p>FX Lab is a flagship research vertical within BR3N Macro Labs. It studies conditional forecastability in currency markets — whether observable regimes of trend, volatility, carry, liquidity stress, and payment-flow pressure can identify when FX behavior becomes more structured than a random walk. The lab separates forecast accuracy, trading P&amp;L, and hedge-governance usefulness.</p>
    <a href="fx-lab.html" class="btn">Enter FX Lab</a>
  </div>
</section>

<section class="home-section">
  <h2>Research Discipline</h2>
  <ul class="discipline-strip">{badges}</ul>
</section>

<section class="home-section">
  <h2>Current Focus</h2>
  <ul class="focus-grid">{focus}</ul>
</section>

<section class="home-section">
  <h2>Core Research Questions</h2>
  <ol class="questions-list">{questions}</ol>
</section>
"""


def _home_shell(body: str) -> str:
    hero = f"""
<header class="hero-cover">
  <div class="header-inner">
    <div style="margin-bottom:1rem;">{bfi_header_logo(inverse=True)}</div>
    <div class="logo-frame" style="background:transparent;border:none;box-shadow:none;padding:0;">
      <img src="{FX_LAB_LOGO}" alt="{html.escape(LAB_NAME_DISPLAY)}" class="fx-lab-logo"/>
    </div>
    <h1 class="lab-title">{html.escape(LAB_NAME)}</h1>
    <p class="home-subtitle">Cross-Border Value Infrastructure Research</p>
    <p class="motto">{html.escape(BRAND_MOTTO)}</p>
    <p class="home-hero-line">FX prices trust. Settlement makes value real. Stablecoins move risk somewhere else.</p>
    <p class="author">A division of {html.escape(ROOT_BRAND)} · Prepared by Brendan Bowers</p>
    <div class="cta-row">
      <a href="fx-lab.html" class="primary">FX Lab Overview</a>
      <a href="usdmxn-research.html" class="secondary">USD/MXN Research</a>
      <a href="corridor.html" class="secondary">Corridor Roadmap</a>
      <a href="dashboard/index.html" class="secondary">Dashboards</a>
    </div>
    {_nav_fx("home")}
  </div>
</header>"""
    foot = (
        f"{html.escape(LAB_NAME)} · {html.escape(ROOT_BRAND)} · Prepared by Brendan Bowers · "
        "Research and risk-framing only · Not investment advice · No live trading."
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <meta name="description" content="{html.escape(LAB_NAME)} — division of {html.escape(ROOT_BRAND)}"/>
  <title>{html.escape(LAB_NAME)} — {html.escape(ROOT_BRAND)}</title>
  {bfi_favicon_tags()}
  <style>{_css_home()}</style>
</head>
<body class="cover-page home-page">
  {hero}
  <main class="cover-main wide">
    {body}
  </main>
  <footer>
    <p>{foot}</p>
    <div class="disclaimer">Research and risk-framing only. Not investment advice. No live trading.</div>
  </footer>
</body>
</html>"""


def _landing_stats() -> str:
    """Key stats cards from ladder CSVs if available."""
    l2 = ROOT / "reports/research_ladder/level2_oos_splits.csv"
    l3 = ROOT / "reports/research_ladder/level3_oos_summary.csv"
    l6 = ROOT / "reports/research_ladder/level6_white_reality_check.csv"

    oos_splits = "3/3"
    cross_pct = "—"
    wrc_p = "—"

    if l3.exists():
        import pandas as pd

        df = pd.read_csv(l3)
        if not df.empty:
            cross_pct = f"{df.iloc[0]['pct_beats_rw']:.0f}%"

    if l6.exists():
        import pandas as pd

        df = pd.read_csv(l6)
        s = df[df["strategy"] == "_SUMMARY"]
        if not s.empty:
            wrc_p = str(s.iloc[0].get("white_rc_pvalue", "—"))

    return f"""
<div class="stat-grid">
  <div class="stat"><div class="label">MXN OOS splits</div><div class="value good">{oos_splits}</div><div class="label">beat flat benchmark</div></div>
  <div class="stat"><div class="label">Cross-pair OOS</div><div class="value">{cross_pct}</div><div class="label">cells beat benchmark</div></div>
  <div class="stat"><div class="label">White RC p-value</div><div class="value warn">{wrc_p}</div><div class="label">data-snooping check</div></div>
</div>
"""


def _model_zoo_stats() -> str:
    """Summary cards from model zoo scorecards when available."""
    fc_path = ROOT / "data/outputs/model_zoo_forecast_scorecard.csv"
    tr_path = ROOT / "data/outputs/model_zoo_trading_scorecard.csv"
    hg_path = ROOT / "data/outputs/model_zoo_hedge_scorecard.csv"
    log_path = ROOT / "data/outputs/model_zoo_run_log.csv"

    attempted = success = skipped = "—"
    best_fc = best_tr = best_hg = "—"
    beats_rmse = "—"

    if log_path.exists():
        import pandas as pd

        log = pd.read_csv(log_path)
        attempted = str(len(log))
        success = str(int((log["status"] == "success").sum()))
        skipped = str(int((log["status"] == "skipped").sum()))

    if fc_path.exists():
        import pandas as pd

        fc = pd.read_csv(fc_path)
        if not fc.empty:
            best_fc = str(fc.sort_values("rmse_model").iloc[0]["model_name"])
            beats_rmse = str(int(fc["model_beats_rw_rmse"].sum()))

    if tr_path.exists():
        import pandas as pd

        tr = pd.read_csv(tr_path)
        if not tr.empty and "sharpe_net" in tr.columns:
            best_tr = str(tr.sort_values("sharpe_net", ascending=False).iloc[0]["model_name"])

    if hg_path.exists():
        import pandas as pd

        hg = pd.read_csv(hg_path)
        if not hg.empty:
            best_hg = str(
                hg.sort_values("cost_adjusted_risk_reduction", ascending=False).iloc[0]["model_name"]
            )

    return f"""
<div class="stat-grid">
  <div class="stat"><div class="label">Models run</div><div class="value">{success}/{attempted}</div><div class="label">successful</div></div>
  <div class="stat"><div class="label">Beat RW (RMSE)</div><div class="value warn">{beats_rmse}</div><div class="label">forecast models</div></div>
  <div class="stat"><div class="label">Best trading</div><div class="value">{best_tr}</div><div class="label">by net Sharpe</div></div>
  <div class="stat"><div class="label">Best hedge</div><div class="value good">{best_hg}</div><div class="label">cost-adj risk reduction</div></div>
</div>
"""


def build_site(out_dir: Path | None = None) -> Dict[str, Path]:
    out_dir = out_dir or PUB_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    one_pager = (out_dir / "ONE_PAGER.md").read_text(encoding="utf-8") if (out_dir / "ONE_PAGER.md").exists() else ""
    memo = (out_dir / "FX_REGIME_RESEARCH_NOTE.md").read_text(encoding="utf-8") if (out_dir / "FX_REGIME_RESEARCH_NOTE.md").exists() else ""

    # Bowers Frontier Institute — parent brand homepage + hub pages
    bfi_paths = build_bfi_pages(out_dir)

    # BR3N Macro Lab division home (formerly site index)
    macro_lab_path = out_dir / "macro-lab.html"
    macro_lab_path.write_text(_home_shell(_home_body()), encoding="utf-8")

    fx_lab_path = out_dir / "fx-lab.html"
    fx_lab_md = _read_md(VERTICALS_DIR / "FX_LAB_LANDING.md")
    fx_lab_path.write_text(
        _shell(
            "FX Lab",
            _md_to_html(fx_lab_md, research_links=FX_LAB_RESEARCH_LINKS),
            wide=True,
            nav_active="fx",
            nav_html=_nav_fx("fx"),
            subtitle="Regime intelligence · Corridor research · Research only · Not investment advice",
        ),
        encoding="utf-8",
    )

    # Research one-pager
    research_body = f"""
<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>
{_landing_stats()}
<div class="card">
  <h3>Research depth</h3>
  <ul>
    <li><strong>This page</strong> — 2-minute USD/MXN summary</li>
    <li><a href="memo.html"><strong>Full research note</strong></a> — methods, tables, limitations</li>
    <li><a href="corridor.html"><strong>Corridor roadmap</strong></a> — remittance corridor expansion</li>
    <li><a href="ladder.html"><strong>Evidence ladder</strong></a> — eight-level checklist</li>
    <li><a href="hedge-governance.html"><strong>Hedge governance memo</strong></a> — forecast failure, hedge usefulness</li>
    <li><a href="model-zoo.html"><strong>Model zoo</strong></a> — conditional forecastability tests</li>
    <li><a href="lab-status.html"><strong>Lab status</strong></a> — nightly pipeline health snapshot</li>
    <li><a href="macro-lab.html"><strong>Macro Lab home</strong></a></li>
    <li><a href="index.html"><strong>{html.escape(ROOT_BRAND)}</strong></a></li>
  </ul>
</div>
{_md_to_html(one_pager)}
"""
    usdmxn_path = out_dir / "usdmxn-research.html"
    usdmxn_path.write_text(
        _shell(
            "USD/MXN Regime Research",
            research_body,
            nav_active="research",
            nav_html=_nav_fx("research"),
        ),
        encoding="utf-8",
    )

    memo_body = f'<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>{_md_to_html(memo)}'
    memo_path = out_dir / "memo.html"
    memo_path.write_text(
        _shell("Full Research Note", memo_body, wide=True, nav_active="memo", nav_html=_nav_fx("memo")),
        encoding="utf-8",
    )

    ladder_md = _read_md(ROOT / "reports/research_ladder/RESEARCH_LADDER.md") or "_Run the research ladder first._"
    ladder_path = out_dir / "ladder.html"
    ladder_path.write_text(
        _shell(
            "Research Ladder",
            f'<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>{_md_to_html(ladder_md)}',
            wide=True,
            nav_active="ladder",
            nav_html=_nav_fx("ladder"),
            subtitle="Eight-level evidence framework · Research only",
        ),
        encoding="utf-8",
    )

    hedge_md = _read_md(out_dir / "HEDGE_GOVERNANCE_MEMO.md") or _read_md(ROOT / "reports/publication/HEDGE_GOVERNANCE_MEMO.md")
    pre_reg = _read_md(ROOT / "reports/research_log/PRE_REGISTRATION_LOG.md")
    snap_dirs = sorted((ROOT / "research_snapshots").glob("*/SNAPSHOT_SUMMARY.md"), reverse=True) if (ROOT / "research_snapshots").exists() else []
    snap_note = ""
    if snap_dirs:
        latest = snap_dirs[0].parent.name
        snap_note = f"<p><strong>Latest research snapshot:</strong> <code>research_snapshots/{latest}/</code></p>"

    hedge_body = f"""
<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>
<div class="principle-box"><p><strong>Flagship thesis:</strong> A model may fail as a price forecast but still be useful for hedge governance. This tests conditional forecastability and hedge discipline — not FX prediction.</p></div>
{_model_zoo_stats()}
{snap_note}
{_md_to_html(hedge_md) if hedge_md else "<p><em>Hedge governance memo pending.</em></p>"}
<hr/>
<h2>Pre-registration log</h2>
{_md_to_html(pre_reg) if pre_reg else "<p><em>See reports/research_log/PRE_REGISTRATION_LOG.md</em></p>"}
<p>Related: <a href="ladder.html">Research Ladder</a> · <a href="model-zoo.html">Model Zoo</a> · <a href="memo.html">Full Memo</a></p>
"""
    hedge_path = out_dir / "hedge-governance.html"
    hedge_path.write_text(
        _shell(
            "Forecast Failure and Hedge Usefulness",
            hedge_body,
            wide=True,
            nav_active="hedge",
            nav_html=_nav_fx("hedge"),
            subtitle="Regime-based hedge governance · Research only",
        ),
        encoding="utf-8",
    )

    corridor_md_path = ROOT / "reports" / "corridor_roadmap_report.md"
    corridor_md = _read_md(corridor_md_path) or "_Run `python scripts/run_corridor_roadmap.py` first._"
    corridor_path = out_dir / "corridor.html"
    corridor_path.write_text(
        _shell(
            "Remittance Corridor Roadmap",
            f'<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>{_md_to_html(corridor_md)}',
            wide=True,
            nav_active="corridor",
            nav_html=_nav_fx("corridor"),
            subtitle="Multi-corridor FX research · Exploratory · Not investment advice",
        ),
        encoding="utf-8",
    )

    fx_desk_md_path = ROOT / "reports" / "FX_DESK_DECISION_FRAMEWORK.md"
    fx_desk_md = _read_md(fx_desk_md_path) or "_Run `python scripts/run_fx_desk_framework.py` first._"
    fx_desk_path = out_dir / "fx_desk.html"
    fx_desk_path.write_text(
        _shell(
            "Cross-Border Payments FX Desk Framework",
            f'<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>{_md_to_html(fx_desk_md)}',
            wide=True,
            nav_active="fx_desk",
            nav_html=_nav_fx("fx_desk"),
            subtitle="Payments and treasury FX decisions · Research only · Not investment advice",
        ),
        encoding="utf-8",
    )

    zoo_summary = _read_md(out_dir / "MODEL_ZOO_SUMMARY.md") or _read_md(ROOT / "reports/publication/MODEL_ZOO_SUMMARY.md")
    zoo_report = _read_md(ROOT / "reports/model_zoo_report.md")
    zoo_body = f"""
<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>
{_model_zoo_stats()}
<div class="principle-box">
  <p><strong>Research discipline:</strong> The model zoo tests conditional forecastability — not FX prediction.
  A model that performs well in-sample but fails walk-forward or cost-adjusted tests should not be treated as evidence of forecastability.</p>
</div>
{_md_to_html(zoo_summary)}
<hr/>
<h2>Full model zoo report</h2>
{_md_to_html(zoo_report) if zoo_report else "<p><em>Run <code>python scripts/run_model_zoo.py</code> then <code>python scripts/generate_model_zoo_report.py</code>.</em></p>"}
"""
    model_zoo_path = out_dir / "model-zoo.html"
    model_zoo_path.write_text(
        _shell(
            "Model Zoo",
            zoo_body,
            wide=True,
            nav_active="model_zoo",
            nav_html=_nav_fx("model_zoo"),
            subtitle="Conditional forecastability · Research only · Not investment advice",
        ),
        encoding="utf-8",
    )

    lab_status_md = _read_md(ROOT / "reports/LAB_STATUS.md")
    lab_status_body = f"""
<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>
<div class="principle-box">
  <p><strong>Ops only:</strong> Lab Status is regenerated by the nightly pipeline. It summarizes data quality,
  provenance, and layer health — not trading readiness or publication claims.</p>
</div>
{_md_to_html(lab_status_md) if lab_status_md else "<p><em>Run <code>python scripts/generate_lab_status.py</code> or <code>bash scripts/auto_improve_daily.sh</code>.</em></p>"}
"""
    lab_status_path = out_dir / "lab-status.html"
    lab_status_path.write_text(
        _shell(
            "Lab Status",
            lab_status_body,
            wide=True,
            nav_active="lab_status",
            nav_html=_nav_fx("lab_status"),
            subtitle="Nightly pipeline health · Research only · Not investment advice",
        ),
        encoding="utf-8",
    )

    unanswered_summary = _read_md(out_dir / "UNANSWERED_FX_QUESTIONS_SUMMARY.md") or _read_md(
        ROOT / "reports/publication/UNANSWERED_FX_QUESTIONS_SUMMARY.md"
    )
    flagship_md = _read_md(ROOT / "reports/FLAGSHIP_RESEARCH_LANE.md")
    unanswered_full = _read_md(ROOT / "reports/UNANSWERED_FX_QUESTIONS.md")
    unanswered_body = f"""
<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>
<div class="principle-box">
  <p><strong>Research framing:</strong> These are unresolved questions in FX — not claims of predictability or trading readiness.</p>
</div>
{_md_to_html(unanswered_summary) if unanswered_summary else ""}
<hr/>
<h2>Flagship Research Lane</h2>
{_md_to_html(flagship_md) if flagship_md else "<p><em>Run <code>python scripts/run_flagship_research_lane.py</code>.</em></p>"}
<hr/>
<h2>Full Question Framework</h2>
{_md_to_html(unanswered_full) if unanswered_full else "<p><em>Missing reports/UNANSWERED_FX_QUESTIONS.md</em></p>"}
"""
    unanswered_path = out_dir / "unanswered-fx.html"
    unanswered_path.write_text(
        _shell(
            "Unanswered FX Questions",
            unanswered_body,
            wide=True,
            nav_active="unanswered_fx",
            nav_html=_nav_fx("unanswered_fx"),
            subtitle="Major research questions · Research only · Not investment advice",
        ),
        encoding="utf-8",
    )

    history_public = _read_md(out_dir / "FX_HISTORY_PAGE.md") or _read_md(
        ROOT / "reports/publication/FX_HISTORY_PAGE.md"
    )
    history_full = _read_md(ROOT / "reports/FX_HISTORY_AND_ACADEMIC_FOUNDATIONS.md")
    history_body = f"""
<p class="back-link"><a href="fx-lab.html">← Back to FX Lab</a></p>
<div class="principle-box">
  <p><strong>Academic framing:</strong> FX Lab builds on prior exchange-rate research. Random walk remains the benchmark.
  The lab does not claim to solve FX forecasting — it asks whether regime information can improve hedge-governance
  decisions when prediction fails.</p>
</div>
{_md_to_html(history_public) if history_public else "<p><em>Missing FX_HISTORY_PAGE.md</em></p>"}
<hr/>
<h2>Full Academic Foundations</h2>
{_md_to_html(history_full) if history_full else "<p><em>Missing reports/FX_HISTORY_AND_ACADEMIC_FOUNDATIONS.md</em></p>"}
"""
    history_path = out_dir / "history.html"
    history_path.write_text(
        _shell(
            "FX History & Academic Foundations",
            history_body,
            wide=True,
            nav_active="history",
            nav_html=_nav_fx("history"),
            subtitle="The 300-year road to FX Lab · Research only · Not investment advice",
        ),
        encoding="utf-8",
    )

    os_ai_path = out_dir / "open-source-ai.html"
    os_ai_path.write_text(
        _shell_os_lab(
            "Open Source FX AI Model Lab",
            _open_source_ai_body(out_dir),
            nav_html=_nav_fx("open_source_ai"),
            subtitle="Borrow. Benchmark. Improve. Explain.",
        ),
        encoding="utf-8",
    )

    global_fx_path = out_dir / "global-fx-lab.html"
    global_fx_path.write_text(
        _shell_os_lab(
            "Global FX & Remittance Research Lab",
            _global_fx_lab_body(out_dir),
            nav_html=_nav_fx("global_fx_lab"),
            subtitle="Who bears the cost when value crosses borders?",
        ),
        encoding="utf-8",
    )

    vsi_path = out_dir / "value-survival-index.html"
    vsi_path.write_text(
        _shell_os_lab(
            "BR3N Value Survival Index",
            _value_survival_index_body(out_dir),
            nav_html=_nav_fx("value_survival_index"),
            subtitle="Measuring how much value survives when money crosses borders.",
        ),
        encoding="utf-8",
    )

    settlement_path = out_dir / "settlement-economics-lab.html"
    settlement_path.write_text(
        _shell_os_lab(
            "BR3N Settlement Economics Lab",
            _settlement_lab_body(out_dir),
            nav_html=_nav_fx("settlement_lab"),
            subtitle="Settlement drag, liquidity burden, finality quality, and payment-network fragility.",
        ),
        encoding="utf-8",
    )

    stablecoin_path = out_dir / "stablecoin-settlement-lab.html"
    stablecoin_path.write_text(
        _shell_os_lab(
            "BR3N Stablecoin Settlement Window Lab",
            _stablecoin_lab_body(out_dir),
            nav_html=_nav_fx("stablecoin_lab"),
            subtitle="Finality quality, settlement window compression, liquidity transformation, and digital run conditions.",
        ),
        encoding="utf-8",
    )

    return {
        "index": bfi_paths["index"],
        "macro_lab": macro_lab_path,
        "research": bfi_paths["research"],
        "labs": bfi_paths["labs"],
        "methodology": bfi_paths["methodology"],
        "dashboards": bfi_paths["dashboards"],
        "about": bfi_paths["about"],
        "usdmxn_research": usdmxn_path,
        "fx_lab": fx_lab_path,
        "memo": memo_path,
        "ladder": ladder_path,
        "hedge_governance": hedge_path,
        "corridor": corridor_path,
        "fx_desk": fx_desk_path,
        "model_zoo": model_zoo_path,
        "lab_status": lab_status_path,
        "unanswered_fx": unanswered_path,
        "history": history_path,
        "open_source_ai": os_ai_path,
        "global_fx_lab": global_fx_path,
        "value_survival_index": vsi_path,
        "settlement_economics_lab": settlement_path,
        "stablecoin_settlement_lab": stablecoin_path,
    }
