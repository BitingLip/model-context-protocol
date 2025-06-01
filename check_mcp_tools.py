#!/usr/bin/env python3
"""
Check MCP Server Tools
"""
import sys
import asyncio
from pathlib import Path

# Add the src directory to the path
script_dir = Path(__file__).parent
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

from full_mcp_server import FullBitingLipMCPServer

async def check_tools():
    server = FullBitingLipMCPServer()
    tools = await server.handle_list_tools()
    
    memory_tool_names = [
        'store_memory', 'recall_memories', 'reflect_on_interaction', 
        'get_memory_summary', 'get_emotional_insights', 'update_memory', 
        'cleanup_expired_memories', 'get_project_context'
    ]
    
    found_memory_tools = [t['name'] for t in tools['tools'] if t['name'] in memory_tool_names]
    
    print(f"Total tools: {len(tools['tools'])}")
    print(f"Memory tools found: {len(found_memory_tools)}")
    print(f"Memory tools: {found_memory_tools}")
    
    print("\nAll available tools:")
    for i, tool in enumerate(tools['tools'], 1):
        name = tool['name']
        marker = " 🧠" if name in memory_tool_names else ""
        print(f"  {i:2d}. {name}{marker}")

if __name__ == "__main__":
    asyncio.run(check_tools())
