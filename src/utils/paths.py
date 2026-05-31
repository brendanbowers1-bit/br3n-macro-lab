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
FIGURES_DIR = REPORTS_DIR / "figures"
TABLES_DIR = REPORTS_DIR / "tables"
MEMOS_DIR = REPORTS_DIR / "memos"
WORKING_PAPER_DIR = REPORTS_DIR / "working_paper"
NOTEBOOKS_DIR = ROOT / "notebooks"

for _d in (RAW_DIR, PROCESSED_DIR, FEATURES_DIR, TRADE_MEMOS_DIR, FIGURES_DIR, TABLES_DIR, MEMOS_DIR, WORKING_PAPER_DIR):
    _d.mkdir(parents=True, exist_ok=True)
