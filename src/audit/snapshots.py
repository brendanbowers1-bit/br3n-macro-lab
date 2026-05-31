"""Project snapshot create / list / restore."""

from __future__ import annotations

import csv
import fnmatch
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from src.audit.git_utils import git_branch, git_commit_hash, project_root

SNAPSHOT_DIR_NAME = "_snapshots"
LOG_REL = Path("audit/change_logs/snapshot_log.csv")
LOG_COLUMNS = [
    "snapshot_id", "timestamp", "git_branch", "git_commit_hash_if_available",
    "snapshot_path", "file_count", "total_size_mb", "reason", "created_by",
]


def _load_ignore_patterns(root: Path) -> list[str]:
    ignore_file = root / ".snapshotignore"
    patterns: list[str] = []
    if ignore_file.exists():
        for line in ignore_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line)
    return patterns


def _should_exclude(rel: str, patterns: list[str]) -> bool:
    parts = Path(rel).parts
    for pat in patterns:
        if pat.endswith("/"):
            if any(fnmatch.fnmatch(p + "/", pat) for p in parts):
                return True
        if fnmatch.fnmatch(rel, pat) or any(fnmatch.fnmatch(p, pat.rstrip("/")) for p in parts):
            return True
    return False


def _include_file(rel: str) -> bool:
    p = Path(rel)
    if p.suffix.lower() in {".py", ".md", ".yaml", ".yml", ".json", ".toml", ".ini", ".sh", ".txt", ".html", ".css", ".js", ".ts", ".tsx", ".sql", ".ipynb", ".csv"}:
        return True
    name = p.name.lower()
    return name in {"makefile", "dockerfile", "requirements.txt", "readme", ".snapshotignore", ".gitignore", ".pre-commit-config.yaml"}


def create_snapshot(reason: str = "manual", created_by: str = "system", root: Path | None = None) -> Path:
    root = root or project_root()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    snapshot_id = f"{ts}_project_snapshot"
    snap_dir = root / SNAPSHOT_DIR_NAME
    snap_dir.mkdir(parents=True, exist_ok=True)
    zip_path = snap_dir / f"{snapshot_id}.zip"

    patterns = _load_ignore_patterns(root)
    include_roots = [
        "src", "scripts", "tests", "settlement_lab", "reports", "config.yaml",
        "requirements.txt", "settlement_lab/requirements.txt", "README.md",
        "REPLICATION.md", "VALUE_SURVIVAL_INDEX.md", "CHANGELOG_RESEARCH.md",
        "Makefile", "pytest.ini", ".snapshotignore", ".gitignore",
        ".pre-commit-config.yaml", "audit/change_logs",
    ]

    file_count = 0
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in include_roots:
            path = root / item
            if path.is_file():
                rel = item
                if not _should_exclude(rel, patterns):
                    zf.write(path, rel)
                    file_count += 1
            elif path.is_dir():
                for fp in path.rglob("*"):
                    if not fp.is_file():
                        continue
                    rel = str(fp.relative_to(root))
                    if _should_exclude(rel, patterns):
                        continue
                    if not _include_file(rel) and fp.suffix not in (".md",):
                        continue
                    zf.write(fp, rel)
                    file_count += 1

    size_mb = round(zip_path.stat().st_size / (1024 * 1024), 3)
    log_path = root / LOG_REL
    log_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "snapshot_id": snapshot_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_branch": git_branch(root),
        "git_commit_hash_if_available": git_commit_hash(root),
        "snapshot_path": str(zip_path.relative_to(root)),
        "file_count": file_count,
        "total_size_mb": size_mb,
        "reason": reason,
        "created_by": created_by,
    }
    write_header = not log_path.exists()
    with open(log_path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LOG_COLUMNS)
        if write_header:
            w.writeheader()
        w.writerow(row)
    return zip_path


def list_snapshots(root: Path | None = None) -> list[dict]:
    root = root or project_root()
    snap_dir = root / SNAPSHOT_DIR_NAME
    if not snap_dir.exists():
        return []
    rows = []
    for zp in sorted(snap_dir.glob("*_project_snapshot.zip"), reverse=True):
        st = zp.stat()
        rows.append({
            "snapshot_id": zp.stem,
            "path": str(zp.relative_to(root)),
            "size_mb": round(st.st_size / (1024 * 1024), 3),
            "modified": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
        })
    return rows


def restore_snapshot(snapshot: str | Path, target: str | Path, root: Path | None = None) -> Path:
    root = root or project_root()
    snap_path = Path(snapshot)
    if not snap_path.is_absolute():
        snap_path = root / snap_path
    if not snap_path.exists():
        alt = root / SNAPSHOT_DIR_NAME / snap_path.name
        if alt.exists():
            snap_path = alt
        else:
            raise FileNotFoundError(f"Snapshot not found: {snapshot}")

    target_path = Path(target)
    if not target_path.is_absolute():
        target_path = root / target_path
    target_path.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(snap_path, "r") as zf:
        zf.extractall(target_path)
    return target_path
