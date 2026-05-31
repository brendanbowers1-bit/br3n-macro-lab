import json
from pathlib import Path

from src.audit.time_tracking import TimeTracker


def test_time_tracker_start_stop():
    root = Path(__file__).resolve().parents[1]
    tt = TimeTracker(root)
    if tt.status().get("active"):
        tt.stop(notes="cleanup previous session")
    sid = tt.start("pytest time tracker test")["session_id"]
    assert sid
    assert tt.status().get("active") is True
    entry = tt.stop(notes="pytest")
    assert entry["duration_minutes"] >= 0
    assert (root / "audit/project_metrics/time_log.csv").exists()
