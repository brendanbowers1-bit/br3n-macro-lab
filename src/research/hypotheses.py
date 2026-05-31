"""
Testable research hypotheses for the Value Survival Index.

Each hypothesis includes identification limitations and credibility risks.
Research-only — not investment advice.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Hypothesis:
    id: str
    title: str
    statement: str
    dependent_variable: str
    independent_variables: list[str]
    controls: list[str]
    data_needed: list[str]
    identification_limitation: str
    chart: str
    regression_suggestion: str
    expected_sign: str
    credibility_risk: str


HYPOTHESES: list[Hypothesis] = [
    Hypothesis(
        id="H1",
        title="RPW total cost and VSI",
        statement="Corridors with higher RPW total cost are associated with lower Value Survival Index.",
        dependent_variable="vsi_risk_adjusted",
        independent_variables=["total_cost_pct", "fee_pct", "fx_margin_pct"],
        controls=["send_amount_usd", "provider_type", "transfer_speed_days"],
        data_needed=["world_bank_rpw", "corridor_prices"],
        identification_limitation="Cross-sectional association; RPW total cost may bundle unobserved provider quality.",
        chart="vsi_core_ranked_bar.png vs total_cost_pct scatter",
        regression_suggestion="VSI ~ total_cost_pct + provider_type FE + sender/receiver country FE",
        expected_sign="Negative on total_cost_pct",
        credibility_risk="RPW samples may not represent all payout rails or send amounts.",
    ),
    Hypothesis(
        id="H2",
        title="FX volatility and risk-adjusted VSI",
        statement="Higher FX volatility is associated with lower risk-adjusted VSI under the timing/volatility specification.",
        dependent_variable="vsi_risk_adjusted",
        independent_variables=["fx_volatility_30d", "volatility_loss_pct"],
        controls=["corridor FE", "year FE", "hedge_access_score"],
        data_needed=["imf_fx", "fx_rates"],
        identification_limitation="Volatility is endogenous to macro conditions; no exogenous shock without event study.",
        chart="volatility_loss_pct by corridor",
        regression_suggestion="VSI_RISK_ADJUSTED ~ fx_volatility_30d + corridor FE + year FE",
        expected_sign="Negative on fx_volatility_30d",
        credibility_risk="Volatility penalty weight (0.10 baseline) is a modeling assumption, not observed loss.",
    ),
    Hypothesis(
        id="H3",
        title="Inflation and real value survival",
        statement="Higher recipient-country inflation is associated with lower real value survival (inflation erosion channel).",
        dependent_variable="vsi_core",
        independent_variables=["inflation_yoy", "inflation_erosion_pct"],
        controls=["receiver_country FE", "year FE", "days_held"],
        data_needed=["world_bank_wdi", "imf_ifs_weo"],
        identification_limitation="Inflation correlates with FX depreciation and policy credibility.",
        chart="inflation_erosion_pct stacked component",
        regression_suggestion="VSI_CORE ~ inflation_yoy + receiver_country FE + year FE",
        expected_sign="Negative on inflation_yoy",
        credibility_risk="Annual inflation applied to short transfer windows may overstate erosion for fast transfers.",
    ),
    Hypothesis(
        id="H4",
        title="Remittance dependence and aggregate welfare loss",
        statement="Higher remittance dependence magnifies aggregate welfare loss from low VSI (scale effect, not causal welfare).",
        dependent_variable="aggregate_value_loss_usd",
        independent_variables=["remittances_gdp", "total_value_loss_pct", "annual_remittance_usd"],
        controls=["receiver_country FE", "year FE"],
        data_needed=["world_bank_knomad", "world_bank_wdi", "vsi_outputs"],
        identification_limitation="Flow estimates are model-based; aggregate loss is arithmetic, not household welfare.",
        chart="aggregate_welfare_loss_by_corridor.png",
        regression_suggestion="log(aggregate_value_loss_usd) ~ total_value_loss_pct × remittances_gdp + controls",
        expected_sign="Positive interaction on loss × dependence",
        credibility_risk="KNOMAD flows are estimated, not transaction-level.",
    ),
    Hypothesis(
        id="H5",
        title="Currency trust and extended VSI",
        statement="Lower currency trust scores are associated with higher extended value leakage (VSI_EXTENDED).",
        dependent_variable="vsi_extended",
        independent_variables=["currency_trust_score", "trust_discount_pct"],
        controls=["receiver_country FE", "macro_reserves_imports"],
        data_needed=["currency_trust", "macro_country_panel"],
        identification_limitation="Trust score is composite; trust discount is model-based, not market-observed.",
        chart="vsi_extended vs currency_trust_score",
        regression_suggestion="VSI_EXTENDED ~ currency_trust_score + receiver_country FE (extended spec only)",
        expected_sign="Positive on trust_discount_pct; negative on currency_trust_score",
        credibility_risk="Extended specification — not in baseline VSI_CORE.",
    ),
    Hypothesis(
        id="H6",
        title="Dollar shocks and dollar-dependent currencies",
        statement="Dollar-dependent currencies show greater VSI deterioration during dollar shock periods (event-study association).",
        dependent_variable="delta_vsi_risk_adjusted",
        independent_variables=["dollar_dependency_score", "dxy_return_90d"],
        controls=["corridor FE", "pre-event VSI", "global_risk_regime"],
        data_needed=["fred_dxy", "dollar_dependency", "event_study_panel"],
        identification_limitation="DXY shocks are global; confounding macro events common.",
        chart="event_window_vsi_change.png",
        regression_suggestion="ΔVSI ~ dollar_dependency_score × post_shock + corridor FE",
        expected_sign="Negative interaction on dependency × shock",
        credibility_risk="Requires sufficient event dates and non-mock FX data.",
    ),
]


def hypotheses_dataframe():
    import pandas as pd

    return pd.DataFrame(
        [
            {
                "id": h.id,
                "title": h.title,
                "hypothesis": h.statement,
                "dependent_variable": h.dependent_variable,
                "independent_variables": "; ".join(h.independent_variables),
                "expected_sign": h.expected_sign,
                "identification_limitation": h.identification_limitation,
                "credibility_risk": h.credibility_risk,
            }
            for h in HYPOTHESES
        ]
    )
