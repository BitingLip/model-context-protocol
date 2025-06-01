#!/usr/bin/env python3
"""
Memory MCP Server - AI Memory System Tools

Model Context Protocol server specifically for AI memory management and persistence.
This server provides sophisticated memory storage, retrieval, and emotional context 
management to enable true continuity in AI-human collaboration.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add the current directory to the path for tool imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Import memory tools
from tools.memory_mcp_tool import MemoryMCPTool  # type: ignore


def get_project_root() -> str:
    """Get the Biting Lip project root directory (5 levels up from this file)."""
    return str(Path(__file__).parent.parent.parent.parent.parent)


class MemoryMCPServer:
    """MCP Server for AI Memory System - Persistent memory across conversations."""
    
    def __init__(self):
        self.name = "memory"
        self.version = "1.0.0"
        self.project_root = get_project_root()
        
        # Initialize memory system
        self.memory_tool = MemoryMCPTool(self.project_root)
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version,
                "description": "AI Memory System for persistent collaboration context"
            }
        }
    
    async def handle_list_tools(self) -> Dict[str, Any]:
        """List all memory-related tools."""
        return {
            "tools": [
                {
                    "name": "store_memory",
                    "description": "Store a new memory for later recall across conversations",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "memory_type": {"type": "string", "description": "Type of memory (e.g., 'code_insight', 'user_preference', 'problem_solution')"},
                            "content": {"description": "Memory content (text or structured data)"},
                            "title": {"type": "string", "description": "Optional short title for the memory"},
                            "importance": {"type": "number", "minimum": 0, "maximum": 1, "description": "Importance score (0.0 to 1.0)"},
                            "emotional_context": {"type": "object", "description": "Emotional context data"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "List of tags for categorization"},
                            "expires_in_days": {"type": "integer", "description": "Auto-delete after this many days"}
                        },
                        "required": ["memory_type", "content"]
                    }
                },
                {
                    "name": "recall_memories",
                    "description": "Recall relevant memories based on query and filters",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Text query for semantic search"},
                            "memory_type": {"type": "string", "description": "Filter by memory type"},
                            "project_id": {"type": "string", "description": "Filter by project (defaults to current)"},
                            "importance_threshold": {"type": "number", "minimum": 0, "maximum": 1, "description": "Minimum importance score"},
                            "limit": {"type": "integer", "minimum": 1, "maximum": 100, "description": "Maximum number of memories to return"},
                            "include_other_projects": {"type": "boolean", "description": "Include memories from other projects"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "recall_memories_weighted",
                    "description": "Enhanced recall with weighted scoring based on importance, recency, and relevance",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Text query for semantic search"},
                            "memory_type": {"type": "string", "description": "Filter by memory type"},
                            "project_id": {"type": "string", "description": "Filter by project (defaults to current)"},
                            "importance_threshold": {"type": "number", "minimum": 0, "maximum": 1, "description": "Minimum importance score"},
                            "limit": {"type": "integer", "minimum": 1, "maximum": 100, "description": "Maximum number of memories to return"},
                            "include_other_projects": {"type": "boolean", "description": "Include memories from other projects"},
                            "importance_weight": {"type": "number", "minimum": 0, "maximum": 1, "description": "Weight for importance score"},
                            "recency_weight": {"type": "number", "minimum": 0, "maximum": 1, "description": "Weight for recency score"},
                            "relevance_weight": {"type": "number", "minimum": 0, "maximum": 1, "description": "Weight for relevance score"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "store_persona_memory",
                    "description": "Store or update AI persona characteristics for identity evolution",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "persona_type": {"type": "string", "description": "Type of persona attribute (e.g., 'preference', 'skill', 'personality_trait')"},
                            "attribute_name": {"type": "string", "description": "Name of the attribute (e.g., 'coding_style', 'communication_preference')"},
                            "current_value": {"description": "Current value of the attribute"},
                            "confidence_score": {"type": "number", "minimum": 0, "maximum": 1, "description": "Confidence in this attribute (0.0 to 1.0)"},
                            "ai_instance_id": {"type": "string", "description": "Specific AI instance identifier"}
                        },
                        "required": ["persona_type", "attribute_name", "current_value"]
                    }
                },
                {
                    "name": "get_current_persona",
                    "description": "Retrieve current AI persona characteristics organized by type",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "persona_type": {"type": "string", "description": "Filter by specific persona type"},
                            "min_confidence": {"type": "number", "minimum": 0, "maximum": 1, "description": "Minimum confidence threshold"},
                            "ai_instance_id": {"type": "string", "description": "Specific AI instance identifier"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "generate_self_reflection",
                    "description": "Generate self-reflection on recent interactions for continuous improvement",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "reflection_trigger": {"type": "string", "description": "What triggered this reflection"},
                            "situation_summary": {"type": "string", "description": "Summary of the situation being reflected upon"},
                            "what_went_well": {"type": "string", "description": "What went well in the interaction"},
                            "what_could_improve": {"type": "string", "description": "What could be improved"},
                            "lessons_learned": {"type": "string", "description": "Key lessons learned"},
                            "reflection_scope": {"type": "string", "description": "Scope of reflection ('session', 'interaction', 'task')"}
                        },
                        "required": ["reflection_trigger", "situation_summary"]
                    }
                },
                {
                    "name": "apply_forgetting_curve",
                    "description": "Apply forgetting curve algorithm to decay old or unused memories",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "days_threshold": {"type": "integer", "description": "Age threshold in days"},
                            "access_threshold": {"type": "integer", "description": "Minimum access count threshold"},
                            "dry_run": {"type": "boolean", "description": "Just return what would be affected"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "get_persona_evolution_summary",
                    "description": "Get summary of how the AI persona has evolved over time",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "days_back": {"type": "integer", "minimum": 1, "maximum": 365, "description": "Number of days to analyze"},
                            "persona_type": {"type": "string", "description": "Filter by specific persona type"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "get_project_context",
                    "description": "Get context about the current project and memory system state",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]
        }
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution requests."""
        try:
            # Memory System Tools
            if name == "store_memory":
                result = self.memory_tool.store_memory(**arguments)
            elif name == "recall_memories":
                result = self.memory_tool.recall_memories(**arguments)
            elif name == "recall_memories_weighted":
                result = self.memory_tool.recall_memories_weighted(**arguments)
            elif name == "store_persona_memory":
                result = self.memory_tool.store_persona_memory(**arguments)
            elif name == "get_current_persona":
                result = self.memory_tool.get_current_persona(**arguments)
            elif name == "generate_self_reflection":
                result = self.memory_tool.generate_self_reflection(**arguments)
            elif name == "apply_forgetting_curve":
                result = self.memory_tool.apply_forgetting_curve(**arguments)
            elif name == "get_persona_evolution_summary":
                result = self.memory_tool.get_persona_evolution_summary(**arguments)
            elif name == "reflect_on_interaction":
                result = self.memory_tool.reflect_on_interaction(**arguments)
            elif name == "get_memory_summary":
                result = self.memory_tool.get_memory_summary(**arguments)
            elif name == "get_emotional_insights":
                result = self.memory_tool.get_emotional_insights(**arguments)
            elif name == "update_memory":
                result = self.memory_tool.update_memory(**arguments)
            elif name == "cleanup_expired_memories":
                result = self.memory_tool.cleanup_expired_memories(**arguments)
            elif name == "get_project_context":
                result = self.memory_tool.get_project_context(**arguments)
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: Unknown tool '{name}'"
                        }
                    ],
                    "isError": True
                }
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2, default=str)
                    }
                ]
            }
            
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing {name}: {str(e)}"
                    }
                ],
                "isError": True
            }
async def main():
    """Main MCP server loop."""
    server = MemoryMCPServer()
    
    # Send initial capabilities to stderr for debugging
    sys.stderr.write("Memory MCP Server Starting (8 memory tools)...\n")
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
