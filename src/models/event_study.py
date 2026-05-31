"""
Event study: hidden FX tax and welfare around DXY shock events.

Uses FRED broad dollar index from data/raw/fred/dxy_daily.csv or macro panel.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.paths import RAW_DIR


def load_dxy_series() -> pd.DataFrame:
    p = RAW_DIR / "fred" / "dxy_daily.csv"
    if p.exists():
        df = pd.read_csv(p, parse_dates=["date"])
        return df.sort_values("date")
    cache = Path(__file__).resolve().parents[2] / "data" / "processed" / "macro_panel.csv"
    if cache.exists():
        m = pd.read_csv(cache, parse_dates=[0], index_col=0)
        col = "dxy_broad" if "dxy_broad" in m.columns else "dxy"
        if col in m.columns:
            df = m[[col]].reset_index()
            df.columns = ["date", "dxy_broad"]
            df["dxy_return"] = df["dxy_broad"].pct_change()
            df["dxy_return_20d"] = df["dxy_broad"].pct_change(20)
            return df
    return pd.DataFrame()


def identify_dxy_shock_events(
    dxy: pd.DataFrame,
    percentile: float = 0.90,
    window: int = 20,
) -> pd.DataFrame:
    """Flag dates when 20-day DXY return exceeds percentile threshold."""
    df = dxy.copy()
    col = "dxy_return_20d" if "dxy_return_20d" in df.columns else "dxy_return"
    if col not in df.columns:
        df["dxy_return_20d"] = df["dxy_broad"].pct_change(window)
        col = "dxy_return_20d"
    thresh = df[col].quantile(percentile)
    df["dxy_surge"] = (df[col] >= thresh).astype(int)
    df["event_date"] = df["date"].where(df["dxy_surge"] == 1)
    events = df[df["dxy_surge"] == 1][["date", col]].rename(columns={col: "dxy_shock_magnitude"})
    events["event_type"] = "dxy_surge"
    return events.dropna(subset=["date"])


def event_study_hidden_tax(
    hidden_fx_tax: pd.DataFrame,
    events: pd.DataFrame,
    window_days: int = 30,
) -> pd.DataFrame:
    """
    Compare average hidden FX tax in pre vs post window around DXY surge events.
    """
    if hidden_fx_tax.empty or events.empty:
        return pd.DataFrame()

    hft = hidden_fx_tax.copy()
    hft["date"] = pd.to_datetime(hft["date"])
    rows = []
    for _, ev in events.iterrows():
        ed = pd.Timestamp(ev["date"])
        pre = hft[(hft["date"] >= ed - pd.Timedelta(days=window_days)) & (hft["date"] < ed)]
        post = hft[(hft["date"] >= ed) & (hft["date"] <= ed + pd.Timedelta(days=window_days))]
        rows.append(
            {
                "event_date": ed,
                "dxy_shock_magnitude": ev.get("dxy_shock_magnitude"),
                "pre_hidden_fx_tax_mean": pre["hidden_fx_tax_pct"].mean() if len(pre) else np.nan,
                "post_hidden_fx_tax_mean": post["hidden_fx_tax_pct"].mean() if len(post) else np.nan,
                "change_hidden_fx_tax": (
                    post["hidden_fx_tax_pct"].mean() - pre["hidden_fx_tax_pct"].mean()
                    if len(pre) and len(post) else np.nan
                ),
                "n_corridors_pre": pre["corridor"].nunique() if len(pre) else 0,
                "n_corridors_post": post["corridor"].nunique() if len(post) else 0,
            }
        )
    return pd.DataFrame(rows)


def run_dxy_event_study(
    hidden_fx_tax: pd.DataFrame,
    welfare: pd.DataFrame | None = None,
) -> dict:
    dxy = load_dxy_series()
    if dxy.empty:
        return {
            "error": "No DXY series — run scripts/fetch_global_fx_data.py",
            "limitation": "Event study requires FRED DXY or macro panel cache.",
        }
    events = identify_dxy_shock_events(dxy)
    tax_study = event_study_hidden_tax(hidden_fx_tax, events)
    summary = {
        "n_events": len(events),
        "event_dates": events["date"].dt.strftime("%Y-%m-%d").tolist()[:10],
        "avg_pre_hidden_tax": float(tax_study["pre_hidden_fx_tax_mean"].mean()) if not tax_study.empty else None,
        "avg_post_hidden_tax": float(tax_study["post_hidden_fx_tax_mean"].mean()) if not tax_study.empty else None,
        "avg_change": float(tax_study["change_hidden_fx_tax"].mean()) if not tax_study.empty else None,
        "interpretation": (
            "Positive change → hidden FX tax rose after dollar surge events (consistent with "
            "widening margins / volatility pass-through). Research only — not causal proof."
        ),
        "detail": tax_study.to_dict(orient="records") if not tax_study.empty else [],
    }
    if welfare is not None and not welfare.empty:
        summary["welfare_note"] = "Welfare loss may rise with dollar stress in EM receiving countries."
    return summary
