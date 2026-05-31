"""Canonical table schemas for the Global FX & Remittance Research Lab."""

from __future__ import annotations

CORRIDOR_PRICES_COLUMNS = [
    "date",
    "quarter",
    "sender_country",
    "receiver_country",
    "sender_currency",
    "receiver_currency",
    "corridor",
    "provider",
    "provider_type",
    "send_amount_usd",
    "total_cost_pct",
    "fee_pct",
    "fx_margin_pct",
    "transfer_speed_days",
    "payout_method",
    "transparency_flag",
]

FX_RATES_COLUMNS = [
    "date",
    "currency",
    "country",
    "usd_fx_rate",
    "daily_return",
    "monthly_return",
    "quarterly_return",
    "volatility_30d",
    "volatility_90d",
    "depreciation_30d",
    "depreciation_90d",
    "depreciation_365d",
    "drawdown_365d",
    "drawdown_1y",
    "source",
]

VALUE_SURVIVAL_OUTPUTS_COLUMNS = [
    "date",
    "year",
    "quarter",
    "corridor",
    "sender_country",
    "receiver_country",
    "original_value_sent_usd",
    "explicit_fee_loss_pct",
    "fx_spread_loss_pct",
    "timing_loss_pct",
    "volatility_loss_pct",
    "inflation_erosion_pct",
    "payout_friction_pct",
    "dollar_dependency_drag_pct",
    "trust_discount_pct",
    "total_value_loss_pct",
    "real_usable_value_delivered_pct",
    "value_survival_index",
    "value_loss_usd_per_100",
    "interpretation",
    "data_quality_score",
    "mock_data_flag",
    "data_mode",
    "limitations",
    "source",
]

MACRO_COUNTRY_PANEL_COLUMNS = [
    "date",
    "year",
    "quarter",
    "country",
    "currency",
    "inflation_yoy",
    "policy_rate",
    "gdp_growth",
    "current_account_gdp",
    "reserves_months_imports",
    "external_debt_gdp",
    "remittances_gdp",
    "imports_gdp",
    "trade_openness",
    "unemployment",
]

REMITTANCE_FLOWS_COLUMNS = [
    "year",
    "sender_country",
    "receiver_country",
    "corridor",
    "remittance_usd",
    "receiver_gdp",
    "remittance_share_gdp",
    "corridor_weight",
]

CURRENCY_MARKET_STRUCTURE_COLUMNS = [
    "year",
    "currency",
    "fx_turnover_usd",
    "global_turnover_share",
    "liquidity_score",
    "dollar_pair_share",
]

SCHEMAS = {
    "corridor_prices": CORRIDOR_PRICES_COLUMNS,
    "fx_rates": FX_RATES_COLUMNS,
    "macro_country_panel": MACRO_COUNTRY_PANEL_COLUMNS,
    "remittance_flows": REMITTANCE_FLOWS_COLUMNS,
    "currency_market_structure": CURRENCY_MARKET_STRUCTURE_COLUMNS,
    "value_survival_outputs": VALUE_SURVIVAL_OUTPUTS_COLUMNS,
}
