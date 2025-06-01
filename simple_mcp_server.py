#!/usr/bin/env python3
"""
Simplified MCP Server for GitHub Copilot Integration
"""

import asyncio
import json
import sys
from typing import Any, Dict, List

class SimpleMCPServer:
    """Simplified MCP Server for GitHub Copilot."""
    
    def __init__(self):
        self.name = "biting-lip-tools"
        self.version = "1.0.0"
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version
            }
        }
    
    async def handle_list_tools(self) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {
            "tools": [
                {
                    "name": "hello_world",
                    "description": "Simple test tool that returns a greeting",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name to greet"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "analyze_project",
                    "description": "Analyze the Biting Lip project structure",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]
        }
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        if name == "hello_world":
            user_name = arguments.get("name", "World")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Hello, {user_name}! This is the Biting Lip MCP Server working with GitHub Copilot."
                    }
                ]
            }
        elif name == "analyze_project":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Biting Lip AI Platform Analysis:\n\n✅ 21 specialized tools available\n✅ Multiple managers (cluster, model, task, gateway)\n✅ CLI, GUI, and MCP interfaces\n✅ Configuration management system\n✅ Docker containerization ready"
                    }
                ]
            }
        else:
            raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main MCP server loop."""
    server = SimpleMCPServer()
    
    # Send initial capabilities to stderr for debugging
    sys.stderr.write("Biting Lip MCP Server Starting...\n")
    sys.stderr.flush()
    
    while True:
        try:
            # Read a line from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            # Parse the JSON-RPC message
            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                sys.stderr.write(f"JSON decode error: {e} for line: {line}\n")
                sys.stderr.flush()
                continue
            
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            sys.stderr.write(f"Received method: {method}\n")
            sys.stderr.flush()
            
            # Handle the request
            try:
                if method == "initialize":
                    result = await server.handle_initialize(params)
                elif method == "initialized":
                    # Just acknowledge the initialized notification
                    continue
                elif method == "tools/list":
                    result = await server.handle_list_tools()
                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    result = await server.handle_call_tool(tool_name, arguments)
                elif method == "ping":
                    result = {"status": "pong"}
                elif method == "notifications/initialized":
                    # Handle notification
                    continue
                else:
                    # Unknown method
                    sys.stderr.write(f"Unknown method: {method}\n")
                    sys.stderr.flush()
                    if request_id is not None:
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method not found: {method}"
                            }
                        }
                        print(json.dumps(error_response))
                        sys.stdout.flush()
                    continue
                
                # Send successful response (only for requests with id)
                if request_id is not None:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                    print(json.dumps(response))
                    sys.stdout.flush()
                
            except Exception as e:
                sys.stderr.write(f"Error handling method {method}: {e}\n")
                sys.stderr.flush()
                # Send error response (only for requests with id)
                if request_id is not None:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": str(e)
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                
        except Exception as e:
            sys.stderr.write(f"Server error: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    asyncio.run(main())
