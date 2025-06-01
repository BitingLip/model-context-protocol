#!/usr/bin/env python3
"""
Check Memory Tools in MCP Server
"""
import asyncio
import json
import sys
from pathlib import Path

# Add the src directory to the path
script_dir = Path(__file__).parent
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

from full_mcp_server import FullBitingLipMCPServer

async def check_memory_tools():
    """Check all memory tools in the server."""
    server = FullBitingLipMCPServer()
    result = await server.handle_list_tools()
    tools = result['tools']
    
    print(f"Total tools: {len(tools)}")
    print("\nAll memory-related tools:")
    
    memory_keywords = ['memory', 'recall', 'reflect', 'emotional', 'cleanup', 'context']
    memory_tools = []
    
    for i, tool in enumerate(tools, 1):
        name = tool['name']
        desc = tool.get('description', 'No description')
        
        if any(keyword in name.lower() for keyword in memory_keywords):
            memory_tools.append(name)
            print(f"   {i:2d}. {name}")
            print(f"       {desc[:60]}...")
    
    print(f"\nFound {len(memory_tools)} memory tools:")
    for tool in memory_tools:
        print(f"   ✅ {tool}")
    
    # Check specific expected tools
    expected_memory_tools = [
        'store_memory', 'recall_memories', 'reflect_on_interaction',
        'get_memory_summary', 'get_emotional_insights', 'update_memory',
        'cleanup_expired_memories', 'get_project_context'
    ]
    
    missing = set(expected_memory_tools) - set([t['name'] for t in tools])
    if missing:
        print(f"\n❌ Missing expected tools: {missing}")
    else:
        print(f"\n✅ All {len(expected_memory_tools)} expected memory tools are present!")

if __name__ == "__main__":
    asyncio.run(check_memory_tools())
