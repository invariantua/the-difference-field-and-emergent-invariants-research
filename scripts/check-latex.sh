#!/usr/bin/env bash
set -euo pipefail

if command -v chktex >/dev/null 2>&1; then
  chktex -q -n22 papers/position-paper/src/main.tex || true
else
  echo "chktex not installed; skipping."
fi
