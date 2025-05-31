#!/usr/bin/env python3
"""
Quick test to verify the MCP server can start and list tools.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from server import app

async def test_server():
    """Test that the server can list tools."""
    print("Testing MCP Server...")
    
    try:        # Test listing tools - need to call the handler directly
        from server import handle_list_tools
        tools = await handle_list_tools()
        
        print(f"✅ Server can list {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
            
        print("\n✅ MCP Server is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)
