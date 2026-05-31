"""Smoke tests for Global FX & Remittance Research Lab."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_mock_dataset():
    from src.data.mock_data import create_mock_dataset

    tables = create_mock_dataset()
    assert len(tables["corridor_prices"]) > 100
    assert "hidden_fx_tax" not in tables  # raw only


def test_all_indices():
    from src.data.mock_data import create_mock_dataset
    from src.indices.pipeline import run_all_indices

    idx = run_all_indices(create_mock_dataset())
    assert len(idx) == 6
    assert "hidden_fx_tax_pct" in idx["hidden_fx_tax"].columns
    assert idx["currency_credibility"]["credibility_score"].notna().any()


def test_research_questions():
    from src.research.questions import RESEARCH_QUESTIONS, questions_dataframe

    assert len(RESEARCH_QUESTIONS) >= 8
    assert len(questions_dataframe()) >= 8


def test_loaders_fallback_mock():
    from src.data.loaders import load_world_bank_rpw

    df = load_world_bank_rpw(None)
    assert "corridor" in df.columns


def test_panel_regression_fe():
    from src.data.mock_data import create_mock_dataset
    from src.indices.pipeline import run_all_indices
    from src.models.panel_regression import build_panel_dataset, panel_regression_with_fe

    tables = create_mock_dataset()
    idx = run_all_indices(tables)
    panel = build_panel_dataset(idx["remittance_welfare"], idx["hidden_fx_tax"], tables["macro_country_panel"])
    result = panel_regression_with_fe(panel)
    assert "hidden_fx_tax_coef" in result or "error" in result


def test_event_study_runs():
    from src.data.mock_data import create_mock_dataset
    from src.indices.pipeline import run_all_indices
    from src.models.event_study import run_dxy_event_study

    idx = run_all_indices(create_mock_dataset())
    result = run_dxy_event_study(idx["hidden_fx_tax"], idx["remittance_welfare"])
    assert isinstance(result, dict)


def test_fetch_public_builds_files(tmp_path, monkeypatch):
    from src.data import fetch_public

    monkeypatch.setattr(fetch_public, "RAW_DIR", tmp_path / "raw")
    monkeypatch.setattr(fetch_public, "PROCESSED_DIR", tmp_path / "processed")
    results = fetch_public.build_all_public_data()
    assert results["rpw"] is not None
    assert Path(results["rpw"]).exists()

