"""Settlement lab data validation — delegates to project-wide validator."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.quality.data_validation import run_data_validation  # noqa: E402

__all__ = ["run_data_validation"]
