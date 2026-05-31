#!/usr/bin/env python3
"""Smoke tests for BR3N Value Survival Index — production readiness."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_mock_data_creation():
    from src.data.mock_data import create_mock_dataset

    tables = create_mock_dataset()
    assert len(tables["corridor_prices"]) > 50
    assert "United States→Mexico" in tables["corridor_prices"]["corridor"].values


def test_vsi_calculation():
    from src.data.build_dataset import build_value_survival_dataset

    ds = build_value_survival_dataset()
    vsi = ds["value_survival_outputs"]
    assert "value_survival_index" in vsi.columns
    assert vsi["value_survival_index"].notna().any()
    assert (vsi["value_survival_index"] >= 0).all()
    assert (vsi["value_survival_index"] <= 100).all()


def test_no_negative_vsi():
    from src.data.build_dataset import build_value_survival_dataset

    vsi = build_value_survival_dataset()["value_survival_outputs"]
    assert (vsi["value_survival_index"] >= 0).all()
    assert (vsi["real_usable_value_delivered_pct"] >= 0).all()
    assert (vsi["real_usable_value_delivered_pct"] <= 1).all()


def test_output_columns():
    required = [
        "corridor", "explicit_fee_loss_pct", "fx_spread_loss_pct", "timing_loss_pct",
        "volatility_loss_pct", "inflation_erosion_pct", "payout_friction_pct",
        "dollar_dependency_drag_pct", "trust_discount_pct", "total_value_loss_pct",
        "real_usable_value_delivered_pct", "value_survival_index", "value_loss_usd_per_100",
        "interpretation", "mock_data_flag", "data_mode", "data_quality_score", "limitations",
    ]
    from src.data.build_dataset import build_value_survival_dataset

    vsi = build_value_survival_dataset()["value_survival_outputs"]
    for col in required:
        assert col in vsi.columns, f"Missing column: {col}"


def test_data_quality_scoring():
    from src.data.build_dataset import build_value_survival_dataset
    from src.data.vsi_quality import assess_dataset_provenance

    ds = build_value_survival_dataset()
    prov = assess_dataset_provenance(ds)
    assert prov.data_mode in ("real", "mixed", "demo")
    assert 0 <= prov.overall_quality_score <= 1
    assert (ds["value_survival_outputs"]["data_quality_score"] >= 0).all()
    assert (ds["value_survival_outputs"]["data_quality_score"] <= 1).all()


def test_hidden_fx_tax_subindex():
    from src.data.mock_data import create_mock_dataset
    from src.indices.hidden_fx_tax import calculate_hidden_fx_tax_table, rank_corridors_by_hidden_fx_tax

    tables = create_mock_dataset()
    hft = calculate_hidden_fx_tax_table(tables["corridor_prices"], tables["fx_rates"])
    ranked = rank_corridors_by_hidden_fx_tax(hft)
    assert "hidden_fx_tax_pct" in ranked.columns
    assert len(ranked) > 0


def test_currency_trust():
    from src.data.mock_data import create_mock_dataset
    from src.indices.currency_trust import calculate_currency_trust_table

    tables = create_mock_dataset()
    trust = calculate_currency_trust_table(tables["macro_country_panel"], tables["fx_rates"])
    assert "currency_trust_score" in trust.columns


def test_dashboard_import():
    import importlib

    mod = importlib.import_module("src.dashboard.app")
    assert hasattr(mod, "main")


def test_visuals_module():
    from src.visuals.vsi_charts import chart_ranked_vsi, corridor_summary
    from src.data.vsi_loader import load_vsi_dataset

    ds = load_vsi_dataset(rebuild=False)
    summary = corridor_summary(ds["value_survival_outputs"])
    fig = chart_ranked_vsi(summary)
    assert fig is not None


def test_make_visuals_script():
    import subprocess

    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "make_visuals.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr or r.stdout
    assert (ROOT / "reports" / "figures" / "vsi_corridor_summary.csv").exists()


def main() -> None:
    tests = [
        test_mock_data_creation,
        test_vsi_calculation,
        test_no_negative_vsi,
        test_output_columns,
        test_data_quality_scoring,
        test_hidden_fx_tax_subindex,
        test_currency_trust,
        test_dashboard_import,
        test_visuals_module,
        test_make_visuals_script,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {t.__name__}: {exc}")
    print(f"\n{passed}/{len(tests)} passed")
    if passed != len(tests):
        sys.exit(1)


if __name__ == "__main__":
    main()
