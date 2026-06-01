# Data Sources — Stablecoin Settlement Window Lab

Registry of official, market, manual, and mock data sources. Full machine-readable registry: `stablecoin_lab/src/config/data_sources.py` and `stablecoin_lab/data/metadata/source_registry.json`.

## Credibility tiers

| Tier | Description |
|------|-------------|
| 1 | Central bank / BIS / IMF / World Bank / regulator |
| 2 | Regulated issuer attestation / public filing |
| 3 | Reputable market data provider |
| 4 | Manual assumption / expert estimate |
| 5 | Mock/demo only — **never use for inference** |

## Primary sources

| Source ID | Provider | Use |
|-----------|----------|-----|
| `fed_research` | Federal Reserve | Financial stability, reserves, cross-border payments |
| `bis_cpmi` | BIS CPMI | Settlement finality, singleness of money |
| `bis_innovation` | BIS Innovation Hub | Tokenization pilots, CBDC coexistence |
| `fsb` | Financial Stability Board | Stablecoin policy, implementation gaps |
| `circle_attestation` | Circle | USDC reserve composition |
| `tether_attestation` | Tether | USDT reserve composition |
| `defillama` | DeFiLlama | Circulating supply by chain |
| `coingecko` | CoinGecko | Price, peg deviation, volatility |
| `chain_data` | Public chain explorers | Fees, confirmation time, finality |
| `exchange_liquidity` | CEX / market data vendors | Secondary market depth |
| `world_bank_rpw` | World Bank RPW | Traditional remittance cost baseline |
| `imf_macro` | IMF | FX volatility, inflation controls |
| `bis_triennial_fx` | BIS | USD dominance, FX liquidity |
| `regulatory_events` | Regulators / curated research | Law changes, sanctions |
| `manual_assumptions` | Research team | Off-ramp times, legal finality placeholders |
| `MOCK_DEMO_ONLY` | Lab generator | Pipeline testing only |

## Where to place files

### Lab raw directory

```
stablecoin_lab/data/raw/
  stablecoin_supply/
  stablecoin_prices/
  stablecoin_reserves/
  chain_fees/
  chain_finality/
  exchange_liquidity/
  remittance_costs/
  fx_rates/
  macro/
  regulatory_events/
  issuer_attestations/
  manual/
```

### Medallion data lake (repo root)

```
data_lake/bronze_raw/stablecoins/
data_lake/silver_cleaned/stablecoin_supply/
data_lake/silver_cleaned/stablecoin_price_peg/
data_lake/silver_cleaned/stablecoin_reserves/
data_lake/silver_cleaned/blockchain_settlement_characteristics/
data_lake/silver_cleaned/off_ramp_characteristics/
data_lake/gold_research/stablecoin_finality_quality/
data_lake/gold_research/settlement_window_compression/
data_lake/gold_research/stablecoin_value_survival/
data_lake/gold_research/digital_run_velocity/
data_lake/gold_research/tokenized_money_singleness/
```

Bronze holds untouched extracts. Silver holds cleaned canonical tables. Gold holds research-ready index outputs.

## Required metadata (every row)

`source_id`, `methodology_version`, `mock_data_flag`, `data_quality_score`, `data_quality_grade`, `observed_vs_estimated_flag`, `credibility_tier`, extraction and publication dates where available.

## Checksums

After adding raw files:

```bash
shasum -a 256 stablecoin_lab/data/raw/**/*.csv
```

Record hashes in `stablecoin_lab/data/metadata/file_checksums.csv`.

## Official fetch (recommended)

```bash
cd stablecoin_lab
export PYTHONPATH=.
python scripts/fetch_stablecoin_data.py
```

| Fetch output | Tier | Source |
|--------------|------|--------|
| `stablecoin_supply/defillama_supply.csv` | 3 | DeFiLlama stablecoin API |
| `stablecoin_prices/defillama_prices.csv` | 3 | DeFiLlama prices |
| `issuer_attestations/reserve_attestations.csv` | 2 | Circle / Tether transparency pages |
| `manual/redemption_from_attestations.csv` | 2 | Derived redemption parameters |
| `remittance_costs/rpw_remittance_comparison.csv` | 1 + 4 | World Bank RPW + manual stablecoin rail |
| `regulatory_events/official_regulatory_events.csv` | 1 | MiCA, CFTC, CBN, Fed references |
| `manual/fed_stablecoin_research.csv` | 1 | Fed FEDS / research catalog |
| `manual/bis_tokenization_references.csv` | 1 | BIS Innovation Hub tokenization |
| `manual/bis_cpmi_bridge.csv` | 1 | Bridge from settlement_lab BIS CPMI |
| `chain_fees/`, `chain_finality/` | 4 | Documented chain settlement reference |

**Still manual:** off-ramp fee schedules (`data/raw/manual/off_ramp_assumptions.csv` — not yet populated by fetch).

## Next official sources to add

1. Exchange off-ramp fee schedules (Tier 3/4)
2. CoinGecko daily peg history (Tier 3)
3. IMF macro panel for dollarization controls (Tier 1)
4. Live chain fee scrapes replacing reference table (Tier 3)
