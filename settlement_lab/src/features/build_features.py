"""Settlement feature engineering."""

from __future__ import annotations

import pandas as pd


def build_all_features(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    flows = tables.get("payment_flow_observations", pd.DataFrame())
    liq = tables.get("settlement_liquidity_table", pd.DataFrame())
    if flows.empty:
        return pd.DataFrame()

    f = flows.groupby(["country", "payment_system", "rail_type"], as_index=False).agg(
        settlement_lag_days=("settlement_lag_days", "mean"),
        finality_lag_hours=("finality_lag_hours", "mean"),
        availability_lag_hours=("availability_lag_hours", "mean"),
        settlement_value_usd=("transaction_value_usd", "sum"),
        value_in_transit_usd=("transaction_value_usd", lambda s: s.sum() * 0.1),
        failure_rate=("failure_rate", "mean"),
        return_rate=("return_rate", "mean"),
        chargeback_rate=("chargeback_rate", "mean"),
        mock_data_flag=("mock_data_flag", "first"),
        data_quality_score=("data_quality_score", "mean"),
        source_id=("source_id", "first"),
        methodology_version=("methodology_version", "first"),
    )
    f["settlement_velocity"] = 1 / f["settlement_lag_days"].clip(lower=0.01)
    f["payment_turnover_ratio"] = f["settlement_value_usd"] / f["settlement_value_usd"].mean()

    if not liq.empty:
        l = liq.groupby("payment_system", as_index=False).agg(
            prefunding_ratio=("prefunding_required_usd", lambda s: s.sum()),
            liquidity_buffer_ratio=("liquidity_buffer_usd", lambda s: s.sum()),
            avg_settlement_usd=("average_daily_settlement_value_usd", "mean"),
        )
        f = f.merge(l, left_on="payment_system", right_on="payment_system", how="left")
        f["prefunding_ratio"] = f["prefunding_ratio"] / f["avg_settlement_usd"].replace(0, 1)
        f["liquidity_buffer_ratio"] = f["liquidity_buffer_ratio"] / f["avg_settlement_usd"].replace(0, 1)

    fin = tables.get("finality_characteristics", pd.DataFrame())
    if not fin.empty:
        fin_agg = fin.groupby(["country", "rail_type"], as_index=False).agg(
            legal_finality_score=("legal_finality_score", "mean"),
            operational_finality_score=("operational_finality_score", "mean"),
            reversibility_risk_score=("reversibility_risk_score", "mean"),
            reconciliation_quality_score=("reconciliation_quality_score", "mean"),
        )
        f = f.merge(fin_agg, on=["country", "rail_type"], how="left")

    acc = tables.get("payment_access_and_inclusion", pd.DataFrame())
    if not acc.empty:
        f = f.merge(
            acc[["country", "digital_payment_usage_pct", "account_ownership_pct", "cash_dependency_proxy"]],
            on="country", how="left",
        )

    f["source_id"] = f.get("source_id", "MOCK_DEMO_ONLY")
    f["methodology_version"] = f.get("methodology_version", "settlement-lab-credible-1.0")
    if "data_quality_grade" not in f.columns:
        f["data_quality_grade"] = "Demo only"
    return f
