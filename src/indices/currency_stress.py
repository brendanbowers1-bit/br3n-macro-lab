"""
Currency Stress Index — detect when currency belief is under stress.
"""

from __future__ import annotations

import pandas as pd

from src.indices._utils import interpret_stress, normalize_index


def calculate_currency_stress_row(
    fx_row: pd.Series,
    macro_row: pd.Series | None = None,
    dxy_shock: float = 0.0,
) -> dict:
    dep30 = abs(min(float(fx_row.get("monthly_return") or 0) * 2, 0))
    dep90 = abs(min(float(fx_row.get("quarterly_return") or 0), 0))
    vol = float(fx_row.get("volatility_30d") or 0.12)
    dd = abs(min(float(fx_row.get("drawdown_1y") or 0), 0))

    infl = float(macro_row.get("inflation_yoy") or 0.05) if macro_row is not None else 0.05
    ca = float(macro_row.get("current_account_gdp") or -0.03) if macro_row is not None else -0.03
    remit = float(macro_row.get("remittances_gdp") or 0) if macro_row is not None else 0
    reserves_ph = 0.5  # placeholder decline signal

    stress = (
        dep30 * 200 * 0.15
        + dep90 * 100 * 0.15
        + vol * 100 * 0.20
        + dd * 100 * 0.15
        + max(infl - 0.05, 0) * 200 * 0.10
        + max(-ca, 0) * 100 * 0.10
        + remit * 50 * 0.05
        + abs(dxy_shock) * 50 * 0.05
        + reserves_ph * 0.05 * 100
    )
    stress = min(stress, 100)

    drivers = []
    if dep30 > 0.02:
        drivers.append("recent depreciation")
    if vol > 0.2:
        drivers.append("elevated FX volatility")
    if infl > 0.08:
        drivers.append("high inflation")
    if ca < -0.04:
        drivers.append("current account pressure")
    if not drivers:
        drivers.append("no dominant stress driver")

    return {
        "stress_score": stress,
        "stress_index_0_100": stress,
        "regime": interpret_stress(stress),
        "drivers": "; ".join(drivers),
        "depreciation_30d": dep30,
        "volatility_component": vol,
        "inflation_component": infl,
    }


def calculate_currency_stress_table(
    fx_rates: pd.DataFrame,
    macro: pd.DataFrame | None = None,
) -> pd.DataFrame:
    latest = fx_rates.sort_values("date").groupby("currency", as_index=False).tail(1)
    macro_latest = {}
    if macro is not None and not macro.empty:
        for _, r in macro.sort_values("date").groupby("country").tail(1).iterrows():
            macro_latest[r["country"]] = r

    rows = []
    for _, fx in latest.iterrows():
        m = macro_latest.get(fx["country"])
        scores = calculate_currency_stress_row(fx, m)
        rows.append({**fx.to_dict(), **scores})
    out = pd.DataFrame(rows)
    out["explanation"] = out.apply(
        lambda r: f"{r['country']} ({r['currency']}): {r['regime']} — {r['drivers']}", axis=1
    )
    return out
