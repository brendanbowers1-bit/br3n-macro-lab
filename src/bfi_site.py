"""
Bowers Frontier Institute — parent-brand site pages and styling.
"""

from __future__ import annotations

import html
from datetime import datetime
from typing import Dict

ROOT_BRAND = "Bowers Frontier Institute"
CORE_LINE = "Markets. Machines. Monetary Systems."
TAGLINE = "Research for the financial frontier."

BFI_BRAND_DIR = "assets/brand"
BFI_LOGO_HORIZONTAL = f"{BFI_BRAND_DIR}/bfi-logo-horizontal-corrected.svg"
BFI_LOGO_HORIZONTAL_INVERSE = f"{BFI_BRAND_DIR}/bfi-logo-horizontal-inverse-corrected.svg"
BFI_LOGO_STACKED = f"{BFI_BRAND_DIR}/bfi-logo-stacked-corrected.svg"
BFI_ICON = f"{BFI_BRAND_DIR}/bfi-icon.svg"
BFI_ICON_TRANSPARENT = f"{BFI_BRAND_DIR}/bfi-icon-transparent.svg"

BFI_NAV = [
    ("index.html", "Home", "home"),
    ("research.html", "Research", "research"),
    ("labs.html", "Labs", "labs"),
    ("methodology.html", "Methodology", "methodology"),
    ("dashboards.html", "Dashboards", "dashboards"),
    ("about.html", "About", "about"),
]

BFI_CORE_DOMAINS: list[tuple[str, str, str, str]] = [
    (
        "macro-lab.html",
        "Foreign Exchange & Global Markets",
        "Research on FX behavior, carry, forward points, volatility, liquidity, corridors, and macro transmission across global currency systems.",
        "Markets",
    ),
    (
        "settlement-economics-lab.html",
        "Settlement & Monetary Infrastructure",
        "Analysis of payment rails, settlement windows, timing risk, cross-border money movement, stablecoins, tokenized money, and treasury infrastructure.",
        "Infrastructure",
    ),
    (
        "open-source-ai.html",
        "AI Market Intelligence",
        "Transparent machine-learning workflows for market classification, anomaly detection, stress detection, signal validation, and model-risk review.",
        "Intelligence",
    ),
    (
        "lab-status.html",
        "Research Infrastructure",
        "Open datasets, reproducible notebooks, methodology libraries, dashboards, and public-facing analytical tools.",
        "Platform",
    ),
    (
        "global-fx-lab.html",
        "Frontier Financial Systems",
        "Long-horizon research on the architecture of money, risk transfer, machine-mediated markets, and the future of global financial infrastructure.",
        "Frontier",
    ),
]

BFI_QUESTIONS: list[str] = [
    "What happens when global settlement systems move from banking hours to machine-speed rails?",
    "Where does hidden liquidity risk accumulate before markets break?",
    "Can AI models detect structural fragility in FX corridors before humans see it?",
    "How should stablecoins, tokenized deposits, central bank systems, and traditional treasury networks coexist?",
    "What would a truly transparent, reproducible, institutional-grade FX research platform look like?",
    "What becomes possible when financial research is built in public with academic discipline and frontier-level ambition?",
]

BFI_PRINCIPLES: list[tuple[str, str]] = [
    (
        "Rigor Over Hype",
        "Every model, dashboard, and research claim must be testable, explainable, and open to challenge.",
    ),
    (
        "Systems Over Signals",
        "The goal is not isolated prediction. The goal is to understand the structure beneath market behavior.",
    ),
    (
        "Transparency Over Black Boxes",
        "Research should be reproducible, documented, and clear enough to be audited.",
    ),
    (
        "Frontier Over Consensus",
        "The institute focuses on questions that are early, difficult, underexplored, and structurally important.",
    ),
    (
        "Public Knowledge Over Private Mystery",
        "Financial systems shape the world. Serious research about them should be accessible, intelligible, and built with public value in mind.",
    ),
]

BFI_LABS: list[tuple[str, str, str, str]] = [
    (
        "macro-lab.html",
        "Bowers Macro Lab",
        "Foreign exchange, interest rates, liquidity, global corridors, carry, forwards, volatility, treasury operations, and macro-market structure.",
        "Macro",
    ),
    (
        "open-source-ai.html",
        "Bowers Intelligence Lab",
        "Machine learning, model validation, anomaly detection, AI-assisted market analysis, research automation, and financial data infrastructure.",
        "Intelligence",
    ),
    (
        "value-survival-index.html",
        "Bowers Market Structure Lab",
        "Settlement windows, payment rails, stablecoins, tokenized deposits, monetary infrastructure, risk transfer, and cross-border financial architecture.",
        "Structure",
    ),
    (
        "dashboards.html",
        "BR3N Studio",
        "Research design, visual systems, dashboards, publication design, and institutional storytelling.",
        "Studio",
    ),
]


def _css_bfi() -> str:
    return """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
  --bg: #050608;
  --surface: #0b0f14;
  --surface-alt: #111827;
  --border: #1f2937;
  --border-soft: rgba(255,255,255,0.06);
  --text: #f4f4f5;
  --muted: #94a3b8;
  --navy: #07182D;
  --paper: #F7F6F2;
  --accent: #38bdf8;
  --gold: #c9a962;
  --silver: #9ca3af;
  --font: "Inter", "Helvetica Neue", Arial, sans-serif;
  --serif: "Cormorant Garamond", Georgia, serif;
  --mono: "JetBrains Mono", ui-monospace, monospace;
  --wide: 1080px;
  --narrow: 680px;
}
*, *::before, *::after { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body.bfi {
  margin: 0;
  font-family: var(--font);
  background:
    linear-gradient(rgba(56,189,248,0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(56,189,248,0.018) 1px, transparent 1px),
    var(--bg);
  background-size: 56px 56px, 56px 56px, auto;
  color: var(--text);
  line-height: 1.72;
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--accent); text-decoration: none; transition: color 0.15s ease; }
a:hover { color: #7dd3fc; }
.bfi-header {
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #d8dce2;
  background: rgba(247, 246, 242, 0.97);
  backdrop-filter: blur(14px);
}
.bfi-header-inner {
  max-width: var(--wide);
  margin: 0 auto;
  padding: 0.85rem 1.5rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.brand-lockup {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  text-decoration: none;
  color: var(--navy);
  white-space: nowrap;
  flex-shrink: 0;
}
.brand-lockup:hover { opacity: 0.92; text-decoration: none; }
.brand-mark {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 28px;
  letter-spacing: -1.5px;
  font-weight: 500;
  line-height: 1;
}
.brand-divider {
  width: 1px;
  height: 28px;
  background: rgba(7, 24, 45, 0.35);
  display: inline-block;
}
.brand-name {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 13px;
  letter-spacing: 2.8px;
  text-transform: uppercase;
  line-height: 1;
}
.brand-lockup--inverse {
  color: #F7F6F2;
}
.brand-lockup--inverse .brand-divider {
  background: rgba(247, 246, 242, 0.35);
}
@media (max-width: 720px) {
  .brand-name { display: none; }
  .brand-divider { display: none; }
  .brand-mark { font-size: 32px; }
}
.bfi-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}
.bfi-nav a {
  padding: 0.38rem 0.75rem;
  border-radius: 3px;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #46515C;
  border: 1px solid transparent;
}
.bfi-nav a:hover { color: #07182D; border-color: #c8cdd2; text-decoration: none; }
.bfi-nav a.active {
  color: #07182D;
  border: 1px solid transparent;
  border-bottom: 2px solid rgba(7, 24, 45, 0.42);
  background: transparent;
  border-radius: 0;
}
.bfi-hero {
  background: #F7F6F2;
  border-bottom: 1px solid #d8dce2;
  margin: 0;
  max-width: none;
  padding: 4.5rem 1.5rem 3.5rem;
  animation: bfiFadeUp 0.9s ease both;
}
.bfi-hero .hero-inner {
  max-width: var(--wide);
  margin: 0 auto;
}
.hero-eyebrow {
  font-size: 12px;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: rgba(7, 24, 45, 0.62);
  margin-bottom: 28px;
}
.bfi-hero h1 {
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(54px, 8vw, 118px);
  line-height: 0.95;
  letter-spacing: -3.5px;
  color: var(--navy);
  max-width: 1050px;
  font-weight: 500;
  margin: 0;
}
.hero-subtitle {
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(24px, 3vw, 38px);
  color: rgba(7, 24, 45, 0.72);
  margin-top: 28px;
  margin-bottom: 0;
}
.hero-thesis {
  max-width: 720px;
  font-size: 18px;
  line-height: 1.7;
  color: rgba(7, 24, 45, 0.68);
  margin-top: 24px;
  margin-bottom: 0;
}
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-top: 2.25rem;
}
@keyframes bfiFadeUp {
  from { opacity: 0; transform: translateY(18px); }
  to { opacity: 1; transform: translateY(0); }
}
.bfi-hero .lead {
  max-width: 42rem;
  font-size: 1.05rem;
  color: var(--muted);
  line-height: 1.75;
  margin: 0 0 1.25rem;
}
.bfi-hero .lead-strong {
  color: var(--text);
  font-weight: 500;
}
.bfi-hero .stance {
  margin: 2rem 0;
  padding-left: 1.25rem;
  border-left: 2px solid rgba(201,169,98,0.45);
}
.bfi-hero .stance p {
  margin: 0.35rem 0;
  font-family: var(--serif);
  font-size: 1.08rem;
  color: var(--silver);
  font-style: italic;
}
.bfi-hero .bfi-cta.primary {
  background: var(--navy);
  border-color: var(--navy);
  color: #F7F6F2;
}
.bfi-hero .bfi-cta.primary:hover {
  background: #0a2540;
  border-color: #0a2540;
  color: #F7F6F2;
  text-decoration: none;
}
.bfi-hero .bfi-cta.secondary {
  background: transparent;
  border-color: rgba(7, 24, 45, 0.28);
  color: var(--navy);
}
.bfi-hero .bfi-cta.secondary:hover {
  border-color: rgba(7, 24, 45, 0.5);
  color: var(--navy);
  text-decoration: none;
}
.bfi-main .lead {
  max-width: 42rem;
  font-size: 1.05rem;
  color: var(--muted);
  line-height: 1.75;
  margin: 0 0 1.25rem;
}
.bfi-main .lead-strong { color: var(--text); font-weight: 500; }
.bfi-main .stance {
  margin: 2rem 0;
  padding-left: 1.25rem;
  border-left: 2px solid rgba(148, 163, 184, 0.35);
}
.bfi-main .stance p {
  margin: 0.35rem 0;
  font-family: var(--serif);
  font-size: 1.08rem;
  color: var(--silver);
  font-style: italic;
}
.bfi-cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-top: 2.25rem;
}
.bfi-cta {
  display: inline-block;
  padding: 0.65rem 1.25rem;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  border-radius: 3px;
  transition: all 0.18s ease;
}
.bfi-cta.primary {
  background: rgba(56,189,248,0.1);
  border: 1px solid rgba(56,189,248,0.4);
  color: var(--accent);
}
.bfi-cta.primary:hover { background: rgba(56,189,248,0.16); text-decoration: none; }
.bfi-cta.secondary {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--muted);
}
.bfi-cta.secondary:hover { border-color: rgba(201,169,98,0.4); color: var(--gold); text-decoration: none; }
.bfi-main { max-width: var(--wide); margin: 0 auto; padding: 0 1.5rem 4rem; }
.bfi-section {
  margin: 3.5rem 0;
  animation: bfiFadeUp 0.7s ease both;
}
.bfi-section:nth-child(2) { animation-delay: 0.05s; }
.bfi-section:nth-child(3) { animation-delay: 0.1s; }
.bfi-section h2 {
  font-family: var(--serif);
  font-size: 1.55rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  margin: 0 0 1.25rem;
  padding-bottom: 0.55rem;
  border-bottom: 1px solid var(--border);
  color: var(--text);
}
.bfi-section h3 {
  font-family: var(--serif);
  font-size: 1.12rem;
  margin: 0 0 0.45rem;
  color: var(--text);
}
.bfi-section p {
  margin: 0.65rem 0;
  color: var(--muted);
  max-width: 46rem;
  line-height: 1.75;
}
.bfi-section .emph { color: var(--text); }
.bfi-punch-list {
  list-style: none;
  margin: 1.25rem 0 0;
  padding: 0;
}
.bfi-punch-list li {
  padding: 0.35rem 0;
  font-family: var(--serif);
  font-size: 1.12rem;
  color: var(--text);
  letter-spacing: 0.02em;
}
.bfi-punch-list li::before {
  content: "—";
  color: var(--gold);
  margin-right: 0.65rem;
}
.bfi-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}
.bfi-card {
  display: block;
  background: linear-gradient(155deg, rgba(11,15,20,0.98) 0%, rgba(17,24,39,0.5) 100%);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1.4rem 1.45rem;
  text-decoration: none;
  color: inherit;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
  box-shadow: inset 0 1px 0 var(--border-soft);
}
.bfi-card:hover {
  border-color: rgba(56,189,248,0.35);
  box-shadow: 0 10px 36px rgba(0,0,0,0.35);
  transform: translateY(-2px);
  text-decoration: none;
}
.bfi-card .tag {
  font-size: 0.6rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--gold);
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.bfi-card h3 { font-size: 1.08rem; margin: 0 0 0.55rem; }
.bfi-card p { margin: 0; font-size: 0.88rem; line-height: 1.62; color: var(--muted); }
.bfi-questions {
  list-style: none;
  margin: 0;
  padding: 0;
  counter-reset: bfiq;
}
.bfi-questions li {
  counter-increment: bfiq;
  position: relative;
  padding: 1rem 0 1rem 2.75rem;
  border-bottom: 1px solid var(--border);
  font-family: var(--serif);
  font-size: 1.05rem;
  color: var(--text);
  line-height: 1.5;
}
.bfi-questions li:last-child { border-bottom: none; }
.bfi-questions li::before {
  content: counter(bfiq, decimal-leading-zero);
  position: absolute;
  left: 0;
  top: 1rem;
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--gold);
  letter-spacing: 0.06em;
}
.bfi-mission-block {
  max-width: var(--narrow);
  padding: 1.5rem 0;
}
.bfi-mission-block p {
  font-family: var(--serif);
  font-size: 1.2rem;
  line-height: 1.65;
  color: var(--text);
  margin: 0;
}
.bfi-principles {
  display: grid;
  gap: 1rem;
  margin-top: 0.5rem;
}
.bfi-principle {
  padding: 1.15rem 1.25rem;
  border-left: 2px solid rgba(56,189,248,0.4);
  background: rgba(11,15,20,0.6);
  border-radius: 0 4px 4px 0;
}
.bfi-principle h3 { font-size: 0.95rem; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.35rem; color: var(--accent); }
.bfi-principle p { margin: 0; font-size: 0.9rem; }
.bfi-closing {
  text-align: center;
  padding: 3.5rem 1.5rem 2rem;
  border-top: 1px solid var(--border);
  margin-top: 3rem;
}
.bfi-closing .brand {
  font-family: var(--serif);
  font-size: 1.35rem;
  color: var(--text);
  margin-bottom: 0.35rem;
}
.bfi-closing .core { color: var(--gold); font-family: var(--serif); font-size: 1.05rem; margin: 0.25rem 0; }
.bfi-closing .tag { font-size: 0.72rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--muted); }
.bfi-footer {
  border-top: 1px solid var(--border);
  padding: 2rem 1.5rem 1.5rem;
  text-align: center;
  font-size: 0.78rem;
  color: var(--muted);
  letter-spacing: 0.04em;
}
.footer-brand {
  margin-bottom: 1.25rem;
}
.footer-brand-mark {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.35rem;
  letter-spacing: -0.5px;
  color: var(--text);
  margin-bottom: 0.35rem;
}
.footer-brand-name {
  font-family: var(--serif);
  font-size: 0.95rem;
  color: var(--silver);
  margin-bottom: 0.25rem;
}
.footer-brand-tagline {
  font-size: 0.68rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted);
}
.bfi-footer .disc {
  margin-top: 0.65rem;
  font-size: 0.72rem;
  color: var(--silver);
  max-width: 36rem;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.55;
}
.bfi-hub-intro { max-width: 40rem; margin-bottom: 2rem; }
.bfi-hub-list { list-style: none; padding: 0; margin: 0; }
.bfi-hub-list li {
  padding: 0.85rem 0;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.5rem;
  align-items: baseline;
}
.bfi-hub-list a { font-weight: 500; }
.bfi-hub-list .meta { font-size: 0.82rem; color: var(--muted); }
.light-zone {
  background: var(--paper);
  color: var(--navy);
}
.bfi-page-inner {
  max-width: var(--wide);
  margin: 0 auto;
  padding: 0 1.5rem;
}
.page-hero {
  padding: 96px 0 72px;
  border-bottom: 1px solid rgba(7, 24, 45, 0.12);
}
.research-standards {
  padding: 78px 0 96px;
}
.page-eyebrow {
  font-size: 12px;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: rgba(7, 24, 45, 0.62);
  margin-bottom: 24px;
}
.page-hero h1 {
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(44px, 6vw, 86px);
  line-height: 0.98;
  letter-spacing: -2.5px;
  color: var(--navy);
  max-width: 1080px;
  font-weight: 500;
  margin: 0;
}
.page-subtitle {
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(22px, 2.5vw, 34px);
  color: rgba(7, 24, 45, 0.72);
  max-width: 900px;
  line-height: 1.3;
  margin-top: 28px;
  margin-bottom: 0;
}
.page-thesis {
  max-width: 780px;
  font-size: 18px;
  line-height: 1.7;
  color: rgba(7, 24, 45, 0.68);
  margin-top: 24px;
  margin-bottom: 0;
}
.research-standards .section-kicker {
  font-size: 12px;
  letter-spacing: 3.5px;
  text-transform: uppercase;
  color: rgba(7, 24, 45, 0.56);
  margin-bottom: 18px;
}
.section-title {
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(34px, 4vw, 58px);
  line-height: 1.05;
  letter-spacing: -1.6px;
  color: var(--navy);
  margin: 0 0 20px;
  font-weight: 500;
}
.section-intro {
  max-width: 760px;
  font-size: 17px;
  line-height: 1.7;
  color: rgba(7, 24, 45, 0.68);
  margin: 0;
}
.principle-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-top: 36px;
}
.principle-card {
  border: 1px solid rgba(7, 24, 45, 0.14);
  background: rgba(255, 255, 255, 0.26);
  padding: 24px;
  min-height: 210px;
  display: flex;
  flex-direction: column;
}
.principle-card h3 {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 24px;
  line-height: 1.12;
  color: var(--navy);
  margin: 0 0 14px;
  font-weight: 500;
}
.principle-card p {
  font-size: 15px;
  line-height: 1.6;
  color: rgba(7, 24, 45, 0.68);
  margin: 0;
  flex: 1;
}
.research-index-dark,
.dark-zone,
.corridor-dashboard {
  background:
    radial-gradient(circle at 20% 0%, rgba(120, 145, 180, 0.12), transparent 34%),
    linear-gradient(180deg, #07182D 0%, #05070A 100%);
  color: var(--paper);
  padding: 96px 0 110px;
  border-top: 1px solid rgba(7, 24, 45, 0.18);
}
.research-index-dark {
  padding: 96px 0 110px;
}
.dark-kicker {
  font-size: 12px;
  letter-spacing: 3.5px;
  text-transform: uppercase;
  color: rgba(247, 246, 242, 0.58);
  margin-bottom: 18px;
}
.dark-section-title {
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(38px, 5vw, 72px);
  line-height: 1.02;
  letter-spacing: -2px;
  color: var(--paper);
  max-width: 980px;
  margin: 0 0 22px;
  font-weight: 500;
}
.dark-section-intro {
  max-width: 760px;
  font-size: 17px;
  line-height: 1.75;
  color: rgba(247, 246, 242, 0.68);
  margin: 0 0 66px;
}
.research-index-dark .research-domain {
  margin-top: 64px;
}
.research-index-dark .research-domain:first-of-type {
  margin-top: 0;
}
.dark-domain-title {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 32px;
  color: var(--paper);
  letter-spacing: -0.6px;
  margin: 0 0 22px;
  font-weight: 500;
}
.dark-research-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
.dark-research-card {
  border: 1px solid rgba(247, 246, 242, 0.14);
  background: rgba(247, 246, 242, 0.035);
  padding: 26px;
  min-height: 230px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: border-color 0.18s ease, background 0.18s ease;
}
.dark-research-card:hover {
  border-color: rgba(247, 246, 242, 0.34);
  background: rgba(247, 246, 242, 0.055);
}
.dark-card-label {
  font-size: 11px;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: rgba(247, 246, 242, 0.46);
  margin-bottom: 18px;
}
.dark-research-card h3 {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 24px;
  line-height: 1.14;
  color: var(--paper);
  margin: 0 0 14px;
  font-weight: 500;
}
.dark-research-card p {
  font-size: 15px;
  line-height: 1.65;
  color: rgba(247, 246, 242, 0.66);
  margin: 0;
  flex: 1;
}
.dark-research-card a {
  display: inline-block;
  margin-top: 24px;
  font-size: 12px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--paper);
  text-decoration: none;
  border-bottom: 1px solid rgba(247, 246, 242, 0.42);
  padding-bottom: 5px;
  width: fit-content;
}
.dark-research-card a:hover {
  color: var(--paper);
  border-bottom-color: var(--paper);
  text-decoration: none;
}
body.bfi.bfi-research-page .bfi-footer,
body.bfi.bfi-corridor-page .bfi-footer {
  background: #05070A;
  color: rgba(247, 246, 242, 0.72);
  border-top: 1px solid rgba(247, 246, 242, 0.12);
}
body.bfi.bfi-research-page .footer-brand-mark,
body.bfi.bfi-research-page .footer-brand-name,
body.bfi.bfi-corridor-page .footer-brand-mark,
body.bfi.bfi-corridor-page .footer-brand-name {
  color: rgba(247, 246, 242, 0.88);
}
body.bfi.bfi-research-page .footer-brand-tagline,
body.bfi.bfi-research-page .bfi-footer .disc,
body.bfi.bfi-corridor-page .footer-brand-tagline,
body.bfi.bfi-corridor-page .bfi-footer .disc {
  color: rgba(247, 246, 242, 0.52);
}
.page-disclaimer {
  margin-top: 22px;
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(7, 24, 45, 0.55);
  max-width: 640px;
}
.corridor-dashboard .dark-section-title {
  font-size: clamp(32px, 4vw, 52px);
  margin-bottom: 14px;
}
.corridor-dashboard .dark-section-intro {
  margin-bottom: 0;
}
body.bfi-corridor-page {
  --paper: #F7F4EC;
  --ink: #05070A;
  --slate: #7C8794;
  --silver: #CBD3DD;
  --cyan: #6EE7F9;
  --teal: #2DD4BF;
  --green: #7DDC8A;
  --amber: #F2C14E;
  --rose: #FF6B6B;
  --blue: #7AA7FF;
  --violet: #A78BFA;
}
.corridor-dashboard {
  background:
    radial-gradient(circle at 18% 0%, rgba(110, 231, 249, 0.07), transparent 32%),
    radial-gradient(circle at 82% 12%, rgba(167, 139, 250, 0.06), transparent 28%),
    radial-gradient(circle at 20% 0%, rgba(120, 145, 180, 0.12), transparent 34%),
    linear-gradient(180deg, #07182D 0%, #05070A 100%);
}
.insight-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin: 48px 0 28px;
}
.insight-card {
  border: 1px solid rgba(247, 244, 236, 0.14);
  background: linear-gradient(155deg, rgba(247, 244, 236, 0.055) 0%, rgba(247, 244, 236, 0.02) 100%);
  padding: 24px 22px;
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.65s ease, transform 0.65s ease, border-color 0.25s ease;
}
.insight-card.is-visible {
  opacity: 1;
  transform: translateY(0);
}
.insight-card:nth-child(2) { transition-delay: 0.08s; }
.insight-card:nth-child(3) { transition-delay: 0.16s; }
.insight-card:nth-child(4) { transition-delay: 0.24s; }
.insight-card:hover {
  border-color: rgba(247, 244, 236, 0.28);
}
.insight-label {
  font-size: 11px;
  letter-spacing: 2.2px;
  text-transform: uppercase;
  color: rgba(247, 244, 236, 0.48);
  margin-bottom: 14px;
}
.insight-value {
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(28px, 3vw, 38px);
  line-height: 1.05;
  color: var(--paper);
  letter-spacing: -0.5px;
  margin-bottom: 10px;
}
.insight-value.positive { color: var(--teal); }
.insight-value.negative { color: var(--rose); }
.insight-value.neutral { color: var(--silver); }
.insight-value.peak { color: var(--green); }
.insight-delta {
  font-size: 13px;
  letter-spacing: 0.04em;
  margin-bottom: 8px;
}
.insight-delta.positive { color: var(--green); }
.insight-delta.negative { color: var(--rose); }
.insight-delta.neutral { color: var(--slate); }
.insight-sub {
  font-size: 11px;
  line-height: 1.45;
  color: rgba(247, 244, 236, 0.46);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.story-panel {
  border: 1px solid rgba(110, 231, 249, 0.18);
  background: rgba(110, 231, 249, 0.04);
  padding: 22px 26px;
  margin-bottom: 12px;
  opacity: 0;
  transform: translateY(14px);
  transition: opacity 0.7s ease 0.2s, transform 0.7s ease 0.2s;
}
.story-panel.is-visible {
  opacity: 1;
  transform: translateY(0);
}
.story-kicker {
  font-size: 10px;
  letter-spacing: 2.4px;
  text-transform: uppercase;
  color: var(--cyan);
  margin-bottom: 10px;
}
.story-panel p {
  margin: 0;
  font-size: 16px;
  line-height: 1.65;
  color: rgba(247, 244, 236, 0.82);
  max-width: 920px;
}
.story-panel strong {
  color: var(--paper);
  font-weight: 600;
}
.meta-strip {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin: 36px 0 8px;
  padding-top: 28px;
  border-top: 1px solid rgba(247, 244, 236, 0.1);
}
.meta-chip {
  font-size: 11px;
  line-height: 1.45;
  color: rgba(247, 244, 236, 0.42);
  letter-spacing: 0.04em;
}
.meta-chip span {
  display: block;
  font-size: 10px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: rgba(247, 244, 236, 0.32);
  margin-bottom: 6px;
}
.chart-panel.featured {
  border-color: rgba(110, 231, 249, 0.22);
  background: linear-gradient(180deg, rgba(247, 244, 236, 0.045) 0%, rgba(247, 244, 236, 0.02) 100%);
}
.chart-legend-row {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  margin-top: 16px;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(247, 244, 236, 0.48);
}
.chart-legend-row span::before {
  content: "";
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
  vertical-align: -1px;
}
.legend-up::before { background: var(--green); }
.legend-down::before { background: var(--rose); }
.legend-line::before { background: var(--cyan); border-radius: 2px; width: 14px; height: 2px; }
.legend-gap::before { background: var(--blue); border-radius: 2px; width: 14px; height: 2px; }
.chart-grid-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-top: 18px;
}
.metric-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin: 44px 0;
}
.metric-card {
  border: 1px solid rgba(247, 246, 242, 0.14);
  background: rgba(247, 246, 242, 0.035);
  padding: 22px;
}
.metric-label {
  font-size: 11px;
  letter-spacing: 2.2px;
  text-transform: uppercase;
  color: rgba(247, 246, 242, 0.48);
  margin-bottom: 12px;
}
.metric-value {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 22px;
  color: var(--paper);
  line-height: 1.15;
}
.chart-panel {
  border: 1px solid rgba(247, 246, 242, 0.14);
  background: rgba(247, 246, 242, 0.035);
  padding: 28px;
  margin-top: 28px;
}
.chart-header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-start;
  margin-bottom: 26px;
}
.chart-kicker {
  font-size: 11px;
  letter-spacing: 2.3px;
  text-transform: uppercase;
  color: rgba(247, 246, 242, 0.46);
  margin-bottom: 10px;
}
.chart-header h3 {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 30px;
  color: var(--paper);
  margin: 0;
  font-weight: 500;
}
.chart-note {
  max-width: 260px;
  font-size: 12px;
  line-height: 1.5;
  color: rgba(247, 246, 242, 0.52);
  text-align: right;
}
.chart-canvas-wrap {
  position: relative;
  height: 380px;
  width: 100%;
}
.chart-canvas-wrap.chart-canvas-tall {
  height: 420px;
}
.chart-canvas-wrap canvas {
  width: 100% !important;
  max-height: 420px;
}
.corridor-methodology {
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid rgba(247, 246, 242, 0.12);
  max-width: 820px;
}
.corridor-methodology h4 {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 18px;
  color: rgba(247, 246, 242, 0.88);
  margin: 0 0 12px;
  font-weight: 500;
}
.corridor-methodology h4:not(:first-child) {
  margin-top: 28px;
}
.corridor-methodology p,
.corridor-methodology li {
  font-size: 14px;
  line-height: 1.65;
  color: rgba(247, 246, 242, 0.62);
}
.corridor-methodology ul {
  margin: 0;
  padding-left: 1.15rem;
}
.bfi-parent-link {
  display: inline-block;
  margin-bottom: 1.25rem;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--gold);
}
@media (max-width: 980px) {
  .principle-grid,
  .dark-research-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 640px) {
  .page-hero {
    padding: 72px 0 52px;
  }
  .research-standards {
    padding: 52px 0 64px;
  }
  .research-index-dark {
    padding: 72px 0 84px;
  }
  .corridor-dashboard {
    padding: 72px 0 84px;
  }
  .metric-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .insight-strip {
    grid-template-columns: repeat(2, 1fr);
  }
  .chart-grid-two {
    grid-template-columns: 1fr;
  }
  .meta-strip {
    grid-template-columns: repeat(2, 1fr);
  }
  .chart-header {
    flex-direction: column;
  }
  .chart-note {
    text-align: left;
    max-width: 100%;
  }
  .principle-grid,
  .dark-research-grid {
    grid-template-columns: 1fr;
  }
  .principle-card,
  .dark-research-card {
    min-height: auto;
  }
  .metric-grid {
    grid-template-columns: 1fr;
  }
  .insight-strip {
    grid-template-columns: 1fr;
  }
  .meta-strip {
    grid-template-columns: 1fr;
  }
  .bfi-hero { padding-top: 3rem; }
  .bfi-card-grid { grid-template-columns: 1fr; }
  .hero-actions { flex-direction: column; align-items: flex-start; }
}
"""


def bfi_favicon_tags() -> str:
    return (
        f'<link rel="icon" href="{BFI_ICON}" type="image/svg+xml"/>'
        f'<link rel="apple-touch-icon" href="{BFI_ICON}"/>'
    )


def bfi_brand_lockup(*, inverse: bool = False, href: str = "index.html") -> str:
    cls = "brand-lockup brand-lockup--inverse" if inverse else "brand-lockup"
    return (
        f'<a class="{cls}" href="{html.escape(href, quote=True)}" '
        f'aria-label="{html.escape(ROOT_BRAND)} home">'
        f'<span class="brand-mark">BFI</span>'
        f'<span class="brand-divider"></span>'
        f'<span class="brand-name">BOWERS FRONTIER INSTITUTE</span>'
        f"</a>"
    )


def bfi_brand_lockup_css() -> str:
    return """
.brand-lockup {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  text-decoration: none;
  color: #07182D;
  white-space: nowrap;
  flex-shrink: 0;
}
.brand-lockup:hover { opacity: 0.92; text-decoration: none; }
.brand-mark {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 28px;
  letter-spacing: -1.5px;
  font-weight: 500;
  line-height: 1;
}
.brand-divider {
  width: 1px;
  height: 28px;
  background: rgba(7, 24, 45, 0.35);
  display: inline-block;
}
.brand-name {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 13px;
  letter-spacing: 2.8px;
  text-transform: uppercase;
  line-height: 1;
}
.brand-lockup--inverse { color: #F7F6F2; }
.brand-lockup--inverse .brand-divider { background: rgba(247, 246, 242, 0.35); }
@media (max-width: 720px) {
  .brand-name { display: none; }
  .brand-divider { display: none; }
  .brand-mark { font-size: 32px; }
}
"""


def bfi_header_logo(*, inverse: bool = False) -> str:
    """Text-based institute lockup for headers."""
    return bfi_brand_lockup(inverse=inverse)


def bfi_footer_brand() -> str:
    return (
        f'<div class="footer-brand">'
        f'<div class="footer-brand-mark">BFI</div>'
        f'<div class="footer-brand-name">{html.escape(ROOT_BRAND)}</div>'
        f'<div class="footer-brand-tagline">{html.escape(CORE_LINE)}</div>'
        f"</div>"
    )


def _nav_bfi(active: str) -> str:
    parts = ['<nav class="bfi-nav">']
    for href, label, key in BFI_NAV:
        cls = ' class="active"' if key == active else ""
        parts.append(f'<a href="{href}"{cls}>{html.escape(label)}</a>')
    parts.append("</nav>")
    return "\n".join(parts)


def _bfi_shell(
    body: str,
    *,
    active: str = "home",
    title: str | None = None,
    page_class: str = "",
    head_extra: str = "",
    scripts: str = "",
) -> str:
    page_title = title or ROOT_BRAND
    body_cls = "bfi" + (f" {page_class}" if page_class else "")
    foot = (
        f"{html.escape(ROOT_BRAND)} · Prepared by Brendan Bowers · "
        "Research and risk-framing only · Not investment advice · No live trading."
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <meta name="description" content="{html.escape(ROOT_BRAND)} — {html.escape(TAGLINE)}"/>
  <title>{html.escape(page_title)}</title>
  {bfi_favicon_tags()}
  {head_extra}
  <style>{_css_bfi()}</style>
</head>
<body class="{body_cls}">
  <header class="bfi-header">
    <div class="bfi-header-inner">
      {bfi_header_logo()}
      {_nav_bfi(active)}
    </div>
  </header>
  {body}
  <footer class="bfi-footer">
    {bfi_footer_brand()}
    <p>{foot}</p>
    <p class="disc">Independent research institute. Not affiliated with any employer, bank, or payment company unless explicitly stated.</p>
  </footer>
  {scripts}
</body>
</html>"""


def _card_grid(items: list[tuple[str, str, str, str]], css_class: str = "bfi-card") -> str:
    cards = []
    for href, title, desc, tag in items:
        cards.append(
            f'<a href="{html.escape(href, quote=True)}" class="{css_class}">'
            f'<div class="tag">{html.escape(tag)}</div>'
            f"<h3>{html.escape(title)}</h3>"
            f"<p>{html.escape(desc)}</p>"
            f"</a>"
        )
    return f'<div class="bfi-card-grid">{"".join(cards)}</div>'


def bfi_index_body() -> str:
    questions = "".join(f"<li>{html.escape(q)}</li>" for q in BFI_QUESTIONS)
    principles = "".join(
        f'<div class="bfi-principle"><h3>{html.escape(t)}</h3><p>{html.escape(d)}</p></div>'
        for t, d in BFI_PRINCIPLES
    )
    return f"""
<section class="bfi-hero hero">
  <div class="hero-inner">
    <div class="hero-eyebrow">BOWERS FRONTIER INSTITUTE</div>
    <h1>{html.escape(CORE_LINE)}</h1>
    <p class="hero-subtitle">{html.escape(TAGLINE)}</p>
    <p class="hero-thesis">An independent research platform studying the systems that move money, information, and risk.</p>
    <div class="hero-actions">
      <a href="research.html" class="bfi-cta primary">Read the Research</a>
      <a href="labs.html" class="bfi-cta secondary">Explore the Labs</a>
      <a href="methodology.html" class="bfi-cta secondary">View Methodology</a>
    </div>
  </div>
</section>

<main class="bfi-main">
  <section class="bfi-section" id="research">
    <p class="lead">The world&rsquo;s financial systems move faster than the institutions built to understand them.</p>
    <p class="lead">Currencies reprice in milliseconds. Settlement risk hides inside timing gaps. Liquidity fractures across jurisdictions, platforms, currencies, and payment rails. Artificial intelligence is beginning to interpret markets faster than humans can audit the models behind it.</p>
    <p class="lead lead-strong">{html.escape(ROOT_BRAND)} studies the systems that move money, information, and risk.</p>
    <p class="lead">We are building an independent research platform focused on foreign exchange, settlement infrastructure, monetary systems, AI-driven market intelligence, and the future of global market architecture.</p>
    <div class="stance">
      <p>This is not a trading blog.</p>
      <p>This is not another dashboard.</p>
      <p>This is not hype dressed up as research.</p>
    </div>
    <p class="lead lead-strong">This is a frontier institute for the questions that sit between markets, machines, and money.</p>
  </section>

  <section class="bfi-section" id="frontier">
    <h2>The Frontier</h2>
    <p class="emph">The next generation of financial risk will not look like the last one.</p>
    <p>It will emerge from speed, opacity, automation, fragmented liquidity, model dependency, and settlement architecture that was not designed for an AI-native financial world.</p>
    <p>{html.escape(ROOT_BRAND)} exists to study these systems with rigor, transparency, and ambition.</p>
    <ul class="bfi-punch-list">
      <li>Not just where markets move.</li>
      <li>Why they move.</li>
      <li>How they break.</li>
      <li>Where risk hides.</li>
      <li>What infrastructure comes next.</li>
    </ul>
  </section>

  <section class="bfi-section" id="domains">
    <h2>Core Research Domains</h2>
    {_card_grid(BFI_CORE_DOMAINS)}
  </section>

  <section class="bfi-section" id="questions">
    <h2>The Questions</h2>
    <ol class="bfi-questions">{questions}</ol>
  </section>

  <section class="bfi-section" id="why-now">
    <h2>Why Now</h2>
    <p>Foreign exchange remains the largest market in the world, but many of its most important mechanics are still poorly understood outside specialized institutions.</p>
    <p>Settlement infrastructure is changing. Stablecoins are moving from speculation into payment architecture. AI is becoming a market interpreter. Treasury systems are evolving from back-office plumbing into strategic infrastructure.</p>
    <p class="emph">The frontier is no longer just price prediction.</p>
    <p>The frontier is understanding how global money systems behave under stress, automation, fragmentation, and speed.</p>
  </section>

  <section class="bfi-section" id="mission">
    <h2>Mission</h2>
    <div class="bfi-mission-block">
      <p>To advance open, rigorous, and independent research on the systems that move money, information, and risk across the global economy.</p>
    </div>
  </section>

  <section class="bfi-section" id="vision">
    <h2>Vision</h2>
    <div class="bfi-mission-block">
      <p>A world where the most important questions in financial systems are studied openly with the seriousness, transparency, and ambition they deserve.</p>
    </div>
  </section>

  <section class="bfi-section" id="principles">
    <h2>Operating Principles</h2>
    <div class="bfi-principles">{principles}</div>
  </section>

  <section class="bfi-section" id="labs">
    <h2>Research Labs</h2>
    {_card_grid(BFI_LABS)}
  </section>

  <div class="bfi-closing">
    <p class="brand">{html.escape(ROOT_BRAND)}</p>
    <p class="core">{html.escape(CORE_LINE)}</p>
    <p class="tag">{html.escape(TAGLINE)}</p>
  </div>
</main>
"""


def _principle_card(title: str, desc: str) -> str:
    return (
        f'<div class="principle-card">'
        f"<h3>{html.escape(title)}</h3>"
        f"<p>{html.escape(desc)}</p>"
        f"</div>"
    )


def _principle_grid(items: list[tuple[str, str]]) -> str:
    cards = "".join(_principle_card(t, d) for t, d in items)
    return f'<div class="principle-grid">{cards}</div>'


def _dark_research_card(href: str, title: str, label: str, desc: str) -> str:
    return (
        f'<article class="dark-research-card">'
        f'<div class="dark-card-label">{html.escape(label)}</div>'
        f"<h3>{html.escape(title)}</h3>"
        f"<p>{html.escape(desc)}</p>"
        f'<a href="{html.escape(href, quote=True)}">View Research</a>'
        f"</article>"
    )


def _dark_research_domain(domain_title: str, cards: list[tuple[str, str, str, str]]) -> str:
    grid = "".join(_dark_research_card(h, t, lbl, d) for h, t, lbl, d in cards)
    return (
        f'<div class="research-domain">'
        f'<h3 class="dark-domain-title">{html.escape(domain_title)}</h3>'
        f'<div class="dark-research-grid">{grid}</div>'
        f"</div>"
    )


def bfi_research_hub_body() -> str:
    principles = [
        (
            "Reproducibility",
            "Methods, inputs, and assumptions should be clear enough to review.",
        ),
        (
            "Model Discipline",
            "Outputs should be validated, stress-tested, and separated from narrative.",
        ),
        (
            "Market Structure First",
            "Research should explain systems, not just chase signals.",
        ),
        (
            "Stated Limitations",
            "Every claim should make uncertainty visible.",
        ),
    ]
    domains = [
        (
            "Macro Lab",
            [
                (
                    "usdmxn-research.html",
                    "USD/MXN Regime Research",
                    "Macro Lab",
                    "Regime behavior, corridor dynamics, volatility context, and macro transmission.",
                ),
                (
                    "hedge-governance.html",
                    "Hedge Governance Memo",
                    "Macro Lab",
                    "Practical treasury governance, hedging process, controls, and risk framing.",
                ),
                (
                    "memo.html",
                    "Full Research Note",
                    "Macro Lab",
                    "Long-form institutional research note and thesis documentation.",
                ),
                (
                    "global-fx-lab.html",
                    "Global FX Research Lab",
                    "Macro Lab",
                    "Core FX research environment for currencies, carry, forwards, volatility, and liquidity.",
                ),
                (
                    "corridor.html",
                    "Corridor Roadmap",
                    "Macro Lab",
                    "Priority corridors, data expansion, model direction, and research sequencing.",
                ),
            ],
        ),
        (
            "Market Structure",
            [
                (
                    "value-survival-index.html",
                    "Value Survival Index",
                    "Market Structure",
                    "A framework for stress, durability, and relative value under changing market regimes.",
                ),
                (
                    "settlement-economics-lab.html",
                    "Settlement Economics Lab",
                    "Market Structure",
                    "Settlement timing, payment rails, liquidity windows, and operational risk.",
                ),
                (
                    "stablecoin-settlement-lab.html",
                    "Stablecoin Settlement Lab",
                    "Market Structure",
                    "Stablecoins, tokenized money, settlement architecture, and cross-border payment design.",
                ),
            ],
        ),
        (
            "Intelligence",
            [
                (
                    "model-zoo.html",
                    "Model Zoo",
                    "Intelligence",
                    "Inventory of models, experiments, validation approaches, and research workflows.",
                ),
                (
                    "open-source-ai.html",
                    "Open Source FX AI Lab",
                    "Intelligence",
                    "Open-source model development for FX classification, anomaly detection, and market intelligence.",
                ),
            ],
        ),
        (
            "Foundations",
            [
                (
                    "unanswered-fx.html",
                    "Unanswered FX Questions",
                    "Foundations",
                    "Frontier questions in foreign exchange, monetary infrastructure, and market behavior.",
                ),
                (
                    "history.html",
                    "FX History & Foundations",
                    "Foundations",
                    "Historical context, major milestones, academic foundations, and key research lineage.",
                ),
            ],
        ),
    ]
    domain_html = "".join(_dark_research_domain(title, cards) for title, cards in domains)
    return f"""
<main class="bfi-research-page">
  <section class="page-hero research-hero light-zone">
    <div class="bfi-page-inner">
      <div class="page-eyebrow">RESEARCH LIBRARY</div>
      <h1>Open research on markets, machines, and monetary systems.</h1>
      <p class="page-subtitle">Published memos, model notes, technical briefs, dashboards, and frontier questions from {html.escape(ROOT_BRAND)} labs.</p>
      <p class="page-thesis">The library organizes BFI research across foreign exchange, settlement infrastructure, AI market intelligence, model validation, and the future architecture of global financial systems.</p>
    </div>
  </section>

  <section class="section research-standards light-zone" id="research-standards">
    <div class="bfi-page-inner">
      <div class="section-kicker">Institute Standards</div>
      <h2 class="section-title">Research Standards</h2>
      <p class="section-intro">{html.escape(ROOT_BRAND)} treats research as infrastructure: documented, reproducible, clearly scoped, and open to challenge. Each memo, model output, and dashboard should make its assumptions visible, separate signal from speculation, and state its limitations.</p>
      {_principle_grid(principles)}
    </div>
  </section>

  <section class="research-index-dark dark-zone" id="research">
    <div class="bfi-page-inner">
      <div class="dark-kicker">RESEARCH INDEX</div>
      <h2 class="dark-section-title">Working papers, labs, models, and technical notes.</h2>
      <p class="dark-section-intro">A structured index of BFI research across macro systems, market structure, intelligence, and monetary infrastructure.</p>
      {domain_html}
    </div>
  </section>
</main>
"""


def bfi_labs_hub_body() -> str:
    return f"""
<section class="bfi-hero" style="padding-bottom:2rem;">
  <p class="tagline">Laboratory Structure</p>
  <h1>Research Labs</h1>
  <p class="lead">Specialized research divisions under {html.escape(ROOT_BRAND)}. Each lab maintains its own methodology, datasets, and publication stream while sharing common standards for transparency and reproducibility.</p>
</section>
<main class="bfi-main">
  <section class="bfi-section">
    {_card_grid(BFI_LABS)}
  </section>
  <section class="bfi-section">
    <h2>BR3N Macro Lab</h2>
    <p>The operational research platform for cross-border value infrastructure — VSI, settlement economics, stablecoin finality, data lake governance, and interactive dashboards.</p>
    <p><a href="macro-lab.html" class="bfi-cta secondary">Enter BR3N Macro Lab →</a></p>
  </section>
</main>
"""


def bfi_methodology_body() -> str:
    principles = "".join(
        f'<div class="bfi-principle"><h3>{html.escape(t)}</h3><p>{html.escape(d)}</p></div>'
        for t, d in BFI_PRINCIPLES
    )
    return f"""
<section class="bfi-hero" style="padding-bottom:2rem;">
  <p class="tagline">Standards &amp; Discipline</p>
  <h1>Methodology</h1>
  <p class="lead">How {html.escape(ROOT_BRAND)} approaches research design, validation, documentation, and public release.</p>
</section>
<main class="bfi-main">
  <section class="bfi-section">
    <h2>Operating Principles</h2>
    <div class="bfi-principles">{principles}</div>
  </section>
  <section class="bfi-section">
    <h2>Evidence Framework</h2>
    <p>Eight-level evidence ladder for assessing research maturity — from descriptive statistics through out-of-sample validation, cross-market replication, and institutional-grade governance.</p>
    <p><a href="ladder.html">Research Evidence Ladder →</a></p>
  </section>
  <section class="bfi-section">
    <h2>Data Quality &amp; Lineage</h2>
    <p>Source registry, file hashes, mock-data flags, validation reports, and nightly audit snapshots. No unlabeled data in published outputs.</p>
    <p><a href="lab-status.html">Lab Status &amp; Audit →</a></p>
  </section>
</main>
"""


def bfi_dashboards_body() -> str:
    return f"""
<section class="bfi-hero" style="padding-bottom:2rem;">
  <p class="tagline">Analytical Tools</p>
  <h1>Dashboards</h1>
  <p class="lead">Interactive research interfaces built by BR3N Studio. Python computes; dashboards visualize. Research only — not investment advice.</p>
</section>
<main class="bfi-main">
  <section class="bfi-section">
    {_card_grid([
      ("us-mexico-corridor.html", "US/Mexico Corridor", "Remittance flows, FX context, and corridor-level market structure for the United States → Mexico corridor.", "Corridor"),
      ("dashboard/index.html", "Command Center", "Cross-lab KPIs, Sankey flows, value survival, settlement timeline, finality matrix, and data lineage.", "Primary"),
      ("dashboard/value-flow/index.html", "Global Value Flow", "Geo-arc corridor map with leakage-weighted paths.", "Visualization"),
      ("dashboard/value-survival/index.html", "Value Survival", "Interactive Sankey decomposition by corridor.", "VSI"),
      ("dashboard/settlement/index.html", "Settlement Economics", "SDI rankings and animated finality timeline.", "Settlement"),
      ("dashboard/stablecoins/index.html", "Stablecoin Finality", "Ledger vs economic finality matrix.", "Stablecoin"),
      ("dashboard/data-lake/index.html", "Data Lake", "Bronze/silver/gold lineage force graph.", "Infrastructure"),
    ])}
  </section>
</main>
"""


def bfi_us_mexico_corridor_body() -> str:
    return """
<main class="bfi-corridor-page-main">
  <section class="page-hero light-zone">
    <div class="bfi-page-inner">
      <div class="page-eyebrow">CORRIDOR DASHBOARD</div>
      <h1>United States → Mexico corridor.</h1>
      <p class="page-subtitle">A live-style research dashboard for remittance flows, FX context, and corridor-level financial structure.</p>
      <p class="page-thesis">The US/Mexico corridor is more than a remittance channel. It is a monetary system connecting household income, labor markets, exchange rates, settlement rails, liquidity timing, and cross-border financial infrastructure.</p>
      <p class="page-disclaimer">Research and education only. Not investment advice. No live trading.</p>
    </div>
  </section>

  <section class="corridor-dashboard dark-zone">
    <div class="bfi-page-inner">
      <div class="dark-kicker">CORRIDOR INTELLIGENCE</div>
      <h2 class="dark-section-title">Flow, pressure, and change in the US/Mexico corridor.</h2>
      <p class="dark-section-intro">This prototype focuses on one simple question: is the corridor accelerating, slowing, or structurally changing?</p>

      <div class="insight-strip" id="insightStrip">
        <article class="insight-card" data-animate>
          <div class="insight-label">Latest monthly flow</div>
          <div class="insight-value neutral" id="insightLatest" data-count="5060" data-suffix="">0</div>
          <div class="insight-sub">Nov 2025 · USD millions · starter data</div>
        </article>
        <article class="insight-card" data-animate>
          <div class="insight-label">Latest YoY change</div>
          <div class="insight-value negative" id="insightYoyPct" data-count="-7.8" data-decimals="1" data-suffix="%">0</div>
          <div class="insight-delta negative" id="insightYoyAbs">−429M vs Nov 2024</div>
          <div class="insight-sub">Nov 2025 vs Nov 2024 · starter data</div>
        </article>
        <article class="insight-card" data-animate>
          <div class="insight-label">2025 YTD flow</div>
          <div class="insight-value neutral" id="insightYtd" data-count="55651" data-suffix="">0</div>
          <div class="insight-sub">Jan–Nov 2025 · USD millions · starter data</div>
        </article>
        <article class="insight-card" data-animate>
          <div class="insight-label">Peak month</div>
          <div class="insight-value peak" id="insightPeak" data-count="5723" data-suffix="">0</div>
          <div class="insight-sub">Oct 2024 · dataset high · starter data</div>
        </article>
      </div>

      <div class="story-panel" id="storyPanel" data-animate>
        <div class="story-kicker">Corridor read · starter data</div>
        <p id="corridorStory">Loading corridor narrative…</p>
      </div>

      <div class="chart-panel featured">
        <div class="chart-header">
          <div>
            <div class="chart-kicker">PRIMARY FLOW · BANXICO SIE · SAMPLE DATA</div>
            <h3>Monthly remittances to Mexico</h3>
          </div>
          <div class="chart-note">Point color = month-over-month direction. Annotations mark peak and trough in starter series.</div>
        </div>
        <div class="chart-canvas-wrap chart-canvas-tall">
          <canvas id="remittanceChart"></canvas>
        </div>
        <div class="chart-legend-row">
          <span class="legend-up">MoM increase</span>
          <span class="legend-down">MoM decrease</span>
          <span class="legend-line">Monthly flow</span>
        </div>
      </div>

      <div class="chart-grid-two">
        <div class="chart-panel">
          <div class="chart-header">
            <div>
              <div class="chart-kicker">MOM CHANGE · USD MILLIONS</div>
              <h3>Month-over-month delta</h3>
            </div>
          </div>
          <div class="chart-canvas-wrap">
            <canvas id="momChart"></canvas>
          </div>
        </div>
        <div class="chart-panel">
          <div class="chart-header">
            <div>
              <div class="chart-kicker">YOY GAP · USD MILLIONS</div>
              <h3>Year-over-year monthly gap</h3>
            </div>
          </div>
          <div class="chart-canvas-wrap">
            <canvas id="yoyGapChart"></canvas>
          </div>
          <div class="chart-legend-row">
            <span class="legend-up">Above prior year</span>
            <span class="legend-down">Below prior year</span>
          </div>
        </div>
      </div>

      <div class="chart-panel">
        <div class="chart-header">
          <div>
            <div class="chart-kicker">12-MONTH ROLLING · USD MILLIONS</div>
            <h3>Trailing twelve-month corridor flow</h3>
          </div>
          <div class="chart-note">Rolling sum from starter dataset · structural pace indicator</div>
        </div>
        <div class="chart-canvas-wrap">
          <canvas id="rollingChart"></canvas>
        </div>
      </div>

      <div class="meta-strip">
        <div class="meta-chip"><span>Corridor</span>United States → Mexico</div>
        <div class="meta-chip"><span>Primary flow</span>Worker remittances</div>
        <div class="meta-chip"><span>Frequency</span>Monthly</div>
        <div class="meta-chip"><span>Unit</span>USD millions</div>
        <div class="meta-chip"><span>Source</span>Banco de México / Banxico SIE</div>
      </div>

      <div class="corridor-methodology">
        <h4>Sources</h4>
        <ul>
          <li>Banco de México SIE, Workers&rsquo; Remittances, monthly flows, millions of USD.</li>
          <li>World Bank Remittance Prices Worldwide may be added later for transfer-cost analysis.</li>
          <li>Future versions should ingest official CSV/API data and add USD/MXN, fee, speed, and provider-cost layers.</li>
        </ul>
        <h4>Methodology</h4>
        <p>This page is a corridor research prototype. Starter visualization values must be replaced with official Banxico SIE export/API data before external publication. Animations and color cues are for research communication only — not trading signals.</p>
      </div>
    </div>
  </section>
</main>
"""


def bfi_us_mexico_corridor_scripts() -> str:
    return r"""
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
(function () {
  const C = {
    paper: "#F7F4EC",
    green: "#7DDC8A",
    rose: "#FF6B6B",
    teal: "#2DD4BF",
    cyan: "#6EE7F9",
    blue: "#7AA7FF",
    silver: "#CBD3DD",
    slate: "rgba(247, 244, 236, 0.55)",
    grid: "rgba(247, 244, 236, 0.08)"
  };

  const monthLabels = [
    "Jan 2024", "Feb 2024", "Mar 2024", "Apr 2024", "May 2024", "Jun 2024",
    "Jul 2024", "Aug 2024", "Sep 2024", "Oct 2024", "Nov 2024", "Dec 2024",
    "Jan 2025", "Feb 2025", "Mar 2025", "Apr 2025", "May 2025", "Jun 2025",
    "Jul 2025", "Aug 2025", "Sep 2025", "Oct 2025", "Nov 2025"
  ];
  const remittances = [
    4575, 4510, 5120, 5422, 5624, 5578, 5614, 5579, 5360, 5723, 5489, 5228,
    4761, 4459, 5145, 5130, 5360, 5201, 5330, 5085, 5050, 5070, 5060
  ];

  const n = remittances.length - 1;
  const latest = remittances[n];
  const prev = remittances[n - 1];
  const nov2024 = remittances[10];
  const yoyAbs = latest - nov2024;
  const yoyPct = (yoyAbs / nov2024) * 100;
  const momAbs = latest - prev;
  const momPct = (momAbs / prev) * 100;
  const ytd2025 = remittances.slice(12, 23).reduce((a, b) => a + b, 0);
  const peakVal = Math.max(...remittances);
  const troughVal = Math.min(...remittances);
  const peakIdx = remittances.indexOf(peakVal);
  const troughIdx = remittances.indexOf(troughVal);

  const momDeltas = remittances.map((v, i) => (i === 0 ? null : v - remittances[i - 1]));
  const momLabels = monthLabels.slice(1);
  const momValues = momDeltas.slice(1);
  const momColors = momValues.map(v => v > 0 ? "rgba(125, 220, 138, 0.72)" : v < 0 ? "rgba(255, 107, 107, 0.72)" : "rgba(203, 211, 221, 0.45)");

  const yoyGapLabels = monthLabels.slice(12, 23);
  const yoyGapValues = yoyGapLabels.map((_, i) => remittances[12 + i] - remittances[i]);
  const yoyGapColors = yoyGapValues.map(v => v >= 0 ? "rgba(125, 220, 138, 0.65)" : "rgba(255, 107, 107, 0.65)");

  const pointColors = remittances.map((v, i) => {
    if (i === peakIdx) return C.green;
    if (i === troughIdx) return C.rose;
    if (i === 0) return C.cyan;
    const d = v - remittances[i - 1];
    if (d > 0) return C.teal;
    if (d < 0) return C.rose;
    return C.silver;
  });
  const pointRadii = remittances.map((_, i) => (i === peakIdx || i === troughIdx || i === n ? 6 : 3));

  function fmt(n, dec) {
    return n.toLocaleString("en-US", { maximumFractionDigits: dec || 0, minimumFractionDigits: dec || 0 });
  }

  function countUp(el, target, duration, decimals, prefix, suffix) {
    const start = performance.now();
    const from = 0;
    function frame(now) {
      const t = Math.min((now - start) / duration, 1);
      const ease = 1 - Math.pow(1 - t, 3);
      const val = from + (target - from) * ease;
      el.textContent = (prefix || "") + fmt(val, decimals) + (suffix || "");
      if (t < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function animateInsights() {
    document.querySelectorAll("[data-count]").forEach(el => {
      const target = parseFloat(el.getAttribute("data-count"));
      const decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
      const suffix = el.getAttribute("data-suffix") || "";
      const prefix = target > 0 && el.id === "insightYoyPct" ? "+" : (target < 0 && el.id === "insightYoyPct" ? "" : "");
      countUp(el, target, 1400, decimals, prefix, suffix);
    });
    const yoyAbsEl = document.getElementById("insightYoyAbs");
    if (yoyAbsEl) {
      const sign = yoyAbs >= 0 ? "+" : "−";
      yoyAbsEl.textContent = sign + fmt(Math.abs(yoyAbs)) + "M vs Nov 2024";
      yoyAbsEl.className = "insight-delta " + (yoyAbs >= 0 ? "positive" : "negative");
    }
  }

  function buildStory() {
    const momWord = Math.abs(momPct) < 0.5 ? "flat" : (momPct > 0 ? "accelerating" : "easing");
    const yoyWord = yoyPct >= 0 ? "above" : "below";
    const pace = latest < peakVal * 0.92 ? "cooled from 2024 highs" : "holding elevated levels";
    return (
      "Corridor flows peaked at <strong>" + fmt(peakVal) + "M</strong> in " + monthLabels[peakIdx] +
      ". The latest reading (<strong>" + fmt(latest) + "M</strong>, " + monthLabels[n] + ") sits <strong>" +
      Math.abs(yoyPct).toFixed(1) + "% " + yoyWord + "</strong> the same month last year and looks <strong>" +
      momWord + "</strong> month-over-month (" + (momAbs >= 0 ? "+" : "") + fmt(momAbs) + "M). " +
      "2025 YTD (Jan–Nov) totals <strong>" + fmt(ytd2025) + "M</strong>, suggesting the corridor has <strong>" +
      pace + "</strong> while remaining structurally large. Trough in starter series: <strong>" +
      fmt(troughVal) + "M</strong> (" + monthLabels[troughIdx] + ")."
    );
  }

  const storyEl = document.getElementById("corridorStory");
  if (storyEl) storyEl.innerHTML = buildStory();

  let insightsAnimated = false;
  function triggerInsights() {
    if (insightsAnimated) return;
    insightsAnimated = true;
    animateInsights();
  }

  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      if (entry.target.id === "insightStrip" || entry.target.classList.contains("insight-card")) {
        triggerInsights();
      }
      io.unobserve(entry.target);
    });
  }, { threshold: 0.2 });

  document.querySelectorAll("[data-animate]").forEach(el => io.observe(el));
  io.observe(document.getElementById("insightStrip"));

  const peakTroughPlugin = {
    id: "peakTroughLabels",
    afterDatasetsDraw(chart) {
      const { ctx } = chart;
      const meta = chart.getDatasetMeta(0);
      [peakIdx, troughIdx, n].forEach(i => {
        const pt = meta.data[i];
        if (!pt) return;
        const label = i === peakIdx ? "PEAK" : (i === troughIdx ? "TROUGH" : "LATEST");
        const color = i === peakIdx ? C.green : (i === troughIdx ? C.rose : C.cyan);
        ctx.save();
        ctx.fillStyle = color;
        ctx.font = "600 10px Inter, Helvetica, sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(label, pt.x, pt.y - 14);
        ctx.restore();
      });
    }
  };

  const baseScales = {
    x: {
      ticks: { color: C.slate, maxRotation: 45, minRotation: 45, font: { size: 10 } },
      grid: { color: C.grid },
      title: { display: true, text: "Month", color: "rgba(247,244,236,0.45)", font: { size: 11 } }
    },
    y: {
      ticks: { color: C.slate, font: { size: 11 } },
      grid: { color: C.grid },
      title: { display: true, text: "USD millions", color: "rgba(247,244,236,0.45)", font: { size: 11 } }
    }
  };

  const basePlugins = {
    legend: { display: false },
    tooltip: {
      backgroundColor: "rgba(5, 7, 10, 0.94)",
      borderColor: "rgba(247, 244, 236, 0.18)",
      borderWidth: 1,
      titleColor: C.paper,
      bodyColor: "rgba(247, 244, 236, 0.78)",
      callbacks: {
        label(ctx) {
          let line = ctx.dataset.label + ": " + fmt(ctx.parsed.y) + "M";
          if (ctx.chart.canvas.id === "momChart") return "MoM: " + (ctx.parsed.y >= 0 ? "+" : "") + fmt(ctx.parsed.y) + "M";
          if (ctx.chart.canvas.id === "yoyGapChart") return "YoY gap: " + (ctx.parsed.y >= 0 ? "+" : "") + fmt(ctx.parsed.y) + "M";
          return line;
        }
      }
    }
  };

  const anim = { duration: 1400, easing: "easeOutQuart" };

  new Chart(document.getElementById("remittanceChart"), {
    type: "line",
    data: {
      labels: monthLabels,
      datasets: [{
        label: "Monthly remittances",
        data: remittances,
        borderColor: C.cyan,
        backgroundColor: "rgba(110, 231, 249, 0.06)",
        borderWidth: 2.5,
        pointRadius: pointRadii,
        pointHoverRadius: 8,
        pointBackgroundColor: pointColors,
        pointBorderColor: "rgba(5, 7, 10, 0.85)",
        pointBorderWidth: 1.5,
        tension: 0.28,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: anim,
      plugins: basePlugins,
      scales: baseScales
    },
    plugins: [peakTroughPlugin]
  });

  new Chart(document.getElementById("momChart"), {
    type: "bar",
    data: {
      labels: momLabels,
      datasets: [{
        label: "MoM change",
        data: momValues,
        backgroundColor: momColors,
        borderColor: momColors.map(c => c.replace("0.72", "1").replace("0.45", "0.8")),
        borderWidth: 1,
        borderRadius: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: anim,
      plugins: basePlugins,
      scales: {
        ...baseScales,
        y: { ...baseScales.y, title: { ...baseScales.y.title, text: "USD millions change" } }
      }
    }
  });

  new Chart(document.getElementById("yoyGapChart"), {
    type: "bar",
    data: {
      labels: yoyGapLabels,
      datasets: [{
        label: "YoY gap",
        data: yoyGapValues,
        backgroundColor: yoyGapColors,
        borderColor: yoyGapColors.map(c => c.replace("0.65", "1")),
        borderWidth: 1,
        borderRadius: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: anim,
      plugins: basePlugins,
      scales: {
        ...baseScales,
        y: { ...baseScales.y, title: { ...baseScales.y.title, text: "2025 minus 2024 (USD millions)" } }
      }
    }
  });

  const rollingLabels = [];
  const rollingValues = [];
  for (let i = 11; i < remittances.length; i++) {
    let sum = 0;
    for (let j = i - 11; j <= i; j++) sum += remittances[j];
    rollingLabels.push(monthLabels[i]);
    rollingValues.push(sum);
  }

  new Chart(document.getElementById("rollingChart"), {
    type: "line",
    data: {
      labels: rollingLabels,
      datasets: [{
        label: "12-month rolling total",
        data: rollingValues,
        borderColor: C.blue,
        backgroundColor: "rgba(122, 167, 255, 0.08)",
        borderWidth: 2,
        pointRadius: 2,
        pointBackgroundColor: C.blue,
        tension: 0.25,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: anim,
      plugins: basePlugins,
      scales: baseScales
    }
  });
})();
</script>
"""


def bfi_about_body() -> str:
    return f"""
<section class="bfi-hero" style="padding-bottom:2rem;">
  <p class="tagline">Institute</p>
  <h1>About</h1>
  <p class="lead">{html.escape(ROOT_BRAND)} is an independent research institute studying foreign exchange, settlement infrastructure, monetary systems, and AI-mediated market intelligence.</p>
</section>
<main class="bfi-main">
  <section class="bfi-section">
    <h2>Mission</h2>
    <div class="bfi-mission-block"><p>To advance open, rigorous, and independent research on the systems that move money, information, and risk across the global economy.</p></div>
  </section>
  <section class="bfi-section">
    <h2>Vision</h2>
    <div class="bfi-mission-block"><p>A world where the most important questions in financial systems are studied openly with the seriousness, transparency, and ambition they deserve.</p></div>
  </section>
  <section class="bfi-section">
    <h2>Structure</h2>
    <p><strong>Bowers Macro Lab</strong> — FX, rates, corridors, macro structure.<br/>
    <strong>Bowers Intelligence Lab</strong> — ML, model validation, research automation.<br/>
    <strong>Bowers Market Structure Lab</strong> — Settlement, stablecoins, payment architecture.<br/>
    <strong>BR3N Studio</strong> — Visual systems, dashboards, publication design.<br/>
    <strong>BR3N Macro Lab</strong> — Integrated research platform and data lake.</p>
  </section>
  <section class="bfi-section">
    <h2>Contact &amp; Attribution</h2>
    <p>Prepared by Brendan Bowers · Independent Research</p>
    <p>Research and risk-framing only. Not investment advice. No live trading.</p>
  </section>
</main>
"""


def build_bfi_pages(out_dir) -> Dict[str, Path]:
    """Write Bowers Frontier Institute parent-brand pages."""
    pages = {
        "index": out_dir / "index.html",
        "research": out_dir / "research.html",
        "labs": out_dir / "labs.html",
        "methodology": out_dir / "methodology.html",
        "dashboards": out_dir / "dashboards.html",
        "us_mexico_corridor": out_dir / "us-mexico-corridor.html",
        "about": out_dir / "about.html",
    }
    pages["index"].write_text(_bfi_shell(bfi_index_body(), active="home"), encoding="utf-8")
    pages["research"].write_text(
        _bfi_shell(
            bfi_research_hub_body(),
            active="research",
            title=f"Research — {ROOT_BRAND}",
            page_class="bfi-research-page",
        ),
        encoding="utf-8",
    )
    pages["labs"].write_text(
        _bfi_shell(bfi_labs_hub_body(), active="labs", title=f"Labs — {ROOT_BRAND}"),
        encoding="utf-8",
    )
    pages["methodology"].write_text(
        _bfi_shell(bfi_methodology_body(), active="methodology", title=f"Methodology — {ROOT_BRAND}"),
        encoding="utf-8",
    )
    pages["dashboards"].write_text(
        _bfi_shell(bfi_dashboards_body(), active="dashboards", title=f"Dashboards — {ROOT_BRAND}"),
        encoding="utf-8",
    )
    pages["us_mexico_corridor"].write_text(
        _bfi_shell(
            bfi_us_mexico_corridor_body(),
            active="dashboards",
            title=f"US/Mexico Corridor Dashboard — {ROOT_BRAND}",
            page_class="bfi-corridor-page",
            scripts=bfi_us_mexico_corridor_scripts(),
        ),
        encoding="utf-8",
    )
    pages["about"].write_text(
        _bfi_shell(bfi_about_body(), active="about", title=f"About — {ROOT_BRAND}"),
        encoding="utf-8",
    )
    return pages
