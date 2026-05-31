from pathlib import Path

from src.audit.metrics import count_project_lines


def test_count_project_lines_returns_totals():
    root = Path(__file__).resolve().parents[1]
    m = count_project_lines(root)
    assert m["totals"]["files"] > 0
    assert m["totals"]["code_lines"] >= 0
    assert "code" in m["by_category"]
