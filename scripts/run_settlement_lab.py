#!/usr/bin/env python3
"""Run settlement lab pipeline from repo root."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "settlement_lab"


def main() -> None:
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(LAB)}
    r = subprocess.run(
        [sys.executable, str(LAB / "scripts" / "reproduce_settlement_lab.py")],
        cwd=str(LAB),
        env=env,
    )
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
