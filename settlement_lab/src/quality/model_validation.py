"""Settlement lab model validation wrapper."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from src.quality.model_validation import run_model_validation  # noqa: E402,F401
