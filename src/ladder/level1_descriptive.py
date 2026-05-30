"""
Level 1: Descriptive evidence — do returns differ by regime?
"""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from ..backtest import run_strategy_backtest
from ..metrics import performance_metrics


def regime_descriptive_table(df: pd.DataFrame, cfg: dict) -> Dict[str, pd.DataFrame]:
    """bps/day, Sharpe, max DD within each regime (spot + strategy)."""
    ann = int(cfg["backtest"]["annualization_days"])
    primary = cfg["backtest"].get("primary_strategy", "flat_range")
    bt = run_strategy_backtest(df, cfg, primary)

    rows_spot = []
    rows_strat = []
    mix = df["regime"].value_counts(normalize=True).mul(100).round(2)

    for regime in sorted(df["regime"].unique()):
        mask = df["regime"] == regime
        sub_spot = df.loc[mask, "daily_return"].dropna()
        sub_strat = bt.loc[mask, "net_strategy_return"].dropna()
        pct_time = float(mix.get(regime, 0))

        if len(sub_spot) > 10:
            eq_spot = (1 + sub_spot).cumprod()
            m_spot = performance_metrics(sub_spot, eq_spot, ann, regime)
            dd_spot = float((eq_spot / eq_spot.cummax() - 1).min() * 100)
        else:
            m_spot = {"ann_return_pct": np.nan, "sharpe": np.nan}
            dd_spot = np.nan

        if len(sub_strat) > 10:
            eq_st = (1 + sub_strat).cumprod()
            m_st = performance_metrics(sub_strat, eq_st, ann, regime)
            dd_st = float((eq_st / eq_st.cummax() - 1).min() * 100)
        else:
            m_st = {"sharpe": np.nan}
            dd_st = np.nan

        rows_spot.append(
            {
                "regime": regime,
                "pct_time": pct_time,
                "days": int(mask.sum()),
                "avg_bps_day_spot": round(float(sub_spot.mean() * 10000), 2) if len(sub_spot) else np.nan,
                "sharpe_spot": m_spot.get("sharpe", np.nan),
                "max_dd_pct_spot": round(dd_spot, 2),
            }
        )
        rows_strat.append(
            {
                "regime": regime,
                f"avg_bps_day_{primary}": round(float(sub_strat.mean() * 10000), 2) if len(sub_strat) else np.nan,
                f"sharpe_{primary}": m_st.get("sharpe", np.nan),
                f"max_dd_pct_{primary}": round(dd_st, 2),
            }
        )

    return {
        "regime_mix": mix.rename("pct_days").reset_index().rename(columns={"index": "regime"}),
        "spot_by_regime": pd.DataFrame(rows_spot),
        "strategy_by_regime": pd.DataFrame(rows_strat),
    }
