"""Shared utilities for the FX research terminal."""

from .config import load_terminal_config
from .paths import DATA_DIR, FEATURES_DIR, PROCESSED_DIR, RAW_DIR, REPORTS_DIR, TRADE_MEMOS_DIR

__all__ = [
    "load_terminal_config",
    "DATA_DIR",
    "RAW_DIR",
    "PROCESSED_DIR",
    "FEATURES_DIR",
    "REPORTS_DIR",
    "TRADE_MEMOS_DIR",
]
