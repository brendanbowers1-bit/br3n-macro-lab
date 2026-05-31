"""Generate methodology markdown reports for flagship indices."""

from __future__ import annotations

from pathlib import Path

from src.utils.paths import REPORTS_DIR

WORKING_PAPER_TITLE = "The Hidden FX Tax: Measuring the Cost of Value Crossing Borders"

WORKING_PAPER_ABSTRACT = """This paper develops a corridor-level framework for measuring the real economic burden imposed by foreign exchange frictions in cross-border money movement. Existing remittance cost measures focus on explicit fees and exchange-rate margins. This project extends the measurement framework to include transfer timing, FX volatility, inflation erosion, payout frictions, and recipient purchasing-power loss. The resulting Hidden FX Tax Index estimates who bears the cost when value crosses borders and provides a foundation for studying remittances, dollar dependency, currency credibility, and monetary sovereignty."""

METHODOLOGIES = {
    "hidden_fx_tax_methodology.md": """# Hidden FX Tax Index — Methodology

## Definition
Measures the full burden of moving money across currencies beyond visible fees.

## Components
- fee_pct, fx_margin_pct, timing_risk_pct, volatility_penalty_pct
- inflation_erosion_pct, payout_friction_pct, transparency_penalty

## Formula
hidden_fx_tax_pct = sum(components)

## Limitations
- Mock volatility/inflation when real data missing
- Timing risk is modelled, not observed settlement delay
- Does not capture informal FX markets
""",
    "remittance_welfare_loss_methodology.md": """# Remittance Welfare Loss Index — Methodology

## Definition
Estimates purchasing power lost between sender and recipient.

## Formula
welfare_loss_pct = 1 - real_value_delivered / gross_sent_usd
aggregate_welfare_loss_usd = remittance_usd × welfare_loss_pct

## Limitations
- Flow data may be lagged; corridor weights approximate
- Cash-out frictions use default assumptions
""",
    "currency_credibility_methodology.md": """# Currency Credibility Index — Methodology

## Definition
Transparent weighted score (0–100) of monetary credibility.

## Weights
Inflation 20%, reserves 15%, current account 15%, debt 15%, FX vol 15%, depreciation 10%, institutions 10% (placeholder).

## Limitations
- Institutional risk placeholder until manual data added
- Cross-country comparability requires harmonized macro vintages
""",
    "dollar_dependency_methodology.md": """# Dollar Dependency Index — Methodology

## Definition
Measures reliance on USD infrastructure for trade, finance, and payments.

## Components
USD debt share, invoicing, FX turnover vs USD, reserves, remittance dependence (placeholders flagged).

## Limitations
- Several components are placeholders pending manual/BIS data
""",
    "labor_conversion_methodology.md": """# Labor Conversion Index — Methodology

## Definition
Translates local hourly wage into global USD, remittance-adjusted, and PPP-adjusted value.

## Limitations
- Wage table is mock/manual placeholder
- PPP adjustment simplified
""",
    "currency_stress_methodology.md": """# Currency Stress Index — Methodology

## Definition
Detects stress in currency belief via depreciation, volatility, inflation, and external pressure.

## Regimes
normal | watchlist | stressed | crisis

## Limitations
- Not a trading signal; research early-warning only
- Reserve decline component placeholder
""",
    "working_paper_outline.md": f"""# {WORKING_PAPER_TITLE}

## Abstract
{WORKING_PAPER_ABSTRACT}

## 1. Introduction
Who bears the cost when value crosses borders?

## 2. Literature
Remittance costs, UIP/carry, dollar dominance, welfare economics of migration.

## 3. Data
World Bank RPW, KNOMAD, IMF, BIS, FRED — with mock-data audit trail.

## 4. Hidden FX Tax Index
Component breakdown and corridor rankings.

## 5. Remittance Welfare Loss
Aggregate dollar estimates.

## 6. Currency Credibility & Dollar Dependency
Sovereignty framing.

## 7. Labor Conversion
Global repricing of human time.

## 8. Currency Stress Monitor
Belief crises before collapse.

## 9. Limitations & Future Work
Placeholders, informal markets, policy implications (research only).

## Disclaimer
Research and education only. Not investment advice.
""",
}


def generate_all_reports(out_dir: Path | None = None) -> list[Path]:
    from src.utils.paths import MEMOS_DIR, WORKING_PAPER_DIR

    wp_dir = out_dir / "working_paper" if out_dir else WORKING_PAPER_DIR
    memo_dir = MEMOS_DIR if not out_dir else out_dir / "memos"
    wp_dir.mkdir(parents=True, exist_ok=True)
    memo_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for fname, body in METHODOLOGIES.items():
        dest = wp_dir / fname if "working_paper" in fname else memo_dir / fname
        dest.write_text(body.strip() + "\n", encoding="utf-8")
        paths.append(dest)
    return paths
