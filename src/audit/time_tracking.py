"""Project time tracking."""

from __future__ import annotations

import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from src.audit.git_utils import git_branch, git_commit_hash, project_root

SESSION_FILE = ".time_tracker_session.json"
LOG_REL = Path("audit/project_metrics/time_log.csv")
LOG_COLUMNS = [
    "session_id", "start_time", "stop_time", "duration_minutes",
    "task", "git_branch", "git_commit_hash_if_available", "notes",
]


class TimeTracker:
    def __init__(self, root: Path | None = None):
        self.root = root or project_root()
        self.session_path = self.root / SESSION_FILE
        self.log_path = self.root / LOG_REL

    def _load_session(self) -> dict | None:
        if not self.session_path.exists():
            return None
        return json.loads(self.session_path.read_text())

    def _save_session(self, data: dict | None) -> None:
        if data is None:
            if self.session_path.exists():
                self.session_path.unlink()
            return
        self.session_path.write_text(json.dumps(data, indent=2))

    def start(self, task: str, notes: str = "") -> dict:
        if self._load_session():
            raise RuntimeError("Session already active. Run stop first.")
        session = {
            "session_id": str(uuid.uuid4())[:8],
            "start_time": datetime.now(timezone.utc).isoformat(),
            "task": task,
            "notes": notes,
            "git_branch": git_branch(self.root),
            "git_commit_hash_if_available": git_commit_hash(self.root),
        }
        self._save_session(session)
        return session

    def stop(self, notes: str = "") -> dict:
        session = self._load_session()
        if not session:
            raise RuntimeError("No active session.")
        stop_time = datetime.now(timezone.utc)
        start = datetime.fromisoformat(session["start_time"])
        duration = round((stop_time - start).total_seconds() / 60.0, 2)
        row = {
            "session_id": session["session_id"],
            "start_time": session["start_time"],
            "stop_time": stop_time.isoformat(),
            "duration_minutes": duration,
            "task": session["task"],
            "git_branch": session.get("git_branch", git_branch(self.root)),
            "git_commit_hash_if_available": session.get("git_commit_hash_if_available", git_commit_hash(self.root)),
            "notes": notes or session.get("notes", ""),
        }
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        write_header = not self.log_path.exists()
        with open(self.log_path, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=LOG_COLUMNS)
            if write_header:
                w.writeheader()
            w.writerow(row)
        self._save_session(None)
        return row

    def status(self) -> dict:
        session = self._load_session()
        if not session:
            return {"active": False}
        start = datetime.fromisoformat(session["start_time"])
        elapsed = round((datetime.now(timezone.utc) - start).total_seconds() / 60.0, 2)
        return {"active": True, "elapsed_minutes": elapsed, **session}

    def report(self) -> Path:
        out = self.root / "audit" / "project_metrics" / "time_report.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Time Tracking Report",
            "",
            "> Historical time before this tracker was installed cannot be measured exactly.",
            "> This report starts from installation date. See `time_report_estimated.csv` for git-based estimates.",
            "",
        ]
        if self.log_path.exists():
            import pandas as pd
            df = pd.read_csv(self.log_path)
            total = df["duration_minutes"].sum()
            lines.append(f"**Tracked sessions:** {len(df)}")
            lines.append(f"**Total tracked minutes:** {total:.1f}")
            lines.append("")
            lines.append("| Task | Minutes |")
            lines.append("|------|--------:|")
            for task, mins in df.groupby("task")["duration_minutes"].sum().items():
                lines.append(f"| {task} | {mins:.1f} |")
        else:
            lines.append("No tracked sessions yet.")
        out.write_text("\n".join(lines), encoding="utf-8")
        return out
