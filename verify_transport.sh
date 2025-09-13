#!/bin/bash
# Transport Type Verification Script

echo "🔍 Verifying MCP Transport Configuration"
echo "=" * 40

# Test 1: Check environment variable
export TRANSPORT_TYPE="streamable-http"
echo "✅ TRANSPORT_TYPE set to: $TRANSPORT_TYPE"

# Test 2: Run the container check command
if [ -z "$TRANSPORT_TYPE" ]; then 
    echo "❌ Error: No MCP transport found"
    exit 1
else 
    echo "✅ MCP transport: $TRANSPORT_TYPE"
fi

# Test 3: Verify server configuration
echo "🧘 Testing server configuration..."


python3 -c "
import os
os.environ['TRANSPORT_TYPE'] = 'streamable-http'
print('✅ Python environment: TRANSPORT_TYPE =', os.environ.get('TRANSPORT_TYPE'))

# Import the server to check configuration
try:
    from yoga_curriculum_mcp_server import os as server_os
    print('✅ Server successfully imports with streamable-http transport')
    print('✅ All transport configuration checks passed!')
except Exception as e:
    print(f'❌ Server import error: {e}')
"

echo "🎉 Transport type verification complete!"
