#!/usr/bin/env python3
"""
Test MCP Server Connection - Simulate what VS Code does

This script tests the MCP server connection exactly like VS Code would,
to see if the memory tools are accessible.
"""
import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_connection():
    """Test MCP server connection like VS Code does."""
    print("🔍 Testing MCP Server Connection (VS Code simulation)...")
    
    # Start the MCP server process
    server_path = Path("c:/Users/admin/Desktop/BitingLip/biting-lip/interfaces/model-context-protocol")
    
    try:
        process = subprocess.Popen(
            ["python", "full_mcp_server.py"],
            cwd=str(server_path),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ MCP Server process started")
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "vscode-test", "version": "1.0.0"}
            }
        }
        
        print("📤 Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Initialize response: {response.get('result', {}).get('serverInfo', {}).get('name', 'unknown')}")
        
        # Send tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("📤 Requesting tools list...")
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        # Read tools response
        tools_response_line = process.stdout.readline()
        if tools_response_line:
            tools_response = json.loads(tools_response_line.strip())
            tools = tools_response.get('result', {}).get('tools', [])
            
            print(f"\n📊 Found {len(tools)} tools:")
            
            memory_tools = []
            for i, tool in enumerate(tools, 1):
                tool_name = tool.get('name', 'unknown')
                print(f"   {i:2d}. {tool_name}")
                
                if 'memory' in tool_name:
                    memory_tools.append(tool_name)
            
            print(f"\n🧠 Memory tools found: {len(memory_tools)}")
            for memory_tool in memory_tools:
                print(f"   ✅ {memory_tool}")
            
            if len(memory_tools) == 8:
                print("\n🎉 SUCCESS: All 8 memory tools are accessible via MCP!")
            else:
                print(f"\n❌ ISSUE: Expected 8 memory tools, found {len(memory_tools)}")
        
        # Cleanup
        process.terminate()
        process.wait(timeout=5)
        
    except Exception as e:
        print(f"❌ Error testing MCP connection: {e}")
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
