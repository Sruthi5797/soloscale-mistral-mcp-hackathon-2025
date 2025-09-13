#!/bin/bash
set -e
echo "Python deps"
uv sync --frozen
echo "Node deps + build"
pushd src/poseflow_backend
npm ci || npm install
npm run build
popd