import pytest

from scripts.run_all_quality_checks import run_all_checks


@pytest.mark.slow
def test_quality_runner_smoke():
    result = run_all_checks(skip_snapshot=True)
    assert "summary" in result
    assert result["summary"]["pass"] >= 0
