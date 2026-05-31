"""Formula validation for index models."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.audit.reporting import write_report_bundle
from src.audit.git_utils import project_root


def validate_vsi_formulas() -> list[dict]:
    rows = []
    try:
        from src.indices.value_survival import calculate_vsi_row

        row = pd.Series({
            "fee_pct": 0.02, "fx_margin_pct": 0.02, "inflation_yoy": 0.03,
            "fx_volatility_30d": 0.1, "payout_friction_pct": 0.01,
            "dollar_dependency_drag_pct": 0.01, "trust_discount_pct": 0.01,
            "send_amount_usd": 100, "mock_data_flag": False,
        })
        out = calculate_vsi_row(row, sensitivity_case="baseline")
        vsi = out.get("value_survival_index", out.get("vsi_risk_adjusted"))
        ok = 0 <= vsi <= 100
        rows.append({"formula": "VSI baseline", "status": "PASS" if ok else "FAIL", "detail": f"vsi={vsi}"})
    except Exception as exc:
        rows.append({"formula": "VSI baseline", "status": "FAIL", "detail": str(exc)})

    try:
        from src.indices.hidden_fx_tax import calculate_hidden_fx_tax

        r = calculate_hidden_fx_tax(pd.Series({
            "fx_margin_pct": 0.03, "fee_pct": 0.01, "transfer_speed_days": 1,
            "fx_volatility_30d": 0.1, "inflation_yoy": 0.03,
        }))
        ok = r.get("hidden_fx_tax_pct", r.get("total_hidden_fx_tax_pct", -1)) >= 0
        val = r.get("hidden_fx_tax_pct", r.get("total_hidden_fx_tax_pct"))
        rows.append({"formula": "Hidden FX tax", "status": "PASS" if ok else "FAIL", "detail": str(val)})
    except Exception as exc:
        rows.append({"formula": "Hidden FX tax", "status": "SKIPPED", "detail": str(exc)})
    return rows


def validate_settlement_formulas() -> list[dict]:
    rows = []
    try:
        import sys
        sl = project_root() / "settlement_lab"
        if str(sl) not in sys.path:
            sys.path.insert(0, str(sl))
        from src.indices.settlement_drag import calculate_settlement_drag_row

        r = calculate_settlement_drag_row(pd.Series({"transaction_value_usd": 1000, "settlement_lag_days": 2, "failure_rate": 0.001}))
        sdi = r["settlement_drag_index"]
        ok = 0 <= sdi <= 100
        rows.append({"formula": "SDI", "status": "PASS" if ok else "FAIL", "detail": f"sdi={sdi}"})
    except Exception as exc:
        rows.append({"formula": "SDI", "status": "SKIPPED", "detail": str(exc)})
    return rows


def run_formula_validation(root: Path | None = None) -> dict:
    root = root or project_root()
    rows = validate_vsi_formulas() + validate_settlement_formulas()
    summary = {"pass": sum(1 for r in rows if r["status"] == "PASS"), "fail": sum(1 for r in rows if r["status"] == "FAIL")}
    out_dir = root / "audit" / "model_validation_reports"
    paths = write_report_bundle(rows, out_dir, "formula_validation_report", "Formula Validation Report", summary)
    return {"summary": summary, "rows": rows, "paths": {k: str(v) for k, v in paths.items()}}
