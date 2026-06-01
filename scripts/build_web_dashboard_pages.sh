#!/usr/bin/env bash
# Static-export Next.js dashboard for GitHub Pages at /br3n-macro-lab/dashboard/
set -euo pipefail
cd "$(dirname "$0")/.."

PAGES_BASE="${PAGES_BASE:-/br3n-macro-lab/dashboard}"
PUB_DIR="${1:-reports/publication/dashboard}"

if [[ ! -f web_dashboard/public/api/dashboard.json ]]; then
  echo "==> Exporting dashboard JSON..."
  python3 scripts/export_dashboard_api.py
fi

echo "==> Building Next.js static export (base: $PAGES_BASE)..."
(
  cd web_dashboard
  export NEXT_PUBLIC_BASE_PATH="$PAGES_BASE"
  export NEXT_STATIC_EXPORT=1
  npm run build
)

echo "==> Copying to $PUB_DIR ..."
rm -rf "$PUB_DIR"
mkdir -p "$PUB_DIR"
cp -r web_dashboard/out/* "$PUB_DIR/"

echo "Done. Dashboard will be served at: ${PAGES_BASE}/"
