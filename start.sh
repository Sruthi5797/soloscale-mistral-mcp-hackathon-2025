#!/bin/bash
# Alpine MCP Server Entry Point
# This script loads environment variables and starts the Yoga Curriculum MCP Server

set -e  # Exit on any error

echo "🏔️  Alpine MCP Server Startup"
echo "=============================="

# Load environment variables from .env.example (Alpine deployment)
if [ -f ".env.example" ]; then
    echo "📄 Loading environment variables..."
    set -a  # automatically export all variables
    source .env.example
    set +a
fi

# Ensure TRANSPORT_TYPE is set for Alpine
export TRANSPORT_TYPE="streamable-http"

echo "🔍 Environment Check:"
echo "TRANSPORT_TYPE: $TRANSPORT_TYPE"
echo "MISTRAL_API_KEY: ${MISTRAL_API_KEY:+***set***}"
echo "QDRANT_URL: ${QDRANT_URL:+***set***}"

# Verify transport type (this is the check that was failing)
if [ -z "$TRANSPORT_TYPE" ]; then 
    echo "❌ Error: No MCP transport found"
    exit 1
else 
    echo "✅ MCP transport: $TRANSPORT_TYPE"
fi

echo "🧘 Starting Yoga Curriculum MCP Server..."

# Set Python path for proper imports
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Navigate to server directory
cd src/mcpservers

# Start the FastMCP server
exec python3 yoga_curriculum_mcp_server.py
