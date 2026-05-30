# BR3N Macro Labs Data Strategy

> Research only — not investment advice.

## Core Principle

The best FX research lab does not rely on one data source. It uses a **layered data stack** where **Tier 1 is the highest quality** and **Tier 4 is prototype/dev only**:

**Tier 1 official → Tier 2 professional → Tier 3 proprietary → Tier 4 prototype**

The lab must always label **source name**, **tier number**, and **tier label** on every model test.

---

## Data Quality Tiers

### Tier 1 — Official / Academic-Grade

**Purpose:** Reliable research and publication-quality analysis.

**Examples:**
- Federal Reserve H.10
- FRED (e.g. `DEXMXUS` for USD/MXN)
- BIS effective exchange rates
- IMF International Financial Statistics
- World Bank remittance data
- Banxico and other central banks

**Strengths:**
- official or institutionally recognized
- citable in academic memos and public reports
- often long histories

**Weaknesses:**
- may be daily/weekly/monthly rather than intraday
- no bid/ask spreads or forward points
- may not reflect executable prices

**Best use:** Random-walk tests, macro FX research, academic memos, public reports.

**Free upgrade path in this lab:** `python scripts/fetch_tier1_official.py`

---

### Tier 2 — Professional Market Data

**Purpose:** Realistic trading and hedging research.

**Examples:**
- Bloomberg
- LSEG / Refinitiv
- FactSet
- CME DataMine
- Cboe FX
- EBS
- 360T
- FXall
- bank quote history

**Strengths:**
- professional quality, often bid/ask and forwards
- useful for execution-cost and hedge research

**Weaknesses:**
- expensive, licensing restrictions, often not publishable

**Best use:** Forward/carry modeling, execution-cost analysis, options/collar hedging.

---

### Tier 3 — Proprietary Data

**Purpose:** Potentially unique research edge (internal only).

**Examples:**
- payment corridor flows
- customer order flow
- transaction count and payout demand
- settlement timing
- hedge execution data
- bank quote spreads (internal)

**Strengths:**
- differentiated; may reveal pressure before public macro data

**Weaknesses:**
- private, sensitive, compliance-bound; cannot publish without permission

**Best use:** Internal corridor-pressure models, proprietary hedge-governance tools.

---

### Tier 4 — Prototype Data

**Purpose:** Fast experimentation and local development.

**Examples:**
- Yahoo / yfinance
- Stooq
- free web sources
- manually downloaded CSVs

**Strengths:**
- free, easy, good for dashboards and code testing

**Weaknesses:**
- unofficial, may break, inconsistent closes, not publication- or trading-grade

**Best use:** Initial model development, dashboard testing, simple backtests.

**Current lab default:** Tier 4 (yfinance) for USD/MXN spot.

---

## Best Data by Research Question

### Random-Walk / Forecast Testing

**Tier 1 sources:** FRED, Federal Reserve H.10, BIS, central banks

**Required fields:** date, FX spot, price convention, data source, tier number, frequency, missing-value treatment

### Carry and Forward Testing

**Tier 1 prototype:** policy rate differentials via FRED / central banks

**Tier 2 best:** actual FX forward points, swaps, NDFs, cross-currency basis

### Hedge Governance Testing

**Tier 4 prototype:** spot returns + estimated transaction costs

**Tier 2 best:** bank quotes, forwards, real execution costs

### Payment-Corridor Flow Pressure

**Tier 1 public:** World Bank remittances, central-bank remittance stats, calendar proxies

**Tier 3 best:** payment volumes, transaction count, corridor-level flows

---

## Data Quality Checklist

Every dataset should be reviewed for:

1. Source name
2. **Tier number (1–4) and tier label**
3. Official or unofficial source
4. License restrictions
5. Update frequency
6. Time zone
7. Spot convention (USD/MXN vs MXN/USD)
8. Close time (New York, London, etc.)
9. Bid, ask, mid, close, or last
10. Missing values
11. Holiday handling
12. Revisions or vintage issues
13. Can this be published publicly?
14. Can this be used commercially?
15. Is it research-grade or trading-grade?

---

## Final Principle

A model should never be evaluated without recording the **quality tier** of the data behind it.

Results on **Tier 4 prototype data** are not publication-grade until rerun on **Tier 1 official** sources. Trading and hedging claims require **Tier 2 professional** data (bid/ask, forwards, execution costs).
