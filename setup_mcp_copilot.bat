@echo off
echo ========================================
echo Biting Lip MCP Server Setup for Copilot
echo ========================================
echo.

cd "c:\Users\admin\Desktop\BitingLip\biting-lip\interfaces\model-context-protocol"

echo Step 1: Testing MCP Server...
echo {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}} | python src/server.py > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: MCP Server failed to start. Check Python installation and dependencies.
    pause
    exit /b 1
)
echo ✓ MCP Server is working

echo.
echo Step 2: Creating MCP Configuration Files...

echo Creating global MCP config...
if not exist "%APPDATA%\Code\User" mkdir "%APPDATA%\Code\User"

echo {"mcpServers": {"biting-lip-tools": {"command": "python", "args": ["src/server.py"], "cwd": "c:\\Users\\admin\\Desktop\\BitingLip\\biting-lip\\interfaces\\model-context-protocol", "env": {}}}} > "%APPDATA%\Code\User\mcp.json"
echo ✓ Created global MCP config

echo.
echo Step 3: Starting MCP Server in Background...
start /B python src/server.py
echo ✓ MCP Server started

echo.
echo Step 4: Configuration Summary
echo ========================================
echo Server Location: c:\Users\admin\Desktop\BitingLip\biting-lip\interfaces\model-context-protocol\src\server.py
echo Tools Available: 21 specialized tools
echo Configuration: %APPDATA%\Code\User\mcp.json
echo.
echo Step 5: VS Code Integration
echo ========================================
echo 1. Install one of these MCP extensions in VS Code:
echo    - "Copilot MCP" (automatalabs.copilot-mcp)
echo    - "MCP-Client" (m1self.mcp-client)
echo.
echo 2. Restart VS Code completely
echo.
echo 3. Open GitHub Copilot Chat and try:
echo    - @mcp list tools
echo    - @biting-lip-tools
echo    - Look for "Biting Lip" in available tools
echo.
echo 4. Alternative: Use Claude/Anthropic with MCP support
echo.
pause
