"""
Forecast accuracy tests — separate from trading P&L.

Research only. Compares model forecasts to random-walk benchmarks.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def make_random_walk_forecast(df: pd.DataFrame, horizon: int = 1, mode: str = "return") -> pd.DataFrame:
    """
    Random-walk benchmarks.

    Price mode:
      - forecast = current price
      - target   = future price at t+horizon

    Return mode (default):
      - forecast = 0 (no expected change)
      - target   = future return over horizon
    """
    out = df.copy()
    if mode == "price":
        out["rw_forecast"] = out["price"]
        out["target"] = out["price"].shift(-horizon)
    else:
        out["rw_forecast"] = 0.0
        if horizon == 1:
            out["target"] = out.get("fwd_return_1d", out["price"].pct_change().shift(-1))
        else:
            out["target"] = out["price"].pct_change(horizon).shift(-horizon)
    return out


def calculate_forecast_errors(
    df: pd.DataFrame,
    forecast_col: str,
    target_col: str,
    benchmark_col: str,
) -> pd.DataFrame:
    """Row-level forecast errors vs benchmark."""
    sub = df[[forecast_col, target_col, benchmark_col]].dropna()
    out = pd.DataFrame(index=sub.index)
    out["model_error"] = sub[target_col] - sub[forecast_col]
    out["benchmark_error"] = sub[target_col] - sub[benchmark_col]
    out["model_abs_error"] = out["model_error"].abs()
    out["benchmark_abs_error"] = out["benchmark_error"].abs()
    out["model_squared_error"] = out["model_error"] ** 2
    out["benchmark_squared_error"] = out["benchmark_error"] ** 2
    return out


def forecast_scorecard(
    df: pd.DataFrame,
    model_forecast_col: str,
    target_col: str,
    benchmark_forecast_col: str,
) -> pd.DataFrame:
    """
    Aggregate forecast accuracy metrics.

    Directional accuracy (return forecasts):
      - model direction = sign(model forecast); 0 forecast -> 0 direction
      - actual direction = sign(actual return)
      - random walk direction = 0 (no-change forecast), so RW only "correct" when actual ~ 0
    """
    err = calculate_forecast_errors(df, model_forecast_col, target_col, benchmark_forecast_col)
    if err.empty:
        return pd.DataFrame([{"observations": 0}])

    rmse_m = float(np.sqrt(err["model_squared_error"].mean()))
    rmse_rw = float(np.sqrt(err["benchmark_squared_error"].mean()))
    mae_m = float(err["model_abs_error"].mean())
    mae_rw = float(err["benchmark_abs_error"].mean())

    actual = df[target_col].reindex(err.index)
    pred = df[model_forecast_col].reindex(err.index)
    mask = actual != 0
    if mask.sum() > 0:
        dir_m = float((np.sign(pred[mask]) == np.sign(actual[mask])).mean() * 100)
    else:
        dir_m = np.nan

    # RW return forecast = 0 -> direction 0; "accuracy" = fraction of near-zero moves
    near_zero = actual.abs() < 1e-8
    dir_rw = float(near_zero.mean() * 100) if len(actual) else np.nan

    row = {
        "rmse_model": round(rmse_m, 8),
        "rmse_random_walk": round(rmse_rw, 8),
        "mae_model": round(mae_m, 8),
        "mae_random_walk": round(mae_rw, 8),
        "model_beats_rw_rmse": rmse_m < rmse_rw,
        "model_beats_rw_mae": mae_m < mae_rw,
        "directional_accuracy_model": round(dir_m, 2) if not np.isnan(dir_m) else None,
        "directional_accuracy_random_walk": round(dir_rw, 2),
        "observations": len(err),
    }
    return pd.DataFrame([row])


def regime_conditioned_return_forecast(df: pd.DataFrame, train: pd.DataFrame) -> pd.Series:
    """Simple regime-conditioned mean return forecast (research baseline)."""
    if "regime" not in train.columns:
        mu = train["daily_return"].mean()
        return pd.Series(mu, index=df.index)
    regime_means = train.groupby("regime")["daily_return"].mean()
    pred = pd.Series(0.0, index=df.index)
    for reg, mu in regime_means.items():
        pred.loc[df["regime"] == reg] = mu
    return pred.fillna(train["daily_return"].mean())


def save_forecast_scorecard(scorecard: pd.DataFrame, path: Optional[Path] = None) -> Path:
    path = path or ROOT / "data" / "outputs" / "forecast_scorecard.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    scorecard.to_csv(path, index=False)
    return path
