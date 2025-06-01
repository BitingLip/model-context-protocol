@echo off
REM Biting Lip MCP Server Startup Script for Windows
REM This script starts the MCP server for GitHub Copilot integration

echo Starting Biting Lip MCP Server...
echo =====================================

REM Change to the MCP directory
cd /d "c:\Users\admin\Desktop\BitingLip\biting-lip\interfaces\model-context-protocol"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import mcp, yaml" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
)

REM Test the server
echo Testing MCP server...
python test_mcp_integration.py

if errorlevel 1 (
    echo ERROR: MCP server test failed
    pause
    exit /b 1
)

echo.
echo ✅ MCP Server is ready!
echo.
echo 📋 To connect to GitHub Copilot:
echo 1. Open VS Code with the Biting Lip workspace
echo 2. The MCP configuration is already added to .vscode/settings.json
echo 3. Restart VS Code to load the MCP server
echo 4. GitHub Copilot will automatically use the 21 available tools
echo.
echo Press any key to start the MCP server in JSON-RPC mode...
pause >nul

echo Starting MCP server (press Ctrl+C to stop)...
python src/server.py
