"""
News feature tests — exploratory regime/risk analysis.

News is tested as a regime feature, not as a price prediction claim.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats

from .regimes import R1, R2, R3, R4

ROOT = Path(__file__).resolve().parents[1]


def _regime_distribution(df: pd.DataFrame) -> str:
    if "regime" not in df.columns or df.empty:
        return ""
    pct = df["regime"].value_counts(normalize=True).mul(100).round(1)
    return "; ".join(f"{k}:{v}%" for k, v in pct.items())


def _regime_pct(df: pd.DataFrame, regime: str) -> Optional[float]:
    if "regime" not in df.columns or df.empty:
        return None
    return round(float((df["regime"] == regime).mean() * 100), 2)


def run_news_feature_tests(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare high-news-stress vs normal days; regime distribution; R2 split.

    Output saved to data/outputs/news_feature_test_results.csv
    """
    rows = []

    if "news_stress_regime" not in df.columns:
        rows.append(
            {
                "test_name": "high_vs_normal_news_stress",
                "observations_high_news": 0,
                "observations_normal": len(df),
                "interpretation": "Missing news_stress_regime — run scripts/run_news_layer.py first.",
            }
        )
        return pd.DataFrame(rows)

    high = df[df["news_stress_regime"].astype(bool)]
    normal = df[~df["news_stress_regime"].astype(bool)]
    rets_h = high["daily_return"].dropna() if "daily_return" in df.columns else pd.Series(dtype=float)
    rets_n = normal["daily_return"].dropna() if "daily_return" in df.columns else pd.Series(dtype=float)

    ann = np.sqrt(252)
    if len(rets_h) >= 5 and len(rets_n) >= 5:
        t_stat, p_val = stats.ttest_ind(rets_h, rets_n, equal_var=False, nan_policy="omit")
    else:
        t_stat, p_val = float("nan"), float("nan")

    vol_h = float(rets_h.std() * ann * 100) if len(rets_h) else float("nan")
    vol_n = float(rets_n.std() * ann * 100) if len(rets_n) else float("nan")

    rows.append(
        {
            "test_name": "high_vs_normal_news_stress",
            "observations_high_news": len(rets_h),
            "observations_normal": len(rets_n),
            "average_return_high_news": round(float(rets_h.mean()), 6) if len(rets_h) else None,
            "average_return_normal": round(float(rets_n.mean()), 6) if len(rets_n) else None,
            "volatility_high_news": round(vol_h, 4) if not np.isnan(vol_h) else None,
            "volatility_normal": round(vol_n, 4) if not np.isnan(vol_n) else None,
            "percent_positive_high_news": round(float((rets_h > 0).mean() * 100), 2) if len(rets_h) else None,
            "percent_positive_normal": round(float((rets_n > 0).mean() * 100), 2) if len(rets_n) else None,
            "regime_distribution_high_news": _regime_distribution(high),
            "regime_distribution_normal": _regime_distribution(normal),
            "t_stat_return_difference": round(float(t_stat), 4) if not np.isnan(t_stat) else None,
            "p_value_return_difference": round(float(p_val), 4) if not np.isnan(p_val) else None,
            "volatility_higher_on_high_news": vol_h > vol_n if not np.isnan(vol_h) and not np.isnan(vol_n) else None,
        }
    )

    rows.append(
        {
            "test_name": "regime_frequency_during_news_stress",
            "observations_high_news": len(high),
            "R1_frequency_during_news_stress": _regime_pct(high, R1),
            "R2_frequency_during_news_stress": _regime_pct(high, R2),
            "R3_frequency_during_news_stress": _regime_pct(high, R3),
            "R4_frequency_during_news_stress": _regime_pct(high, R4),
            "R1_frequency_normal": _regime_pct(normal, R1),
            "R2_frequency_normal": _regime_pct(normal, R2),
            "R3_frequency_normal": _regime_pct(normal, R3),
            "R4_frequency_normal": _regime_pct(normal, R4),
        }
    )

    if "regime" in df.columns and "daily_return" in df.columns:
        r2 = df[df["regime"] == R2]
        r2_low = r2[~r2["news_stress_regime"].astype(bool)]
        r2_high = r2[r2["news_stress_regime"].astype(bool)]
        rl = r2_low["daily_return"].dropna()
        rh = r2_high["daily_return"].dropna()

        if len(rl) >= 5 and len(rh) >= 5:
            t_r2, p_r2 = stats.ttest_ind(rl, rh, equal_var=False, nan_policy="omit")
        else:
            t_r2, p_r2 = float("nan"), float("nan")

        rows.append(
            {
                "test_name": "r2_low_news_vs_r2_high_news",
                "observations_r2_low_news": len(rl),
                "observations_r2_high_news": len(rh),
                "average_return_r2_low_news": round(float(rl.mean()), 6) if len(rl) else None,
                "average_return_r2_high_news": round(float(rh.mean()), 6) if len(rh) else None,
                "volatility_r2_low_news": round(float(rl.std() * ann * 100), 4) if len(rl) else None,
                "volatility_r2_high_news": round(float(rh.std() * ann * 100), 4) if len(rh) else None,
                "sharpe_proxy_r2_low_news": round(float(rl.mean() / (rl.std() + 1e-12) * ann), 4) if len(rl) else None,
                "sharpe_proxy_r2_high_news": round(float(rh.mean() / (rh.std() + 1e-12) * ann), 4) if len(rh) else None,
                "t_stat_return_difference": round(float(t_r2), 4) if not np.isnan(t_r2) else None,
                "p_value_return_difference": round(float(p_r2), 4) if not np.isnan(p_r2) else None,
            }
        )

    return pd.DataFrame(rows)


def save_news_test_results(
    results: pd.DataFrame,
    path: Optional[Path] = None,
) -> Path:
    path = path or ROOT / "data" / "outputs" / "news_feature_test_results.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(path, index=False)
    return path
