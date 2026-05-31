"""Ensure settlement_lab tests import settlement_lab/src, not root src."""

import sys
from pathlib import Path

SL_ROOT = Path(__file__).resolve().parents[1]
if str(SL_ROOT) not in sys.path:
    sys.path.insert(0, str(SL_ROOT))
