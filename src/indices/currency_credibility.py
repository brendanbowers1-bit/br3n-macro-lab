"""
Currency Credibility Index — transparent weighted scoring of national monetary credibility.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.indices._utils import interpret_credibility, normalize_index


def _score_lower_better(val: float, lo: float, hi: float) -> float:
    if pd.isna(val):
        return 50.0
    return float(np.clip((hi - val) / (hi - lo) * 100, 0, 100))


def _score_higher_better(val: float, lo: float, hi: float) -> float:
    if pd.isna(val):
        return 50.0
    return float(np.clip((val - lo) / (hi - lo) * 100, 0, 100))


def calculate_currency_credibility_row(row: pd.Series, fx_row: pd.Series | None = None) -> dict:
    infl = float(row.get("inflation_yoy") or 0.05)
    reserves = float(row.get("reserves_months_imports") or 5)
    ca = float(row.get("current_account_gdp") or -0.03)
    debt = float(row.get("external_debt_gdp") or 0.5)
    vol = float(fx_row.get("volatility_30d") if fx_row is not None else 0.12) or 0.12
    dep = float(fx_row.get("quarterly_return") if fx_row is not None else 0) or 0
    institution = float(row.get("institution_score") or 50)  # placeholder

    inflation_score = _score_lower_better(infl, 0.02, 0.15)
    reserve_score = _score_higher_better(reserves, 2, 12)
    ca_score = _score_higher_better(ca, -0.08, 0.02)
    debt_score = _score_lower_better(debt, 0.2, 1.0)
    vol_score = _score_lower_better(vol, 0.05, 0.35)
    dep_score = _score_higher_better(-dep, -0.15, 0.05)  # less depreciation = better
    institution_score = institution

    credibility = (
        inflation_score * 0.20
        + reserve_score * 0.15
        + ca_score * 0.15
        + debt_score * 0.15
        + vol_score * 0.15
        + dep_score * 0.10
        + institution_score * 0.10
    )
    return {
        "inflation_score": inflation_score,
        "reserve_score": reserve_score,
        "current_account_score": ca_score,
        "debt_score": debt_score,
        "fx_volatility_score": vol_score,
        "depreciation_score": dep_score,
        "institution_score": institution_score,
        "credibility_score": credibility,
        "interpretation": interpret_credibility(credibility),
    }


def calculate_currency_credibility_table(
    macro: pd.DataFrame,
    fx_rates: pd.DataFrame | None = None,
) -> pd.DataFrame:
    latest_macro = macro.sort_values("date").groupby("country", as_index=False).tail(1)
    fx_latest = None
    if fx_rates is not None and not fx_rates.empty:
        fx_latest = fx_rates.sort_values("date").groupby("currency", as_index=False).tail(1).set_index("currency")

    rows = []
    for _, row in latest_macro.iterrows():
        fx_row = fx_latest.loc[row["currency"]] if fx_latest is not None and row["currency"] in fx_latest.index else None
        scores = calculate_currency_credibility_row(row, fx_row)
        rows.append({**row.to_dict(), **scores})
    return pd.DataFrame(rows)
