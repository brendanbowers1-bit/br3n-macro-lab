"""Project line-count and metrics."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from src.audit.git_utils import git_diff_stats, project_root

CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".sql"}
DOC_EXTS = {".md", ".rst", ".txt"}
CONFIG_EXTS = {".yaml", ".yml", ".json", ".toml", ".ini"}
NOTEBOOK_EXTS = {".ipynb"}

EXCLUDE_DIRS = {
    ".venv", "__pycache__", ".git", "node_modules", "_snapshots",
    ".pytest_cache", ".mypy_cache", ".ruff_cache",
}
EXCLUDE_PATH_PREFIXES = (
    "data/raw/", "data/runs/", "data/processed/", "data/outputs/",
    "research_snapshots/", "settlement_lab/data/raw/", "settlement_lab/data/processed/",
    "settlement_lab/data/outputs/",
)


def _iter_files(root: Path):
    for fp in root.rglob("*"):
        if not fp.is_file():
            continue
        rel = str(fp.relative_to(root))
        if any(part in EXCLUDE_DIRS for part in fp.parts):
            continue
        if any(rel.startswith(p) for p in EXCLUDE_PATH_PREFIXES):
            continue
        yield fp, rel


def _classify(ext: str, rel: str) -> str:
    if ext in CODE_EXTS:
        if "test" in rel.lower() or rel.startswith("tests/"):
            return "test_code"
        return "code"
    if ext in DOC_EXTS:
        return "documentation"
    if ext in CONFIG_EXTS:
        return "config"
    if ext in NOTEBOOK_EXTS:
        return "notebook"
    if ext in {".html", ".css"}:
        return "generated_report"
    return "other"


def count_project_lines(root: Path | None = None) -> dict:
    root = root or project_root()
    per_file = []
    totals = defaultdict(int)
    by_category = defaultdict(lambda: {"files": 0, "lines": 0, "code": 0, "comments": 0, "blank": 0})

    for fp, rel in _iter_files(root):
        ext = fp.suffix.lower()
        cat = _classify(ext, rel)
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        lines = text.splitlines()
        n = len(lines)
        blank = sum(1 for ln in lines if not ln.strip())
        comments = 0
        if ext == ".py":
            comments = sum(1 for ln in lines if ln.strip().startswith("#"))
        code_lines = n - blank - comments
        per_file.append({
            "path": rel,
            "category": cat,
            "extension": ext,
            "total_lines": n,
            "code_lines": code_lines,
            "comment_lines": comments,
            "blank_lines": blank,
        })
        totals["files"] += 1
        totals["total_lines"] += n
        totals["code_lines"] += code_lines
        totals["comment_lines"] += comments
        totals["blank_lines"] += blank
        by_category[cat]["files"] += 1
        by_category[cat]["lines"] += n
        by_category[cat]["code"] += code_lines
        by_category[cat]["comments"] += comments
        by_category[cat]["blank"] += blank

    test_lines = by_category["test_code"]["code"]
    code_lines = totals["code_lines"]
    ratio = round(test_lines / code_lines, 4) if code_lines else 0.0
    largest = sorted(per_file, key=lambda x: x["total_lines"], reverse=True)[:25]

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "totals": dict(totals),
        "by_category": dict(by_category),
        "test_to_code_ratio": ratio,
        "largest_files": largest,
        "per_file": per_file,
        "git_diff_since_head": git_diff_stats(root),
    }


def write_metrics_reports(metrics: dict, root: Path | None = None) -> dict[str, Path]:
    root = root or project_root()
    out_dir = root / "audit" / "project_metrics"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "project_metrics.json"
    json_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    import pandas as pd

    csv_path = out_dir / "line_count_report.csv"
    pd.DataFrame(metrics["per_file"]).to_csv(csv_path, index=False)

    t = metrics["totals"]
    md = f"""# Project Line Count Report

**Generated:** {metrics['timestamp']}

## Totals

| Metric | Count |
|--------|------:|
| Files | {t.get('files', 0)} |
| Total lines | {t.get('total_lines', 0)} |
| Code lines | {t.get('code_lines', 0)} |
| Comment lines | {t.get('comment_lines', 0)} |
| Blank lines | {t.get('blank_lines', 0)} |
| Test-to-code ratio | {metrics.get('test_to_code_ratio', 0)} |

## By category

"""
    for cat, vals in metrics.get("by_category", {}).items():
        md += f"- **{cat}**: {vals['files']} files, {vals['lines']} lines ({vals['code']} code)\n"

    md += "\n## Largest files\n\n"
    for item in metrics.get("largest_files", [])[:15]:
        md += f"- `{item['path']}` — {item['total_lines']} lines\n"

    md_path = out_dir / "line_count_report.md"
    md_path.write_text(md, encoding="utf-8")
    return {"json": json_path, "csv": csv_path, "md": md_path}
