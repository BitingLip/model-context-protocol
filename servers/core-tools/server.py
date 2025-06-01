#!/usr/bin/env python3
"""
Core Tools MCP Server - Project Analysis and Infrastructure Tools

Model Context Protocol server for regular project analysis tools including
project tree generation, code analysis, service discovery, configuration analysis,
and infrastructure analysis tools.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add the current directory to the path for tool imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Import core project analysis tools
from tools.project_tree import ProjectTreeGenerator  # type: ignore
from tools.code_analysis import CodeAnalyzer  # type: ignore
from tools.service_discovery import ServiceDiscovery  # type: ignore
from tools.config_analysis import ConfigAnalyzer  # type: ignore
from tools.docker_analysis import DockerAnalyzer  # type: ignore
from tools.test_mapping import TestMapper  # type: ignore
from tools.dependency_analysis import DependencyAnalyzer  # type: ignore
from tools.git_analysis import GitAnalyzer  # type: ignore
from tools.api_endpoint_discovery import APIEndpointDiscovery  # type: ignore
from tools.database_schema_analysis import DatabaseSchemaAnalysis  # type: ignore
from tools.log_analysis import LogAnalysis  # type: ignore


def get_project_root() -> str:
    """Get the Biting Lip project root directory (5 levels up from this file)."""
    return str(Path(__file__).parent.parent.parent.parent.parent)


class CoreToolsMCPServer:
    """MCP Server for core project analysis and infrastructure tools."""
    
    def __init__(self):
        self.name = "core-tools"
        self.version = "1.0.0"
        self.project_root = get_project_root()
        
        # Initialize core project analysis tools
        self.code_analyzer = CodeAnalyzer(self.project_root)
        self.service_discovery = ServiceDiscovery(self.project_root)
        self.config_analyzer = ConfigAnalyzer(self.project_root)
        self.docker_analyzer = DockerAnalyzer(self.project_root)
        self.test_mapper = TestMapper(self.project_root)
        self.dependency_analyzer = DependencyAnalyzer(self.project_root)
        self.git_analyzer = GitAnalyzer(self.project_root)
        self.api_endpoint_discovery = APIEndpointDiscovery(self.project_root)
        self.database_schema_analysis = DatabaseSchemaAnalysis(self.project_root)
        self.log_analysis = LogAnalysis(self.project_root)
    
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
        """List all available core tools."""
        return {
            "tools": [
                # Project Structure and Code Analysis
                {
                    "name": "generate_project_tree",
                    "description": "Generate a visual tree structure of a project directory with optional filtering",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "root_path": {"type": "string", "description": "Root directory path to analyze (defaults to Biting Lip project root)"},
                            "ignore_patterns": {"type": "array", "items": {"type": "string"}, "description": "Array of patterns to ignore (e.g., ['*.pyc', '__pycache__'])"},
                            "max_depth": {"type": "integer", "description": "Maximum depth to traverse"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "analyze_python_file",
                    "description": "Analyze a Python file and extract classes, functions, imports, and constants",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the Python file to analyze (relative to project root)"}
                        },
                        "required": ["file_path"]
                    }
                },
                {
                    "name": "get_project_overview",
                    "description": "Get a lightweight project overview (FIXED: no longer causes MCP loops)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "max_files": {"type": "integer", "description": "Maximum number of files to analyze (default: 20)", "default": 20},
                            "include_details": {"type": "boolean", "description": "Include detailed class/function info (default: false)", "default": False}
                        },
                        "required": []
                    }
                },
                {
                    "name": "get_project_overview_paginated",
                    "description": "Get paginated project overview for large projects",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer", "description": "Page number (0-based)", "default": 0},
                            "files_per_page": {"type": "integer", "description": "Files per page (default: 10)", "default": 10}
                        },
                        "required": []
                    }
                },
                {
                    "name": "search_code",
                    "description": "Search for code patterns in the project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query string"},
                            "file_type": {"type": "string", "description": "File extension to search in (default: 'py')"},
                            "project_root": {"type": "string", "description": "Root directory to search in (defaults to Biting Lip project root)"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "find_python_files",
                    "description": "Find all Python files in a directory",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "directory": {"type": "string", "description": "Directory to search in (defaults to Biting Lip project root)"}
                        },
                        "required": []
                    }
                },
                # Service Discovery Tools
                {
                    "name": "discover_services",
                    "description": "Discover and analyze all services in the Biting Lip platform including managers, interfaces, and their configurations",
                    "inputSchema": {"type": "object", "properties": {}, "required": []}
                },
                {
                    "name": "get_service_dependencies",
                    "description": "Get dependencies for a specific service including internal and external dependencies",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "service_name": {"type": "string", "description": "Name of the service to analyze dependencies for"}
                        },
                        "required": ["service_name"]
                    }
                },
                # Configuration Analysis
                {
                    "name": "analyze_config_files",
                    "description": "Analyze configuration files in the project including .env, YAML, JSON, Python configs, and Docker files",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "target_path": {"type": "string", "description": "Specific path to analyze (defaults to project root)"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "get_config_summary",
                    "description": "Get a high-level summary of all configuration in the project",
                    "inputSchema": {"type": "object", "properties": {}, "required": []}
                },
                # Docker and Infrastructure
                {
                    "name": "get_docker_info",
                    "description": "Get comprehensive Docker analysis including containers, images, Compose files, and Dockerfiles",
                    "inputSchema": {"type": "object", "properties": {}, "required": []}
                },
                # Testing
                {
                    "name": "find_test_files",
                    "description": "Find test files mapping to source files or analyze overall test structure",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "target_file": {"type": "string", "description": "Specific source file to find tests for (optional)"}
                        },
                        "required": []
                    }
                },
                # Dependencies
                {
                    "name": "analyze_dependencies",
                    "description": "Analyze project dependencies including Python packages, system requirements, and internal modules",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "analysis_type": {"type": "string", "enum": ["all", "python", "system", "internal"], "description": "Type of dependency analysis to perform"}
                        },
                        "required": []
                    }
                },
                # Git Analysis
                {
                    "name": "get_git_info",
                    "description": "Get git repository information including status, branches, commits, and remote info",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "info_type": {"type": "string", "enum": ["all", "status", "branches", "commits", "remote"], "description": "Type of git information to retrieve"}
                        },
                        "required": []
                    }
                },
                # API and Database Analysis
                {
                    "name": "discover_api_endpoints",
                    "description": "Discover and analyze API endpoints across different frameworks (Flask, FastAPI, Django, Express.js, etc.)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "framework": {"type": "string", "enum": ["flask", "fastapi", "django", "express", "nextjs", "spring"], "description": "Specific framework to analyze (optional, analyzes all if not specified)"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "analyze_database_schemas",
                    "description": "Analyze database schemas and structures across different database systems",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "database_type": {"type": "string", "enum": ["sqlite", "postgresql", "mysql", "mongodb", "django_orm", "sqlalchemy"], "description": "Specific database type to analyze (optional, analyzes all if not specified)"}
                        },
                        "required": []
                    }
                },
                # Log Analysis
                {
                    "name": "analyze_logs",
                    "description": "Analyze application logs, error patterns, and performance metrics",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "log_type": {"type": "string", "enum": ["error", "access", "application", "system"], "description": "Specific log type to analyze (optional, analyzes all if not specified)"},
                            "time_range": {"type": "object", "properties": {"start": {"type": "string", "description": "Start time (ISO format)"}, "end": {"type": "string", "description": "End time (ISO format)"}}, "description": "Time range filter for log analysis"}
                        },
                        "required": []
                    }
                }
            ]
        }
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution requests."""
        try:
            # Project Structure and Code Analysis Tools
            if name == "generate_project_tree":
                root_path = arguments.get("root_path", self.project_root)
                ignore_patterns = arguments.get("ignore_patterns", ["*.pyc", "__pycache__", ".git"])
                max_depth = arguments.get("max_depth")
                tree_gen = ProjectTreeGenerator(
                    root_path=root_path,
                    ignore_patterns=ignore_patterns,
                    max_depth=max_depth
                )
                result = tree_gen.generate()
            elif name == "analyze_python_file":
                file_path = arguments["file_path"]
                if not Path(file_path).is_absolute():
                    file_path = str(Path(self.project_root) / file_path)
                result = self.code_analyzer.analyze_python_file(file_path)
            elif name == "get_project_overview":
                max_files = arguments.get("max_files", 20)
                include_details = arguments.get("include_details", False)
                result = self.code_analyzer.get_project_summary(max_files, include_details)
            elif name == "get_project_overview_paginated":
                page = arguments.get("page", 0)
                files_per_page = arguments.get("files_per_page", 10)
                result = self.code_analyzer.get_project_overview_paginated(page, files_per_page)
            elif name == "search_code":
                query = arguments["query"]
                file_type = arguments.get("file_type", "py")
                result = self.code_analyzer.search_code(query, file_type)
            elif name == "find_python_files":
                directory = arguments.get("directory")
                result = self.code_analyzer.find_python_files(directory)
            
            # Service Discovery Tools
            elif name == "discover_services":
                result = self.service_discovery.discover_services()
            elif name == "get_service_dependencies":
                service_name = arguments["service_name"]
                result = self.service_discovery.get_service_dependencies(service_name)
            
            # Configuration Analysis
            elif name == "analyze_config_files":
                target_path = arguments.get("target_path")
                result = self.config_analyzer.analyze_config_files(target_path)
            elif name == "get_config_summary":
                result = self.config_analyzer.get_config_summary()
            
            # Docker and Infrastructure
            elif name == "get_docker_info":
                result = self.docker_analyzer.get_docker_info()
            
            # Testing
            elif name == "find_test_files":
                target_file = arguments.get("target_file")
                result = self.test_mapper.find_test_files(target_file)
            
            # Dependencies
            elif name == "analyze_dependencies":
                analysis_type = arguments.get("analysis_type", "all")
                result = self.dependency_analyzer.analyze_dependencies(analysis_type)
            
            # Git Analysis
            elif name == "get_git_info":
                info_type = arguments.get("info_type", "all")
                result = self.git_analyzer.get_git_info(info_type)
            
            # API and Database Analysis
            elif name == "discover_api_endpoints":
                framework = arguments.get("framework")
                result = self.api_endpoint_discovery.discover_endpoints(framework)
            elif name == "analyze_database_schemas":
                database_type = arguments.get("database_type")
                result = self.database_schema_analysis.analyze_schemas(database_type)
            
            # Log Analysis
            elif name == "analyze_logs":
                log_type = arguments.get("log_type")
                time_range = arguments.get("time_range")
                result = self.log_analysis.analyze_logs(log_type, time_range)
            
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
    server = CoreToolsMCPServer()
    
    # Send initial capabilities to stderr for debugging
    sys.stderr.write("Core Tools MCP Server Starting (17 tools)...\n")
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
