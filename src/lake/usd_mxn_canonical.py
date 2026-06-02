"""Build canonical USD/MXN daily corridor dataset from data-lake raw layers."""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from src.corridor_intelligence.dataset import load_us_mx_remittances
from src.corridor_intelligence.risk_score import compute_corridor_risk_score
from src.corridor_intelligence.validate import validate_us_mx_dataset
from src.lake.derived_features import (
    apply_flag_series,
    compute_fx_features,
    compute_liquidity_proxy,
    compute_spread_proxy_bps,
)
from src.lake.paths import (
    BANXICO_POLICY_CSV,
    CORRIDOR_DAILY_JSON,
    EVENTS_CSV,
    FED_POLICY_CSV,
    HOLIDAYS_CSV,
    PROCESSED_CORRIDORS,
    PROCESSED_FEATURES,
    PROCESSED_MODEL_READY,
    REMITTANCES_CSV,
    RPW_COST_CSV,
    USD_MXN_DAILY_PARQUET,
    USD_MXN_FEATURES_PARQUET,
    USD_MXN_MODEL_READY_PARQUET,
    USD_MXN_SPOT_CSV,
)

METHODOLOGY_VERSION = "usd_mxn_canonical_v2"


def _ffill_series(frame: pd.DataFrame, date_col: str, value_col: str, daily: pd.DatetimeIndex) -> np.ndarray:
    series = frame.set_index(date_col)[value_col].sort_index()
    return series.reindex(daily, method="ffill").to_numpy()


def _load_rate_csv(path: Path, rate_col: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["date", rate_col])
    df = pd.read_csv(path)
    date_col = "date" if "date" in df.columns else df.columns[0]
    val_col = rate_col if rate_col in df.columns else df.columns[1]
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df[date_col]),
            rate_col: pd.to_numeric(df[val_col], errors="coerce"),
        }
    ).dropna()
    return out.sort_values("date").reset_index(drop=True)


def _load_fx_spot() -> pd.DataFrame:
    return _load_rate_csv(USD_MXN_SPOT_CSV, "usd_mxn_spot")


def _load_fed_policy() -> pd.DataFrame:
    if not FED_POLICY_CSV.exists():
        return pd.DataFrame(columns=["date", "us_policy_rate"])
    df = pd.read_csv(FED_POLICY_CSV)
    date_col = "observation_date" if "observation_date" in df.columns else df.columns[0]
    rate_col = "DFEDTARU" if "DFEDTARU" in df.columns else df.columns[1]
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df[date_col]),
            "us_policy_rate": pd.to_numeric(df[rate_col], errors="coerce"),
        }
    ).dropna()
    return out.sort_values("date").reset_index(drop=True)


def _load_rpw_cost() -> pd.DataFrame:
    if not RPW_COST_CSV.exists():
        return pd.DataFrame(columns=["date", "remittance_cost_proxy", "fx_margin_pct"])
    df = pd.read_csv(RPW_COST_CSV)
    return pd.DataFrame(
        {
            "date": pd.to_datetime(df["date"]),
            "remittance_cost_proxy": pd.to_numeric(df["remittance_cost_proxy"], errors="coerce"),
            "fx_margin_pct": pd.to_numeric(df.get("fx_margin_pct"), errors="coerce"),
        }
    ).dropna(subset=["date", "remittance_cost_proxy"]).sort_values("date")


def _monthly_crs_by_month(rem_df: pd.DataFrame) -> pd.DataFrame:
    validation = validate_us_mx_dataset(rem_df)
    rows = []
    for end_idx in range(len(rem_df)):
        window = rem_df.iloc[: end_idx + 1]
        if len(window) < 2:
            continue
        score = compute_corridor_risk_score(window, data_quality_score=validation.data_quality_score)
        month = pd.Timestamp(window.iloc[-1]["month"]) + pd.offsets.MonthEnd(0)
        rows.append({"month_end": month, "corridor_risk_score": score.score})
    return pd.DataFrame(rows)


def _infer_data_mode(*, has_fed: bool, has_mx: bool, has_fx: bool, has_rpw: bool, rem_starter: bool) -> str:
    live_count = sum([has_fed, has_mx, has_fx, has_rpw])
    if live_count >= 3 and not rem_starter:
        return "live"
    if live_count >= 2 or (live_count >= 1 and rem_starter):
        return "mixed"
    if rem_starter:
        return "research_starter"
    return "mixed"


def build_usd_mxn_canonical(
    *,
    corridor_json_src: Path | None = None,
    retrieval_date: date | None = None,
) -> pd.DataFrame:
    """Merge remittances, rates, FX, RPW, flags onto daily spine; write parquet outputs."""
    retrieval_date = retrieval_date or date.today()
    rem_df = load_us_mx_remittances(REMITTANCES_CSV)
    fed_df = _load_fed_policy()
    mx_df = _load_rate_csv(BANXICO_POLICY_CSV, "mx_policy_rate")
    fx_df = _load_fx_spot()
    rpw_df = _load_rpw_cost()

    rem_starter = "starter" in " ".join(rem_df.get("source", pd.Series(dtype=str)).astype(str)).lower()

    starts = [rem_df["month"].min()]
    ends = [rem_df["month"].max()]
    for frame in (fed_df, mx_df, fx_df, rpw_df):
        if not frame.empty:
            starts.append(frame["date"].min())
            ends.append(frame["date"].max())
    daily = pd.date_range(start=min(starts), end=max(ends), freq="D")
    df = pd.DataFrame({"date": daily})

    if not fed_df.empty:
        df["us_policy_rate"] = _ffill_series(fed_df, "date", "us_policy_rate", daily)
    else:
        df["us_policy_rate"] = np.nan

    if not mx_df.empty:
        df["mx_policy_rate"] = _ffill_series(mx_df, "date", "mx_policy_rate", daily)
    else:
        df["mx_policy_rate"] = np.nan

    if not fx_df.empty:
        df["usd_mxn_spot"] = _ffill_series(fx_df, "date", "usd_mxn_spot", daily)
    else:
        df["usd_mxn_spot"] = np.nan

    rem_monthly = rem_df.copy()
    rem_monthly["month_end"] = rem_monthly["month"] + pd.offsets.MonthEnd(0)
    df["remittance_usd_millions"] = _ffill_series(
        rem_monthly, "month_end", "remittance_usd_millions", daily
    )

    crs_monthly = _monthly_crs_by_month(rem_df)
    if not crs_monthly.empty:
        df["corridor_risk_score"] = _ffill_series(crs_monthly, "month_end", "corridor_risk_score", daily)
    else:
        df["corridor_risk_score"] = np.nan

    if not rpw_df.empty:
        df["remittance_cost_proxy"] = _ffill_series(rpw_df, "date", "remittance_cost_proxy", daily)
        df["fx_margin_pct"] = _ffill_series(rpw_df, "date", "fx_margin_pct", daily)
    else:
        df["remittance_cost_proxy"] = np.nan
        df["fx_margin_pct"] = np.nan

    fx_features = compute_fx_features(df["usd_mxn_spot"])
    df["usd_return_1d"] = fx_features["usd_return_1d"].to_numpy()
    df["usd_return_5d"] = fx_features["usd_return_5d"].to_numpy()
    df["volatility_20d"] = fx_features["volatility_20d"].to_numpy()
    df["volatility_regime"] = fx_features["volatility_regime"].to_numpy()

    df["spread_proxy_bps"] = compute_spread_proxy_bps(df["fx_margin_pct"]).to_numpy()
    df["liquidity_proxy"] = compute_liquidity_proxy(df["volatility_20d"], df["spread_proxy_bps"]).to_numpy()

    if HOLIDAYS_CSV.exists():
        hol = pd.read_csv(HOLIDAYS_CSV)
        df["holiday_flag"] = apply_flag_series(daily, pd.to_datetime(hol["date"]))
    else:
        df["holiday_flag"] = False

    if EVENTS_CSV.exists():
        ev = pd.read_csv(EVENTS_CSV)
        df["event_flag"] = apply_flag_series(daily, pd.to_datetime(ev["date"]))
    else:
        df["event_flag"] = False

    df["rate_differential"] = df["mx_policy_rate"] - df["us_policy_rate"]
    df["carry_proxy"] = df["rate_differential"]

    data_mode = _infer_data_mode(
        has_fed=fed_df.shape[0] > 0,
        has_mx=mx_df.shape[0] > 0,
        has_fx=fx_df.shape[0] > 0,
        has_rpw=rpw_df.shape[0] > 0,
        rem_starter=rem_starter,
    )
    df["source_id"] = "usd_mxn_canonical_v1"
    df["retrieval_date"] = pd.Timestamp(retrieval_date)
    df["data_mode"] = data_mode
    df["synthetic_flag"] = False
    df["methodology_version"] = METHODOLOGY_VERSION

    if "fx_margin_pct" in df.columns:
        df = df.drop(columns=["fx_margin_pct"])

    PROCESSED_CORRIDORS.mkdir(parents=True, exist_ok=True)
    df.to_parquet(USD_MXN_DAILY_PARQUET, index=False)

    feature_cols = [
        "date",
        "usd_mxn_spot",
        "usd_return_1d",
        "usd_return_5d",
        "volatility_20d",
        "volatility_regime",
        "us_policy_rate",
        "mx_policy_rate",
        "rate_differential",
        "carry_proxy",
        "spread_proxy_bps",
        "liquidity_proxy",
        "remittance_cost_proxy",
        "remittance_usd_millions",
        "corridor_risk_score",
        "event_flag",
        "holiday_flag",
        "source_id",
        "retrieval_date",
        "data_mode",
        "synthetic_flag",
        "methodology_version",
    ]
    features = df[feature_cols].copy()
    PROCESSED_FEATURES.mkdir(parents=True, exist_ok=True)
    features.to_parquet(USD_MXN_FEATURES_PARQUET, index=False)

    model_ready = features.dropna(subset=["us_policy_rate"]).copy()
    PROCESSED_MODEL_READY.mkdir(parents=True, exist_ok=True)
    model_ready.to_parquet(USD_MXN_MODEL_READY_PARQUET, index=False)

    if corridor_json_src and corridor_json_src.exists():
        shutil.copy2(corridor_json_src, CORRIDOR_DAILY_JSON)

    return df


def canonical_summary(df: pd.DataFrame) -> dict:
    return {
        "rows": len(df),
        "date_min": str(df["date"].min().date()),
        "date_max": str(df["date"].max().date()),
        "us_policy_rate_non_null": int(df["us_policy_rate"].notna().sum()),
        "mx_policy_rate_non_null": int(df["mx_policy_rate"].notna().sum()),
        "usd_mxn_spot_non_null": int(df["usd_mxn_spot"].notna().sum()),
        "remittance_non_null": int(df["remittance_usd_millions"].notna().sum()),
        "remittance_cost_non_null": int(df["remittance_cost_proxy"].notna().sum()),
        "corridor_risk_score_non_null": int(df["corridor_risk_score"].notna().sum()),
        "event_flag_count": int(df["event_flag"].sum()) if "event_flag" in df.columns else 0,
        "holiday_flag_count": int(df["holiday_flag"].sum()) if "holiday_flag" in df.columns else 0,
        "output_parquet": str(USD_MXN_DAILY_PARQUET),
    }
