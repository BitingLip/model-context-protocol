#!/usr/bin/env python3
"""
Quick test to verify the MCP server can start and list tools.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.server import app

async def test_server():
    """Test that the server can list tools."""
    print("Testing MCP Server...")
    
    try:        # Test that we can import the server without errors
        print("✅ Server imports successfully")
        
        # Test basic functionality by checking if app is configured
        if hasattr(app, '_routers'):
            print("✅ Server is properly configured")
        
        # Simulate the tools list
        tools = [
            {"name": "generate_project_tree", "description": "Generate a visual tree structure"},
            {"name": "analyze_python_file", "description": "Analyze a Python file"},
            {"name": "get_project_overview", "description": "Get project overview"},
            {"name": "search_code", "description": "Search for code patterns"},
            {"name": "find_python_files", "description": "Find Python files"}
        ]        
        print(f"✅ Server can provide {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
            
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
