#!/usr/bin/env python3
"""Append structured change log entries."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.audit.git_utils import git_branch, git_commit_hash, project_root

LOG_CSV = Path("audit/change_logs/change_log.csv")
CHANGELOG_MD = Path("CHANGELOG_RESEARCH.md")
COLUMNS = [
    "timestamp", "change_type", "files_changed", "lines_added", "lines_removed",
    "reason", "model_or_dataset_affected", "validation_status", "snapshot_id",
    "git_commit_hash_if_available", "notes",
]


def _git_diff_stats(root: Path) -> tuple[str, int, int]:
    try:
        r = subprocess.run(
            ["git", "diff", "--stat", "HEAD"],
            cwd=root, capture_output=True, text=True, check=False,
        )
        if r.returncode != 0:
            r = subprocess.run(
                ["git", "diff", "--stat"],
                cwd=root, capture_output=True, text=True, check=False,
            )
        stat = r.stdout.strip()
        added = removed = 0
        for line in stat.splitlines():
            if "|" in line and "file" not in line.lower():
                parts = line.split("|")[-1].strip().split()
                if len(parts) >= 2 and parts[1].startswith("+"):
                    try:
                        added += int(parts[1].replace("+", ""))
                        removed += int(parts[2].replace("-", ""))
                    except ValueError:
                        pass
        files = str(len([ln for ln in stat.splitlines() if "|" in ln and "file" not in ln.lower()]))
        return files, added, removed
    except Exception:
        return "unknown", 0, 0


def append_entry(
    change_type: str,
    reason: str,
    model_or_dataset: str = "",
    validation_status: str = "pending",
    snapshot_id: str = "",
    notes: str = "",
    root: Path | None = None,
) -> dict:
    root = root or project_root()
    log_path = root / LOG_CSV
    log_path.parent.mkdir(parents=True, exist_ok=True)

    files_changed, lines_added, lines_removed = _git_diff_stats(root)
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "change_type": change_type,
        "files_changed": files_changed,
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "reason": reason,
        "model_or_dataset_affected": model_or_dataset,
        "validation_status": validation_status,
        "snapshot_id": snapshot_id,
        "git_commit_hash_if_available": git_commit_hash(root),
        "notes": notes,
    }

    write_header = not log_path.exists() or log_path.stat().st_size == 0
    with log_path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        if write_header:
            w.writeheader()
        w.writerow(row)

    md_path = root / CHANGELOG_MD
    line = f"- **{row['timestamp'][:19]}** [{change_type}] {reason} ({files_changed} files, +{lines_added}/-{lines_removed})\n"
    if md_path.exists():
        content = md_path.read_text(encoding="utf-8")
        if "## Entries" in content:
            content = content.replace("## Entries\n", f"## Entries\n\n{line}")
        else:
            content += f"\n## Entries\n\n{line}"
    else:
        content = f"# Research Change Log\n\n## Entries\n\n{line}"
    md_path.write_text(content, encoding="utf-8")
    return row


def main() -> int:
    p = argparse.ArgumentParser(description="Update research change log")
    p.add_argument("--type", required=True, help="Change type (e.g. model validation)")
    p.add_argument("--reason", required=True, help="Reason for change")
    p.add_argument("--model", default="", help="Model or dataset affected")
    p.add_argument("--validation", default="pending", help="Validation status")
    p.add_argument("--snapshot-id", default="", help="Related snapshot id")
    p.add_argument("--notes", default="", help="Additional notes")
    args = p.parse_args()
    row = append_entry(
        args.type, args.reason, args.model, args.validation, args.snapshot_id, args.notes,
    )
    print(f"Logged change: {row['timestamp']} — {args.reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
