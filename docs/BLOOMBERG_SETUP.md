# Bloomberg Setup for Bowers Frontier Macro Labs

> Tier 2 — professional market data. Research only.

## What you need

Bloomberg is **not free**. You need one of:

| Option | Typical cost | Best for |
|--------|--------------|----------|
| **Bloomberg Terminal** | ~$24k+/year (individual; firm pricing varies) | Full desktop + API on same machine |
| **B-PIPE** (server feed) | Institutional pricing | Production / server-side pulls |
| **Bloomberg Anywhere** | Add-on to Terminal | Remote access to Terminal |

Contact: [Bloomberg Professional Services](https://www.bloomberg.com/professional/solution/bloomberg-terminal/)

---

## Quick start (Terminal on your Mac)

### 1. Get Bloomberg Terminal installed

- Your employer or school may provide access
- Otherwise request a trial or subscription from Bloomberg sales
- Install from Bloomberg's installer (not from this repo)

### 2. Install Python bridge

**Option A — xbbg (recommended if Terminal runs on same machine):**

```bash
cd ~/fx_regime_lab
source .venv/bin/activate
pip install xbbg
```

**Option B — official blpapi SDK:**

1. Download **Bloomberg API** (blpapi) from `{WAPI}` on Terminal or [Bloomberg API Library](https://www.bloomberg.com/professional/support/api-library/)
2. Install the Python blpapi wheel for your OS/Python version
3. Optionally: `pip install pdblp`

### 3. Log in to Terminal

Bloomberg API calls fail if Terminal is not running and logged in.

### 4. Check connectivity

```bash
python scripts/fetch_bloomberg_spot.py --check
```

### 5. Fetch USD/MXN

```bash
python scripts/fetch_bloomberg_spot.py
```

Output: `data/processed/usdmxn_curncy_bloomberg_tier2.csv`

---

## Config (`config.yaml`)

```yaml
bloomberg:
  enabled: false
  usdmxn_ticker: "USDMXN Curncy"
  host: "localhost"
  port: 8194
```

---

## What Bloomberg unlocks (Tier 2)

- **PX_LAST, BID, ASK** — realistic spreads for hedge cost research
- **Forward points** — carry and hedge modeling (future module)
- **FX vol surfaces** — options/collar hedging research
- **Intraday bars** — execution timing research

---

## If you don't have Bloomberg yet

Use the free upgrade path first:

```bash
python scripts/fetch_tier1_official.py   # FRED H.10 — Tier 1 academic
```

Tier 1 is sufficient for **publication-style random-walk and regime research**.  
Tier 2 is required for **trading-grade and execution/hedge claims**.

---

## Licensing reminder

- Do **not** publish raw Bloomberg data in GitHub, Substack, or public reports
- Cite Bloomberg as source; show charts derived from licensed analysis only
- Follow your firm's Bloomberg agreement and compliance rules
