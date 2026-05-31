from pathlib import Path

from src.audit.snapshots import create_snapshot, list_snapshots


def test_create_and_list_snapshot(tmp_path):
    root = Path(__file__).resolve().parents[1]
    snap = create_snapshot(reason="pytest snapshot test", created_by="pytest", root=root)
    assert snap.exists()
    assert snap.suffix == ".zip"
    snaps = list_snapshots(root=root)
    assert any(s["path"].endswith(snap.name) for s in snaps)
