"""Git helpers for audit trail."""

from __future__ import annotations

import subprocess
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def git_available(cwd: Path | None = None) -> bool:
    cwd = cwd or project_root()
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        return r.returncode == 0
    except Exception:
        return False


def git_branch(cwd: Path | None = None) -> str:
    cwd = cwd or project_root()
    if not git_available(cwd):
        return "unknown"
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return r.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def git_commit_hash(cwd: Path | None = None) -> str:
    cwd = cwd or project_root()
    if not git_available(cwd):
        return "unavailable"
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return r.stdout.strip()
    except Exception:
        return "unavailable"


def git_diff_stats(cwd: Path | None = None) -> dict:
    cwd = cwd or project_root()
    if not git_available(cwd):
        return {"lines_added": 0, "lines_removed": 0, "files_changed": 0}
    try:
        r = subprocess.run(
            ["git", "diff", "--numstat", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        added = removed = files = 0
        for line in r.stdout.strip().splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                a, d = parts[0], parts[1]
                if a.isdigit():
                    added += int(a)
                if d.isdigit():
                    removed += int(d)
                files += 1
        return {"lines_added": added, "lines_removed": removed, "files_changed": files}
    except Exception:
        return {"lines_added": 0, "lines_removed": 0, "files_changed": 0}
