#!/usr/bin/env python3
"""
Test script for the three MCP servers.
"""

import json
import subprocess
import sys
from pathlib import Path

def test_server(server_script, server_name):
    """Test a single MCP server by asking it to list tools."""
    print(f"\n=== Testing {server_name} ===")
    
    try:
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent
        )
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        
        # Send tools/list request
        list_request = {
            "jsonrpc": "2.0", 
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        # Send both requests
        requests = [
            json.dumps(init_request),
            json.dumps(list_request)
        ]
        
        input_data = '\n'.join(requests) + '\n'
        
        # Get response with timeout
        try:
            stdout, stderr = process.communicate(input=input_data, timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"❌ {server_name}: Timeout")
            return False
            
        # Parse responses
        if process.returncode is None:
            process.terminate()
            
        print(f"stderr: {stderr}")
        
        if stdout.strip():
            lines = stdout.strip().split('\n')
            for line in lines:
                try:
                    response = json.loads(line)
                    if response.get('id') == 2:  # tools/list response
                        tools = response.get('result', {}).get('tools', [])
                        print(f"✅ {server_name}: {len(tools)} tools available")
                        for tool in tools[:3]:  # Show first 3 tools
                            print(f"   - {tool['name']}: {tool['description'][:50]}...")
                        if len(tools) > 3:
                            print(f"   ... and {len(tools) - 3} more tools")
                        return True
                except json.JSONDecodeError:
                    continue
                    
        print(f"❌ {server_name}: No valid response")
        return False
        
    except Exception as e:
        print(f"❌ {server_name}: Error - {e}")
        return False

def main():
    """Test all three MCP servers."""
    print("Testing Biting Lip MCP Server Architecture")
    print("=" * 50)
    
    servers = [
        ("memory_server.py", "Memory Server"),
        ("ai_dev_server.py", "AI Development Server"), 
        ("core_tools_server.py", "Core Tools Server")
    ]
    
    results = []
    for script, name in servers:
        result = test_server(script, name)
        results.append((name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} servers")
    
    if passed == len(results):
        print("\n🎉 All MCP servers are working correctly!")
        print("\nNext steps:")
        print("1. Restart VS Code to load the new MCP configuration")
        print("2. The servers will be available as:")
        print("   - biting-lip-memory (8 memory tools)")
        print("   - biting-lip-ai-dev (5 AI development tools)")  
        print("   - biting-lip-core-tools (17 project analysis tools)")
    else:
        print(f"\n⚠️  {len(results) - passed} server(s) need attention")

if __name__ == "__main__":
    main()
