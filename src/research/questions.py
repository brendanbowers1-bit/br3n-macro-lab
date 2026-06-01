"""
Core research questions for the Global FX & Remittance Research Lab.

Mission: Who bears the cost when value crosses borders?
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ResearchQuestion:
    question_id: str
    title: str
    hypothesis: str
    required_data: list[str]
    measurable_variables: list[str]
    proposed_index: str
    possible_chart: str
    possible_regression: str
    interpretation: str


RESEARCH_QUESTIONS: list[ResearchQuestion] = [
    ResearchQuestion(
        question_id="master_value_survival",
        title="Master Question — Value Survival",
        hypothesis="When value crosses a border, a measurable fraction is destroyed by fees, spreads, timing, volatility, inflation, payout friction, dollar dependency, and trust discounts.",
        required_data=["RPW", "KNOMAD", "IMF FX", "macro inflation", "BIS turnover", "sovereignty manual"],
        measurable_variables=["value_survival_index", "total_value_loss_pct", "real_usable_value_delivered_pct"],
        proposed_index="Bowers Frontier Value Survival Index (VSI)",
        possible_chart="Stacked bar: all VSI loss components by corridor",
        possible_regression="real_usable_value_delivered ~ trust_score + dollar_dependency + corridor FE",
        interpretation="Who bears the cost when value crosses borders — the central question of Bowers Frontier Macro Labs.",
    ),
    ResearchQuestion(
        question_id="value_survival_trust",
        title="Value Survival & Trust",
        hypothesis="Currencies with lower trust scores impose higher cross-border value losses via trust discount and volatility channels.",
        required_data=["Currency Trust Score", "VSI outputs", "FX volatility"],
        measurable_variables=["trust_discount_pct", "currency_trust_score", "value_survival_index"],
        proposed_index="Value Survival Index + Currency Trust",
        possible_chart="Scatter: trust score vs VSI by receiver country",
        possible_regression="total_value_loss_pct ~ currency_trust_score + inflation + volatility",
        interpretation="Tests whether monetary trust is priced into cross-border value survival.",
    ),
    ResearchQuestion(
        question_id="hidden_fx_tax",
        title="Hidden FX Tax",
        hypothesis="Explicit fees understate the true cost of cross-border value transfer; timing, volatility, and inflation impose a hidden tax borne disproportionately by recipients.",
        required_data=["World Bank RPW", "IMF FX rates", "macro inflation", "transfer speed"],
        measurable_variables=["fee_pct", "fx_margin_pct", "timing_risk_pct", "volatility_penalty_pct", "hidden_fx_tax_pct"],
        proposed_index="Hidden FX Tax Index",
        possible_chart="Stacked bar: fee vs margin vs timing vs volatility by corridor",
        possible_regression="real_value_delivered ~ hidden_fx_tax_pct + corridor FE + time FE",
        interpretation="Identifies who pays when value crosses borders — often the household that cannot hedge.",
    ),
    ResearchQuestion(
        question_id="remittance_welfare",
        title="Remittance Welfare",
        hypothesis="Remittances function as a decentralized global welfare system; FX spreads act as a regressive tax on family obligation.",
        required_data=["KNOMAD bilateral flows", "RPW costs", "receiver GDP", "poverty indicators"],
        measurable_variables=["welfare_loss_pct", "aggregate_welfare_loss_usd", "real_value_delivered_pct"],
        proposed_index="Remittance Welfare Loss Index",
        possible_chart="Gross sent vs real received by corridor (waterfall)",
        possible_regression="remittance_growth ~ welfare_loss_pct + inflation + volatility + GDP growth",
        interpretation="Quantifies purchasing power destroyed between sender intent and recipient reality.",
    ),
    ResearchQuestion(
        question_id="currency_credibility",
        title="Currency Credibility",
        hypothesis="Exchange rates are market prices of national credibility — inflation, reserves, and institutional trust compound into currency quality.",
        required_data=["IMF IFS/WEO", "FX volatility", "reserves", "current account", "institutional risk (manual)"],
        measurable_variables=["credibility_score", "inflation_score", "reserve_score", "depreciation_score"],
        proposed_index="Currency Credibility Index",
        possible_chart="Radar chart of credibility components by country",
        possible_regression="depreciation ~ credibility_score + policy_rate + terms_of_trade_shock",
        interpretation="Separates stable credibility from fragile credibility before crisis.",
    ),
    ResearchQuestion(
        question_id="labor_conversion",
        title="Labor Conversion",
        hypothesis="FX translates the same hour of human labor into unequal global purchasing power; remittance costs further discount foreign labor.",
        required_data=["wage data (manual/WDI)", "FX rates", "PPP factors", "hidden FX tax"],
        measurable_variables=["global_labor_value_usd", "remittance_adjusted_labor_value", "ppp_adjusted_labor_value"],
        proposed_index="Labor Conversion Index",
        possible_chart="Bar: hourly wage in USD vs PPP-adjusted vs remittance-adjusted by country",
        possible_regression="labor_conversion ~ hidden_fx_tax + inflation + credibility_score",
        interpretation="Makes visible how FX structurally reprices human time across borders.",
    ),
    ResearchQuestion(
        question_id="dollar_dependency",
        title="Dollar Dependency",
        hypothesis="The US dollar is not merely a currency but global financial infrastructure; dependency constrains monetary sovereignty.",
        required_data=["BIS turnover", "trade invoicing (manual)", "USD debt share (manual)", "reserves composition"],
        measurable_variables=["dollar_dependency_score", "dollar_pair_share", "remittance_dependence"],
        proposed_index="Dollar Dependency Index",
        possible_chart="Heatmap: dollar dependency vs remittance reliance",
        possible_regression="stress_score ~ dollar_dependency + current_account + reserves",
        interpretation="Maps who is dollar-constrained vs monetarily autonomous.",
    ),
    ResearchQuestion(
        question_id="monetary_sovereignty",
        title="Monetary Sovereignty",
        hypothesis="Countries can be politically sovereign yet monetarily dependent when FX, debt, and payment rails are dollar-denominated.",
        required_data=["dollar dependency", "credibility", "external debt", "sanctions exposure (manual)"],
        measurable_variables=["sovereignty_gap = political_autonomy_ph - dollar_dependency_score"],
        proposed_index="Dollar Dependency + Credibility composite",
        possible_chart="Scatter: credibility vs dollar dependency quadrants",
        possible_regression="policy_rate_response ~ dollar_dependency + inflation + reserves",
        interpretation="Tests whether policy space is real or constrained by global USD architecture.",
    ),
    ResearchQuestion(
        question_id="currency_stress",
        title="Currency Stress",
        hypothesis="Currency crises are crises of belief detectable before collapse via depreciation, volatility, and macro pressure.",
        required_data=["IMF FX", "inflation", "reserves", "DXY/FRED", "current account"],
        measurable_variables=["stress_score", "regime", "depreciation_30d", "volatility_component"],
        proposed_index="Currency Stress Index",
        possible_chart="Stress monitor time series with regime bands",
        possible_regression="stress_next_90d ~ credibility + dollar_dependency + volatility (logistic)",
        interpretation="Early warning for research — not trading signals.",
    ),
    ResearchQuestion(
        question_id="household_fx_exposure",
        title="Household FX Exposure",
        hypothesis="Poor households are structurally short FX volatility because they cannot hedge remittance and purchasing-power risk.",
        required_data=["hidden FX tax by corridor", "poverty/WDI", "remittance share GDP", "volatility"],
        measurable_variables=["household_burden = hidden_fx_tax * remittance_share * poverty_rate_ph"],
        proposed_index="Hidden FX Tax × Remittance Welfare composite",
        possible_chart="Corridor burden vs poverty proxy",
        possible_regression="welfare_loss ~ poverty_ph + volatility + hidden_fx_tax + corridor FE",
        interpretation="Links macro FX frictions to household welfare inequality.",
    ),
]


def questions_dataframe():
    import pandas as pd

    return pd.DataFrame(
        [
            {
                "question_id": q.question_id,
                "title": q.title,
                "hypothesis": q.hypothesis,
                "proposed_index": q.proposed_index,
                "required_data": "; ".join(q.required_data),
            }
            for q in RESEARCH_QUESTIONS
        ]
    )


def get_question(question_id: str) -> ResearchQuestion:
    for q in RESEARCH_QUESTIONS:
        if q.question_id == question_id:
            return q
    raise KeyError(question_id)
