"""Path constants for the FX research terminal."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FEATURES_DIR = DATA_DIR / "features"
OUTPUTS_DIR = DATA_DIR / "outputs"
REPORTS_DIR = ROOT / "reports"
TRADE_MEMOS_DIR = REPORTS_DIR / "trade_memos"
NOTEBOOKS_DIR = ROOT / "notebooks"

for _d in (RAW_DIR, PROCESSED_DIR, FEATURES_DIR, TRADE_MEMOS_DIR):
    _d.mkdir(parents=True, exist_ok=True)
