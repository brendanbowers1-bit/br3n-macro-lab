"""
Carry regime tests — exploratory research only.

Tests whether carry changes regime behavior, not whether carry predicts FX with certainty.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats

from .regimes import R1, R2, R3, R4

ROOT = Path(__file__).resolve().parents[1]


def _sharpe_like(rets: pd.Series) -> Optional[float]:
    if len(rets) < 5:
        return None
    sd = float(rets.std())
    if sd < 1e-12:
        return None
    return round(float(rets.mean() / sd * np.sqrt(252)), 4)


def _max_dd_proxy(rets: pd.Series) -> Optional[float]:
    if rets.empty:
        return None
    eq = (1.0 + rets.fillna(0)).cumprod()
    return round(float((eq / eq.cummax() - 1).min()) * 100, 3)


def run_carry_regime_tests(df: pd.DataFrame) -> pd.DataFrame:
    """
    Test carry vs regime behavior. Exploratory — p-values are not publication-grade.
    """
    rows = []
    work = df.copy()
    if "date" in work.columns:
        work = work.set_index("date")

    if "carry_proxy" not in work.columns or work["carry_proxy"].isna().all():
        if "is_high_carry" not in work.columns:
            return pd.DataFrame(
                [{"test_name": "carry_unavailable", "interpretation": "No carry data — run carry layer first."}]
            )

    ann = np.sqrt(252)
    rets = work["daily_return"].dropna() if "daily_return" in work.columns else pd.Series(dtype=float)

    # 1. High carry vs low carry
    if "is_high_carry" in work.columns and "is_low_carry" in work.columns:
        hi = work[work["is_high_carry"].astype(bool)]
        lo = work[work["is_low_carry"].astype(bool)]
        rh = hi["daily_return"].dropna()
        rl = lo["daily_return"].dropna()
        t_stat, p_val = (float("nan"), float("nan"))
        if len(rh) >= 5 and len(rl) >= 5:
            t_stat, p_val = stats.ttest_ind(rh, rl, equal_var=False, nan_policy="omit")

        rows.append(
            {
                "test_name": "high_carry_vs_low_carry",
                "observations_high_carry": len(rh),
                "observations_low_carry": len(rl),
                "average_return_high_carry": round(float(rh.mean()), 6) if len(rh) else None,
                "average_return_low_carry": round(float(rl.mean()), 6) if len(rl) else None,
                "volatility_high_carry": round(float(rh.std() * ann * 100), 4) if len(rh) else None,
                "volatility_low_carry": round(float(rl.std() * ann * 100), 4) if len(rl) else None,
                "sharpe_like_high_carry": _sharpe_like(rh),
                "sharpe_like_low_carry": _sharpe_like(rl),
                "t_stat_return_difference": round(float(t_stat), 4) if not np.isnan(t_stat) else None,
                "p_value_return_difference": round(float(p_val), 4) if not np.isnan(p_val) else None,
            }
        )

    # 2. Carry by FX regime
    if "regime" in work.columns and "is_high_carry" in work.columns:
        for regime in work["regime"].dropna().unique():
            for carry_label, mask_fn in [
                ("high_carry", lambda d: d["is_high_carry"].astype(bool)),
                ("all", lambda d: pd.Series(True, index=d.index)),
            ]:
                sub = work[(work["regime"] == regime) & mask_fn(work)]
                r = sub["daily_return"].dropna()
                if len(r) < 3:
                    continue
                rows.append(
                    {
                        "test_name": "carry_by_regime",
                        "regime": regime,
                        "carry_slice": carry_label,
                        "observations": len(r),
                        "average_daily_return": round(float(r.mean()), 6),
                        "annualized_volatility": round(float(r.std() * ann * 100), 4),
                        "percent_positive_days": round(float((r > 0).mean() * 100), 2),
                        "max_drawdown_proxy": _max_dd_proxy(r),
                    }
                )

    # 3. R2 high-carry stable vs fragile
    r2_stable = work[
        (work.get("carry_adjusted_regime", pd.Series("", index=work.index)) == "R2_high_carry_stable")
    ]
    r2_fragile = work[
        (work.get("carry_adjusted_regime", pd.Series("", index=work.index)) == "R2_high_carry_fragile")
    ]
    if r2_stable.empty and "regime" in work.columns:
        in_r2 = work["regime"].astype(str).str.contains("R2", na=False)
        r2_stable = work[in_r2 & work["is_high_carry"].astype(bool) & ~work.get("carry_fragility_regime", False).astype(bool)]
        r2_fragile = work[in_r2 & work.get("carry_fragility_regime", False).astype(bool)]

    rs = r2_stable["daily_return"].dropna() if not r2_stable.empty else pd.Series(dtype=float)
    rf = r2_fragile["daily_return"].dropna() if not r2_fragile.empty else pd.Series(dtype=float)
    if len(rs) >= 3 or len(rf) >= 3:
        t_r2, p_r2 = (float("nan"), float("nan"))
        if len(rs) >= 5 and len(rf) >= 5:
            t_r2, p_r2 = stats.ttest_ind(rs, rf, equal_var=False, nan_policy="omit")
        rows.append(
            {
                "test_name": "r2_high_carry_stable_vs_fragile",
                "observations_r2_stable": len(rs),
                "observations_r2_fragile": len(rf),
                "average_return_r2_stable": round(float(rs.mean()), 6) if len(rs) else None,
                "average_return_r2_fragile": round(float(rf.mean()), 6) if len(rf) else None,
                "volatility_r2_stable": round(float(rs.std() * ann * 100), 4) if len(rs) else None,
                "volatility_r2_fragile": round(float(rf.std() * ann * 100), 4) if len(rf) else None,
                "sharpe_like_r2_stable": _sharpe_like(rs),
                "sharpe_like_r2_fragile": _sharpe_like(rf),
                "t_stat_return_difference": round(float(t_r2), 4) if not np.isnan(t_r2) else None,
                "p_value_return_difference": round(float(p_r2), 4) if not np.isnan(p_r2) else None,
            }
        )

    # 4. R1 high-carry stress
    r1_stress = work[
        work.get("carry_adjusted_regime", pd.Series("", index=work.index)) == "R1_high_carry_stress"
    ]
    if r1_stress.empty and "regime" in work.columns:
        in_r1 = work["regime"].astype(str).str.contains("R1", na=False)
        r1_stress = work[in_r1 & work.get("carry_fragility_regime", False).astype(bool)]

    r1 = r1_stress["daily_return"].dropna() if not r1_stress.empty else pd.Series(dtype=float)
    if len(r1) >= 3:
        rows.append(
            {
                "test_name": "r1_high_carry_stress",
                "observations": len(r1),
                "average_daily_return": round(float(r1.mean()), 6),
                "annualized_volatility": round(float(r1.std() * ann * 100), 4),
                "max_drawdown_proxy": _max_dd_proxy(r1),
                "percent_positive_days": round(float((r1 > 0).mean() * 100), 2),
            }
        )

    # 5. Carry compression
    if "carry_compression" in work.columns:
        comp = work[work["carry_compression"].astype(bool)]
        norm = work[~work["carry_compression"].astype(bool)]
        rc = comp["daily_return"].dropna()
        rn = norm["daily_return"].dropna()
        if len(rc) >= 5 and len(rn) >= 5:
            t_c, p_c = stats.ttest_ind(rc, rn, equal_var=False, nan_policy="omit")
            rows.append(
                {
                    "test_name": "carry_compression",
                    "observations_compression": len(rc),
                    "observations_normal": len(rn),
                    "average_return_compression": round(float(rc.mean()), 6),
                    "average_return_normal": round(float(rn.mean()), 6),
                    "volatility_compression": round(float(rc.std() * ann * 100), 4),
                    "volatility_normal": round(float(rn.std() * ann * 100), 4),
                    "t_stat_return_difference": round(float(t_c), 4),
                    "p_value_return_difference": round(float(p_c), 4),
                }
            )

    return pd.DataFrame(rows) if rows else pd.DataFrame([{"test_name": "no_tests", "interpretation": "Insufficient data."}])


def save_carry_test_results(results: pd.DataFrame, path: Optional[Path] = None) -> Path:
    path = path or ROOT / "data" / "outputs" / "carry_regime_test_results.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(path, index=False)
    return path
