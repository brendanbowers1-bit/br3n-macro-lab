# News and Uncertainty Data Strategy

BR3N Macro Labs uses news data as a **regime and risk feature**, not as a direct trading signal.

The purpose is to test whether policy uncertainty, geopolitical stress, central-bank news, inflation news, commodity news, and country-specific news intensity help explain when FX behaves more or less randomly.

## Core research question

Can news intensity, policy uncertainty, geopolitical risk, and central-bank event information help explain when FX regimes become more or less structured?

This is **research-only**. News does not predict FX. News is tested as a regime/risk modifier.

## Data Tiers

### Tier 1 — Academic/Public News Indices

Sources:
- FRED Economic Policy Uncertainty series
- Geopolitical Risk Index
- VIX / risk proxies
- central-bank event calendars

Use:
- academic-grade risk and uncertainty proxies
- publication-friendly features
- low-frequency or daily uncertainty testing

Limitations:
- not real-time news firehose
- indices may lag and revise
- no entity-level sentiment

### Tier 2 — Open News Firehose

Sources:
- GDELT
- public news APIs where allowed

Use:
- country news intensity
- central-bank news intensity
- event detection
- geopolitical and policy news spikes

Limitations:
- noisy, media-coverage biased
- requires validation before academic claims
- look-ahead bias risk when merging

### Tier 3 — Professional News Analytics

Sources:
- RavenPack
- Bloomberg news analytics
- LSEG news analytics
- Dow Jones / Factiva if available

Use:
- professional sentiment
- entity-level news analytics
- real-time risk/news monitoring
- trading-grade research if license permits

Limitations:
- licensed; redistribution restricted
- not publishable without permission

## Feature set

| Feature | Purpose |
|---------|---------|
| `policy_uncertainty_index` | FRED EPU and similar |
| `geopolitical_risk_index` | GPR-style stress |
| `news_intensity_1d` / `news_intensity_7d` | Daily / rolling news volume |
| `news_intensity_zscore` | Normalized intensity spike detector |
| `central_bank_news_flag` | CB event days |
| `news_stress_regime` | Composite stress classifier |

## Rule

News features should be treated as **explanatory and risk-regime variables** unless they pass out-of-sample tests against random-walk and benchmark models.

Every news-enhanced model output must record:
- data source (FRED, GDELT, placeholder)
- whether features are live or placeholder
- sample period and merge method (forward-fill policy)

## Look-ahead warning

Forward-filling lower-frequency uncertainty indices onto daily FX data is acceptable for **same-day or lagged** indices only. Never merge future news into past dates. All merges use backward/as-of alignment with explicit comments in code.

## Lab modules

| File | Role |
|------|------|
| `src/news_features.py` | Feature engineering and stress regime |
| `src/gdelt_news_loader.py` | Optional GDELT open-news loader |
| `src/news_tests.py` | High-news vs normal-day tests |
| `scripts/run_news_layer.py` | Pipeline runner |

## What we do not claim

- News predicts FX direction
- Headlines create guaranteed signals
- Models are trading-ready based on news alone

News is a **regime/risk feature** requiring out-of-sample validation.
