#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting Poseflow MCP on port 3000..."

# Default: MCP runs on 3000, Node backend on 4000
export PORT=3000
export BACKEND_PORT=4000

# If you want to use an external backend, set POSEFLOW_BACKEND_URL before calling start.sh
# export POSEFLOW_BACKEND_URL=https://your-backend-url

# Start MCP (this will auto-spawn the Node backend if POSEFLOW_BACKEND_URL is not set)
python -m poseflow_mcp.main