"""
Side-by-side model comparison for Bowers Frontier walk-forward benchmarks.

TODO: Phase 6 — wire to src/backtesting/ and model registry outputs.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def compare_models(scorecards: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Merge per-model OOS scorecards under the Bowers Frontier benchmarking standard.

    Args:
        scorecards: model_id -> metrics DataFrame.

    Returns:
        Unified comparison table.

    Raises:
        NotImplementedError: Phase 6 dashboard not yet implemented.
    """
    raise NotImplementedError("Model comparison dashboard — Phase 6")


def summary_markdown(comparison: pd.DataFrame) -> str:
    """Render comparison table as markdown for publication."""
    raise NotImplementedError("Model comparison dashboard — Phase 6")
