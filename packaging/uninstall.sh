#!/bin/bash
# Uninstall Handsfree: quit the app, delete the bundle, and clear its macOS permissions.
#
# Usage: packaging/uninstall.sh [--model]
#   --model   also delete the cached speech model (~442 MB)
#
# Leaves the project folder/venv in place — remove those manually if you no longer want them.
set -euo pipefail

APP="$HOME/Applications/Handsfree.app"
BUNDLE_ID="com.handsfree.dictation"
MODEL_CACHE="$HOME/.cache/huggingface/hub/models--mlx-community--whisper-large-v3-turbo-q4"

echo "Stopping Handsfree..."
pkill -f "Handsfree.app/Contents/MacOS/Handsfree" 2>/dev/null && echo "  stopped" || echo "  (not running)"

if [[ -d "$APP" ]]; then
  rm -rf "$APP"
  echo "Removed $APP"
else
  echo "No app bundle at $APP"
fi

echo "Clearing macOS permissions (Accessibility / Input Monitoring / Microphone)..."
for svc in Accessibility ListenEvent Microphone; do
  tccutil reset "$svc" "$BUNDLE_ID" >/dev/null 2>&1 && echo "  reset $svc" || echo "  ($svc: nothing to reset)"
done

if [[ "${1:-}" == "--model" ]]; then
  if [[ -d "$MODEL_CACHE" ]]; then
    rm -rf "$MODEL_CACHE"
    echo "Removed cached model ($MODEL_CACHE)"
  else
    echo "No cached model at $MODEL_CACHE"
  fi
fi

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo
echo "Done. The project folder was left in place — to remove the source/venv too:"
echo "  rm -rf \"$PROJECT_DIR\""
