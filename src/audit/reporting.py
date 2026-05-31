"""Write audit reports in md/json/csv."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def write_report_bundle(
    rows: list[dict],
    out_dir: Path,
    basename: str,
    title: str,
    summary: dict | None = None,
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows) if rows else pd.DataFrame()
    csv_path = out_dir / f"{basename}.csv"
    json_path = out_dir / f"{basename}.json"
    md_path = out_dir / f"{basename}.md"

    if not df.empty:
        df.to_csv(csv_path, index=False)
    else:
        csv_path.write_text("status\nSKIPPED\n")

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "title": title,
        "summary": summary or {},
        "rows": rows,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = [f"# {title}", "", f"**Generated:** {payload['timestamp']}", ""]
    if summary:
        md.append("## Summary")
        md.append("")
        for k, v in summary.items():
            md.append(f"- **{k}**: {v}")
        md.append("")
    if not df.empty:
        md.append("## Results")
        md.append("")
        cols = list(df.columns)
        md.append("| " + " | ".join(str(c) for c in cols) + " |")
        md.append("| " + " | ".join("---" for _ in cols) + " |")
        for _, row in df.head(200).iterrows():
            md.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
        if len(df) > 200:
            md.append(f"\n_… {len(df) - 200} more rows (see CSV)._")
    else:
        md.append("_No results._")
    md_path.write_text("\n".join(md), encoding="utf-8")
    return {"csv": csv_path, "json": json_path, "md": md_path}
