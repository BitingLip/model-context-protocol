#!/bin/bash
# Biting Lip MCP Server Startup Script for Linux/Mac
# This script starts the MCP server for GitHub Copilot integration

echo "Starting Biting Lip MCP Server..."
echo "====================================="

# Change to the MCP directory
cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Using Python: $PYTHON_CMD"

# Check if required packages are installed
if ! $PYTHON_CMD -c "import mcp, yaml" &> /dev/null; then
    echo "Installing required packages..."
    $PYTHON_CMD -m pip install -r requirements.txt
fi

# Test the server
echo "Testing MCP server..."
$PYTHON_CMD test_mcp_integration.py

if [ $? -ne 0 ]; then
    echo "ERROR: MCP server test failed"
    exit 1
fi

echo ""
echo "✅ MCP Server is ready!"
echo ""
echo "📋 To connect to GitHub Copilot:"
echo "1. Open VS Code with the Biting Lip workspace"
echo "2. The MCP configuration is already added to .vscode/settings.json"
echo "3. Restart VS Code to load the MCP server"
echo "4. GitHub Copilot will automatically use the 21 available tools"
echo ""
echo "Press Enter to start the MCP server in JSON-RPC mode..."
read

echo "Starting MCP server (press Ctrl+C to stop)..."
$PYTHON_CMD src/server.py
