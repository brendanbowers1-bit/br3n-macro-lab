# Reproducibility Report

**Generated:** 2026-05-31T20:59:47.131858+00:00

- Python: `3.9.6`
- OS: macOS-26.5-arm64-arm-64bit
- Git commit: `3d77ef33493a6e1a48e9074d29ad61511391ab79`
- Snapshot: `none`

## Pipeline steps

| Module | Step | Status |
|--------|------|--------|
| vsi | build_dataset.py | PASS |
| vsi | run_vsi.py | PASS |
| vsi | run_sensitivity.py | PASS |
| vsi | run_robustness.py | PASS |
| vsi | make_visuals.py | PASS |
| settlement | build_settlement_dataset.py | PASS |
| settlement | run_settlement_indices.py | PASS |
| settlement | run_settlement_sensitivity.py | PASS |
| settlement | run_settlement_robustness.py | PASS |
| settlement | make_settlement_visuals.py | PASS |

## Validation

[
  {
    "check": "data",
    "status": "FAIL",
    "summary": {
      "pass": 6,
      "fail": 20,
      "warning": 0,
      "total": 26
    }
  },
  {
    "check": "model",
    "status": "FAIL",
    "summary": {
      "pass": 3,
      "fail": 2,
      "skipped": 0
    }
  }
]

## Tests

pytest return code: 0

```
_study_runs
  /Users/brendanbowers/fx_regime_lab/tests/test_global_fx_lab_smoke.py:61: UserWarning: Using MOCK DATA for Global FX Research Lab. Place real files in data/raw/world_bank_rpw/, imf/, bis/, etc.
    idx = run_all_indices(create_mock_dataset())

tests/test_global_fx_lab_smoke.py::test_fetch_public_builds_files
  /Users/brendanbowers/fx_regime_lab/src/data/fetch_public.py:368: FutureWarning: The default fill_method='pad' in Series.pct_change is deprecated and will be removed in a future version. Either fill in any non-leading NA values prior to calling pct_change or specify 'fill_method=None' to not fill NA values.
    df["dxy_return"] = df["dxy_broad"].pct_change()

tests/test_global_fx_lab_smoke.py::test_fetch_public_builds_files
  /Users/brendanbowers/fx_regime_lab/src/data/fetch_public.py:369: FutureWarning: The default fill_method='pad' in Series.pct_change is deprecated and will be removed in a future version. Either fill in any non-leading NA values prior to calling pct_change or specify 'fill_method=None' to not fill NA values.
    df["dxy_return_20d"] = df["dxy_broad"].pct_change(20)

tests/test_snapshot_system.py::test_create_and_list_snapshot
  /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/zipfile.py:1505: UserWarning: Duplicate name: 'settlement_lab/requirements.txt'
    return self._open_to_write(zinfo, force_zip64=force_zip64)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html

```

## Line count

{
  "files": 520,
  "total_lines": 102858,
  "code_lines": 93249,
  "comment_lines": 356,
  "blank_lines": 9253
}