#!/usr/bin/env python3
"""Estimate active project time from git commit timestamps (estimate only)."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MAX_GAP_HOURS = 4
SESSION_CAP_HOURS = 8


def main() -> None:
    out_dir = ROOT / "audit" / "project_metrics"
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        r = subprocess.run(
            ["git", "log", "--format=%ci"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        times = [datetime.fromisoformat(ln.strip()) for ln in r.stdout.splitlines() if ln.strip()]
    except Exception as exc:
        md = f"# Estimated Time Report\n\nGit unavailable: {exc}\n"
        (out_dir / "time_report_estimated.md").write_text(md)
        print(md)
        return

    if not times:
        print("No git commits found.")
        return

    times = sorted(times)
    total_minutes = 0
    session_start = times[0]
    prev = times[0]
    sessions = 1

    for t in times[1:]:
        gap = (t - prev).total_seconds() / 3600
        if gap > MAX_GAP_HOURS:
            elapsed = min((prev - session_start).total_seconds() / 60 + 30, SESSION_CAP_HOURS * 60)
            total_minutes += elapsed
            session_start = t
            sessions += 1
        prev = t
    total_minutes += min((prev - session_start).total_seconds() / 60 + 30, SESSION_CAP_HOURS * 60)

    import pandas as pd
    df = pd.DataFrame([{
        "estimate_type": "git_commit_spacing",
        "sessions_estimated": sessions,
        "total_minutes_estimated": round(total_minutes, 1),
        "first_commit": times[0].isoformat(),
        "last_commit": times[-1].isoformat(),
        "note": "ESTIMATE ONLY — not exact time tracking",
    }])
    df.to_csv(out_dir / "time_report_estimated.csv", index=False)

    md = f"""# Estimated Time From Git (Estimate Only)

> Historical time before the time tracker was installed cannot be measured exactly.
> This is an **estimate** based on git commit spacing (max gap {MAX_GAP_HOURS}h).

- **Estimated sessions:** {sessions}
- **Estimated minutes:** {total_minutes:.0f}
- **First commit:** {times[0].date()}
- **Last commit:** {times[-1].date()}
"""
    (out_dir / "time_report_estimated.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
