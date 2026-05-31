"""
Structured registry of public data sources for flagship FX research indices.

Each entry documents provenance, fields, update frequency, and which indices use it.
Automated = loader implemented; manual = drop files in data/raw/<source>/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class DataSourceSpec:
    source_id: str
    name: str
    url: str
    update_frequency: str
    fields_needed: list[str]
    license_notes: str
    indices_used: list[str]
    ingestion: Literal["automated", "manual", "placeholder"]
    raw_path: str
    description: str = ""


DATA_SOURCES: list[DataSourceSpec] = [
    DataSourceSpec(
        source_id="world_bank_rpw",
        name="World Bank Remittance Prices Worldwide",
        url="https://remittanceprices.worldbank.org/",
        update_frequency="Quarterly",
        fields_needed=[
            "sender_country",
            "receiver_country",
            "provider",
            "provider_type",
            "send_amount_usd",
            "total_cost_pct",
            "fee_pct",
            "fx_margin_pct",
            "transfer_speed_days",
            "payout_method",
        ],
        license_notes="World Bank open data; cite Remittance Prices Worldwide.",
        indices_used=["Hidden FX Tax Index", "Remittance Welfare Loss Index", "Value Survival Index (VSI)"],
        ingestion="manual",
        raw_path="data/raw/world_bank_rpw/",
        description="Corridor-level remittance costs, fees, FX margins, transfer speed.",
    ),
    DataSourceSpec(
        source_id="world_bank_knomad",
        name="World Bank / KNOMAD Bilateral Remittance Matrix",
        url="https://www.knomad.org/data/remittances",
        update_frequency="Annual",
        fields_needed=["sender_country", "receiver_country", "year", "remittance_usd"],
        license_notes="KNOMAD / World Bank; verify citation requirements.",
        indices_used=["Remittance Welfare Loss Index", "Dollar Dependency Index", "Value Survival Index (VSI)"],
        ingestion="manual",
        raw_path="data/raw/world_bank_knomad/",
        description="Bilateral remittance flows for corridor weighting and welfare exposure.",
    ),
    DataSourceSpec(
        source_id="imf_fx",
        name="IMF Exchange Rates Dataset",
        url="https://data.imf.org/",
        update_frequency="Daily / monthly",
        fields_needed=["date", "country", "currency", "usd_fx_rate"],
        license_notes="IMF data terms of use apply.",
        indices_used=[
            "Currency Credibility Index",
            "Currency Stress Index",
            "Labor Conversion Index",
            "Value Survival Index (VSI)",
        ],
        ingestion="manual",
        raw_path="data/raw/imf/",
        description="Official historical FX rates for returns, volatility, depreciation.",
    ),
    DataSourceSpec(
        source_id="imf_ifs_weo",
        name="IMF IFS / WEO Macro Indicators",
        url="https://www.imf.org/en/Data",
        update_frequency="Monthly / annual",
        fields_needed=[
            "inflation_yoy",
            "gdp_growth",
            "reserves",
            "current_account",
            "policy_rate",
            "unemployment",
        ],
        license_notes="IMF data terms of use apply.",
        indices_used=[
            "Currency Credibility Index",
            "Dollar Dependency Index",
            "Currency Stress Index",
        ],
        ingestion="manual",
        raw_path="data/raw/imf/",
        description="CPI, GDP, reserves, current account, policy rates.",
    ),
    DataSourceSpec(
        source_id="world_bank_wdi",
        name="World Bank World Development Indicators",
        url="https://data.worldbank.org/",
        update_frequency="Annual",
        fields_needed=[
            "gdp_per_capita",
            "inflation",
            "remittances_gdp",
            "poverty",
            "trade_openness",
            "imports",
            "exports",
        ],
        license_notes="World Bank open data license.",
        indices_used=[
            "Remittance Welfare Loss Index",
            "Labor Conversion Index",
            "Dollar Dependency Index",
        ],
        ingestion="manual",
        raw_path="data/raw/world_bank_rpw/",
        description="Development context: remittances % GDP, poverty, trade.",
    ),
    DataSourceSpec(
        source_id="fred",
        name="FRED (Federal Reserve Economic Data)",
        url="https://fred.stlouisfed.org/",
        update_frequency="Daily / monthly",
        fields_needed=["DXY", "fed_funds", "treasury_yields", "cpi", "vix"],
        license_notes="FRED terms; attribution required.",
        indices_used=["Currency Stress Index", "Dollar Dependency Index"],
        ingestion="automated",
        raw_path="data/raw/fred/",
        description="Dollar shock and global risk regime via existing macro_loader.",
    ),
    DataSourceSpec(
        source_id="bis_fx_turnover",
        name="BIS Triennial FX Survey",
        url="https://www.bis.org/statistics/aboutfxstats.htm",
        update_frequency="Triennial",
        fields_needed=["currency", "fx_turnover_usd", "year", "global_turnover_share"],
        license_notes="BIS statistics terms; manual download typical.",
        indices_used=["Dollar Dependency Index", "Currency Liquidity Score"],
        ingestion="manual",
        raw_path="data/raw/bis/",
        description="FX market turnover, currency hierarchy, dollar dominance.",
    ),
    DataSourceSpec(
        source_id="manual",
        name="Manual Research Files",
        url="N/A — local drop folder",
        update_frequency="Ad hoc",
        fields_needed=[
            "policy_rates",
            "provider_samples",
            "country_risk_scores",
            "stablecoin_notes",
            "wage_data",
        ],
        license_notes="Researcher's responsibility to verify rights.",
        indices_used=[
            "Labor Conversion Index",
            "Currency Credibility Index",
            "Dollar Dependency Index",
        ],
        ingestion="manual",
        raw_path="data/raw/manual/",
        description="Spreadsheets, central bank rates, wage data, payment rail notes.",
    ),
    DataSourceSpec(
        source_id="fx_prices",
        name="FX Spot Prices (Lab Cache)",
        url="yfinance / FRED H.10 / vendor CSV",
        update_frequency="Daily",
        fields_needed=["date", "pair", "price", "returns", "volatility"],
        license_notes="Tier 1–4 per src/data_sources.py.",
        indices_used=["Hidden FX Tax Index", "Currency Stress Index"],
        ingestion="automated",
        raw_path="data/raw/fx_prices/",
        description="Existing lab FX price cache for volatility and timing risk.",
    ),
]


def sources_dataframe():
    import pandas as pd

    rows = []
    for s in DATA_SOURCES:
        rows.append(
            {
                "source_id": s.source_id,
                "name": s.name,
                "url": s.url,
                "update_frequency": s.update_frequency,
                "ingestion": s.ingestion,
                "indices": "; ".join(s.indices_used),
                "raw_path": s.raw_path,
            }
        )
    return pd.DataFrame(rows)


def get_source(source_id: str) -> DataSourceSpec:
    for s in DATA_SOURCES:
        if s.source_id == source_id:
            return s
    raise KeyError(f"Unknown source: {source_id}")
