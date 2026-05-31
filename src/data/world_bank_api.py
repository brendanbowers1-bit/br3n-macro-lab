"""
World Bank Open Data API client for Global FX Research Lab.

Docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
"""

from __future__ import annotations

import time
from typing import Iterable

import pandas as pd
import requests

BASE = "https://api.worldbank.org/v2"

# Indicators used by flagship indices
INDICATORS = {
    "remittances_gdp": "BX.TRF.PWKR.DT.GD.ZS",
    "remittances_usd": "BX.TRF.PWKR.CD.DT",
    "inflation_yoy": "FP.CPI.TOTL.ZG",
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "current_account_gdp": "BN.CAB.XOKA.GD.ZS",
    "external_debt_gdp": "DT.DOD.DECT.GN.ZS",
    "imports_gdp": "NE.IMP.GNFS.ZS",
    "unemployment": "SL.UEM.TOTL.ZS",
}

COUNTRY_CODES = {
    "Mexico": "MEX",
    "India": "IND",
    "Philippines": "PHL",
    "Colombia": "COL",
    "Brazil": "BRA",
    "Nigeria": "NGA",
    "Pakistan": "PAK",
    "United States": "USA",
    "Germany": "DEU",
    "United Arab Emirates": "ARE",
    "Japan": "JPN",
    "United Kingdom": "GBR",
}


def _country_batch(codes: Iterable[str]) -> str:
    return ";".join(codes)


def fetch_indicator_batch(
    country_codes: list[str],
    indicator: str,
    per_page: int = 2000,
) -> pd.DataFrame:
    """Fetch one indicator for multiple countries in a single API call."""
    url = f"{BASE}/country/{_country_batch(country_codes)}/indicator/{indicator}"
    params = {"format": "json", "per_page": per_page, "date": "2015:2025"}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list) or len(data) < 2 or not data[1]:
        return pd.DataFrame()
    rows = []
    code_to_name = {v: k for k, v in COUNTRY_CODES.items()}
    for obs in data[1]:
        cc = obs.get("countryiso3code") or obs.get("country", {}).get("id", "")
        rows.append(
            {
                "country_code": cc,
                "country": code_to_name.get(cc, cc),
                "year": int(obs["date"]),
                "value": obs["value"],
                "indicator": indicator,
            }
        )
    return pd.DataFrame(rows)


def fetch_country_panel(
    countries: dict[str, str] | None = None,
    indicators: dict[str, str] | None = None,
    pause_s: float = 0.05,
) -> pd.DataFrame:
    """Fetch wide country-year panel from World Bank API (batched by indicator)."""
    countries = countries or COUNTRY_CODES
    indicators = indicators or INDICATORS
    codes = list(countries.values())
    frames = []
    for name, ind in indicators.items():
        try:
            df = fetch_indicator_batch(codes, ind)
            if df.empty:
                continue
            df["field"] = name
            frames.append(df)
        except Exception:
            continue
        time.sleep(pause_s)
    if not frames:
        return pd.DataFrame()
    long = pd.concat(frames, ignore_index=True)
    wide = long.pivot_table(
        index=["country", "year"], columns="field", values="value", aggfunc="first"
    )
    wide = wide.reset_index()
    wide.columns.name = None
    wide["source"] = "world_bank_api"
    return wide


def to_macro_quarterly(panel: pd.DataFrame) -> pd.DataFrame:
    """Expand annual WB panel to quarterly macro_country_panel schema."""
    if panel.empty:
        return panel
    rows = []
    currency_map = {
        "Mexico": "MXN", "India": "INR", "Philippines": "PHP", "Colombia": "COP",
        "Brazil": "BRL", "Nigeria": "NGN", "Pakistan": "PKR", "United States": "USD",
        "Germany": "EUR", "United Arab Emirates": "AED", "Japan": "JPY", "United Kingdom": "GBP",
    }
    for _, r in panel.iterrows():
        year = int(r["year"])
        country = r["country"]
        for q, month in [(1, 1), (2, 4), (3, 7), (4, 10)]:
            d = pd.Timestamp(year=year, month=month, day=1)
            rows.append(
                {
                    "date": d,
                    "year": year,
                    "quarter": f"{year}Q{q}",
                    "country": country,
                    "currency": currency_map.get(country, "USD"),
                    "inflation_yoy": (r.get("inflation_yoy") or 0) / 100 if pd.notna(r.get("inflation_yoy")) else None,
                    "policy_rate": None,
                    "gdp_growth": (r.get("gdp_growth") or 0) / 100 if pd.notna(r.get("gdp_growth")) else None,
                    "current_account_gdp": (r.get("current_account_gdp") or 0) / 100 if pd.notna(r.get("current_account_gdp")) else None,
                    "reserves_months_imports": None,
                    "external_debt_gdp": (r.get("external_debt_gdp") or 0) / 100 if pd.notna(r.get("external_debt_gdp")) else None,
                    "remittances_gdp": (r.get("remittances_gdp") or 0) / 100 if pd.notna(r.get("remittances_gdp")) else None,
                    "imports_gdp": (r.get("imports_gdp") or 0) / 100 if pd.notna(r.get("imports_gdp")) else None,
                    "trade_openness": None,
                    "unemployment": (r.get("unemployment") or 0) / 100 if pd.notna(r.get("unemployment")) else None,
                    "source": "world_bank_api",
                }
            )
    out = pd.DataFrame(rows)
    return out.sort_values(["country", "date"]).reset_index(drop=True)
