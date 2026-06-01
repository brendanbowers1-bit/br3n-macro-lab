"""Canonical table schemas for Stablecoin Settlement Window Lab."""

from __future__ import annotations

LINEAGE_COLUMNS = [
    "source_name", "source_url_or_reference", "data_provider",
    "publication_date", "extraction_date", "vintage_date",
    "update_frequency", "license_or_usage_note", "raw_file_name",
    "raw_file_hash_sha256", "transformation_script", "methodology_version",
    "unit_of_measure", "currency", "blockchain_network", "token_contract_address",
    "jurisdiction", "time_zone", "date_granularity",
    "country_or_region", "entity_type", "observed_vs_estimated_flag",
    "official_vs_manual_flag", "mock_data_flag", "missing_data_pct",
    "outlier_flag", "imputation_flag", "confidence_score",
    "data_quality_score", "data_quality_grade",
]

STABLECOIN_SUPPLY_COLUMNS = [
    "date", "stablecoin", "ticker", "issuer", "blockchain_network",
    "supply_usd", "market_cap_usd", "circulating_supply",
    "source_id", "data_quality_score", "mock_data_flag",
]

STABLECOIN_PRICE_PEG_COLUMNS = [
    "timestamp", "date", "stablecoin", "ticker", "price_usd",
    "peg_deviation_bps", "max_intraday_deviation_bps", "daily_volatility_bps",
    "depeg_event_flag", "source_id", "data_quality_score", "mock_data_flag",
]

STABLECOIN_RESERVES_COLUMNS = [
    "date", "stablecoin", "issuer", "total_reserves_usd",
    "cash_usd", "bank_deposits_usd", "treasury_bills_usd", "repo_usd",
    "commercial_paper_usd", "other_assets_usd", "reserve_liquidity_score",
    "attestation_provider", "attestation_date",
    "source_id", "data_quality_score", "mock_data_flag",
]

BLOCKCHAIN_SETTLEMENT_COLUMNS = [
    "date", "blockchain_network", "average_transaction_fee_usd",
    "median_transaction_fee_usd", "average_confirmation_time_seconds",
    "probabilistic_finality_seconds", "economic_finality_assumption_seconds",
    "outage_flag", "congestion_score",
    "source_id", "data_quality_score", "mock_data_flag",
]

STABLECOIN_REDEMPTION_COLUMNS = [
    "date", "stablecoin", "issuer", "minimum_redemption_amount_usd",
    "redemption_fee_pct", "estimated_redemption_time_hours",
    "direct_redemption_available_flag", "banking_hours_dependency_flag",
    "redemption_gate_flag", "freeze_authority_flag", "jurisdiction",
    "source_id", "data_quality_score", "mock_data_flag",
]

OFF_RAMP_COLUMNS = [
    "date", "corridor", "country", "stablecoin", "exchange_or_provider",
    "off_ramp_fee_pct", "fiat_withdrawal_fee_pct", "estimated_off_ramp_time_hours",
    "kyc_required_flag", "compliance_delay_hours", "local_bank_dependency_flag",
    "source_id", "data_quality_score", "mock_data_flag",
]

REMITTANCE_COMPARISON_COLUMNS = [
    "date", "corridor", "sender_country", "receiver_country",
    "traditional_fee_pct", "traditional_fx_margin_pct", "traditional_transfer_speed_days",
    "stablecoin_onramp_fee_pct", "stablecoin_chain_fee_pct", "stablecoin_offramp_fee_pct",
    "stablecoin_fx_spread_pct", "stablecoin_effective_finality_hours",
    "source_id", "data_quality_score", "mock_data_flag",
]

REGULATORY_EVENT_COLUMNS = [
    "event_id", "date", "country", "jurisdiction", "stablecoin", "issuer",
    "event_type", "event_description", "severity_score", "affected_component",
    "source_id", "data_quality_score", "mock_data_flag",
]

MODEL_OUTPUT_COLUMNS = [
    "date", "model_name", "model_version", "entity", "entity_type", "score",
    "score_min", "score_max", "interpretation", "confidence_score",
    "data_quality_score", "sensitivity_case", "source_coverage_pct",
    "limitations", "created_at",
]

CANONICAL_TABLES = {
    "stablecoin_supply": STABLECOIN_SUPPLY_COLUMNS,
    "stablecoin_price_peg": STABLECOIN_PRICE_PEG_COLUMNS,
    "stablecoin_reserves": STABLECOIN_RESERVES_COLUMNS,
    "blockchain_settlement_characteristics": BLOCKCHAIN_SETTLEMENT_COLUMNS,
    "stablecoin_redemption_characteristics": STABLECOIN_REDEMPTION_COLUMNS,
    "off_ramp_characteristics": OFF_RAMP_COLUMNS,
    "remittance_comparison": REMITTANCE_COMPARISON_COLUMNS,
    "regulatory_events": REGULATORY_EVENT_COLUMNS,
    "model_outputs": MODEL_OUTPUT_COLUMNS,
}
