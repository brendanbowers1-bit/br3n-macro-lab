"""
Stablecoin Dollarization Index — retail digital dollar dependence outside banking.

Research-only. Not investment advice.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import LAB_LIMITATIONS, METHODOLOGY_VERSION

SDI_LIMITATIONS = (
    "Stablecoin dollarization scores combine usage proxies with macro pressure indicators. "
    "Capital controls and banking access may use manual placeholders. "
    + LAB_LIMITATIONS
)


def _clamp(score: float) -> float:
    return max(0.0, min(100.0, float(score)))


def calculate_stablecoin_dollarization_row(row: pd.Series) -> dict:
    usage = float(row.get("stablecoin_usage_proxy", row.get("stablecoin_supply_share", 0.05)) or 0.05)
    inflation = float(row.get("local_inflation_yoy", row.get("inflation_yoy", 0.04)) or 0.04)
    fx_vol = float(row.get("local_fx_volatility_30d", row.get("fx_volatility_30d", 0.12)) or 0.12)
    bank_access = float(row.get("bank_account_access_pct", row.get("account_ownership_pct", 0.6)) or 0.6)
    capital_controls = float(row.get("capital_controls_proxy", 0.2) or 0.2)
    depreciation = float(row.get("local_currency_depreciation_yoy", 0.05) or 0.05)
    remittance = float(row.get("remittance_dependency", row.get("remittances_gdp", 0.03)) or 0.03)
    exchange_access = float(row.get("crypto_exchange_access_score", 70) or 70)
    usd_deposit_access = float(row.get("local_usd_deposit_access_score", 40) or 40)

    score = (
        usage * 100 * 0.25
        + min(inflation, 0.5) * 100 * 0.15
        + min(fx_vol, 0.5) * 100 * 0.15
        + (1 - bank_access) * 100 * 0.10
        + capital_controls * 100 * 0.10
        + min(depreciation, 0.5) * 100 * 0.10
        + min(remittance, 0.15) * 100 * 0.10
        + exchange_access / 100 * 10
        + (1 - usd_deposit_access / 100) * 10
    )
    score = _clamp(score)

    if score < 25:
        interp = "Low digital dollarization (estimated)"
    elif score < 45:
        interp = "Emerging digital dollarization (estimated)"
    elif score < 65:
        interp = "High stablecoin dollar dependence (estimated)"
    else:
        interp = "Severe monetary sovereignty pressure (estimated)"

    return {
        "stablecoin_dollarization_index": score,
        "stablecoin_usage_proxy": usage,
        "local_inflation_yoy": inflation,
        "local_fx_volatility_30d": fx_vol,
        "bank_account_access_pct": bank_access,
        "capital_controls_proxy": capital_controls,
        "local_currency_depreciation_yoy": depreciation,
        "remittance_dependency": remittance,
        "crypto_exchange_access_score": _clamp(exchange_access),
        "local_usd_deposit_access_score": _clamp(usd_deposit_access),
        "interpretation": interp,
        "methodology_version": METHODOLOGY_VERSION,
        "limitations": SDI_LIMITATIONS,
        "data_quality_score": row.get("data_quality_score"),
        "mock_data_flag": row.get("mock_data_flag", False),
    }


def calculate_stablecoin_dollarization_table(
    macro: pd.DataFrame,
    supply: pd.DataFrame | None = None,
    corridors: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if macro.empty:
        return pd.DataFrame()

    usage_map = {}
    if supply is not None and not supply.empty:
        total = supply["supply_usd"].sum()
        if total > 0:
            by_country = supply.groupby("country")["supply_usd"].sum() if "country" in supply.columns else None
            if by_country is not None:
                usage_map = (by_country / total).to_dict()

    rows = []
    for _, row in macro.iterrows():
        merged = row.to_dict()
        country = row.get("country", row.get("receiver_country", "unknown"))
        merged["stablecoin_usage_proxy"] = usage_map.get(country, merged.get("stablecoin_usage_proxy", 0.05))
        if corridors is not None and not corridors.empty:
            corr = corridors[corridors["receiver_country"] == country]
            if not corr.empty:
                merged["remittance_dependency"] = corr["traditional_fee_pct"].mean() * 0.01
        calc = calculate_stablecoin_dollarization_row(pd.Series(merged))
        calc["entity"] = country
        calc["entity_type"] = "country"
        calc["country"] = country
        rows.append({**merged, **calc})
    return pd.DataFrame(rows)
