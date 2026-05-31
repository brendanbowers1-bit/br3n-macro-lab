"""
Currency Trust Score — trustworthiness of a currency system for cross-border value survival.

Research-only. Institutional and crisis placeholders clearly labelled.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.sovereignty import sovereignty_lookup


CURRENCY_TRUST_LIMITATIONS = (
    "Institutional trust and crisis history use research placeholders from sovereignty manual file. "
    "Not a sovereign credit rating. Not investment advice."
)


def score_inflation_stability(inflation_yoy: float) -> float:
    infl = float(inflation_yoy or 0.05)
    return float(np.clip((0.15 - infl) / 0.13 * 100, 0, 100))


def score_fx_stability(volatility_90d: float) -> float:
    vol = float(volatility_90d or 0.15)
    return float(np.clip((0.35 - vol) / 0.30 * 100, 0, 100))


def score_reserve_adequacy(reserves_months_imports: float) -> float:
    r = float(reserves_months_imports or 5)
    return float(np.clip((r - 2) / 10 * 100, 0, 100))


def score_current_account(current_account_gdp: float) -> float:
    ca = float(current_account_gdp or -0.03)
    return float(np.clip((ca + 0.08) / 0.10 * 100, 0, 100))


def score_external_debt(external_debt_gdp: float) -> float:
    debt = float(external_debt_gdp or 0.5)
    return float(np.clip((1.0 - debt) / 0.80 * 100, 0, 100))


def calculate_currency_trust_score(row: pd.Series) -> dict:
    infl_s = score_inflation_stability(row.get("inflation_yoy"))
    fx_s = score_fx_stability(row.get("volatility_90d") or row.get("volatility_30d"))
    res_s = score_reserve_adequacy(row.get("reserves_months_imports"))
    ca_s = score_current_account(row.get("current_account_gdp"))
    debt_s = score_external_debt(row.get("external_debt_gdp"))

    sov = sovereignty_lookup().get(str(row.get("country", "")), {})
    institution_ph = float(sov.get("institution_score") or row.get("institution_score") or 50)
    crisis_ph = float(sov.get("political_risk_score") or 50)
    crisis_s = float(np.clip(100 - crisis_ph, 0, 100))

    trust = (
        infl_s * 0.25
        + fx_s * 0.20
        + res_s * 0.15
        + ca_s * 0.15
        + debt_s * 0.10
        + institution_ph * 0.10
        + crisis_s * 0.05
    )

    if trust >= 70:
        interp = "high trust"
    elif trust >= 50:
        interp = "stable but vulnerable"
    elif trust >= 30:
        interp = "fragile"
    else:
        interp = "crisis-prone"

    return {
        "inflation_stability_score": infl_s,
        "fx_stability_score": fx_s,
        "reserve_adequacy_score": res_s,
        "current_account_score": ca_s,
        "external_debt_score": debt_s,
        "institutional_trust_ph": institution_ph,
        "crisis_history_ph": crisis_s,
        "currency_trust_score": trust,
        "interpretation": interp,
    }


def calculate_currency_trust_table(
    macro: pd.DataFrame,
    fx_rates: pd.DataFrame | None = None,
) -> pd.DataFrame:
    latest = macro.sort_values("date").groupby("country", as_index=False).tail(1)
    if fx_rates is not None and not fx_rates.empty:
        fx_latest = (
            fx_rates.sort_values("date")
            .groupby("currency", as_index=False)
            .tail(1)
            .set_index("currency")
        )
        vol90 = fx_latest["volatility_90d"].to_dict() if "volatility_90d" in fx_latest.columns else {}
        vol30 = fx_latest["volatility_30d"].to_dict()
        latest["volatility_90d"] = latest["currency"].map(vol90).fillna(
            latest["currency"].map(vol30).fillna(0.15)
        )
    rows = []
    for _, row in latest.iterrows():
        scores = calculate_currency_trust_score(row)
        rows.append({**row.to_dict(), **scores})
    return pd.DataFrame(rows)
