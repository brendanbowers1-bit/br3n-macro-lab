# FX Lab Data Upgrade Report

_Generated: 2026-05-31T12:30:14+00:00 UTC_

## Source load status

- **FRED H.10 USD/MXN:** SUCCESS
- **yfinance USDMXN=X:** SUCCESS

## Comparison (USD/MXN)

| Metric | FRED H.10 | yfinance |
|--------|-----------|----------|
| Observations | 6267 | 5858 |
| Start | 2001-05-22 | 2003-12-01 |
| End | 2026-05-22 | 2026-05-31 |
| Missing values | 0 | 0 |
| Latest price | 17.3241 | 17.285 |

- **Overlap days:** 5625
- **Daily return correlation:** 0.482037
- **Max |daily return diff|:** 0.155195
- **Agree closely:** No

## Source of truth

**FRED H.10 (DEXMXUS)**

FRED/Fed H.10 is academic-grade public data suitable for research memos. yfinance is prototype data — good for development, not sufficient alone for academic claims.

## Still missing for academic claims

- Forward points and cross-currency basis
- Bid/ask spreads and executable close conventions
- Independent validation against Banxico fix (optional cross-check)
- Documented missing-value policy on merged macro panels

## Still missing for trading / hedging claims

- Bid/ask and effective spread by tenor
- Forward points, roll, and carry at executable levels
- Transaction cost distributions from real executions
- Options implied volatility surfaces
- Proprietary payment-flow data (requires authorization)

## Limitations

This lab does **not** claim trading-ready or publication-grade models until official data is used consistently and hedge economics include forward costs.
