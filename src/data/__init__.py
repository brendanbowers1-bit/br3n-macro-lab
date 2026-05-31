"""
FX research terminal data layer.

Wraps existing src.data_loader and src.macro_loader; adds mock generators
and unified multi-pair ingestion. Does not replace legacy flat modules.
"""

from .constants import CORE_FX_PAIRS, TERMINAL_CORRIDORS, pair_label
from .market import load_pair_spot, load_all_core_pairs
from .mock import generate_mock_market_panel, generate_mock_macro_panel
from .pipeline import build_terminal_data_bundle

__all__ = [
    "CORE_FX_PAIRS",
    "TERMINAL_CORRIDORS",
    "pair_label",
    "load_pair_spot",
    "load_all_core_pairs",
    "generate_mock_market_panel",
    "generate_mock_macro_panel",
    "build_terminal_data_bundle",
]
