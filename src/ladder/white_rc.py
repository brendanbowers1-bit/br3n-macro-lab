"""
White (2000) Reality Check — bootstrap p-value for best-of-multiple strategies.

Uses stationary bootstrap on mean daily returns (annualized Sharpe statistic).
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd


def _sharpe(r: np.ndarray, ann: int = 252) -> float:
    if len(r) < 2 or r.std() < 1e-12:
        return 0.0
    return float(r.mean() / r.std() * np.sqrt(ann))


def stationary_bootstrap_indices(
    n: int,
    block_len: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Politis-Romano style stationary bootstrap indices."""
    lam = 1.0 / max(block_len, 1)
    idx = np.zeros(n, dtype=int)
    idx[0] = rng.integers(0, n)
    for t in range(1, n):
        if rng.random() < lam:
            idx[t] = rng.integers(0, n)
        else:
            idx[t] = (idx[t - 1] + 1) % n
    return idx


def white_reality_check(
    returns_by_strategy: Dict[str, pd.Series],
    ann: int = 252,
    n_boot: int = 2000,
    block_len: int = 10,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Compare observed max Sharpe across strategies to bootstrap null.

    Returns one row per strategy plus summary row 'MAX' with reality-check p-value.
    """
    names = sorted(returns_by_strategy.keys())
    aligned = pd.DataFrame({k: returns_by_strategy[k] for k in names}).dropna()
    if aligned.empty or len(aligned) < 60:
        return pd.DataFrame([{"status": "insufficient_data", "bars": len(aligned)}])

    r_mat = aligned.values
    n, k = r_mat.shape
    obs_stats = [_sharpe(r_mat[:, j], ann) for j in range(k)]
    obs_max = float(max(obs_stats))
    best_idx = int(np.argmax(obs_stats))
    best_name = names[best_idx]

    rng = np.random.default_rng(seed)
    boot_max = np.zeros(n_boot)
    for b in range(n_boot):
        idx = stationary_bootstrap_indices(n, block_len, rng)
        sample = r_mat[idx, :]
        boot_max[b] = max(_sharpe(sample[:, j], ann) for j in range(k))

    # One-sided: P(boot max >= observed max)
    p_value = float((boot_max >= obs_max).mean())

    rows: List[dict] = []
    for j, name in enumerate(names):
        rows.append(
            {
                "strategy": name,
                "observed_sharpe": round(obs_stats[j], 4),
                "is_best": name == best_name,
                "bars": n,
            }
        )
    rows.append(
        {
            "strategy": "_SUMMARY",
            "best_strategy": best_name,
            "observed_max_sharpe": round(obs_max, 4),
            "white_rc_pvalue": round(p_value, 4),
            "n_boot": n_boot,
            "block_len": block_len,
            "rejects_data_mining_5pct": p_value < 0.05,
        }
    )
    return pd.DataFrame(rows)
