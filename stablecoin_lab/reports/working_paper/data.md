# Data (Draft)

## Sources

Tier 1–3 sources documented in [DATA_SOURCES_STABLECOIN.md](../../../DATA_SOURCES_STABLECOIN.md).

## Canonical tables

- `stablecoin_supply` — circulating supply by stablecoin and chain
- `stablecoin_price_peg` — peg deviation and volatility
- `stablecoin_reserves` — attestation-based reserve composition
- `blockchain_settlement_characteristics` — confirmation time, fees, congestion
- `stablecoin_redemption_characteristics` — redemption windows, gates
- `off_ramp_characteristics` — corridor compliance and off-ramp delays
- `remittance_comparison` — stablecoin vs traditional corridor costs
- `regulatory_events` — policy and enforcement timeline

## Data quality

Every row carries `source_id`, `mock_data_flag`, `data_quality_score`, `methodology_version`. Mock demo data capped at score 30.

## Medallion layout

Bronze: `data_lake/bronze_raw/stablecoins/`  
Silver: `data_lake/silver_cleaned/*`  
Gold: `data_lake/gold_research/*`

## Current status

Pipeline runs on labeled synthetic demo data until official files are ingested. Mixed mode flags when curated and mock rows coexist.
