# Known Limitations (Stablecoin Lab)

**Updated:** 2026-06-01

## Current data mode: MIXED (official + manual)

Official fetchers populate most canonical tables. **Off-ramp characteristics** still use Tier 4 manual assumptions (mock fallback) until exchange/partner fee data is wired.

| Table | Source mode | Notes |
|-------|-------------|-------|
| stablecoin_supply | DeFiLlama (Tier 3) | Live API via `fetch_stablecoin_data.py` |
| stablecoin_price_peg | DeFiLlama (Tier 3) | Live prices |
| stablecoin_reserves | Circle/Tether attestations (Tier 2) | Curated snapshot rows |
| blockchain_settlement_characteristics | Chain reference (Tier 4 documented) | Documented parameters, not live chain scrape |
| stablecoin_redemption_characteristics | Derived from attestations (Tier 2) | `manual/redemption_from_attestations.csv` |
| remittance_comparison | World Bank RPW + manual stablecoin rail (Tier 1 + 4) | Traditional leg observed; stablecoin leg partly manual |
| regulatory_events | Curated MiCA/CFTC/CBN/Fed refs (Tier 1) | Not exhaustive |
| off_ramp_characteristics | **Mock / manual fallback** | `mock_data_flag=True` until real off-ramp files added |

Run `python scripts/fetch_stablecoin_data.py` before reproduction to refresh official extracts.

## What works end-to-end

- Fetch: 12 raw/metadata files written
- Smoke tests: 9/9 PASS
- Full reproduction pipeline: PASS (fetch → validate → build → indices → models → sensitivity → robustness → visuals)
- Pytest suite: PASS (when run with `PYTHONPATH=.` from `stablecoin_lab/`)

## Remaining official data (priority)

1. **Exchange off-ramp fee schedules** → `data/raw/manual/off_ramp_assumptions.csv`
2. **CoinGecko daily peg history** (longer panel than DeFiLlama snapshot)
3. **IMF macro panel** for dollarization controls → `data/raw/macro/`
4. **Live chain fee scrapes** (replace Tier 4 chain reference table)

## Data lake

Bronze/Silver/Gold folders exist under `data_lake/` as placeholders. DuckDB views are **not yet wired** — no DuckDB integration in parent repo yet.

## Empirical tests

With mixed data, empirical tests remain descriptive-only — no causal claims without identification design.
