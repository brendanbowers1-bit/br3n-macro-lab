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

ROOT = Path(__file__).resolve().parents[1]
PUB_DIR = ROOT / "reports" / "publication"
VERTICALS_DIR = PUB_DIR / "verticals"

PUBLIC_SITE_BASE = "https://brendanbowers1-bit.github.io/br3n-macro-lab"

FX_LAB_TAGLINE = "Testing When Currency Markets Become Less Random"
FX_LAB_LOGO = "assets/fx_lab_logo.png"


def _css() -> str:
    return """
:root {
  --bg: #0c0f14;
  --surface: #141a24;
  --border: #243044;
  --text: #e8edf4;
  --muted: #8b9cb3;
  --accent: #3d8bfd;
  --accent-dim: #2563b8;
  --good: #34d399;
  --warn: #fbbf24;
  --font: "SF Pro Text", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
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
  line-height: 1.65;
  font-size: 17px;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
header {
  border-bottom: 1px solid var(--border);
  background: linear-gradient(180deg, #121824 0%, var(--bg) 100%);
  padding: 2.5rem 1.5rem 2rem;
}
.header-inner { max-width: var(--wide); margin: 0 auto; }
.brand {
  font-size: 0.8rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 0.5rem;
}
h1.title { font-size: 2rem; font-weight: 650; margin: 0 0 0.75rem; line-height: 1.2; }
.subtitle { color: var(--muted); font-size: 1.05rem; max-width: 42rem; }
nav.top {
  max-width: var(--wide);
  margin: 1.25rem auto 0;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}
nav.top a {
  padding: 0.45rem 0.9rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.9rem;
  background: var(--surface);
}
nav.top a.primary {
  background: var(--accent-dim);
  border-color: var(--accent);
  color: #fff;
}
main { max-width: var(--max); margin: 0 auto; padding: 2rem 1.5rem 4rem; }
main.wide { max-width: var(--wide); }
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  margin: 1.5rem 0;
}
.card h3 { margin-top: 0; font-size: 1rem; color: var(--accent); }
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin: 1.5rem 0;
}
.stat {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
}
.stat .label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }
.stat .value { font-size: 1.35rem; font-weight: 650; margin-top: 0.25rem; }
.stat .value.good { color: var(--good); }
.stat .value.warn { color: var(--warn); }
blockquote {
  margin: 1.5rem 0;
  padding: 1rem 1.25rem;
  border-left: 3px solid var(--accent);
  background: var(--surface);
  border-radius: 0 8px 8px 0;
  color: var(--muted);
  font-style: italic;
}
h2 { font-size: 1.35rem; margin: 2.25rem 0 1rem; padding-bottom: 0.35rem; border-bottom: 1px solid var(--border); }
h3 { font-size: 1.1rem; margin: 1.5rem 0 0.75rem; }
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
th { background: #1a2230; color: var(--muted); font-weight: 600; }
code, pre {
  font-family: var(--mono);
  font-size: 0.85rem;
  background: #0a0e13;
  border: 1px solid var(--border);
  border-radius: 6px;
}
code { padding: 0.15rem 0.4rem; }
pre { padding: 1rem; overflow-x: auto; }
pre code { border: none; padding: 0; background: none; }
footer {
  max-width: var(--wide);
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.85rem;
}
.disclaimer {
  background: #1a1510;
  border: 1px solid #4a3820;
  color: #d4a574;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.88rem;
  margin-top: 1rem;
}
/* Cover page */
body.cover-page header.hero-cover {
  border-bottom: none;
  padding: 4rem 1.5rem 3rem;
  text-align: center;
  background:
    radial-gradient(ellipse 80% 60% at 50% -10%, rgba(61, 139, 253, 0.18) 0%, transparent 55%),
    linear-gradient(180deg, #0e1420 0%, var(--bg) 100%);
}
.hero-cover .lab-title {
  font-size: clamp(2.2rem, 6vw, 3.75rem);
  font-weight: 700;
  letter-spacing: 0.12em;
  margin: 0 0 1rem;
  line-height: 1.1;
  background: linear-gradient(135deg, #e8edf4 0%, #8b9cb3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-cover .tagline {
  color: var(--muted);
  font-size: clamp(1rem, 2.5vw, 1.2rem);
  max-width: 40rem;
  margin: 0 auto 0.75rem;
  line-height: 1.5;
}
.hero-cover .author {
  color: var(--accent);
  font-size: 0.95rem;
  margin-bottom: 2rem;
}
.fx-lab-logo {
  display: block;
  max-width: min(520px, 92vw);
  width: 100%;
  height: auto;
  margin: 0 auto 1.25rem;
  border-radius: 12px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.45);
}
.fx-lab-logo-sm {
  display: block;
  max-width: 280px;
  width: 100%;
  height: auto;
  margin: 0 0 1rem;
  border-radius: 8px;
}
.cta-row {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 1.5rem;
}
.cta-row a {
  padding: 0.65rem 1.25rem;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  text-decoration: none;
}
.cta-row a.primary {
  background: var(--accent-dim);
  border: 1px solid var(--accent);
  color: #fff;
}
.cta-row a.secondary {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
}
.principle-box {
  background: linear-gradient(135deg, #141f33 0%, var(--surface) 100%);
  border: 1px solid var(--accent);
  border-radius: 12px;
  padding: 1.5rem 1.75rem;
  margin: 2rem 0;
  font-size: 1.05rem;
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
  border-radius: 12px;
  padding: 1.5rem;
  text-align: left;
  transition: border-color 0.15s ease;
}
.vertical-card:hover { border-color: var(--accent); }
.vertical-card .tag {
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.5rem;
}
.vertical-card h3 {
  margin: 0 0 0.5rem;
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
  padding: 0.55rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  color: #fff;
}
.vertical-card a.btn:hover { text-decoration: none; opacity: 0.92; }
.back-link {
  display: inline-block;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: var(--muted);
}
@media (max-width: 600px) {
  h1.title { font-size: 1.55rem; }
  body { font-size: 16px; }
  .hero-cover .lab-title { letter-spacing: 0.08em; }
}
"""


def _md_to_html(text: str) -> str:
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
                out.append("<table>")
                out.append("<thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in rows[0]) + "</tr></thead>")
                out.append("<tbody>")
                for row in rows[2:]:
                    out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in row) + "</tr>")
                out.append("</tbody></table>")
            continue

        if line.startswith("# "):
            out.append(f"<h1>{_inline(line[2:])}</h1>")
        elif line.startswith("## "):
            out.append(f"<h2>{_inline(line[3:])}</h2>")
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


def _inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s


def _nav_fx(active: str = "home") -> str:
    links = [
        ("index.html", "Home", "home"),
        ("fx-lab.html", "FX Lab", "fx"),
        ("research.html", "Research", "research"),
        ("corridor.html", "Corridor", "corridor"),
        ("fx_desk.html", "FX Desk", "fx_desk"),
        ("memo.html", "Memo", "memo"),
        ("ladder.html", "Ladder", "ladder"),
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
  <style>{_css()}</style>
</head>
<body>
  <header>
    <div class="header-inner">
      <img src="{FX_LAB_LOGO}" alt="{html.escape(LAB_NAME_DISPLAY)} FX Lab" class="fx-lab-logo-sm"/>
      <div class="brand">{html.escape(LAB_NAME_DISPLAY)} · FX LAB</div>
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


def _cover_shell(body: str) -> str:
    hero = f"""
<header class="hero-cover">
  <div class="header-inner">
    <img src="{FX_LAB_LOGO}" alt="{html.escape(LAB_NAME_DISPLAY)} FX Lab" class="fx-lab-logo"/>
    <p class="author">Prepared by Brendan Bowers</p>
    <div class="cta-row">
      <a href="fx-lab.html" class="primary">FX Lab Overview</a>
      <a href="research.html" class="secondary">USD/MXN Research</a>
      <a href="corridor.html" class="secondary">Corridor Roadmap</a>
      <a href="fx_desk.html" class="secondary">FX Desk Framework</a>
    </div>
    {_nav_fx("home")}
  </div>
</header>"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <meta name="description" content="{html.escape(LAB_NAME)} FX Lab — conditional forecastability research"/>
  <title>{html.escape(LAB_NAME_DISPLAY)} — FX Lab</title>
  <style>{_css()}</style>
</head>
<body class="cover-page">
  {hero}
  <main class="cover-main wide">
    {body}
  </main>
  <footer>
    <p>{html.escape(LAB_NAME)} · FX Lab · Prepared by Brendan Bowers · {datetime.now():%Y-%m-%d}</p>
    <div class="disclaimer">Research and risk-framing only. Not investment advice. No live trading.</div>
  </footer>
</body>
</html>"""


def _cover_body_from_md(text: str) -> str:
    """Convert LAB_COVER.md, skipping title block (rendered in hero)."""
    lines = text.splitlines()
    start = 0
    for i, line in enumerate(lines):
        if line.startswith("## "):
            start = i
            break
    return _md_to_html("\n".join(lines[start:]))


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


def build_site(out_dir: Path | None = None) -> Dict[str, Path]:
    out_dir = out_dir or PUB_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    one_pager = (out_dir / "ONE_PAGER.md").read_text(encoding="utf-8") if (out_dir / "ONE_PAGER.md").exists() else ""
    memo = (out_dir / "FX_REGIME_RESEARCH_NOTE.md").read_text(encoding="utf-8") if (out_dir / "FX_REGIME_RESEARCH_NOTE.md").exists() else ""
    cover_md = (out_dir / "LAB_COVER.md").read_text(encoding="utf-8") if (out_dir / "LAB_COVER.md").exists() else ""

    fx_cover = _read_md(out_dir / "FX_LAB_COVER_PAGE.md") or cover_md

    # Home — FX Lab only (no links to other verticals)
    cover_path = out_dir / "index.html"
    cover_path.write_text(_cover_shell(_cover_body_from_md(fx_cover)), encoding="utf-8")

    fx_lab_path = out_dir / "fx-lab.html"
    fx_lab_md = _read_md(VERTICALS_DIR / "FX_LAB_LANDING.md")
    fx_lab_path.write_text(
        _shell(
            "FX Lab",
            _md_to_html(fx_lab_md),
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
    <li><a href="ladder.html"><strong>Evidence ladder</strong></a> — six-level checklist</li>
    <li><a href="index.html"><strong>FX Lab home</strong></a></li>
  </ul>
</div>
{_md_to_html(one_pager)}
"""
    research_path = out_dir / "research.html"
    research_path.write_text(
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
            subtitle="Six-level evidence framework · Research only",
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

    return {
        "index": cover_path,
        "fx_lab": fx_lab_path,
        "research": research_path,
        "memo": memo_path,
        "ladder": ladder_path,
        "corridor": corridor_path,
        "fx_desk": fx_desk_path,
    }
