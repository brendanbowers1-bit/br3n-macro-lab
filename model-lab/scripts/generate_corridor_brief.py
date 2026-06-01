#!/usr/bin/env python3
"""Generate USD/MXN corridor intelligence brief."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    subprocess.run([sys.executable, str(ROOT / "scripts" / "run_corridor_intelligence.py")], check=True)
