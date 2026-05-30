"""
Model zoo — simple, explainable FX models for research only.

Tests conditional forecastability against random-walk benchmarks.
Does NOT claim FX prediction, guaranteed returns, or live-trading readiness.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .regimes import R1, R2, R3, R4, RANGE_REGIMES, TREND_REGIMES

logger = logging.getLogger(__name__)

# Standard output columns for every model run.
OUTPUT_COLS = [
    "model_name",
    "date",
    "signal",
    "forecast_return",
    "forecast_price",
    "hedge_ratio",
    "model_type",
]


def normalize_signal(signal: pd.Series) -> pd.Series:
    """Clip trading signal to {-1, 0, +1}."""
    return signal.fillna(0).astype(float).clip(-1, 1).round().astype(int)


def safe_columns_exist(df: pd.DataFrame, columns: List[str]) -> bool:
    """Return True when every named column exists in df."""
    return all(c in df.columns for c in columns)


def _zero_series(df: pd.DataFrame) -> pd.Series:
    return pd.Series(0.0, index=df.index)


def _build_output(
    df: pd.DataFrame,
    model_name: str,
    model_type: str,
    signal: pd.Series,
    forecast_return: Optional[pd.Series] = None,
    forecast_price: Optional[pd.Series] = None,
    hedge_ratio: Optional[pd.Series] = None,
) -> pd.DataFrame:
    """Assemble the standard model output frame."""
    sig = normalize_signal(signal)
    if forecast_return is None:
        forecast_return = _zero_series(df)
    if hedge_ratio is None:
        hedge_ratio = pd.Series(np.nan, index=df.index)
    if forecast_price is None and "price" in df.columns:
        forecast_price = df["price"] * (1.0 + forecast_return.fillna(0.0))
    elif forecast_price is None:
        forecast_price = pd.Series(np.nan, index=df.index)

    dates = pd.to_datetime(df["date"]) if "date" in df.columns else pd.to_datetime(df.index)

    out = {
        "model_name": model_name,
        "date": dates,
        "signal": sig,
        "forecast_return": forecast_return.astype(float),
        "forecast_price": forecast_price.astype(float),
        "hedge_ratio": hedge_ratio.astype(float),
        "model_type": model_type,
    }
    return pd.DataFrame(out, index=df.index)


def _build_output_with_position(
    df: pd.DataFrame,
    model_name: str,
    model_type: str,
    signal: pd.Series,
    position: pd.Series,
    forecast_return: Optional[pd.Series] = None,
) -> pd.DataFrame:
    """Model output with explicit fractional position (vol-scaled trading)."""
    frame = _build_output(df, model_name, model_type, signal, forecast_return)
    frame["position"] = position.astype(float)
    return frame


# ── Individual models ─────────────────────────────────────────────────────────


def random_walk_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """Benchmark: next return = 0, next price = current price."""
    sig = _zero_series(df).astype(int)
    fc_ret = _zero_series(df)
    fc_price = df["price"].copy() if "price" in df.columns else pd.Series(np.nan, index=df.index)
    return _build_output(df, "random_walk_model", "forecast", sig, fc_ret, fc_price)


def buy_and_hold_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """Trading benchmark: always long."""
    sig = pd.Series(1, index=df.index, dtype=int)
    return _build_output(df, "buy_and_hold_model", "trading", sig)


def always_flat_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """Trading / hedge benchmark: no position."""
    sig = _zero_series(df).astype(int)
    return _build_output(df, "always_flat_model", "trading", sig)


def ma_crossover_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """+1 if MA20 > MA60, -1 if MA20 < MA60, else 0."""
    sig = _zero_series(df).astype(int)
    sig.loc[df["ma20"] > df["ma60"]] = 1
    sig.loc[df["ma20"] < df["ma60"]] = -1
    mag = df["daily_return"].rolling(60, min_periods=20).mean().shift(1).fillna(0.0)
    fc_ret = sig.astype(float) * mag
    return _build_output(df, "ma_crossover_model", "hybrid", sig, fc_ret)


def regime_trend_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """Trend signal only in R1/R2; flat in R3/R4."""
    sig = _zero_series(df).astype(int)
    in_trend = df["regime"].isin(TREND_REGIMES)
    sig.loc[in_trend & (df["ma20"] > df["ma60"])] = 1
    sig.loc[in_trend & (df["ma20"] < df["ma60"])] = -1
    mag = df["daily_return"].rolling(60, min_periods=20).mean().shift(1).fillna(0.0)
    fc_ret = sig.astype(float) * mag
    return _build_output(df, "regime_trend_model", "hybrid", sig, fc_ret)


def r2_only_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """Signal only in R2 trend + low vol."""
    sig = _zero_series(df).astype(int)
    in_r2 = df["regime"] == R2
    sig.loc[in_r2 & (df["ma20"] > df["ma60"])] = 1
    sig.loc[in_r2 & (df["ma20"] < df["ma60"])] = -1
    mag = df["daily_return"].rolling(60, min_periods=20).mean().shift(1).fillna(0.0)
    fc_ret = sig.astype(float) * mag
    return _build_output(df, "r2_only_model", "hybrid", sig, fc_ret)


def r2_only_vol_scaled_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """R2-only trend with volatility-scaled position sizing."""
    mz = cfg.get("model_zoo", {})
    target_vol = float(mz.get("r2_vol_scaled_target_vol", 0.10))
    max_pos = float(mz.get("r2_vol_scaled_max_position", 1.0))

    direction = _zero_series(df)
    in_r2 = df["regime"] == R2
    direction.loc[in_r2 & (df["ma20"] > df["ma60"])] = 1.0
    direction.loc[in_r2 & (df["ma20"] < df["ma60"])] = -1.0

    ann_vol = df["realized_vol_20d"].replace(0, np.nan).shift(1).fillna(target_vol)
    size = (target_vol / ann_vol).clip(0.0, max_pos)
    position = (direction * size).fillna(0.0)

    sig = normalize_signal(direction)
    mag = df["daily_return"].rolling(60, min_periods=20).mean().shift(1).fillna(0.0)
    fc_ret = direction * size * mag
    return _build_output_with_position(
        df, "r2_only_vol_scaled_model", "hybrid", sig, position, fc_ret
    )


def r1_risk_off_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """R1 high-vol danger: flat; R2 trend allowed; R3/R4 flat."""
    sig = _zero_series(df).astype(int)
    in_r2 = df["regime"] == R2
    sig.loc[in_r2 & (df["ma20"] > df["ma60"])] = 1
    sig.loc[in_r2 & (df["ma20"] < df["ma60"])] = -1
    mag = df["daily_return"].rolling(60, min_periods=20).mean().shift(1).fillna(0.0)
    fc_ret = sig.astype(float) * mag
    return _build_output(df, "r1_risk_off_model", "hybrid", sig, fc_ret)


def volatility_breakout_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """Breakout above/below rolling window; trade only when vol not extreme."""
    mz = cfg.get("model_zoo", {})
    window = int(mz.get("breakout_window", 20))
    vol_pct_thresh = float(cfg.get("features", {}).get("vol_percentile_threshold", 0.60))

    roll_high = df["price"].rolling(window, min_periods=window).max().shift(1)
    roll_low = df["price"].rolling(window, min_periods=window).min().shift(1)
    low_vol = df.get("realized_vol_percentile", pd.Series(0.5, index=df.index)) < vol_pct_thresh

    sig = _zero_series(df).astype(int)
    sig.loc[low_vol & (df["price"] > roll_high)] = 1
    sig.loc[low_vol & (df["price"] < roll_low)] = -1
    mag = df["daily_return"].rolling(window, min_periods=5).mean().shift(1).fillna(0.0)
    fc_ret = sig.astype(float) * mag
    return _build_output(df, "volatility_breakout_model", "hybrid", sig, fc_ret)


def mean_reversion_range_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """Mean reversion in R3/R4 only; flat in trend regimes."""
    mz = cfg.get("model_zoo", {})
    z_thresh = float(mz.get("mean_reversion_z_threshold", 1.0))

    ma = df["ma20"]
    std = df["daily_return"].rolling(20, min_periods=10).std().shift(1).replace(0, np.nan)
    z = (df["price"] - ma) / (ma * std).replace(0, np.nan)

    sig = _zero_series(df).astype(int)
    in_range = df["regime"].isin(RANGE_REGIMES)
    sig.loc[in_range & (z > z_thresh)] = -1
    sig.loc[in_range & (z < -z_thresh)] = 1
    fc_ret = -sig.astype(float) * df["daily_return"].rolling(20, min_periods=10).mean().shift(1).fillna(0.0)
    return _build_output(df, "mean_reversion_range_model", "hybrid", sig, fc_ret)


def dollar_stress_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """Favor USD vs EM when global stress is elevated."""
    stress_cols = [c for c in ("dollar_stress", "risk_off", "vix_pct") if c in df.columns]
    if not stress_cols:
        raise ValueError("missing_stress_data")

    stress = pd.Series(False, index=df.index)
    if "dollar_stress" in df.columns:
        stress = stress | df["dollar_stress"].astype(bool)
    if "risk_off" in df.columns:
        stress = stress | df["risk_off"].astype(bool)
    if "vix_pct" in df.columns:
        thresh = float(cfg.get("macro", {}).get("vix_stress_percentile", 0.75))
        stress = stress | (df["vix_pct"] >= thresh)

    sig = _zero_series(df).astype(int)
    # Long USD/MXN (positive signal) when stress high — USD strengthens vs EM
    sig.loc[stress] = 1
    sig.loc[~stress] = 0
    mag = df["daily_return"].rolling(60, min_periods=20).mean().shift(1).fillna(0.0).abs()
    fc_ret = sig.astype(float) * mag
    return _build_output(df, "dollar_stress_model", "hybrid", sig, fc_ret)


def flow_pressure_model(
    df: pd.DataFrame,
    cfg: dict,
    train_df: Optional[pd.DataFrame] = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """Signal on flow-pressure windows using training-window directional bias."""
    if "is_flow_pressure_window" not in df.columns:
        raise ValueError("missing_flow_pressure")

    train = train_df if train_df is not None else df
    window_mask = train["is_flow_pressure_window"].astype(bool)
    if window_mask.sum() < 30:
        raise ValueError("insufficient_flow_window_history")

    window_ret = train.loc[window_mask, "daily_return"].mean()
    bias = 1 if window_ret > 0 else (-1 if window_ret < 0 else 0)

    sig = _zero_series(df).astype(int)
    sig.loc[df["is_flow_pressure_window"].astype(bool)] = bias
    mag = abs(float(window_ret)) if not np.isnan(window_ret) else 0.0
    fc_ret = sig.astype(float) * mag
    return _build_output(df, "flow_pressure_model", "hybrid", sig, fc_ret)


def ensemble_vote_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """Majority vote across available sub-models."""
    mz = cfg.get("model_zoo", {})
    min_votes = int(mz.get("ensemble_min_votes", 2))
    train_df = kwargs.get("train_df")

    voters: List[str] = ["ma_crossover_model", "r2_only_model"]
    optional = ["carry_proxy_model", "dollar_stress_model", "flow_pressure_model"]

    signals: List[pd.Series] = []
    for name in voters:
        try:
            out = generate_model_outputs(df, cfg, name, train_df=train_df)
            signals.append(out["signal"].astype(float))
        except Exception:
            pass
    for name in optional:
        try:
            out = generate_model_outputs(df, cfg, name, train_df=train_df)
            signals.append(out["signal"].astype(float))
        except Exception:
            pass

    if not signals:
        raise ValueError("no_ensemble_voters")

    vote_sum = sum(signals)
    vote_count = sum((s != 0).astype(int) for s in signals)
    sig = _zero_series(df).astype(int)
    sig.loc[vote_sum >= min_votes] = 1
    sig.loc[vote_sum <= -min_votes] = -1
    mag = df["daily_return"].rolling(60, min_periods=20).mean().shift(1).fillna(0.0)
    fc_ret = sig.astype(float) * mag
    return _build_output(df, "ensemble_vote_model", "hybrid", sig, fc_ret)


def conservative_hedge_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """Hedge-governance: fixed regime grid (R1=0.60, R2=0.70, R3=0.40, R4=0.30)."""
    grid = {R1: 0.60, R2: 0.70, R3: 0.40, R4: 0.30}
    hr = df["regime"].map(grid).fillna(0.50)
    sig = _zero_series(df).astype(int)
    return _build_output(df, "conservative_hedge_model", "hedge_governance", sig, hedge_ratio=hr)


def no_change_in_range_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """Hedge-governance: freeze in range regimes; gradual moves in trend."""
    hg = cfg.get("hedge_governance", {})
    max_step = float(hg.get("max_daily_hedge_adjustment", 0.10))
    targets = {R1: 0.60, R2: 0.70, R3: None, R4: None}

    ratios: List[float] = []
    prev = 0.50
    for regime in df["regime"]:
        target = targets.get(regime)
        if target is None:
            ratios.append(prev)
            continue
        delta = float(np.clip(target - prev, -max_step, max_step))
        prev = float(np.clip(prev + delta, 0.0, 1.0))
        ratios.append(prev)

    hr = pd.Series(ratios, index=df.index)
    sig = _zero_series(df).astype(int)
    return _build_output(df, "no_change_in_range_model", "hedge_governance", sig, hedge_ratio=hr)


def news_stress_risk_off_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """
    Risk modifier: reduce EM exposure when news_stress_regime is True.

    Does not create signal by itself when stress is False.
    News is a regime/risk feature — not a price prediction claim.
    """
    if "news_stress_regime" not in df.columns:
        raise ValueError("missing_news_stress_regime")

    sig = _zero_series(df).astype(int)
    stress = df["news_stress_regime"].astype(bool)
    # EM/USD long MXN: reduce risk (flat) under news stress; no auto-long when quiet
    sig.loc[stress] = 0
    mag = df["daily_return"].rolling(60, min_periods=20).mean().shift(1).fillna(0.0)
    fc_ret = sig.astype(float) * mag
    return _build_output(df, "news_stress_risk_off_model", "hybrid", sig, fc_ret)


def r2_news_confirmed_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """
    R2 trend only when news_stress_regime is False.

    Tests whether quiet-news R2 regimes are cleaner than news-stressed R2.
    """
    if "news_stress_regime" not in df.columns:
        raise ValueError("missing_news_stress_regime")

    sig = _zero_series(df).astype(int)
    in_r2 = df["regime"] == R2
    quiet = ~df["news_stress_regime"].astype(bool)
    sig.loc[in_r2 & quiet & (df["ma20"] > df["ma60"])] = 1
    sig.loc[in_r2 & quiet & (df["ma20"] < df["ma60"])] = -1
    # High news + R2: flat or reduced — do not trend-follow under stress
    mag = df["daily_return"].rolling(60, min_periods=20).mean().shift(1).fillna(0.0)
    fc_ret = sig.astype(float) * mag
    return _build_output(df, "r2_news_confirmed_model", "hybrid", sig, fc_ret)


def r1_news_escalation_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """
    R1 high-vol trend + news stress → crisis/escalation (risk framing, not alpha).

    Flat signal for trading; elevated hedge ratio for governance lens.
    """
    if "news_stress_regime" not in df.columns:
        raise ValueError("missing_news_stress_regime")

    sig = _zero_series(df).astype(int)
    crisis = (df["regime"] == R1) & df["news_stress_regime"].astype(bool)
    # No normal trading signal — escalation is risk/hedge framing
    hr = pd.Series(np.nan, index=df.index)
    hr.loc[crisis] = 0.85
    hr.loc[~crisis] = 0.50
    fc_ret = _zero_series(df)
    return _build_output(
        df, "r1_news_escalation_model", "hedge_governance", sig, fc_ret, hedge_ratio=hr
    )


def news_flow_pressure_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """
    Combine flow pressure windows with news intensity z-score.

    Tests whether flow + news spikes coincide with higher vol / regime transitions.
    """
    flow_col = "is_flow_pressure_window" if "is_flow_pressure_window" in df.columns else "flow_pressure_window"
    if flow_col not in df.columns:
        raise ValueError("missing_flow_pressure")
    if "news_intensity_zscore" not in df.columns:
        raise ValueError("missing_news_intensity")

    z_thresh = float(cfg.get("news", {}).get("stress_zscore_threshold", 2.0))
    combined = df[flow_col].astype(bool) & (df["news_intensity_zscore"].fillna(0) > z_thresh)

    sig = _zero_series(df).astype(int)
    # No forced directional trade — flag combined stress windows only
    sig.loc[combined] = 0
    mag = df["daily_return"].rolling(20, min_periods=10).std().shift(1).fillna(0.0)
    fc_ret = sig.astype(float) * mag
    return _build_output(df, "news_flow_pressure_model", "hybrid", sig, fc_ret)


# ── Registry ──────────────────────────────────────────────────────────────────

ModelFunc = Callable[..., pd.DataFrame]

MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "random_walk_model": {
        "func": random_walk_model,
        "required_columns": ["price", "daily_return"],
    },
    "buy_and_hold_model": {
        "func": buy_and_hold_model,
        "required_columns": ["daily_return"],
    },
    "always_flat_model": {
        "func": always_flat_model,
        "required_columns": ["daily_return"],
    },
    "ma_crossover_model": {
        "func": ma_crossover_model,
        "required_columns": ["ma20", "ma60", "daily_return"],
    },
    "regime_trend_model": {
        "func": regime_trend_model,
        "required_columns": ["regime", "ma20", "ma60", "daily_return"],
    },
    "r2_only_model": {
        "func": r2_only_model,
        "required_columns": ["regime", "ma20", "ma60", "daily_return"],
    },
    "r2_only_vol_scaled_model": {
        "func": r2_only_vol_scaled_model,
        "required_columns": ["regime", "ma20", "ma60", "daily_return", "realized_vol_20d"],
    },
    "r1_risk_off_model": {
        "func": r1_risk_off_model,
        "required_columns": ["regime", "ma20", "ma60", "daily_return"],
    },
    "volatility_breakout_model": {
        "func": volatility_breakout_model,
        "required_columns": ["price", "daily_return", "realized_vol_percentile"],
    },
    "mean_reversion_range_model": {
        "func": mean_reversion_range_model,
        "required_columns": ["regime", "price", "ma20", "daily_return"],
    },
    "dollar_stress_model": {
        "func": dollar_stress_model,
        "required_columns": ["daily_return"],
        "optional_any": ["dollar_stress", "risk_off", "vix_pct"],
    },
    "flow_pressure_model": {
        "func": flow_pressure_model,
        "required_columns": ["is_flow_pressure_window", "daily_return"],
    },
    "ensemble_vote_model": {
        "func": ensemble_vote_model,
        "required_columns": ["daily_return"],
    },
    "conservative_hedge_model": {
        "func": conservative_hedge_model,
        "required_columns": ["regime"],
    },
    "no_change_in_range_model": {
        "func": no_change_in_range_model,
        "required_columns": ["regime"],
    },
    "news_stress_risk_off_model": {
        "func": news_stress_risk_off_model,
        "required_columns": ["news_stress_regime", "daily_return"],
    },
    "r2_news_confirmed_model": {
        "func": r2_news_confirmed_model,
        "required_columns": ["regime", "news_stress_regime", "ma20", "ma60", "daily_return"],
    },
    "r1_news_escalation_model": {
        "func": r1_news_escalation_model,
        "required_columns": ["regime", "news_stress_regime"],
    },
    "news_flow_pressure_model": {
        "func": news_flow_pressure_model,
        "required_columns": ["daily_return", "news_intensity_zscore"],
        "optional_any": ["is_flow_pressure_window", "flow_pressure_window"],
    },
}


def _check_model_requirements(df: pd.DataFrame, meta: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Return (ok, missing_columns)."""
    missing = [c for c in meta.get("required_columns", []) if c not in df.columns]
    optional_any = meta.get("optional_any")
    if optional_any:
        has_optional = any(c in df.columns for c in optional_any)
        carry_cols = {"carry_proxy", "is_high_carry", "mx_rate", "carry_fragility_regime"}
        if not has_optional and carry_cols.intersection(set(optional_any)):
            # Carry models: need at least one carry column with data
            if "carry_proxy" in df.columns and df["carry_proxy"].notna().any():
                has_optional = True
            elif "is_high_carry" in df.columns:
                has_optional = True
            elif "mx_rate" in df.columns and "us_rate" in df.columns:
                has_optional = True
        if not has_optional:
            missing = list(set(missing + [c for c in optional_any if c not in df.columns]))
    return len(missing) == 0, missing


def _register_carry_models() -> None:
    from .carry_models import CARRY_MODEL_REGISTRY

    MODEL_REGISTRY.update(CARRY_MODEL_REGISTRY)


_register_carry_models()


def generate_model_outputs(
    df: pd.DataFrame,
    cfg: dict,
    model_name: str,
    train_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Dispatch to a single model by name."""
    if model_name not in MODEL_REGISTRY:
        raise KeyError(f"Unknown model: {model_name}")
    meta = MODEL_REGISTRY[model_name]
    ok, missing = _check_model_requirements(df, meta)
    if not ok:
        raise ValueError(f"missing_columns:{','.join(missing)}")
    func: ModelFunc = meta["func"]
    return func(df, cfg, train_df=train_df)


def run_model_zoo(
    df: pd.DataFrame,
    cfg: dict,
    model_names: Optional[List[str]] = None,
    train_df: Optional[pd.DataFrame] = None,
) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
    """
    Run all configured models; skip gracefully when columns are missing.

    Returns (model_outputs_dict, run_log_dataframe).
    """
    mz = cfg.get("model_zoo", {})
    if model_names is None:
        model_names = list(mz.get("models", list(MODEL_REGISTRY.keys())))

    outputs: Dict[str, pd.DataFrame] = {}
    log_rows: List[dict] = []

    for name in model_names:
        if name not in MODEL_REGISTRY:
            log_rows.append(
                {
                    "model_name": name,
                    "status": "skipped",
                    "reason": "unknown_model",
                    "observations": 0,
                    "required_columns_missing": "",
                }
            )
            continue

        meta = MODEL_REGISTRY[name]
        ok, missing = _check_model_requirements(df, meta)

        # carry / dollar_stress: need optional_any satisfied
        optional_any = meta.get("optional_any")
        if optional_any and not any(c in df.columns for c in optional_any):
            ok = False
            missing = list(set(missing + [c for c in optional_any if c not in df.columns]))

        if not ok:
            log_rows.append(
                {
                    "model_name": name,
                    "status": "skipped",
                    "reason": "missing_columns",
                    "observations": len(df),
                    "required_columns_missing": ",".join(missing),
                }
            )
            continue

        try:
            out = generate_model_outputs(df, cfg, name, train_df=train_df)
            outputs[name] = out
            log_rows.append(
                {
                    "model_name": name,
                    "status": "success",
                    "reason": "",
                    "observations": len(out),
                    "required_columns_missing": "",
                }
            )
        except ValueError as exc:
            log_rows.append(
                {
                    "model_name": name,
                    "status": "skipped",
                    "reason": str(exc),
                    "observations": len(df),
                    "required_columns_missing": "",
                }
            )
        except Exception as exc:
            logger.exception("Model %s failed", name)
            log_rows.append(
                {
                    "model_name": name,
                    "status": "error",
                    "reason": str(exc)[:120],
                    "observations": len(df),
                    "required_columns_missing": "",
                }
            )

    return outputs, pd.DataFrame(log_rows)
