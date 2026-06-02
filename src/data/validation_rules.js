/** Validation rules for USD/MXN canonical sample dataset. */
module.exports = {
  schema_id: "usd_mxn_canonical_sample_v1",
  required_columns: [
    "date", "usd_mxn_spot", "usd_return_1d", "usd_return_5d", "us_policy_rate", "mx_policy_rate",
    "rate_differential", "carry_proxy", "volatility_20d", "volatility_regime", "spread_proxy_bps",
    "event_flag", "event_description", "holiday_flag", "holiday_description", "liquidity_proxy",
    "remittance_cost_proxy", "data_mode", "source_lineage",
  ],
  valid_volatility_regimes: ["low", "normal", "elevated", "crisis", "unknown"],
  valid_data_modes: ["synthetic", "sample", "live", "mixed", "research_starter"],
  max_daily_move_pct: 0.05,
  stale_days_warning: 30,
};
