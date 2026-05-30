"""
Central registry of FX data sources and quality tiers.

Tier 1 (best public research) → Tier 4 (prototype/dev).
Lower tier number = higher data quality.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# Tier 1 = highest quality. Tier 4 = prototype/dev only.
DATA_TIERS: Dict[int, Dict[str, str]] = {
    1: {
        "slug": "official",
        "label": "Official / academic-grade",
        "summary": "FRED, Federal Reserve H.10, BIS, IMF, World Bank, central banks",
    },
    2: {
        "slug": "professional",
        "label": "Professional market data",
        "summary": "Bloomberg, LSEG/Refinitiv, FactSet, CME, Cboe FX, EBS, 360T, FXall",
    },
    3: {
        "slug": "proprietary",
        "label": "Proprietary data",
        "summary": "Payment flows, order flow, settlement timing, hedge execution data",
    },
    4: {
        "slug": "prototype",
        "label": "Prototype data",
        "summary": "Yahoo/yfinance, Stooq, free web sources",
    },
}

# Map each registry key → tier number (1–4)
SOURCE_TIER_NUMBER: Dict[str, int] = {
    "yfinance": 4,
    "stooq": 4,
    "fred": 1,
    "fed_h10": 1,
    "bis_eer": 1,
    "imf_ifs": 1,
    "world_bank_remittances": 1,
    "banxico": 1,
    "banxico_remittances": 1,
    "fed_rates": 1,
    "central_bank_policy_rates": 1,
    "cme_datamine": 2,
    "bloomberg": 2,
    "lseg_refinitiv": 2,
    "factset": 2,
    "cboe_fx": 2,
    "ebs": 2,
    "360t": 2,
    "fxall": 2,
    "bank_quotes": 2,
    "proprietary_payment_flows": 3,
    "proprietary_order_flow": 3,
}

# Backward compatibility for old tier slug names
LEGACY_TIER_SLUGS: Dict[str, int] = {
    "academic": 1,
    "official": 1,
    "trading_grade": 2,
    "professional": 2,
    "proprietary_edge": 3,
    "proprietary": 3,
    "prototype": 4,
}


def tier_number_to_slug(n: int) -> str:
    return DATA_TIERS[n]["slug"]


def tier_number_to_label(n: int) -> str:
    return DATA_TIERS[n]["label"]


def normalize_tier_number(tier: Union[int, str]) -> int:
    """Resolve tier number from int, slug, or legacy slug."""
    if isinstance(tier, int):
        if tier in DATA_TIERS:
            return tier
        raise ValueError(f"Invalid tier number: {tier}")
    slug = str(tier).lower().strip()
    if slug.isdigit():
        return normalize_tier_number(int(slug))
    if slug in LEGACY_TIER_SLUGS:
        return LEGACY_TIER_SLUGS[slug]
    for num, meta in DATA_TIERS.items():
        if slug == meta["slug"]:
            return num
    raise ValueError(f"Unknown tier: {tier}")


def enrich_source(key: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    """Add tier_number, tier slug, and tier_label to a source record."""
    n = SOURCE_TIER_NUMBER.get(key, 4)
    out = {"key": key, **meta}
    out["tier_number"] = n
    out["tier"] = tier_number_to_slug(n)
    out["tier_label"] = tier_number_to_label(n)
    return out


DATA_SOURCE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "yfinance": {
        "name": "Yahoo Finance (yfinance)",
        "data_type": "FX spot, equities, macro proxies",
        "official_status": "unofficial",
        "cost_tier": "free",
        "update_frequency": "daily (varies by ticker)",
        "strengths": "Free, easy API, long history for many pairs",
        "weaknesses": "Unofficial, may break, inconsistent close times, not executable",
        "licensing_notes": "Terms of use restrict redistribution; not for commercial data resale",
        "best_use_case": "Prototype backtests, dashboards, code testing",
        "public_url": "https://finance.yahoo.com",
    },
    "stooq": {
        "name": "Stooq",
        "data_type": "FX spot, equities",
        "official_status": "unofficial",
        "cost_tier": "free",
        "update_frequency": "daily",
        "strengths": "Free CSV download, fallback when Yahoo fails",
        "weaknesses": "Unofficial, limited metadata, not research-grade",
        "licensing_notes": "Check Stooq terms; not institutionally recognized",
        "best_use_case": "Fallback spot prices for local development",
        "public_url": "https://stooq.com",
    },
    "fred": {
        "name": "FRED (Federal Reserve Economic Data)",
        "data_type": "Rates, FX indices, macro series",
        "official_status": "official",
        "cost_tier": "free",
        "update_frequency": "daily to monthly depending on series",
        "strengths": "Official US macro source, long history, citable",
        "weaknesses": "Not all FX pairs; may lag; no bid/ask",
        "licensing_notes": "Public domain with attribution; see FRED terms",
        "best_use_case": "Random-walk tests, macro FX research, rate differentials",
        "public_url": "https://fred.stlouisfed.org",
    },
    "fed_h10": {
        "name": "Federal Reserve H.10",
        "data_type": "G.5/H.10 foreign exchange rates",
        "official_status": "official",
        "cost_tier": "free",
        "update_frequency": "daily (business days)",
        "strengths": "Official US FX reference rates, publication-quality",
        "weaknesses": "Daily only; no intraday; no forward points",
        "licensing_notes": "Public domain; Federal Reserve Board",
        "best_use_case": "Academic memos, official spot benchmarks",
        "public_url": "https://www.federalreserve.gov/releases/h10/",
    },
    "bis_eer": {
        "name": "BIS Effective Exchange Rates",
        "data_type": "Nominal and real effective exchange rate indices",
        "official_status": "official",
        "cost_tier": "free",
        "update_frequency": "daily/monthly",
        "strengths": "Institutionally recognized, cross-country comparability",
        "weaknesses": "Indices not bilateral spot; no execution prices",
        "licensing_notes": "BIS terms apply; attribution required",
        "best_use_case": "Macro competitiveness, broad FX pressure research",
        "public_url": "https://www.bis.org/statistics/eer.htm",
    },
    "imf_ifs": {
        "name": "IMF International Financial Statistics",
        "data_type": "FX, reserves, macro financial statistics",
        "official_status": "official",
        "cost_tier": "free/paid tiers",
        "update_frequency": "monthly/quarterly for many series",
        "strengths": "Global coverage, citable, long histories",
        "weaknesses": "Often low frequency; revisions; not trading-grade",
        "licensing_notes": "IMF data use policy; check redistribution rules",
        "best_use_case": "Cross-country macro FX research",
        "public_url": "https://data.imf.org",
    },
    "world_bank_remittances": {
        "name": "World Bank Remittance Data",
        "data_type": "Remittance inflows/outflows by corridor",
        "official_status": "official",
        "cost_tier": "free",
        "update_frequency": "annual",
        "strengths": "Official remittance statistics, corridor context",
        "weaknesses": "Annual frequency; not order-flow; lagged",
        "licensing_notes": "World Bank open data terms",
        "best_use_case": "Payment-corridor context, seasonality hypotheses",
        "public_url": "https://www.worldbank.org/en/topic/migrationremittances",
    },
    "banxico": {
        "name": "Banxico (Banco de México)",
        "data_type": "USD/MXN fix, rates, reserves",
        "official_status": "official",
        "cost_tier": "free",
        "update_frequency": "daily",
        "strengths": "Official Mexico FX and policy data",
        "weaknesses": "Mexico-specific; may differ from global vendor closes",
        "licensing_notes": "Banxico terms; attribution required",
        "best_use_case": "USD/MXN academic research, official fix comparison",
        "public_url": "https://www.banxico.org.mx",
    },
    "banxico_remittances": {
        "name": "Banco de México Remittances",
        "data_type": "Remittance inflows to Mexico",
        "official_status": "official",
        "cost_tier": "free",
        "update_frequency": "monthly",
        "strengths": "Official corridor flow context for USD/MXN",
        "weaknesses": "Monthly; not transaction-level",
        "licensing_notes": "Banxico terms",
        "best_use_case": "Remittance seasonality research for USD/MXN",
        "public_url": "https://www.banxico.org.mx",
    },
    "fed_rates": {
        "name": "Federal Reserve Interest Rates",
        "data_type": "Policy and money market rates",
        "official_status": "official",
        "cost_tier": "free",
        "update_frequency": "daily",
        "strengths": "Official US rate benchmarks for carry research",
        "weaknesses": "Not forward points; not executable FX",
        "licensing_notes": "Public domain",
        "best_use_case": "Carry research, rate differential features",
        "public_url": "https://www.federalreserve.gov",
    },
    "central_bank_policy_rates": {
        "name": "Central Bank Policy Rates (aggregate)",
        "data_type": "Policy rates by country",
        "official_status": "official",
        "cost_tier": "free",
        "update_frequency": "event-driven to daily",
        "strengths": "Carry and macro framing",
        "weaknesses": "Heterogeneous sources; not FX execution data",
        "licensing_notes": "Varies by central bank",
        "best_use_case": "Cross-country carry and macro regime research",
        "public_url": None,
    },
    "cme_datamine": {
        "name": "CME DataMine",
        "data_type": "Futures, FX futures, settlement",
        "official_status": "official exchange",
        "cost_tier": "paid",
        "update_frequency": "intraday to daily",
        "strengths": "Exchange-quality futures and settlement data",
        "weaknesses": "Paid; licensing; not spot OTC bid/ask",
        "licensing_notes": "CME Group license required",
        "best_use_case": "Futures-based FX research, settlement analysis",
        "public_url": "https://datamine.cme.com",
    },
    "bloomberg": {
        "name": "Bloomberg Terminal / B-PIPE",
        "data_type": "Spot, forwards, swaps, options, macro",
        "official_status": "professional vendor",
        "cost_tier": "paid",
        "update_frequency": "real-time to daily",
        "strengths": "Comprehensive FX, forwards, spreads, liquidity",
        "weaknesses": "Expensive; license restrictions; not publicly publishable raw data",
        "licensing_notes": "Bloomberg agreement; no public redistribution",
        "best_use_case": "Professional FX strategy, carry, execution, hedging research",
        "public_url": "https://www.bloomberg.com/professional",
    },
    "lseg_refinitiv": {
        "name": "LSEG / Refinitiv",
        "data_type": "Spot, forwards, swaps, tick history",
        "official_status": "professional vendor",
        "cost_tier": "paid",
        "update_frequency": "real-time to daily",
        "strengths": "Deep FX history, forwards, executable research",
        "weaknesses": "Expensive; licensing; access via institution",
        "licensing_notes": "LSEG data license required",
        "best_use_case": "Trading-grade backtests, forward points, execution",
        "public_url": "https://www.lseg.com/en/data-analytics",
    },
    "factset": {
        "name": "FactSet",
        "data_type": "FX, macro, corporate fundamentals",
        "official_status": "professional vendor",
        "cost_tier": "paid",
        "update_frequency": "real-time to daily",
        "strengths": "Integrated macro and corporate data for treasury research",
        "weaknesses": "Paid; not all FX microstructure",
        "licensing_notes": "FactSet license required",
        "best_use_case": "Corporate treasury and macro FX research",
        "public_url": "https://www.factset.com",
    },
    "cboe_fx": {
        "name": "Cboe FX",
        "data_type": "FX spot and ECN trade data",
        "official_status": "official exchange/ECN",
        "cost_tier": "paid",
        "update_frequency": "intraday",
        "strengths": "Trade-based FX, useful for microstructure",
        "weaknesses": "Not full OTC market; paid access",
        "licensing_notes": "Cboe license required",
        "best_use_case": "Execution and liquidity research",
        "public_url": "https://www.cboe.com",
    },
    "ebs": {
        "name": "EBS (ICAP / CME)",
        "data_type": "Interbank FX spot platform data",
        "official_status": "professional platform",
        "cost_tier": "paid",
        "update_frequency": "tick to daily",
        "strengths": "Major FX liquidity benchmark",
        "weaknesses": "Institutional access only; expensive",
        "licensing_notes": "Platform license required",
        "best_use_case": "Interbank spot and liquidity research",
        "public_url": None,
    },
    "360t": {
        "name": "360T",
        "data_type": "FX trading platform quotes and trades",
        "official_status": "professional platform",
        "cost_tier": "paid",
        "update_frequency": "intraday",
        "strengths": "Corporate and bank FX execution context",
        "weaknesses": "Private platform data; licensing",
        "licensing_notes": "360T / Deutsche Börse terms",
        "best_use_case": "Corporate FX execution and hedge cost research",
        "public_url": "https://www.360t.com",
    },
    "fxall": {
        "name": "FXall (Refinitiv)",
        "data_type": "Multibank FX trading, RFQ, forwards",
        "official_status": "professional platform",
        "cost_tier": "paid",
        "update_frequency": "intraday",
        "strengths": "Multibank quotes, forward and spot execution research",
        "weaknesses": "Institutional only; not public",
        "licensing_notes": "Refinitiv / FXall license",
        "best_use_case": "Hedge execution cost and forward-point research",
        "public_url": None,
    },
    "bank_quotes": {
        "name": "Bank Quote History",
        "data_type": "Customer and interbank FX quotes",
        "official_status": "proprietary institutional",
        "cost_tier": "paid/internal",
        "update_frequency": "intraday",
        "strengths": "Realistic spreads and executable prices",
        "weaknesses": "Not public; bank-specific; compliance restrictions",
        "licensing_notes": "Internal use only; no public publication without approval",
        "best_use_case": "Realistic hedge and transaction cost modeling",
        "public_url": None,
    },
    "proprietary_payment_flows": {
        "name": "Proprietary Payment Flows",
        "data_type": "Corridor payment volumes, timing, payout demand",
        "official_status": "proprietary",
        "cost_tier": "internal",
        "update_frequency": "real-time to daily",
        "strengths": "Unique corridor pressure signal before public macro",
        "weaknesses": "Private; compliance; cannot publish without permission",
        "licensing_notes": "Employer legal/compliance approval required",
        "best_use_case": "Payment-corridor FX pressure, internal hedge tools",
        "public_url": None,
    },
    "proprietary_order_flow": {
        "name": "Proprietary Order Flow",
        "data_type": "Customer order flow, transaction count, net demand",
        "official_status": "proprietary",
        "cost_tier": "internal",
        "update_frequency": "real-time",
        "strengths": "Potential edge in flow-pressure research",
        "weaknesses": "Highly sensitive; legal and privacy constraints",
        "licensing_notes": "Strict internal use; no external publication",
        "best_use_case": "Internal alpha and corridor-pressure models",
        "public_url": None,
    },
}

# FRED series for official USD/MXN (H.10 daily rate, MXN per USD)
FRED_H10_USDMXN_SERIES = "DEXMXUS"


def get_data_source(source_key: str) -> Dict[str, Any]:
    """Return metadata for a registered source (includes tier_number and tier_label)."""
    if source_key not in DATA_SOURCE_REGISTRY:
        raise KeyError(f"Unknown data source: {source_key}. Known: {list(DATA_SOURCE_REGISTRY)}")
    return enrich_source(source_key, DATA_SOURCE_REGISTRY[source_key])


def list_sources_by_tier(tier: Union[int, str]) -> List[Dict[str, Any]]:
    """Return all sources in a tier (by number 1–4 or slug)."""
    n = normalize_tier_number(tier)
    return [
        enrich_source(k, v)
        for k, v in DATA_SOURCE_REGISTRY.items()
        if SOURCE_TIER_NUMBER.get(k, 4) == n
    ]


def list_sources_by_tier_number(tier_number: int) -> List[Dict[str, Any]]:
    """Return all sources for tier number 1–4."""
    return list_sources_by_tier(tier_number)


def list_sources_by_use_case(keyword: str) -> List[Dict[str, Any]]:
    """Search best_use_case and data_type for keyword (case-insensitive)."""
    kw = keyword.lower()
    hits = []
    for key, meta in DATA_SOURCE_REGISTRY.items():
        hay = f"{meta.get('best_use_case', '')} {meta.get('data_type', '')}".lower()
        if kw in hay:
            hits.append(enrich_source(key, meta))
    return hits


def print_data_source_plan() -> None:
    """Print phased data upgrade plan (Tier 1 = best)."""
    plan = """
BR3N Macro Labs — Data Tier Stack (Tier 1 = highest quality)
============================================================

Tier 1 — Official / academic-grade (public research)
  - Federal Reserve H.10
  - FRED (e.g. DEXMXUS for USD/MXN)
  - BIS effective exchange rates
  - IMF International Financial Statistics
  - World Bank remittances
  - Banxico / central banks

Tier 2 — Professional market data (requires license)
  - Bloomberg
  - LSEG / Refinitiv
  - FactSet
  - CME DataMine
  - Cboe FX
  - EBS
  - 360T
  - FXall
  - bank quotes

Tier 3 — Proprietary data (internal only)
  - payment corridor flows
  - order flow
  - settlement timing
  - hedge execution data

Tier 4 — Prototype data (development only)
  - yfinance
  - Stooq
  - free web sources

Principle: Always record source name, tier number, and tier label with every test.
Current lab default: Tier 4 (yfinance). Upgrade path: fetch Tier 1 via FRED/H.10.
"""
    print(plan.strip())


def export_data_source_registry(path: Optional[Path] = None) -> Path:
    """Export enriched registry to CSV."""
    path = path or ROOT / "data" / "outputs" / "data_source_registry.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [enrich_source(k, v) for k, v in DATA_SOURCE_REGISTRY.items()]
    pd.DataFrame(rows).to_csv(path, index=False)
    return path
