"""
Walk-forward validation for open-source model benchmarks.

TODO: Unify with src/model_walk_forward.py and research ladder splits.
Research-only — no look-ahead bias.
"""


def run_walk_forward(model_fn, data, splits: list[dict], config: dict | None = None) -> dict:
    raise NotImplementedError("Unified walk-forward engine pending Phase 5.")
