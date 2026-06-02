"""Paths for the canonical data-lake/ tree (hyphen)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_LAKE_ROOT = ROOT / "data-lake"
METADATA_DIR = DATA_LAKE_ROOT / "metadata"

RAW_FX = DATA_LAKE_ROOT / "raw" / "fx"
RAW_RATES = DATA_LAKE_ROOT / "raw" / "rates"
RAW_MACRO = DATA_LAKE_ROOT / "raw" / "macro"
RAW_REMITTANCES = DATA_LAKE_ROOT / "raw" / "remittances"
RAW_HOLIDAYS = DATA_LAKE_ROOT / "raw" / "holidays"
RAW_EVENTS = DATA_LAKE_ROOT / "raw" / "events"

PROCESSED_CORRIDORS = DATA_LAKE_ROOT / "processed" / "corridors"
PROCESSED_FEATURES = DATA_LAKE_ROOT / "processed" / "features"
PROCESSED_MODEL_READY = DATA_LAKE_ROOT / "processed" / "model_ready"

VALIDATION_RULES = METADATA_DIR / "validation_rules.json"
USD_MXN_SCHEMA = METADATA_DIR / "usd_mxn_schema.json"
DATA_CATALOG = METADATA_DIR / "data_catalog.json"
SOURCE_REGISTRY = METADATA_DIR / "source_registry.json"
VALIDATION_REPORTS = METADATA_DIR / "validation_reports"

REMITTANCES_CSV = RAW_REMITTANCES / "us_mx_banxico_monthly.csv"
FED_POLICY_CSV = RAW_RATES / "fed_policy_rate_dfedtaru.csv"
FED_POLICY_META = RAW_RATES / "fed_policy_rate_dfedtaru.meta.json"
BANXICO_POLICY_CSV = RAW_RATES / "banxico_policy_rate.csv"
BANXICO_POLICY_META = RAW_RATES / "banxico_policy_rate.meta.json"
USD_MXN_SPOT_CSV = RAW_FX / "usd_mxn_spot.csv"
USD_MXN_SPOT_META = RAW_FX / "usd_mxn_spot.meta.json"
RPW_COST_CSV = RAW_REMITTANCES / "us_mx_rpw_cost_quarterly.csv"
RPW_COST_META = RAW_REMITTANCES / "us_mx_rpw_cost_quarterly.meta.json"
HOLIDAYS_CSV = RAW_HOLIDAYS / "us_mx_holidays.csv"
EVENTS_CSV = RAW_EVENTS / "central_bank_decisions.csv"

USD_MXN_DAILY_PARQUET = PROCESSED_CORRIDORS / "usd_mxn_daily.parquet"
USD_MXN_FEATURES_PARQUET = PROCESSED_FEATURES / "usd_mxn_features.parquet"
USD_MXN_MODEL_READY_PARQUET = PROCESSED_MODEL_READY / "usd_mxn_model_ready.parquet"
CORRIDOR_DAILY_JSON = PROCESSED_CORRIDORS / "us_mx_corridor_daily.json"
