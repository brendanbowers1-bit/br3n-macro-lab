# Source Registry

**Authoritative file:** `data-lake/metadata/source_registry.json`  
**Lab:** Bowers Frontier Macro Labs

## Purpose

Single registry of **all data sources** — connected, starter, or placeholder — with license notes, reliability scores, and retrieval methods. No dashboard field should reference a source not listed here.

## How to use

1. Look up `source_id` before building a feature or chart.
2. Add new sources to JSON before placing files in `data-lake/raw/`.
3. Update `last_updated` and `data_mode` when ingesting.
4. Cross-reference `data-lake/metadata/data_catalog.json` for file paths.

## Summary by category

### FX (4 sources)

| source_id | Name | Status |
|-----------|------|--------|
| `fx_usd_mxn_spot` | USD/MXN spot | planned |
| `fx_dxy` | DXY | planned |
| `fx_usd_mxn_forward_points` | Forward points | placeholder |
| `fx_usd_mxn_spread_proxy` | Bid/ask spread proxy | placeholder |

### Rates (4 sources)

| source_id | Name | Status |
|-----------|------|--------|
| `rates_fed_policy` | Fed policy rate | planned |
| `rates_banxico_policy` | Banxico policy rate | planned |
| `rates_us_treasury` | US Treasury yields | planned |
| `rates_mx_gov_yield` | Mexico gov yield | placeholder |

### Macro (5 sources)

| source_id | Name | Status |
|-----------|------|--------|
| `macro_us_cpi` | US CPI | planned |
| `macro_mx_cpi` | Mexico CPI | planned |
| `macro_us_payrolls` | US payrolls | planned |
| `macro_mx_inflation` | Mexico inflation | planned |
| `macro_central_bank_dates` | CB decision dates | planned |

### Corridor (6 sources)

| source_id | Name | Status |
|-----------|------|--------|
| `corridor_us_mx_remittances_banxico` | US→MX remittances | **research_starter (active)** |
| `rates_fed_policy` | Fed policy rate (DFEDTARU) | **live (active)** |
| `corridor_remittance_cost_proxy` | Remittance cost (RPW) | planned |
| `corridor_holiday_calendar` | Holiday calendar | planned |
| `corridor_settlement_calendar` | Settlement calendar | placeholder |
| `corridor_liquidity_proxy` | Liquidity proxy | placeholder |
| `corridor_sanctions_compliance` | Sanctions/compliance events | placeholder |

### Stablecoin (3 sources)

| source_id | Name | Status |
|-----------|------|--------|
| `stablecoin_supply` | Stablecoin supply | placeholder |
| `stablecoin_settlement_rail_research` | Settlement rail research | placeholder |
| `stablecoin_onchain_volume` | On-chain volume | placeholder |

**Total:** 22 registered sources — **2 active** (remittances + FRED policy), **11 planned**, **9 placeholder**

## Required object fields

Each source in JSON includes:

- `source_id`, `source_name`, `category`
- `url_or_reference`, `api_available`, `api_key_required`
- `license_terms_note`, `frequency`, `fields`
- `reliability_score` (0–1 research estimate)
- `retrieval_method`, `last_updated`, `data_mode`, `notes`

## Adding a source (workflow)

```text
1. Edit data-lake/metadata/source_registry.json
2. Add raw file under data-lake/raw/{category}/
3. Register dataset in data_catalog.json
4. Add source note under data-lake/reference/source_notes/
5. Run validation before processed merge
```

## API policy (this phase)

- **Do not** connect live APIs until entry has license review and fetch script.
- Prefer **manual CSV** or **FRED** (with API key in env, not repo) as first live ingest.
- Banxico SIE: research starter only until terms confirmed.

## Related

- [data_lake_architecture.md](data_lake_architecture.md)
- [data_quality_standard.md](data_quality_standard.md)
- [data-lake/README.md](../data-lake/README.md)
