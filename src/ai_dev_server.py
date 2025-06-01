#!/usr/bin/env python3
"""
AI Development MCP Server - AI-Powered Development Tools

Model Context Protocol server for AI-powered development tools like code optimization,
test generation, documentation writing, and code review using local Ollama LLMs.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add the current directory to the path for tool imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Import AI development tools
from tools.ai_code_optimizer import AICodeOptimizer  # type: ignore
from tools.ai_smart_refactorer import AISmartRefactorer  # type: ignore
from tools.ai_test_generator import AITestGenerator  # type: ignore
from tools.ai_documentation_writer import AIDocumentationWriter  # type: ignore
from tools.ai_code_review_assistant import AICodeReviewAssistant  # type: ignore


def get_project_root() -> str:
    """Get the Biting Lip project root directory (3 levels up from this file)."""
    return str(Path(__file__).parent.parent.parent.parent)


class AIDevelopmentMCPServer:
    """MCP Server for AI-powered development tools using local Ollama LLMs."""
    
    def __init__(self):
        self.name = "biting-lip-ai-dev"
        self.version = "1.0.0"
        self.project_root = get_project_root()
        
        # Initialize AI development tools
        self.ai_code_optimizer = AICodeOptimizer(self.project_root)
        self.ai_smart_refactorer = AISmartRefactorer(self.project_root)
        self.ai_test_generator = AITestGenerator()
        self.ai_documentation_writer = AIDocumentationWriter()
        self.ai_code_review_assistant = AICodeReviewAssistant()
    
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
                "description": "AI-powered development tools using local Ollama LLMs"
            }
        }
    
    async def handle_list_tools(self) -> Dict[str, Any]:
        """List all AI development tools."""
        return {
            "tools": [
                {
                    "name": "optimize_code",
                    "description": "AI-powered code optimization using local Ollama LLMs, integrates with VS Code problems panel and Sourcery suggestions",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the file to optimize"},
                            "problems": {"type": "array", "items": {"type": "string"}, "description": "List of problems from VS Code diagnostics (optional)"}
                        },
                        "required": ["file_path"]
                    }
                },
                {
                    "name": "smart_refactor",
                    "description": "AI-powered intelligent code refactoring suggestions using local Ollama LLMs",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the file to refactor"},
                            "target_scope": {"type": "string", "enum": ["function", "class", "method", "file"], "description": "Scope of refactoring"},
                            "target_name": {"type": "string", "description": "Name of the specific function/class/method to refactor (optional)"}
                        },
                        "required": ["file_path"]
                    }
                },
                {
                    "name": "generate_tests",
                    "description": "AI-powered test generation using local Ollama LLMs",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the Python file to generate tests for"},
                            "test_types": {"type": "array", "items": {"type": "string", "enum": ["unit", "integration", "edge", "error"]}, "description": "Types of tests to generate"},
                            "coverage_target": {"type": "number", "description": "Target coverage percentage (0.0-1.0)"},
                            "include_mocks": {"type": "boolean", "description": "Whether to include mock suggestions"},
                            "include_fixtures": {"type": "boolean", "description": "Whether to generate pytest fixtures"}
                        },
                        "required": ["file_path"]
                    }
                },
                {
                    "name": "write_docs",
                    "description": "AI-powered documentation generation using local Ollama LLMs",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the Python file to document"},
                            "doc_types": {"type": "array", "items": {"type": "string", "enum": ["docstrings", "readme", "api", "tutorial"]}, "description": "Types of documentation to generate"},
                            "style": {"type": "string", "enum": ["google", "numpy", "sphinx"], "description": "Docstring style"},
                            "include_examples": {"type": "boolean", "description": "Whether to include code examples"},
                            "include_type_hints": {"type": "boolean", "description": "Whether to include type hint documentation"}
                        },
                        "required": ["file_path"]
                    }
                },
                {
                    "name": "review_code",
                    "description": "AI-powered code review using local Ollama LLMs, analyzes git diffs and provides comprehensive feedback",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_paths": {"type": "array", "items": {"type": "string"}, "description": "Specific files to review (if not using git diff)"},
                            "diff_content": {"type": "string", "description": "Git diff content to review (optional, will get from git if not provided)"},
                            "review_types": {"type": "array", "items": {"type": "string", "enum": ["quality", "security", "style", "performance"]}, "description": "Types of review to perform"},
                            "severity_threshold": {"type": "string", "enum": ["low", "medium", "high", "critical"], "description": "Minimum severity level to report"}                        },
                        "required": []
                    }
                }
            ]
        }
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution requests."""
        try:
            # AI Development Tools
            if name == "optimize_code":
                file_path = arguments["file_path"]
                problems = arguments.get("problems", [])
                result = self.ai_code_optimizer.optimize_code(file_path, problems)
            elif name == "smart_refactor":
                file_path = arguments["file_path"]
                target_scope = arguments.get("target_scope", "file")
                target_name = arguments.get("target_name")
                result = self.ai_smart_refactorer.analyze_refactoring_opportunities(file_path, target_scope)
            elif name == "generate_tests":
                file_path = arguments["file_path"]
                test_types = arguments.get("test_types", ["unit"])
                coverage_target = arguments.get("coverage_target", 0.8)
                include_fixtures = arguments.get("include_fixtures", True)
                include_mocks = arguments.get("include_mocks", True)
                result = await self.ai_test_generator.generate_tests(
                    file_path, test_types, coverage_target, include_fixtures, include_mocks
                )
            elif name == "write_docs":
                file_path = arguments["file_path"]
                doc_types = arguments.get("doc_types", ["docstrings"])
                style = arguments.get("style", "google")
                include_examples = arguments.get("include_examples", True)
                include_type_hints = arguments.get("include_type_hints", True)
                result = await self.ai_documentation_writer.write_docs(
                    file_path, doc_types, style, include_examples, include_type_hints
                )
            elif name == "review_code":
                diff_content = arguments.get("diff_content")
                file_paths = arguments.get("file_paths", [])
                review_types = arguments.get("review_types", ["quality", "security", "style"])
                severity_threshold = arguments.get("severity_threshold", "medium")
                result = await self.ai_code_review_assistant.review_code(
                    diff_content, file_paths, review_types, severity_threshold
                )
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
    server = AIDevelopmentMCPServer()
    
    # Send initial capabilities to stderr for debugging
    sys.stderr.write("AI Development MCP Server Starting (5 AI tools)...\n")
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
