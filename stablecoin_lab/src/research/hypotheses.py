"""Research hypotheses for Stablecoin Settlement Window Lab."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Hypothesis:
    id: str
    title: str
    statement: str
    research_question: str
    dependent: str
    independent: list[str]
    controls: list[str]
    expected_sign: str
    identification_limitation: str


FLAGSHIP_QUESTIONS = [
    "Q1: Is instant settlement always socially optimal?",
    "Q2: What is the difference between ledger finality and economic finality?",
    "Q3: Do stablecoins reduce liquidity risk, or relocate it to issuers and reserve markets?",
    "Q4: Do stablecoins create faster runs than bank deposits?",
    "Q5: Do USD stablecoins export dollar dominance directly to households?",
    "Q6: Can private tokenized money preserve the singleness of money?",
    "Q7: How does settlement-window compression redistribute risk?",
    "Q8: Is compliance the real settlement window?",
    "Q9: What is the optimal cross-border settlement asset?",
    "Q10: Can atomic settlement reduce FX settlement risk without increasing liquidity burden?",
    "Q11: Do stablecoins improve value survival for remittances?",
    "Q12: Are stablecoin issuers private liquidity transformers?",
]

HYPOTHESES = [
    Hypothesis(
        "H1",
        "Ledger speed vs economic finality",
        "Lower ledger settlement time does not necessarily imply higher economic finality.",
        "Q2",
        "stablecoin_finality_quality_index",
        ["ledger_finality_seconds"],
        ["estimated_redemption_time_hours", "reserve_liquidity_score", "off_ramp_reliability_score", "peg_stability_score"],
        "mixed",
        "Chain confirmation is endogenous to network choice; economic finality includes off-chain frictions.",
    ),
    Hypothesis(
        "H2",
        "Stablecoin remittance advantage",
        "Stablecoin value survival improves relative to traditional remittance only when off-ramp and compliance frictions are low.",
        "Q11",
        "stablecoin_advantage_score",
        ["stablecoin_offramp_fee_pct", "stablecoin_chain_fee_pct", "compliance_delay_hours", "traditional_fee_pct", "traditional_fx_margin_pct"],
        ["corridor", "stablecoin", "local_fx_spread_pct"],
        "negative on frictions",
        "Fee structures are correlated with corridor infrastructure; not randomized rail assignment.",
    ),
    Hypothesis(
        "H3",
        "Reserve liquidity and depeg risk",
        "Higher reserve liquidity is associated with lower depeg risk.",
        "Q6",
        "peg_deviation_bps",
        ["reserve_liquidity_score"],
        ["market_stress_proxy", "issuer", "stablecoin"],
        "negative",
        "Reserve scores may come from attestations with lag; stress is not exogenous.",
    ),
    Hypothesis(
        "H4",
        "Macro pressure and stablecoin dollarization",
        "Stablecoin dollarization pressure rises with inflation and local FX volatility.",
        "Q5",
        "stablecoin_dollarization_index",
        ["local_inflation_yoy", "local_fx_volatility_30d", "bank_account_access_pct", "local_currency_depreciation_yoy"],
        ["country", "capital_controls_proxy"],
        "positive on inflation/vol",
        "Usage proxies are coarse; reverse causality from dollarization to stablecoin adoption.",
    ),
    Hypothesis(
        "H5",
        "Compliance drag dominates ledger time",
        "Compliance drag dominates ledger settlement time in regulated cross-border stablecoin payments.",
        "Q8",
        "effective_economic_finality_hours",
        ["ledger_confirmation_time", "compliance_delay_hours", "estimated_off_ramp_time_hours", "estimated_redemption_time_hours"],
        ["corridor", "jurisdiction", "kyc_required_flag"],
        "positive on compliance/off-ramp",
        "Compliance delays are institution-specific; thin cross-section on official data.",
    ),
]


def hypotheses_dataframe():
    import pandas as pd
    return pd.DataFrame([{
        "id": h.id,
        "title": h.title,
        "hypothesis": h.statement,
        "research_question": h.research_question,
        "dependent": h.dependent,
        "independent": "; ".join(h.independent),
        "controls": "; ".join(h.controls),
        "expected_sign": h.expected_sign,
        "limitation": h.identification_limitation,
    } for h in HYPOTHESES])
