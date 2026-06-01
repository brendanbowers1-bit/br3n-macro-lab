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
  --navy: #1e3a5f;
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
.bfi-logo-link {
  display: inline-flex;
  align-items: center;
  text-decoration: none;
  line-height: 0;
  flex-shrink: 0;
}
.bfi-logo-link:hover { opacity: 0.92; text-decoration: none; }
.header-logo,
.brand-logo {
  display: flex;
  align-items: center;
  overflow: visible !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
.logo,
.brand-logo,
.header-logo,
.hero-logo,
.footer-logo,
.logo-wrap,
.brand-wrap,
.bfi-logo-link,
.bfi-footer .footer-logo-wrap {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  overflow: visible !important;
}
.logo img,
.brand-logo img,
.header-logo img,
.hero-logo img,
.footer-logo img,
.bfi-logo-link img,
.bfi-footer .footer-logo img {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  object-fit: contain !important;
  overflow: visible !important;
  display: block;
}
.header-logo img,
.bfi-header .header-logo img,
.bfi-logo-link img {
  height: 50px;
  width: auto;
  max-width: min(720px, 52vw);
}
.hero-logo {
  margin: 0 auto 30px;
  width: min(580px, 86vw);
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
.hero-logo img {
  width: 100%;
  height: auto;
}
.bfi-footer .footer-logo img {
  height: 50px;
  width: auto;
  max-width: min(720px, 52vw);
  margin: 0 auto;
}
.bfi-footer .footer-logo-wrap {
  margin-bottom: 1rem;
}
.bfi-wordmark {
  font-family: var(--serif);
  font-size: 0.78rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--gold);
  font-weight: 600;
}
.bfi-wordmark span { color: var(--muted); font-weight: 500; letter-spacing: 0.12em; }
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
  color: #1e3a5f;
  border-color: rgba(30, 58, 95, 0.35);
  background: rgba(30, 58, 95, 0.06);
}
.bfi-hero {
  max-width: var(--wide);
  margin: 0 auto;
  padding: 4.5rem 1.5rem 3.5rem;
  animation: bfiFadeUp 0.9s ease both;
}
@keyframes bfiFadeUp {
  from { opacity: 0; transform: translateY(18px); }
  to { opacity: 1; transform: translateY(0); }
}
.bfi-hero h1 {
  font-family: var(--serif);
  font-size: clamp(2.2rem, 5.5vw, 3.75rem);
  font-weight: 600;
  letter-spacing: 0.02em;
  margin: 0 0 0.5rem;
  line-height: 1.08;
  color: var(--text);
}
.bfi-hero .core-line {
  font-family: var(--serif);
  font-size: clamp(1.15rem, 2.8vw, 1.65rem);
  color: var(--gold);
  margin: 0 0 0.65rem;
  letter-spacing: 0.03em;
}
.bfi-hero .tagline {
  font-size: 0.82rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0 0 2rem;
  font-weight: 500;
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
  padding: 1.5rem;
  text-align: center;
  font-size: 0.78rem;
  color: var(--muted);
  letter-spacing: 0.04em;
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
.bfi-parent-link {
  display: inline-block;
  margin-bottom: 1.25rem;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--gold);
}
@media (max-width: 850px) {
  .header-logo img,
  .brand-logo img,
  .bfi-header .header-logo img,
  .bfi-logo-link img {
    height: 38px;
    max-width: 70vw;
  }
  .hero-logo {
    width: min(430px, 86vw);
  }
  .bfi-footer .footer-logo img {
    height: 38px;
    max-width: 70vw;
  }
}
@media (max-width: 640px) {
  .bfi-hero { padding-top: 3rem; }
  .bfi-card-grid { grid-template-columns: 1fr; }
}
"""


def bfi_favicon_tags() -> str:
    return (
        f'<link rel="icon" href="{BFI_ICON}" type="image/svg+xml"/>'
        f'<link rel="apple-touch-icon" href="{BFI_ICON}"/>'
    )


def bfi_header_logo(*, inverse: bool = False) -> str:
    """Transparent horizontal mark on institute header (dark ink on off-white bar)."""
    src = BFI_LOGO_HORIZONTAL_INVERSE if inverse else BFI_LOGO_HORIZONTAL
    return (
        f'<a href="index.html" class="bfi-logo-link brand-logo logo-wrap header-logo">'
        f'<img src="{src}" alt="{html.escape(ROOT_BRAND)}" class="header-logo"/>'
        f"</a>"
    )


def bfi_hero_logo() -> str:
    return (
        f'<div class="hero-logo logo-wrap">'
        f'<img src="{BFI_LOGO_STACKED}" alt="{html.escape(ROOT_BRAND)}" class="hero-logo"/>'
        f"</div>"
    )


def bfi_footer_logo() -> str:
    return (
        f'<div class="footer-logo-wrap brand-wrap">'
        f'<img src="{BFI_LOGO_HORIZONTAL_INVERSE}" alt="{html.escape(ROOT_BRAND)}" '
        f'class="footer-logo"/>'
        f"</div>"
    )


def _nav_bfi(active: str) -> str:
    parts = ['<nav class="bfi-nav">']
    for href, label, key in BFI_NAV:
        cls = ' class="active"' if key == active else ""
        parts.append(f'<a href="{href}"{cls}>{html.escape(label)}</a>')
    parts.append("</nav>")
    return "\n".join(parts)


def _bfi_shell(body: str, *, active: str = "home", title: str | None = None) -> str:
    page_title = title or ROOT_BRAND
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
  <style>{_css_bfi()}</style>
</head>
<body class="bfi">
  <header class="bfi-header">
    <div class="bfi-header-inner">
      {bfi_header_logo()}
      {_nav_bfi(active)}
    </div>
  </header>
  {body}
  <footer class="bfi-footer">
    {bfi_footer_logo()}
    <p>{foot}</p>
    <p class="disc">Independent research institute. Not affiliated with any employer, bank, or payment company unless explicitly stated.</p>
  </footer>
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
<section class="bfi-hero">
  {bfi_hero_logo()}
  <h1>{html.escape(ROOT_BRAND)}</h1>
  <p class="core-line">{html.escape(CORE_LINE)}</p>
  <p class="tagline">{html.escape(TAGLINE)}</p>
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
  <div class="bfi-cta-row">
    <a href="research.html" class="bfi-cta primary">Read the Research</a>
    <a href="labs.html" class="bfi-cta secondary">Explore the Labs</a>
    <a href="methodology.html" class="bfi-cta secondary">View Methodology</a>
  </div>
</section>

<main class="bfi-main">
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


def bfi_research_hub_body() -> str:
    items = [
        ("usdmxn-research.html", "USD/MXN Regime Research", "Flagship FX regime summary and key statistics", "Macro Lab"),
        ("hedge-governance.html", "Hedge Governance Memo", "Forecast failure, hedge usefulness, and governance framing", "Macro Lab"),
        ("memo.html", "Full Research Note", "Methods, tables, limitations, and evidence", "Macro Lab"),
        ("global-fx-lab.html", "Global FX Research Lab", "Cross-border value and corridor economics", "Macro Lab"),
        ("value-survival-index.html", "Value Survival Index", "Purchasing power survival across borders", "Market Structure"),
        ("settlement-economics-lab.html", "Settlement Economics Lab", "Settlement drag, finality, liquidity burden", "Market Structure"),
        ("stablecoin-settlement-lab.html", "Stablecoin Settlement Lab", "Finality, window compression, digital runs", "Market Structure"),
        ("model-zoo.html", "Model Zoo", "Conditional forecastability and model comparison", "Intelligence"),
        ("open-source-ai.html", "Open Source FX AI Lab", "OSS model benchmarking and ML workflows", "Intelligence"),
        ("corridor.html", "Corridor Roadmap", "Multi-corridor payment research program", "Macro Lab"),
        ("unanswered-fx.html", "Unanswered FX Questions", "Frontier research agenda", "Institute"),
        ("history.html", "FX History & Foundations", "Three centuries of exchange-rate research", "Foundations"),
    ]
    lis = "".join(
        f'<li><a href="{html.escape(h, quote=True)}">{html.escape(t)}</a>'
        f'<span class="meta">{html.escape(m)}</span></li>'
        for h, t, d, m in items
    )
    return f"""
<section class="bfi-hero" style="padding-bottom:2rem;">
  <p class="tagline">Research Library</p>
  <h1>Research</h1>
  <p class="lead">Published memos, indices, model outputs, and frontier questions from {html.escape(ROOT_BRAND)} labs. All work is research-grade, documented, and subject to stated limitations.</p>
</section>
<main class="bfi-main">
  <ul class="bfi-hub-list">{lis}</ul>
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
        "about": out_dir / "about.html",
    }
    pages["index"].write_text(_bfi_shell(bfi_index_body(), active="home"), encoding="utf-8")
    pages["research"].write_text(
        _bfi_shell(bfi_research_hub_body(), active="research", title=f"Research — {ROOT_BRAND}"),
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
    pages["about"].write_text(
        _bfi_shell(bfi_about_body(), active="about", title=f"About — {ROOT_BRAND}"),
        encoding="utf-8",
    )
    return pages
