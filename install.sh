#!/bin/bash
set -e

echo "📦 Installing Python dependencies..."
uv sync --frozen

echo "📦 Installing Node.js dependencies..."
cd src/poseflow_backend
npm install
cd ../..