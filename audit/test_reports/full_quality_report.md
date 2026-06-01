# Full Quality Report

**Generated:** 2026-06-01T02:46:02.600825+00:00

## Summary

- **pass**: 5
- **fail**: 2
- **warning**: 0
- **skipped**: 6
- **timestamp**: 2026-06-01T02:46:02.547480+00:00
- **python**: 3.9.6 (default, Apr 30 2025, 02:07:17) 
[Clang 17.0.0 (clang-1700.0.13.5)]
- **platform**: macOS-26.5-arm64-arm-64bit
- **git_commit**: 736174d4c86e9d23d96dada9076a4f355e1d65cd

## Results

| step | status | detail |
| --- | --- | --- |
| pre_run_snapshot | SKIPPED | skip_snapshot=True |
| project_metrics | PASS | files=655 |
| data_validation | FAIL | {"pass": 6, "fail": 20, "warning": 0, "total": 26} |
| formula_validation | PASS | {"pass": 2, "fail": 0} |
| model_validation | FAIL | {"pass": 3, "fail": 2, "skipped": 0} |
| pytest_quality | PASS | el/_linear_loss.py:330: RuntimeWarning: divide by zero encountered in matmul
    grad[:n_features] = X.T @ grad_pointwise + l2_reg_strength * weights

tests/test_fx_terminal_smoke.py::test_baseline_model_fit_predict
  /Users/brendanbowers/fx_regime_lab/.venv/lib/python3.9/site-packages/sklearn/linear_model/_linear_loss.py:330: RuntimeWarning: overflow encountered in matmul
    grad[:n_features] = X.T @ grad_pointwise + l2_reg_strength * weights

tests/test_fx_terminal_smoke.py::test_baseline_model_fit_predict
  /Users/brendanbowers/fx_regime_lab/.venv/lib/python3.9/site-packages/sklearn/linear_model/_linear_loss.py:330: RuntimeWarning: invalid value encountered in matmul
    grad[:n_features] = X.T @ grad_pointwise + l2_reg_strength * weights

tests/test_global_fx_lab_smoke.py::test_mock_dataset
  /Users/brendanbowers/fx_regime_lab/tests/test_global_fx_lab_smoke.py:15: UserWarning: Using MOCK DATA for Global FX Research Lab. Place real files in data/raw/world_bank_rpw/, imf/, bis/, etc.
    tables = create_mock_dataset()

tests/test_global_fx_lab_smoke.py::test_all_indices
  /Users/brendanbowers/fx_regime_lab/tests/test_global_fx_lab_smoke.py:24: UserWarning: Using MOCK DATA for Global FX Research Lab. Place real files in data/raw/world_bank_rpw/, imf/, bis/, etc.
    idx = run_all_indices(create_mock_dataset())

tests/test_global_fx_lab_smoke.py::test_panel_regression_fe
  /Users/brendanbowers/fx_regime_lab/tests/test_global_fx_lab_smoke.py:49: UserWarning: Using MOCK DATA for Global FX Research Lab. Place real files in data/raw/world_bank_rpw/, imf/, bis/, etc.
    tables = create_mock_dataset()

tests/test_global_fx_lab_smoke.py::test_event_study_runs
  /Users/brendanbowers/fx_regime_lab/tests/test_global_fx_lab_smoke.py:61: UserWarning: Using MOCK DATA for Global FX Research Lab. Place real files in data/raw/world_bank_rpw/, imf/, bis/, etc.
    idx = run_all_indices(create_mock_dataset())

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
 |
| pytest_settlement | PASS | gs.py::test_mock_source_id
settlement_lab/tests/test_mock_data_flags.py::test_mock_grade
  /Users/brendanbowers/fx_regime_lab/settlement_lab/src/data/mock_data.py:216: UserWarning: ⚠️ DEMO MODE: Synthetic settlement data only. Do not use for research conclusions or operational decisions.
    "fx_settlement_exposure": create_fx_settlement_exposure(),

settlement_lab/tests/test_data_quality.py::test_quality_score_range
settlement_lab/tests/test_data_quality.py::test_mock_quality_cap
settlement_lab/tests/test_mock_data_flags.py::test_mock_source_id
settlement_lab/tests/test_mock_data_flags.py::test_mock_grade
  /Users/brendanbowers/fx_regime_lab/settlement_lab/src/data/mock_data.py:217: UserWarning: ⚠️ DEMO MODE: Synthetic settlement data only. Do not use for research conclusions or operational decisions.
    "finality_characteristics": create_finality_characteristics(),

settlement_lab/tests/test_data_quality.py::test_quality_score_range
settlement_lab/tests/test_data_quality.py::test_mock_quality_cap
settlement_lab/tests/test_mock_data_flags.py::test_mock_source_id
settlement_lab/tests/test_mock_data_flags.py::test_mock_grade
  /Users/brendanbowers/fx_regime_lab/settlement_lab/src/data/mock_data.py:218: UserWarning: ⚠️ DEMO MODE: Synthetic settlement data only. Do not use for research conclusions or operational decisions.
    "payment_access_and_inclusion": create_payment_access(),

settlement_lab/tests/test_data_quality.py::test_quality_score_range
settlement_lab/tests/test_data_quality.py::test_mock_quality_cap
settlement_lab/tests/test_mock_data_flags.py::test_mock_source_id
settlement_lab/tests/test_mock_data_flags.py::test_mock_grade
  /Users/brendanbowers/fx_regime_lab/settlement_lab/src/data/mock_data.py:219: UserWarning: ⚠️ DEMO MODE: Synthetic settlement data only. Do not use for research conclusions or operational decisions.
    "payment_network_stress_events": create_stress_events(),

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
 |
| pytest_stablecoin | PASS | : 3 warnings
tests/test_settlement_window_compression.py: 2 warnings
tests/test_singleness_index.py: 2 warnings
tests/test_stablecoin_vsi.py: 2 warnings
  /Users/brendanbowers/fx_regime_lab/stablecoin_lab/src/data/mock_data.py:299: UserWarning: ⚠️ DEMO MODE: Synthetic stablecoin data only. Do not use for research conclusions, investment decisions, or operational treasury guidance.
    "off_ramp_characteristics": create_off_ramp_characteristics(),

tests/test_compliance_drag.py: 2 warnings
tests/test_data_quality.py: 3 warnings
tests/test_digital_run_velocity.py: 2 warnings
tests/test_dollarization_index.py: 1 warning
tests/test_finality_quality.py: 2 warnings
tests/test_liquidity_transformation.py: 2 warnings
tests/test_mock_data_flags.py: 3 warnings
tests/test_settlement_window_compression.py: 2 warnings
tests/test_singleness_index.py: 2 warnings
tests/test_stablecoin_vsi.py: 2 warnings
  /Users/brendanbowers/fx_regime_lab/stablecoin_lab/src/data/mock_data.py:300: UserWarning: ⚠️ DEMO MODE: Synthetic stablecoin data only. Do not use for research conclusions, investment decisions, or operational treasury guidance.
    "remittance_comparison": create_remittance_comparison(),

tests/test_compliance_drag.py: 2 warnings
tests/test_data_quality.py: 3 warnings
tests/test_digital_run_velocity.py: 2 warnings
tests/test_dollarization_index.py: 1 warning
tests/test_finality_quality.py: 2 warnings
tests/test_liquidity_transformation.py: 2 warnings
tests/test_mock_data_flags.py: 3 warnings
tests/test_settlement_window_compression.py: 2 warnings
tests/test_singleness_index.py: 2 warnings
tests/test_stablecoin_vsi.py: 2 warnings
  /Users/brendanbowers/fx_regime_lab/stablecoin_lab/src/data/mock_data.py:301: UserWarning: ⚠️ DEMO MODE: Synthetic stablecoin data only. Do not use for research conclusions, investment decisions, or operational treasury guidance.
    "regulatory_events": create_regulatory_events(),

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
 |
| smoke_vsi | SKIPPED | run scripts/smoke_test.py manually (slow) |
| smoke_settlement | SKIPPED | run scripts/smoke_test.py manually (slow) |
| reproduce_vsi | SKIPPED | run scripts/reproduce_all.py separately |
| reproduce_settlement | SKIPPED | run settlement_lab/scripts/reproduce_settlement_lab.py separately |
| reproduce_stablecoin | SKIPPED | run stablecoin_lab/scripts/reproduce_stablecoin_lab.py separately |