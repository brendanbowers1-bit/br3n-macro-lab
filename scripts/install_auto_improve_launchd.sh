#!/usr/bin/env bash
# Install macOS LaunchAgent to run lab self-improvement on a schedule.
# Usage:
#   ./scripts/install_auto_improve_launchd.sh              # default: 6:30 AM daily
#   ./scripts/install_auto_improve_launchd.sh "0 7 * * 1"  # custom cron (7 AM Mondays)

set -euo pipefail
LAB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.br3n.fx-regime-lab.auto-improve"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
CRON="${1:-30 6 * * *}"  # minute hour dom month dow — 6:30 AM every day

# Parse simple "min hour * * *" into launchd Hour/Minute
read -r MIN HOUR _ _ _ <<< "$CRON"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${LAB_ROOT}/scripts/auto_improve_daily.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>${HOUR}</integer>
    <key>Minute</key>
    <integer>${MIN}</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>${LAB_ROOT}/data/runs/logs/launchd_stdout.log</string>
  <key>StandardErrorPath</key>
  <string>${LAB_ROOT}/data/runs/logs/launchd_stderr.log</string>
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/${LABEL}"

echo "Installed LaunchAgent: $PLIST"
echo "Schedule: daily at ${HOUR}:$(printf '%02d' "$MIN")"
echo "Logs:     $LAB_ROOT/data/runs/logs/"
echo ""
echo "Test now:  bash $LAB_ROOT/scripts/auto_improve_daily.sh"
echo "Uninstall: launchctl bootout gui/\$(id -u)/${LABEL} && rm $PLIST"
