"""
Labor Conversion Index — how FX translates local labor into global purchasing power.
"""

from __future__ import annotations

import pandas as pd

from src.indices._utils import normalize_index

from src.data.wages import wage_lookup

# Fallback if manual wage file missing
DEFAULT_HOURLY_WAGES_LOCAL = {
    "Mexico": 80.0,
    "India": 250.0,
    "Philippines": 150.0,
    "Colombia": 18000.0,
    "Brazil": 35.0,
    "Nigeria": 2500.0,
    "Pakistan": 800.0,
    "United States": 28.0,
    "Germany": 22.0,
    "United Arab Emirates": 45.0,
}


def calculate_labor_conversion_row(
    country: str,
    currency: str,
    usd_fx_rate: float,
    hidden_fx_tax_pct: float = 0.05,
    ppp_factor: float = 1.0,
) -> dict:
    wage_local = wage_lookup().get(country) or DEFAULT_HOURLY_WAGES_LOCAL.get(country, 100.0)
    rate = max(float(usd_fx_rate or 1), 0.001)
    global_labor_usd = wage_local / rate if currency != "USD" else wage_local
    remit_adj = global_labor_usd * (1 - hidden_fx_tax_pct)
    ppp_adj = remit_adj * ppp_factor

    if ppp_adj >= 15:
        interp = "strong global labor conversion"
    elif ppp_adj >= 8:
        interp = "moderate conversion"
    elif ppp_adj >= 3:
        interp = "weak conversion"
    else:
        interp = "structurally discounted labor"

    return {
        "local_hourly_wage": wage_local,
        "global_labor_value_usd": global_labor_usd,
        "remittance_adjusted_labor_value": remit_adj,
        "ppp_adjusted_labor_value": ppp_adj,
        "hidden_fx_tax_pct": hidden_fx_tax_pct,
        "labor_conversion_index": normalize_index(pd.Series([ppp_adj])).iloc[0],
        "interpretation": interp,
    }


def calculate_labor_conversion_table(
    macro: pd.DataFrame,
    fx_rates: pd.DataFrame,
    hidden_fx_tax: pd.DataFrame | None = None,
) -> pd.DataFrame:
    latest_fx = fx_rates.sort_values("date").groupby("country", as_index=False).tail(1)
    tax_map = {}
    if hidden_fx_tax is not None and not hidden_fx_tax.empty:
        tax_map = hidden_fx_tax.groupby("receiver_country")["hidden_fx_tax_pct"].mean().to_dict()

    rows = []
    for _, fx in latest_fx.iterrows():
        country = fx["country"]
        tax = tax_map.get(country, 0.05)
        ppp = 1.0 - float(
            macro[macro["country"] == country]["inflation_yoy"].iloc[-1]
            if len(macro[macro["country"] == country]) else 0.05
        ) * 0.5
        scores = calculate_labor_conversion_row(country, fx["currency"], fx["usd_fx_rate"], tax, max(ppp, 0.5))
        rows.append({"country": country, "currency": fx["currency"], "date": fx["date"], **scores})
    return pd.DataFrame(rows)
