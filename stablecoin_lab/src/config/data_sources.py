"""
Official and manual data source registry for Stablecoin Settlement Window Lab.

Credibility tiers:
  Tier 1: central bank / BIS / IMF / World Bank / regulator
  Tier 2: regulated issuer attestation / public filing
  Tier 3: reputable market data provider
  Tier 4: manual assumption / expert estimate
  Tier 5: mock/demo only
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StablecoinDataSource:
    source_id: str
    name: str
    provider: str
    url_placeholder: str
    expected_files: list[str]
    required_fields: list[str]
    optional_fields: list[str] = field(default_factory=list)
    update_frequency: str = "monthly"
    credibility_tier: int = 1
    usage_notes: str = ""
    limitations: str = ""
    indices_supported: list[str] = field(default_factory=list)


DATA_SOURCES: list[StablecoinDataSource] = [
    StablecoinDataSource(
        source_id="fed_research",
        name="Federal Reserve Research / FEDS Notes",
        provider="Federal Reserve System",
        url_placeholder="https://www.federalreserve.gov/econres/feds/",
        expected_files=["stablecoin_financial_stability.csv"],
        required_fields=["date", "stablecoin", "topic"],
        credibility_tier=1,
        usage_notes="Financial-stability implications, reserves, monetary policy, cross-border payments.",
        indices_supported=["SFQI", "SWC", "SDI"],
    ),
    StablecoinDataSource(
        source_id="bis_cpmi",
        name="BIS CPMI Payment and Settlement Reports",
        provider="Bank for International Settlements",
        url_placeholder="https://www.bis.org/cpmi/",
        expected_files=["cpmi_tokenization.csv", "settlement_finality.csv"],
        required_fields=["payment_system", "settlement_lag", "country"],
        credibility_tier=1,
        usage_notes="Settlement finality, singleness of money, cross-border payment roadmap.",
        indices_supported=["SFQI", "SWC", "TMS"],
    ),
    StablecoinDataSource(
        source_id="bis_innovation",
        name="BIS Innovation Hub / Project Reports",
        provider="BIS Innovation Hub",
        url_placeholder="https://www.bis.org/about/bisih/",
        expected_files=["project_agora_notes.csv", "tokenization_pilots.csv"],
        required_fields=["project", "date", "jurisdiction"],
        credibility_tier=1,
        usage_notes="Tokenization pilots, CBDC/stablecoin coexistence, cross-border design.",
        indices_supported=["SFQI", "TMS"],
    ),
    StablecoinDataSource(
        source_id="fsb",
        name="FSB Global Stablecoin / Crypto Policy",
        provider="Financial Stability Board",
        url_placeholder="https://www.fsb.org/work-of-the-fsb/",
        expected_files=["fsb_stablecoin_policy.csv"],
        required_fields=["date", "jurisdiction", "policy_area"],
        credibility_tier=1,
        usage_notes="Regulation, financial stability, implementation gaps.",
        indices_supported=["CSD", "DRV"],
    ),
    StablecoinDataSource(
        source_id="circle_attestation",
        name="Circle USDC Reserve Attestations",
        provider="Circle / regulated auditor",
        url_placeholder="https://www.circle.com/en/transparency",
        expected_files=["usdc_reserve_attestation.csv"],
        required_fields=["date", "total_reserves_usd", "attestation_date"],
        credibility_tier=2,
        usage_notes="Reserve composition, T-bills, cash, repo for USDC.",
        indices_supported=["SLT", "SFQI", "TMS"],
    ),
    StablecoinDataSource(
        source_id="tether_attestation",
        name="Tether Reserve Attestations",
        provider="Tether / attestation provider",
        url_placeholder="https://tether.to/en/transparency/",
        expected_files=["usdt_reserve_attestation.csv"],
        required_fields=["date", "total_reserves_usd"],
        credibility_tier=2,
        usage_notes="Reserve composition and liquidity profile for USDT.",
        indices_supported=["SLT", "SFQI", "TMS"],
    ),
    StablecoinDataSource(
        source_id="defillama",
        name="DeFiLlama Stablecoin Supply",
        provider="DeFiLlama",
        url_placeholder="https://defillama.com/stablecoins",
        expected_files=["stablecoin_supply.csv"],
        required_fields=["date", "stablecoin", "supply_usd"],
        update_frequency="daily",
        credibility_tier=3,
        usage_notes="Circulating supply, chain breakdown, market cap proxies.",
        indices_supported=["SDI", "SLT", "DRV"],
    ),
    StablecoinDataSource(
        source_id="coingecko",
        name="CoinGecko Market Data",
        provider="CoinGecko",
        url_placeholder="https://www.coingecko.com/",
        expected_files=["stablecoin_prices.csv"],
        required_fields=["timestamp", "stablecoin", "price_usd"],
        update_frequency="daily",
        credibility_tier=3,
        usage_notes="Price, peg deviation, intraday volatility.",
        indices_supported=["SFQI", "TMS"],
    ),
    StablecoinDataSource(
        source_id="chain_data",
        name="Blockchain Network Metrics",
        provider="Public chain explorers / node APIs",
        url_placeholder="varies by network",
        expected_files=["chain_fees.csv", "chain_finality.csv"],
        required_fields=["date", "blockchain_network", "average_transaction_fee_usd"],
        update_frequency="daily",
        credibility_tier=3,
        usage_notes="Fees, confirmation time, finality assumptions, outages.",
        indices_supported=["SFQI", "SWC", "CSD"],
    ),
    StablecoinDataSource(
        source_id="exchange_liquidity",
        name="Exchange Liquidity / Market Depth",
        provider="CEX public data / market data vendors",
        url_placeholder="varies",
        expected_files=["stablecoin_orderbook_summary.csv"],
        required_fields=["date", "stablecoin", "bid_ask_spread_bps"],
        credibility_tier=3,
        usage_notes="Secondary market stress, redemption/arb liquidity.",
        indices_supported=["DRV", "TMS"],
    ),
    StablecoinDataSource(
        source_id="world_bank_rpw",
        name="World Bank Remittance Prices Worldwide",
        provider="World Bank",
        url_placeholder="https://remittanceprices.worldbank.org/",
        expected_files=["rpw_corridors.csv"],
        required_fields=["sender_country", "receiver_country", "fee_pct"],
        credibility_tier=1,
        usage_notes="Baseline remittance costs vs stablecoin corridor comparisons.",
        indices_supported=["SVSI"],
    ),
    StablecoinDataSource(
        source_id="imf_macro",
        name="IMF Exchange Rates and Macro",
        provider="IMF",
        url_placeholder="https://data.imf.org/",
        expected_files=["fx_rates.csv", "macro_indicators.csv"],
        required_fields=["country", "date"],
        credibility_tier=1,
        usage_notes="FX volatility, inflation, dollarization pressure controls.",
        indices_supported=["SDI", "SVSI"],
    ),
    StablecoinDataSource(
        source_id="bis_triennial_fx",
        name="BIS Triennial FX Survey",
        provider="BIS",
        url_placeholder="https://www.bis.org/statistics/aboutfxstats.htm",
        expected_files=["fx_turnover.csv"],
        required_fields=["currency", "fx_turnover_usd", "year"],
        credibility_tier=1,
        usage_notes="USD dominance, FX liquidity hierarchy.",
        indices_supported=["SDI", "SWC"],
    ),
    StablecoinDataSource(
        source_id="regulatory_events",
        name="Regulatory and Enforcement Events",
        provider="Regulators / curated research",
        url_placeholder="N/A",
        expected_files=["regulatory_events.csv"],
        required_fields=["event_id", "date", "event_type"],
        credibility_tier=1,
        usage_notes="Stablecoin law changes, sanctions, issuer restrictions.",
        indices_supported=["CSD", "DRV"],
    ),
    StablecoinDataSource(
        source_id="manual_assumptions",
        name="Manual Expert Assumptions",
        provider="Research team",
        url_placeholder="N/A",
        expected_files=["stablecoin_assumptions.csv"],
        required_fields=["assumption_id", "value"],
        credibility_tier=4,
        usage_notes="Off-ramp times, redemption gates, legal finality placeholders.",
        limitations="Never treat as official data; always run sensitivity analysis.",
        indices_supported=["SFQI", "SWC", "CSD", "SVSI"],
    ),
    StablecoinDataSource(
        source_id="MOCK_DEMO_ONLY",
        name="Synthetic Demo Data",
        provider="Stablecoin Lab generator",
        url_placeholder="N/A",
        expected_files=[],
        required_fields=[],
        credibility_tier=5,
        usage_notes="Stage 1 synthetic data for pipeline testing only.",
        limitations="Do not use for research conclusions or investment decisions.",
        indices_supported=["SFQI", "SWC", "SLT", "DRV", "SDI", "TMS", "CSD", "SVSI"],
    ),
]


def get_source(source_id: str) -> StablecoinDataSource:
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


def sources_to_registry_dict() -> list[dict]:
    return [
        {
            "source_id": s.source_id,
            "name": s.name,
            "provider": s.provider,
            "url_placeholder": s.url_placeholder,
            "expected_files": s.expected_files,
            "required_fields": s.required_fields,
            "optional_fields": s.optional_fields,
            "update_frequency": s.update_frequency,
            "credibility_tier": s.credibility_tier,
            "usage_notes": s.usage_notes,
            "limitations": s.limitations,
            "indices_supported": s.indices_supported,
        }
        for s in DATA_SOURCES
    ]
