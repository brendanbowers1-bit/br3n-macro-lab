"""
Official and manual data source registry for Settlement Economics Lab.

Credibility tiers:
  Tier 1: official statistical agency, central bank, BIS, IMF, World Bank
  Tier 2: regulated public company filings
  Tier 3: reputable industry reports
  Tier 4: manually collected or expert assumption
  Tier 5: mock/demo only
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SettlementDataSource:
    source_id: str
    name: str
    provider: str
    url_placeholder: str
    expected_files: list[str]
    required_fields: list[str]
    optional_fields: list[str] = field(default_factory=list)
    update_frequency: str = "annual"
    credibility_tier: int = 1
    usage_notes: str = ""
    limitations: str = ""
    indices_supported: list[str] = field(default_factory=list)


DATA_SOURCES: list[SettlementDataSource] = [
    SettlementDataSource(
        source_id="bis_cpmi",
        name="BIS CPMI Reports and Datasets",
        provider="Bank for International Settlements",
        url_placeholder="https://www.bis.org/cpmi/",
        expected_files=["cpmi_payment_systems.csv", "cpmi_cross_border.csv"],
        required_fields=["payment_system", "country", "transaction_value", "settlement_lag"],
        update_frequency="annual",
        credibility_tier=1,
        usage_notes="Payment systems, RTGS, cross-border frictions, liquidity-saving mechanisms.",
        limitations="Coverage varies by jurisdiction; not all rails reported uniformly.",
        indices_supported=["SDI", "OLB", "FQI", "PNF"],
    ),
    SettlementDataSource(
        source_id="bis_triennial_fx",
        name="BIS Triennial FX Survey",
        provider="BIS",
        url_placeholder="https://www.bis.org/statistics/aboutfxstats.htm",
        expected_files=["fx_turnover.csv"],
        required_fields=["currency", "fx_turnover_usd", "year"],
        credibility_tier=1,
        usage_notes="FX liquidity, currency turnover, settlement currency hierarchy.",
        indices_supported=["SDI", "PNF"],
    ),
    SettlementDataSource(
        source_id="world_bank_findex",
        name="World Bank Global Findex",
        provider="World Bank",
        url_placeholder="https://www.worldbank.org/en/publication/globalfindex",
        expected_files=["findex_indicators.csv"],
        required_fields=["country", "year", "account_ownership_pct"],
        credibility_tier=1,
        usage_notes="Account access, digital payments, financial inclusion.",
        indices_supported=["PFI", "FQI"],
    ),
    SettlementDataSource(
        source_id="world_bank_rpw",
        name="World Bank Remittance Prices Worldwide",
        provider="World Bank",
        url_placeholder="https://remittanceprices.worldbank.org/",
        expected_files=["rpw_corridors.csv"],
        required_fields=["sender_country", "receiver_country", "fee_pct", "fx_margin_pct"],
        credibility_tier=1,
        usage_notes="Cross-border payment costs, transfer speed.",
        indices_supported=["SDI", "PFI"],
    ),
    SettlementDataSource(
        source_id="imf",
        name="IMF Datasets",
        provider="IMF",
        url_placeholder="https://data.imf.org/",
        expected_files=["fx_rates.csv", "macro_indicators.csv"],
        required_fields=["country", "date"],
        credibility_tier=1,
        usage_notes="FX rates, reserves, BoP, macro vulnerability.",
        indices_supported=["SDI", "PNF", "OLB"],
    ),
    SettlementDataSource(
        source_id="fred",
        name="FRED / Federal Reserve",
        provider="Federal Reserve Bank of St. Louis",
        url_placeholder="https://fred.stlouisfed.org/",
        expected_files=["sofr.csv", "fed_funds.csv", "financial_stress.csv"],
        required_fields=["date", "value"],
        update_frequency="daily",
        credibility_tier=1,
        usage_notes="SOFR, fed funds, Treasury yields, financial stress.",
        indices_supported=["SDI", "OLB", "PNF"],
    ),
    SettlementDataSource(
        source_id="ecb_payments",
        name="ECB Payment Statistics",
        provider="European Central Bank",
        url_placeholder="https://www.ecb.europa.eu/stats/",
        expected_files=["target_statistics.csv"],
        required_fields=["payment_system", "transaction_value"],
        credibility_tier=1,
        usage_notes="TARGET/TIPS settlement volumes and values.",
        indices_supported=["SDI", "OLB", "FQI"],
    ),
    SettlementDataSource(
        source_id="swift_public",
        name="SWIFT Public Reports",
        provider="SWIFT",
        url_placeholder="https://www.swift.com/",
        expected_files=["rmb_tracker.csv"],
        required_fields=["currency", "share_pct"],
        credibility_tier=3,
        usage_notes="Cross-border payment currency share.",
        indices_supported=["PNF", "PFI"],
    ),
    SettlementDataSource(
        source_id="company_filings",
        name="Company Public Reports",
        provider="Regulated issuers",
        url_placeholder="SEC EDGAR / company IR",
        expected_files=["payment_volume_disclosures.csv"],
        required_fields=["company", "year"],
        credibility_tier=2,
        usage_notes="Payment volume, settlement risk language, liquidity disclosures.",
        indices_supported=["OLB", "PNF", "PFI"],
    ),
    SettlementDataSource(
        source_id="manual_assumptions",
        name="Manual Expert Assumptions",
        provider="Research team",
        url_placeholder="N/A",
        expected_files=["settlement_assumptions.csv"],
        required_fields=["assumption_id", "value"],
        credibility_tier=4,
        usage_notes="Settlement cutoffs, reconciliation costs, failure-risk estimates.",
        limitations="Never treat as official data; always run sensitivity analysis.",
        indices_supported=["SDI", "OLB", "FQI", "PNF", "PFI"],
    ),
    SettlementDataSource(
        source_id="MOCK_DEMO_ONLY",
        name="Synthetic Demo Data",
        provider="Settlement Lab generator",
        url_placeholder="N/A",
        expected_files=[],
        required_fields=[],
        credibility_tier=5,
        usage_notes="Stage 1 synthetic data for pipeline testing only.",
        limitations="Do not use for research conclusions.",
        indices_supported=["SDI", "OLB", "FQI", "PNF", "PFI"],
    ),
]


def get_source(source_id: str) -> SettlementDataSource:
    for s in DATA_SOURCES:
        if s.source_id == source_id:
            return s
    raise KeyError(f"Unknown source: {source_id}")


def sources_dataframe():
    import pandas as pd

    return pd.DataFrame(
        [
            {
                "source_id": s.source_id,
                "name": s.name,
                "provider": s.provider,
                "credibility_tier": s.credibility_tier,
                "update_frequency": s.update_frequency,
                "indices": "; ".join(s.indices_supported),
            }
            for s in DATA_SOURCES
        ]
    )
