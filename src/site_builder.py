"""
Build a styled static HTML site from publication markdown.
"""

from __future__ import annotations

import html
import re
from datetime import datetime
from pathlib import Path
from typing import Dict

from . import LAB_NAME

ROOT = Path(__file__).resolve().parents[1]
PUB_DIR = ROOT / "reports" / "publication"


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
@media (max-width: 600px) {
  h1.title { font-size: 1.55rem; }
  body { font-size: 16px; }
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
        elif line.startswith("> "):
            out.append(f"<blockquote><p>{_inline(line[2:])}</p></blockquote>")
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


def _shell(title: str, body: str, *, wide: bool = False, nav_home: bool = True) -> str:
    nav = ""
    if nav_home:
        nav = """
<nav class="top">
  <a href="index.html" class="primary">One-pager</a>
  <a href="memo.html">Full research note</a>
  <a href="ladder.html">Ladder summary</a>
</nav>"""
    main_class = "wide" if wide else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{html.escape(title)} — {LAB_NAME}</title>
  <style>{_css()}</style>
</head>
<body>
  <header>
    <div class="header-inner">
      <div class="brand">{html.escape(LAB_NAME)}</div>
      <h1 class="title">{html.escape(title)}</h1>
      <p class="subtitle">USD/MXN regime research · Research only · Not investment advice</p>
      {nav}
    </div>
  </header>
  <main class="{main_class}">
    {body}
  </main>
  <footer>
    <p>{html.escape(LAB_NAME)} · Generated {datetime.now():%Y-%m-%d}</p>
    <div class="disclaimer">This site is for research and education only. It is not investment advice, a trading recommendation, or a substitute for professional judgment.</div>
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


def build_site(out_dir: Path | None = None) -> Dict[str, Path]:
    out_dir = out_dir or PUB_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    one_pager = (out_dir / "ONE_PAGER.md").read_text(encoding="utf-8") if (out_dir / "ONE_PAGER.md").exists() else ""
    memo = (out_dir / "FX_REGIME_RESEARCH_NOTE.md").read_text(encoding="utf-8") if (out_dir / "FX_REGIME_RESEARCH_NOTE.md").exists() else ""

    # Landing page: hero + stats + one-pager body
    landing_body = f"""
{_landing_stats()}
<div class="card">
  <h3>Start here</h3>
  <p>Three ways to read this work — pick your depth.</p>
  <ul>
    <li><strong>This page</strong> — 2-minute summary</li>
    <li><a href="memo.html"><strong>Full research note</strong></a> — methods, tables, limitations (~5 min)</li>
    <li><a href="ladder.html"><strong>Ladder summary</strong></a> — six-level evidence checklist</li>
  </ul>
</div>
{_md_to_html(one_pager)}
"""
    index_path = out_dir / "index.html"
    index_path.write_text(_shell("USD/MXN Regime Research", landing_body), encoding="utf-8")

    memo_body = _md_to_html(memo)
    memo_path = out_dir / "memo.html"
    memo_path.write_text(_shell("Full Research Note", memo_body, wide=True), encoding="utf-8")

    ladder_md = (ROOT / "reports/research_ladder/RESEARCH_LADDER.md").read_text(encoding="utf-8") if (ROOT / "reports/research_ladder/RESEARCH_LADDER.md").exists() else "_Run the research ladder first._"
    ladder_path = out_dir / "ladder.html"
    ladder_path.write_text(_shell("Research Ladder", _md_to_html(ladder_md), wide=True), encoding="utf-8")

    return {"index": index_path, "memo": memo_path, "ladder": ladder_path}
