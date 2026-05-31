"""
Currency Credibility Index — transparent weighted scoring of national monetary credibility.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.sovereignty import sovereignty_lookup
from src.indices._utils import interpret_credibility, normalize_index


def _score_lower_better(val: float, lo: float, hi: float) -> float:
    if pd.isna(val):
        return 50.0
    return float(np.clip((hi - val) / (hi - lo) * 100, 0, 100))


def _score_higher_better(val: float, lo: float, hi: float) -> float:
    if pd.isna(val):
        return 50.0
    return float(np.clip((val - lo) / (hi - lo) * 100, 0, 100))


def calculate_currency_credibility_row(
    row: pd.Series,
    fx_row: pd.Series | None = None,
    sovereignty: dict | None = None,
) -> dict:
    infl = float(row.get("inflation_yoy") or 0.05)
    reserves = float(row.get("reserves_months_imports") or 5)
    ca = float(row.get("current_account_gdp") or -0.03)
    debt = float(row.get("external_debt_gdp") or 0.5)
    vol = float(fx_row.get("volatility_30d") if fx_row is not None else 0.12) or 0.12
    dep = float(fx_row.get("quarterly_return") if fx_row is not None else 0) or 0

    sov = sovereignty or {}
    institution = float(sov.get("institution_score") or row.get("institution_score") or 50)
    political_risk = float(sov.get("political_risk_score") or 50)

    inflation_score = _score_lower_better(infl, 0.02, 0.15)
    reserve_score = _score_higher_better(reserves, 2, 12)
    ca_score = _score_higher_better(ca, -0.08, 0.02)
    debt_score = _score_lower_better(debt, 0.2, 1.0)
    vol_score = _score_lower_better(vol, 0.05, 0.35)
    dep_score = _score_higher_better(-dep, -0.15, 0.05)
    institution_score = institution
    political_risk_score = _score_lower_better(political_risk / 100, 0.2, 0.8)

    credibility = (
        inflation_score * 0.18
        + reserve_score * 0.14
        + ca_score * 0.14
        + debt_score * 0.14
        + vol_score * 0.14
        + dep_score * 0.08
        + institution_score * 0.10
        + political_risk_score * 0.08
    )
    return {
        "inflation_score": inflation_score,
        "reserve_score": reserve_score,
        "current_account_score": ca_score,
        "debt_score": debt_score,
        "fx_volatility_score": vol_score,
        "depreciation_score": dep_score,
        "institution_score": institution_score,
        "political_risk_score": political_risk_score,
        "credibility_score": credibility,
        "interpretation": interpret_credibility(credibility),
    }


def calculate_currency_credibility_table(
    macro: pd.DataFrame,
    fx_rates: pd.DataFrame | None = None,
    sovereignty_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    sov_map = sovereignty_lookup() if sovereignty_df is None else {
        str(r["country"]): r.to_dict() for _, r in sovereignty_df.iterrows()
    }

    latest_macro = macro.sort_values("date").groupby("country", as_index=False).tail(1)
    fx_latest = None
    if fx_rates is not None and not fx_rates.empty:
        fx_latest = fx_rates.sort_values("date").groupby("currency", as_index=False).tail(1).set_index("currency")

    rows = []
    for _, row in latest_macro.iterrows():
        fx_row = fx_latest.loc[row["currency"]] if fx_latest is not None and row["currency"] in fx_latest.index else None
        sov = sov_map.get(row["country"], {})
        scores = calculate_currency_credibility_row(row, fx_row, sov)
        rows.append({**row.to_dict(), **scores})
    return pd.DataFrame(rows)
