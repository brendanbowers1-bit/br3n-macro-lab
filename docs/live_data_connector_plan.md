# Live Data Connector Plan

**Lab:** Bowers Frontier Macro Labs  
**Principle:** No fragile scraping; fail closed; document fallbacks.

## Priority 1 (partially implemented)

| Connector | Status | Raw path | Notes |
|-----------|--------|----------|-------|
| USD/MXN FX | **Active (FRED/Banxico SIE)** | `data-lake/raw/fx/` | `BANXICO_SIE_TOKEN` for SF43718 |
| Fed policy rate | **Active** | `data-lake/raw/rates/fed_policy_rate_dfedtaru.csv` | FRED DFEDTARU |
| Banxico policy rate | **Active (mixed)** | `data-lake/raw/rates/banxico_policy_rate.csv` | SIE SF61745 or FRED proxy |
| US/MX holidays | **Starter** | `data-lake/raw/holidays/` | Curated CSV; expand with official feeds |

## Priority 2

US CPI, Mexico CPI, US payrolls, Mexico inflation, US Treasury yields, Mexico yields — FRED/Banxico/INEGI with license review.

## Priority 3

RPW remittance (partial), spread proxies, liquidity proxies, macro event calendar, news feeds.

## Priority 4

Stablecoin supply, settlement volume, on-chain rails — cross-lab with stablecoin_lab.

See `data-lake/metadata/live_connector_backlog.json` for backlog entries.
