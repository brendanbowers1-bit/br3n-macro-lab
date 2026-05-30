"""
Academic statistical tests — forecast comparison and data-snooping warnings.

Simplified implementations for research education. Not publication-grade without extensions.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def diebold_mariano_test(
    e1: np.ndarray,
    e2: np.ndarray,
    power: int = 2,
) -> Dict[str, float | str]:
    """
    Compare predictive accuracy of model vs benchmark forecast errors.

    Loss differential: d = |e1|^power - |e2|^power
    DM stat = mean(d) / SE(d); p-value from normal approximation.

    If p < 0.05 and mean(d) < 0, model significantly improves accuracy.
    """
    e1 = np.asarray(e1, dtype=float)
    e2 = np.asarray(e2, dtype=float)
    mask = np.isfinite(e1) & np.isfinite(e2)
    e1, e2 = e1[mask], e2[mask]
    if len(e1) < 10:
        return {
            "dm_stat": np.nan,
            "p_value": np.nan,
            "interpretation": "Insufficient observations for DM test.",
        }

    d = np.abs(e1) ** power - np.abs(e2) ** power
    d_bar = d.mean()
    se = d.std(ddof=1) / np.sqrt(len(d))
    dm_stat = d_bar / (se + 1e-12)
    p_value = 2 * (1 - 0.5 * (1 + math.erf(abs(dm_stat) / math.sqrt(2))))

    if p_value < 0.05 and d_bar < 0:
        interp = "Model significantly improves forecast accuracy vs benchmark (5% level)."
    elif p_value < 0.05 and d_bar > 0:
        interp = "Benchmark significantly outperforms model (5% level)."
    else:
        interp = "No statistically significant difference in forecast accuracy."

    return {
        "dm_stat": round(float(dm_stat), 4),
        "p_value": round(float(p_value), 4),
        "mean_loss_diff": round(float(d_bar), 8),
        "interpretation": interp,
    }


def simple_white_reality_check(
    strategy_returns_dict: Dict[str, pd.Series],
    benchmark_returns: pd.Series,
    n_boot: int = 500,
    seed: int = 42,
) -> Dict[str, object]:
    """
    Simplified bootstrap data-snooping warning — NOT full White (2000) Reality Check.

    Compares best observed Sharpe excess vs bootstrap distribution of max Sharpe.
    """
    ann = np.sqrt(252)
    bench = benchmark_returns.dropna()
    rows = {}
    for name, rets in strategy_returns_dict.items():
        r = rets.reindex(bench.index).fillna(0)
        excess = r - bench
        if excess.std() < 1e-12:
            sh = 0.0
        else:
            sh = excess.mean() / excess.std() * ann
        rows[name] = sh

    if not rows:
        return {"warning": "No strategy returns provided."}

    best_name = max(rows, key=rows.get)
    best_diff = rows[best_name]

    aligned = pd.DataFrame({k: strategy_returns_dict[k].reindex(bench.index).fillna(0) for k in rows})
    excess_mat = aligned.sub(bench, axis=0).values
    n, k = excess_mat.shape
    rng = np.random.default_rng(seed)
    boot_max = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        sample = excess_mat[idx, :]
        sharpes = [
            sample[:, j].mean() / (sample[:, j].std() + 1e-12) * ann for j in range(k)
        ]
        boot_max.append(max(sharpes))
    boot_max = np.array(boot_max)
    p_val = float((boot_max >= best_diff).mean())

    warning = (
        "Simplified educational bootstrap only — not a full White Reality Check. "
        "Do not treat p-value as publication-grade evidence."
    )
    return {
        "best_strategy": best_name,
        "best_performance_diff": round(float(best_diff), 4),
        "bootstrap_p_value": round(p_val, 4),
        "n_boot": n_boot,
        "warning": warning,
        "rejects_data_mining_5pct": p_val < 0.05,
    }


def save_academic_test_results(results: pd.DataFrame, path: Optional[Path] = None) -> Path:
    path = path or ROOT / "data" / "outputs" / "academic_test_results.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(path, index=False)
    return path
