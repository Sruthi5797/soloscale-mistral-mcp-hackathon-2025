#!/usr/bin/env bash
set -e


echo "Starting poseflow-backend (Node) on :4000 ..."
cd src/poseflow_backend
npm run start &    # run in background
cd ../..

echo "Starting Poseflow MCP (streamable-http) ..."
python -m poseflow_mcp.main