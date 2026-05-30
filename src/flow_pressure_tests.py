"""
Flow-pressure window tests — exploratory, not causal.

Compares public flow-proxy windows vs normal days on returns and volatility.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]


def _regime_distribution(df: pd.DataFrame) -> str:
    if "regime" not in df.columns or df.empty:
        return ""
    pct = df["regime"].value_counts(normalize=True).mul(100).round(1)
    return "; ".join(f"{k}:{v}%" for k, v in pct.items())


def _interpret(p_val: float, vol_f: float, vol_n: float) -> str:
    vol_diff = abs(vol_f - vol_n)
    if p_val < 0.05 and vol_f > vol_n:
        return (
            "Flow windows show statistically different returns and higher volatility; "
            "investigate further."
        )
    if p_val >= 0.05 and vol_diff > 1.0:
        return "Flow windows show volatility differences but weak return evidence."
    return "No strong evidence from public flow proxies."


def run_flow_pressure_tests(
    df: pd.DataFrame,
    corridor_id: Optional[str] = None,
) -> pd.DataFrame:
    """
    Compare is_flow_pressure_window == True vs False.

    Exploratory only — calendar proxies are not causal order-flow data.
    """
    if "is_flow_pressure_window" not in df.columns:
        return pd.DataFrame(
            [
                {
                    "corridor_id": corridor_id,
                    "observations_flow_window": 0,
                    "observations_normal": len(df),
                    "interpretation": "Missing is_flow_pressure_window — run add_corridor_flow_proxies first.",
                }
            ]
        )

    flow = df[df["is_flow_pressure_window"]]
    normal = df[~df["is_flow_pressure_window"]]
    rets_f = flow["daily_return"].dropna()
    rets_n = normal["daily_return"].dropna()

    ann = np.sqrt(252)
    if len(rets_f) < 5 or len(rets_n) < 5:
        t_stat, p_val = float("nan"), float("nan")
    else:
        t_stat, p_val = stats.ttest_ind(rets_f, rets_n, equal_var=False, nan_policy="omit")

    vol_f = float(rets_f.std() * ann * 100) if len(rets_f) else float("nan")
    vol_n = float(rets_n.std() * ann * 100) if len(rets_n) else float("nan")
    p = float(p_val) if not np.isnan(p_val) else 1.0

    row = {
        "corridor_id": corridor_id,
        "observations_flow_window": len(rets_f),
        "observations_normal": len(rets_n),
        "average_return_flow_window": round(float(rets_f.mean()), 6) if len(rets_f) else None,
        "average_return_normal": round(float(rets_n.mean()), 6) if len(rets_n) else None,
        "volatility_flow_window": round(vol_f, 4) if not np.isnan(vol_f) else None,
        "volatility_normal": round(vol_n, 4) if not np.isnan(vol_n) else None,
        "percent_positive_flow_window": round(float((rets_f > 0).mean() * 100), 2) if len(rets_f) else None,
        "percent_positive_normal": round(float((rets_n > 0).mean() * 100), 2) if len(rets_n) else None,
        "regime_distribution_flow_window": _regime_distribution(flow),
        "regime_distribution_normal": _regime_distribution(normal),
        "t_stat_return_difference": round(float(t_stat), 4) if not np.isnan(t_stat) else None,
        "p_value_return_difference": round(p, 4),
        "interpretation": _interpret(p, vol_f if not np.isnan(vol_f) else 0, vol_n if not np.isnan(vol_n) else 0),
    }
    return pd.DataFrame([row])


def save_flow_pressure_results(
    results: pd.DataFrame,
    out_dir: Optional[Path] = None,
    filename: str = "flow_pressure_test_results.csv",
) -> Path:
    out_dir = out_dir or ROOT / "data" / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename
    results.to_csv(path, index=False)
    return path
