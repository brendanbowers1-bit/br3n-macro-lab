"""
Consistent evaluation for model-zoo outputs.

Separates forecast accuracy, trading P&L, and hedge-governance usefulness.
Research only — compares against random-walk benchmarks.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .metrics import performance_metrics


def _lag(series: pd.Series, days: int) -> pd.Series:
    return series.shift(days).fillna(0.0)


def evaluate_forecast_model(
    df: pd.DataFrame,
    model_output: pd.DataFrame,
    horizon: int = 1,
) -> dict:
    """Compare model forecast_return to realized return vs random-walk (zero)."""
    actual = df["daily_return"].astype(float)
    pred = model_output["forecast_return"].reindex(df.index).fillna(0.0)
    rw_pred = pd.Series(0.0, index=df.index)

    err = actual - pred
    err_rw = actual - rw_pred

    rmse_m = float(np.sqrt((err ** 2).mean()))
    rmse_rw = float(np.sqrt((err_rw ** 2).mean()))
    mae_m = float(np.abs(err).mean())
    mae_rw = float(np.abs(err_rw).mean())

    mask = actual != 0
    if mask.sum() > 0:
        dir_acc = float((np.sign(pred[mask]) == np.sign(actual[mask])).mean() * 100)
    else:
        dir_acc = np.nan

    return {
        "model_name": model_output["model_name"].iloc[0],
        "rmse_model": round(rmse_m, 6),
        "rmse_random_walk": round(rmse_rw, 6),
        "mae_model": round(mae_m, 6),
        "mae_random_walk": round(mae_rw, 6),
        "model_beats_rw_rmse": rmse_m < rmse_rw,
        "model_beats_rw_mae": mae_m < mae_rw,
        "directional_accuracy": round(dir_acc, 2) if not np.isnan(dir_acc) else np.nan,
        "observations": int(len(actual.dropna())),
    }


def evaluate_trading_model(
    df: pd.DataFrame,
    model_output: pd.DataFrame,
    cfg: dict,
) -> dict:
    """Backtest signal-based model with transaction costs."""
    lag = int(cfg["backtest"]["execution_lag_days"])
    cost_bps = float(cfg["backtest"]["transaction_cost_bps"])
    max_pos = float(cfg["risk"]["max_position"])
    ann = int(cfg["backtest"]["annualization_days"])
    eq0 = float(cfg["backtest"]["starting_equity"])

    position = _lag(model_output["signal"].astype(float), lag).clip(-max_pos, max_pos)
    gross = position * df["daily_return"]
    turnover = position.diff().abs().fillna(position.abs())
    cost = turnover * (cost_bps / 10_000.0)
    net = gross - cost
    equity = eq0 * (1.0 + net.fillna(0)).cumprod()

    m = performance_metrics(net, equity, ann, model_output["model_name"].iloc[0])
    m["model_name"] = model_output["model_name"].iloc[0]
    m.update(
        {
            "total_return_gross": round(float((1.0 + gross.fillna(0)).prod() - 1.0) * 100, 3),
            "total_return_net": m["total_return_pct"],
            "annualized_return_net": m["ann_return_pct"],
            "annualized_volatility_net": m["ann_vol_pct"],
            "sharpe_net": m["sharpe"],
            "max_drawdown_net": m["max_drawdown_pct"],
            "win_rate_net": m["win_rate_pct"],
            "number_of_trades": int(turnover.gt(0).sum()),
            "total_transaction_cost": round(float(cost.sum()) * 100, 4),
            "percent_time_in_market": round(float((position != 0).mean()) * 100, 1),
        }
    )

    # Return by regime (net)
    if "regime" in df.columns:
        by_reg = net.groupby(df["regime"]).mean() * ann * 100
        m["return_by_regime"] = "; ".join(f"{k}:{v:.2f}" for k, v in by_reg.items())
    else:
        m["return_by_regime"] = ""

    return m


def evaluate_hedge_model(
    df: pd.DataFrame,
    model_output: pd.DataFrame,
    cfg: dict,
) -> dict:
    """Evaluate hedge-ratio path for US entity long MXN exposure."""
    hg_cfg = cfg.get("hedge_governance", {})
    cost_bps = float(
        hg_cfg.get("hedge_transaction_cost_bps")
        or cfg.get("research", {}).get("hedge_transaction_cost_bps", 2.0)
    )

    hedge_ratio = model_output["hedge_ratio"].reindex(df.index).fillna(0.0).clip(0, 1)
    unhedged = -df["daily_return"]  # us_entity_long_mxn
    turnover = hedge_ratio.diff().abs().fillna(hedge_ratio.abs())
    hedge_cost = turnover * (cost_bps / 10_000.0)
    hedged = unhedged * (1.0 - hedge_ratio) - hedge_cost

    ann = np.sqrt(252)
    vol_u = float(unhedged.std() * ann * 100)
    vol_h = float(hedged.std() * ann * 100)
    vol_red = vol_u - vol_h
    total_cost_pct = float(hedge_cost.sum()) * 100

    eq_u = (1.0 + unhedged.fillna(0)).cumprod()
    eq_h = (1.0 + hedged.fillna(0)).cumprod()
    dd_u = float((eq_u / eq_u.cummax() - 1).min()) * 100
    dd_h = float((eq_h / eq_h.cummax() - 1).min()) * 100
    regret = float((hedged - 0.0).abs().mean() * ann * 100)

    return {
        "model_name": model_output["model_name"].iloc[0],
        "hedge_turnover": round(float(turnover.sum()), 3),
        "total_hedge_cost": round(total_cost_pct, 4),
        "average_hedge_ratio": round(float(hedge_ratio.mean()), 3),
        "unhedged_volatility": round(vol_u, 3),
        "hedged_volatility": round(vol_h, 3),
        "volatility_reduction": round(vol_red, 3),
        "max_drawdown_unhedged": round(dd_u, 3),
        "max_drawdown_hedged": round(dd_h, 3),
        "cost_adjusted_risk_reduction": round(vol_red - total_cost_pct, 3),
        "regret_proxy": round(regret, 3),
    }


def evaluate_all_models(
    df: pd.DataFrame,
    model_outputs_dict: Dict[str, pd.DataFrame],
    cfg: dict,
    out_dir: Optional[Path] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Evaluate zoo outputs; save scorecards to data/outputs/."""
    out_dir = out_dir or Path(cfg.get("reporting", {}).get("output_dir", "data/outputs"))
    if not out_dir.is_absolute():
        out_dir = Path(__file__).resolve().parents[1] / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    forecast_rows: List[dict] = []
    trading_rows: List[dict] = []
    hedge_rows: List[dict] = []

    for name, output in model_outputs_dict.items():
        mtype = output["model_type"].iloc[0]

        if mtype in ("forecast", "hybrid", "trading"):
            forecast_rows.append(evaluate_forecast_model(df, output))

        if mtype in ("trading", "hybrid", "forecast"):
            # Random walk / flat also get trading metrics where signal exists
            if mtype != "hedge_governance":
                trading_rows.append(evaluate_trading_model(df, output, cfg))

        if mtype == "hedge_governance" or output["hedge_ratio"].notna().any():
            if output["hedge_ratio"].notna().any():
                hedge_rows.append(evaluate_hedge_model(df, output, cfg))

    fc_sc = pd.DataFrame(forecast_rows)
    tr_sc = pd.DataFrame(trading_rows)
    hg_sc = pd.DataFrame(hedge_rows)

    fc_sc.to_csv(out_dir / "model_zoo_forecast_scorecard.csv", index=False)
    tr_sc.to_csv(out_dir / "model_zoo_trading_scorecard.csv", index=False)
    hg_sc.to_csv(out_dir / "model_zoo_hedge_scorecard.csv", index=False)

    return fc_sc, tr_sc, hg_sc


def save_run_log(run_log: pd.DataFrame, cfg: dict, out_dir: Optional[Path] = None) -> Path:
    out_dir = out_dir or Path(cfg.get("reporting", {}).get("output_dir", "data/outputs"))
    if not out_dir.is_absolute():
        out_dir = Path(__file__).resolve().parents[1] / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "model_zoo_run_log.csv"
    run_log.to_csv(path, index=False)
    return path
