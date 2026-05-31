"""Path constants for BR3N Settlement Economics Lab."""

from __future__ import annotations

from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = LAB_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FEATURES_DIR = DATA_DIR / "features"
OUTPUTS_DIR = DATA_DIR / "outputs"
METADATA_DIR = DATA_DIR / "metadata"
REPORTS_DIR = LAB_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
TABLES_DIR = REPORTS_DIR / "tables"

RAW_SUBDIRS = [
    "bis_cpmi", "world_bank", "imf", "fred", "federal_reserve",
    "ecb", "swift", "company_public_reports", "manual",
]
