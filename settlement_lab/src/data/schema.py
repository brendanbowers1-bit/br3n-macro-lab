"""Canonical table schemas for Settlement Economics Lab."""

from __future__ import annotations

LINEAGE_COLUMNS = [
    "source_name", "source_url_or_reference", "data_provider",
    "publication_date", "extraction_date", "vintage_date",
    "update_frequency", "license_or_usage_note", "raw_file_name",
    "raw_file_hash_sha256", "transformation_script", "methodology_version",
    "unit_of_measure", "currency", "time_zone", "date_granularity",
    "country_or_region", "entity_type", "observed_vs_estimated_flag",
    "official_vs_manual_flag", "mock_data_flag", "missing_data_pct",
    "outlier_flag", "imputation_flag", "confidence_score",
    "data_quality_score", "data_quality_grade",
]

PAYMENT_FLOW_COLUMNS = [
    "date", "period", "country", "region", "payment_system", "rail_type",
    "payment_type", "currency", "transaction_count", "transaction_value_usd",
    "average_transaction_value_usd", "settlement_lag_hours", "settlement_lag_days",
    "availability_lag_hours", "finality_lag_hours", "reversal_window_hours",
    "failure_rate", "return_rate", "chargeback_rate", "source_id",
    "data_quality_score", "mock_data_flag",
]

SETTLEMENT_LIQUIDITY_COLUMNS = [
    "date", "institution_type", "payment_system", "currency",
    "average_daily_settlement_value_usd", "peak_daily_settlement_value_usd",
    "prefunding_required_usd", "collateral_required_usd",
    "settlement_account_balance_usd", "intraday_credit_used_usd",
    "liquidity_buffer_usd", "cost_of_capital_pct", "interest_rate_pct",
    "opportunity_cost_usd", "source_id", "data_quality_score", "mock_data_flag",
]

FX_SETTLEMENT_EXPOSURE_COLUMNS = [
    "date", "currency_pair", "settlement_window_days", "notional_value_usd",
    "fx_volatility_1d", "fx_volatility_5d", "fx_volatility_30d",
    "expected_fx_exposure_usd", "realized_fx_move_pct",
    "source_id", "data_quality_score", "mock_data_flag",
]

FINALITY_COLUMNS = [
    "country", "payment_system", "rail_type", "legal_finality_score",
    "operational_finality_score", "funds_availability_score",
    "reversibility_risk_score", "reconciliation_quality_score",
    "settlement_failure_risk_score", "finality_lag_hours",
    "source_id", "manual_assumption_flag", "data_quality_score", "mock_data_flag",
]

PAYMENT_ACCESS_COLUMNS = [
    "country", "year", "account_ownership_pct", "digital_payment_usage_pct",
    "mobile_money_usage_pct", "card_ownership_pct", "formal_savings_pct",
    "remittance_received_pct", "cash_dependency_proxy",
    "source_id", "data_quality_score", "mock_data_flag",
]

STRESS_EVENT_COLUMNS = [
    "event_id", "date_start", "date_end", "country", "region", "payment_system",
    "event_type", "severity_score", "settlement_delay_change", "failure_rate_change",
    "liquidity_buffer_change", "volume_shock_pct", "public_description",
    "source_id", "data_quality_score", "mock_data_flag",
]

MODEL_OUTPUT_COLUMNS = [
    "date", "model_name", "model_version", "entity", "entity_type", "score",
    "score_min", "score_max", "interpretation", "confidence_score",
    "data_quality_score", "sensitivity_case", "source_coverage_pct",
    "limitations", "created_at",
]
