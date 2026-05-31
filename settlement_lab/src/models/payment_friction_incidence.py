"""
Payment Friction Incidence Model (PFI) — who bears payment-system costs.

Incidence estimates are model-based and require empirical validation.
Research-only.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import LAB_LIMITATIONS, METHODOLOGY_VERSION

PFI_LIMITATIONS = (
    "Incidence estimates are model-based and require empirical validation. "
    "Legal and economic incidence may differ. " + LAB_LIMITATIONS
)

PASS_THROUGH = {
    "conservative": {"merchant": 0.5, "consumer": 0.3, "recipient": 0.1, "bank": 0.05, "network": 0.05},
    "baseline": {"merchant": 0.35, "consumer": 0.25, "recipient": 0.15, "bank": 0.15, "network": 0.10},
    "severe": {"merchant": 0.2, "consumer": 0.4, "recipient": 0.2, "bank": 0.1, "network": 0.1},
}


def calculate_friction_incidence_row(
    total_cost_per_100: float,
    sensitivity_case: str = "baseline",
) -> dict:
    shares = PASS_THROUGH[sensitivity_case]
    return {
        "total_friction_per_100": total_cost_per_100,
        "estimated_cost_borne_by_consumer_pct": shares["consumer"] * 100,
        "estimated_cost_borne_by_merchant_pct": shares["merchant"] * 100,
        "estimated_cost_borne_by_bank_pct": shares["bank"] * 100,
        "estimated_cost_borne_by_network_pct": shares["network"] * 100,
        "estimated_cost_borne_by_recipient_pct": shares["recipient"] * 100,
        "estimated_cost_borne_by_processor_pct": 100 - sum(shares.values()) * 100,
        "pass_through_assumption": sensitivity_case,
        "assumptions": "Model-based pass-through; not observed incidence.",
        "methodology_version": METHODOLOGY_VERSION,
        "limitations": PFI_LIMITATIONS,
    }


def calculate_friction_incidence_table(
    flows: pd.DataFrame,
    sdi: pd.DataFrame,
    olb: pd.DataFrame,
    sensitivity_case: str = "baseline",
) -> pd.DataFrame:
    if flows.empty:
        return pd.DataFrame()

    sdi_map = sdi.groupby("entity")["settlement_drag_cost_per_100"].mean().to_dict() if not sdi.empty else {}
    olb_map = olb.groupby("payment_system")["liquidity_cost_per_100"].mean().to_dict() if not olb.empty else {}

    agg = flows.groupby(["country", "payment_system", "rail_type"], as_index=False).agg(
        chargeback_rate=("chargeback_rate", "mean"),
        failure_rate=("failure_rate", "mean"),
        data_quality_score=("data_quality_score", "mean"),
        mock_data_flag=("mock_data_flag", "first"),
    )

    rows = []
    for _, row in agg.iterrows():
        entity = f"{row['country']} | {row['payment_system']}"
        friction = sdi_map.get(entity, 0.5) + olb_map.get(row["payment_system"], 0.2)
        friction += row["chargeback_rate"] * 100 + row["failure_rate"] * 100
        calc = calculate_friction_incidence_row(friction, sensitivity_case)
        calc["entity"] = entity
        calc["entity_type"] = "rail"
        calc["country"] = row["country"]
        calc["rail_type"] = row["rail_type"]
        calc["data_quality_score"] = row["data_quality_score"]
        calc["data_quality_grade"] = row.get("data_quality_grade", "Demo only")
        calc["mock_data_flag"] = row["mock_data_flag"]
        calc["source_id"] = row.get("source_id", "MOCK_DEMO_ONLY")
        rows.append(calc)
    return pd.DataFrame(rows)
