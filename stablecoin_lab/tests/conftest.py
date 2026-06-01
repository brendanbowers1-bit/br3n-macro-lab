"""Ensure stablecoin_lab tests import stablecoin_lab/src, not root src."""

import sys
from pathlib import Path

SCL_ROOT = Path(__file__).resolve().parents[1]
PARENT_ROOT = SCL_ROOT.parent
if sys.path[0:1] != [str(SCL_ROOT)]:
    sys.path.insert(0, str(SCL_ROOT))
sys.path = [p for p in sys.path if Path(p).resolve() != PARENT_ROOT.resolve() or p == str(SCL_ROOT)]
