from pathlib import Path

from src.quality.model_validation import run_model_validation


def test_run_model_validation_smoke():
    root = Path(__file__).resolve().parents[1]
    res = run_model_validation(root)
    assert "summary" in res
    assert isinstance(res["rows"], list)
