#!/bin/bash
# Build Handsfree.app via py2app in ALIAS mode.
#
# Alias mode gives the app a real in-process Python stub as its main executable, so the
# running process's identity is Handsfree.app — macOS TCC shows "Handsfree" (not "Python 3.12"),
# the grant survives Python/uv updates, and the menu bar renders when launched from the
# .app. It *references* the project's venv (no torch/mlx copy), so the bundle stays small.
#
# Usage: packaging/build_app.sh [output_dir]   (default: ~/Applications)
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${1:-$HOME/Applications}"
BUNDLE_ID="com.handsfree.dictation"

# py2app must run from the STABLE project venv (not an ephemeral `uv run --with` overlay),
# so the alias bundle references the durable interpreter + venv site-packages.
echo "Ensuring build deps (py2app) in the venv"
uv sync --project "$PROJECT_DIR" --group dev >/dev/null
VENV_PY="$PROJECT_DIR/.venv/bin/python"

# Build from a scratch CWD so setuptools doesn't read the project's pyproject.toml
# (its [project].dependencies become install_requires, which py2app rejects).
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT
cd "$BUILD_DIR"
echo "Building Handsfree.app (py2app alias mode) in ${BUILD_DIR}"
"$VENV_PY" "$PROJECT_DIR/packaging/setup_app.py" py2app -A

APP="$BUILD_DIR/dist/Handsfree.app"
[[ -d "$APP" ]] || { echo "error: $APP was not produced" >&2; exit 1; }

# Stable ad-hoc signature → TCC keys on a fixed identity (bundle id + cdhash).
codesign --force --deep --sign - --identifier "$BUNDLE_ID" "$APP"

mkdir -p "$OUT_DIR"
rm -rf "$OUT_DIR/Handsfree.app"
cp -R "$APP" "$OUT_DIR/Handsfree.app"
codesign --force --deep --sign - --identifier "$BUNDLE_ID" "$OUT_DIR/Handsfree.app"

echo "Installed → $OUT_DIR/Handsfree.app"
codesign -dv "$OUT_DIR/Handsfree.app" 2>&1 | grep -iE "Identifier|Signature|format" || true
