"""Test full reproduction pipeline imports."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_smoke_script():
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "smoke_test_settlement_lab.py")],
        cwd=str(ROOT),
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr or r.stdout
