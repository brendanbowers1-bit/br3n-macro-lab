#!/usr/bin/env bash
# Daily auto-improve: re-run pipelines, score evidence, snapshot run history.
# Research-only. Requires Mac to be awake at scheduled time (or use caffeinate).

set -euo pipefail
LAB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$LAB_ROOT/data/runs/logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/auto_improve_$(date +%Y%m%d).log"

{
  echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) auto-improve start ==="
  cd "$LAB_ROOT"
  bash scripts/run_full_lab_pipeline.sh
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python scripts/run_self_improvement.py
  echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) auto-improve done ==="
} >> "$LOG" 2>&1
