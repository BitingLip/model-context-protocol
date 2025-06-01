#!/usr/bin/env python3
"""Quick script to list all available tools in the MCP server."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from server import BitingLipMCPServer

def main():
    server = BitingLipMCPServer()
    
    tools = server.list_tools()
    print(f"Total tools: {len(tools['tools'])}")
    print("\nAvailable tools:")
    print("=" * 50)
    
    for i, tool in enumerate(tools['tools'], 1):
        print(f"{i:2d}. {tool['name']}")
        print(f"    {tool['description']}")
        print()

if __name__ == "__main__":
    main()
