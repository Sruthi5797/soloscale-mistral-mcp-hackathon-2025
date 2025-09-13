#!/usr/bin/env bash
set -euo pipefail

echo "📦 Installing Python + Node dependencies for Poseflow MCP..."

# ---- Python (uv) ----
if command -v uv &>/dev/null; then
  echo "🐍 Syncing Python environment with uv..."
  uv sync --frozen --no-dev
else
  echo "⚠️ uv not found. Please install uv: https://github.com/astral-sh/uv"
  exit 1
fi

# ---- Node backend ----
pushd src/poseflow_backend > /dev/null

if [ -f package-lock.json ]; then
  echo "📦 Installing Node deps with npm ci..."
  npm ci
else
  echo "📦 Installing Node deps with npm install..."
  npm install
fi

echo "🔨 Building TypeScript backend..."
npm run build

popd > /dev/null

echo "✅ install.sh completed successfully."