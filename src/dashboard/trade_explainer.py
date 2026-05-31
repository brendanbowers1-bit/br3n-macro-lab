"""
Trade explanation engine — attribute signals to carry, macro, regime, and news factors.

TODO: Phase 7 — SHAP / feature-attribution or rule-based explainers.
"""

from __future__ import annotations

from typing import Any


def explain_trade(signal_row: dict[str, Any]) -> str:
    """
    Produce a human-readable explanation for a single model signal.

    Args:
        signal_row: Feature values and model outputs at decision time.

    Returns:
        Markdown explanation string.

    Raises:
        NotImplementedError: Phase 7 not yet implemented.
    """
    raise NotImplementedError("Trade explanation engine — Phase 7")
