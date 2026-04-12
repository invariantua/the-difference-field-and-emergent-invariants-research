#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$ROOT_DIR/papers/position-paper/src"
BUILD_DIR="$ROOT_DIR/papers/position-paper/build"

mkdir -p "$BUILD_DIR"

if ! command -v latexmk >/dev/null 2>&1; then
  echo "Error: latexmk is not installed."
  exit 1
fi

latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -outdir="$BUILD_DIR" "$SRC_DIR/main.tex"

echo "Built PDF:"
echo "  $BUILD_DIR/main.pdf"
