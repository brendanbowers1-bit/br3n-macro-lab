#!/usr/bin/env bash
# Full FX Lab research pipeline — data → news → carry → models → reports → status.
# Research-only. No live trading.

set -euo pipefail
LAB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$LAB_ROOT"

# shellcheck disable=SC1091
source .venv/bin/activate

echo "============================================================"
echo "BR3N Macro Labs — Full Lab Pipeline"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) UTC"
echo "============================================================"

run_step() {
  local name="$1"
  shift
  echo ""
  echo ">>> $name"
  if "$@"; then
    echo "    OK: $name"
    return 0
  else
    echo "    FAILED: $name (exit $?)" >&2
    return 1
  fi
}

FAIL=0

run_step "USD/MXN backtest" python scripts/run_usdmxn_backtest.py || FAIL=1
run_step "Data upgrade report" python scripts/run_data_upgrade_report.py || FAIL=1
run_step "Data quality" python scripts/run_data_quality.py || FAIL=1

if [[ -f scripts/run_news_layer.py ]]; then
  run_step "News layer" python scripts/run_news_layer.py || FAIL=1
else
  echo ">>> News layer — skipped (script missing)"
fi

if [[ -f scripts/run_carry_layer.py ]]; then
  run_step "Carry layer" python scripts/run_carry_layer.py || FAIL=1
else
  echo ">>> Carry layer — skipped (script missing)"
fi

run_step "Under-tested research" python scripts/run_under_tested_research.py || FAIL=1

if [[ -f scripts/run_flagship_research_lane.py ]]; then
  run_step "Flagship research lane" python scripts/run_flagship_research_lane.py || FAIL=1
fi

run_step "Model zoo" python scripts/run_model_zoo.py || FAIL=1

if [[ -f scripts/generate_model_zoo_report.py ]]; then
  run_step "Model zoo report" python scripts/generate_model_zoo_report.py || FAIL=1
fi

echo ""
echo "============================================================"
if [[ "$FAIL" -eq 0 ]]; then
  echo "Pipeline complete. Run: python scripts/run_self_improvement.py"
  echo "Then read: reports/LAB_STATUS.md (after self-improvement)"
else
  echo "Pipeline finished with errors. Check logs above."
fi
echo "============================================================"

exit "$FAIL"
