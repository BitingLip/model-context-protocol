#!/usr/bin/env python3
"""
Biting Lip MCP Server

Model Context Protocol server providing handy tools for AI agents working with the Biting Lip AI platform.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add the tools directory to the path
sys.path.append(str(Path(__file__).parent))

from tools.project_tree import ProjectTreeGenerator
from tools.code_analysis import CodeAnalyzer
from tools.service_discovery import ServiceDiscovery
from tools.config_analysis import ConfigAnalyzer
from tools.docker_analysis import DockerAnalyzer
from tools.test_mapping import TestMapper
from tools.dependency_analysis import DependencyAnalyzer
from tools.git_analysis import GitAnalyzer
# Tier 3 AI-powered development tools
from tools.ai_code_optimizer import AICodeOptimizer
from tools.ai_smart_refactorer import AISmartRefactorer
from tools.ai_test_generator import AITestGenerator
from tools.ai_documentation_writer import AIDocumentationWriter
from tools.ai_code_review_assistant import AICodeReviewAssistant
# Tier 4 Infrastructure analysis tools
from tools.api_endpoint_discovery import APIEndpointDiscovery
from tools.database_schema_analysis import DatabaseSchemaAnalysis
from tools.log_analysis import LogAnalysis


def get_project_root() -> str:
    """Get the Biting Lip project root directory (3 levels up from this file)."""
    return str(Path(__file__).parent.parent.parent.parent)


class BitingLipMCPServer:
    """MCP Server for Biting Lip project tools."""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.code_analyzer = CodeAnalyzer(self.project_root)
        self.service_discovery = ServiceDiscovery(self.project_root)
        self.config_analyzer = ConfigAnalyzer(self.project_root)
        self.docker_analyzer = DockerAnalyzer(self.project_root)
        self.test_mapper = TestMapper(self.project_root)
        self.dependency_analyzer = DependencyAnalyzer(self.project_root)
        self.git_analyzer = GitAnalyzer(self.project_root)        
        # Tier 3 AI-powered development tools
        self.ai_code_optimizer = AICodeOptimizer(self.project_root)
        self.ai_smart_refactorer = AISmartRefactorer(self.project_root)
        self.ai_test_generator = AITestGenerator()
        self.ai_documentation_writer = AIDocumentationWriter()
        self.ai_code_review_assistant = AICodeReviewAssistant()
        # Tier 4 Infrastructure analysis tools
        self.api_endpoint_discovery = APIEndpointDiscovery(self.project_root)
        self.database_schema_analysis = DatabaseSchemaAnalysis(self.project_root)
        self.log_analysis = LogAnalysis(self.project_root)
    
    async def handle_list_tools(self) -> Dict[str, Any]:
        """List all available tools."""
        return {
            "tools": [
                {
                    "name": "generate_project_tree",
                    "description": "Generate a visual tree structure of a project directory with optional filtering",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "root_path": {
                                "type": "string",
                                "description": "Root directory path to analyze (defaults to Biting Lip project root)"
                            },
                            "ignore_patterns": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Array of patterns to ignore (e.g., ['*.pyc', '__pycache__'])"
                            },
                            "max_depth": {
                                "type": "integer",
                                "description": "Maximum depth to traverse"
                            }
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
                            "file_path": {
                                "type": "string",
                                "description": "Path to the Python file to analyze (relative to project root)"
                            }
                        },
                        "required": ["file_path"]
                    }
                },
                {
                    "name": "get_project_overview",
                    "description": "Get a comprehensive overview of the Python project structure",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_root": {
                                "type": "string",
                                "description": "Root directory of the project (defaults to Biting Lip project root)"
                            }
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
                            "query": {
                                "type": "string",
                                "description": "Search query string"
                            },
                            "file_type": {
                                "type": "string",
                                "description": "File extension to search in (default: 'py')"
                            },
                            "project_root": {
                                "type": "string",
                                "description": "Root directory to search in (defaults to Biting Lip project root)"
                            }
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
                            "directory": {
                                "type": "string",
                                "description": "Directory to search in (defaults to Biting Lip project root)"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "discover_services",
                    "description": "Discover and analyze all services in the Biting Lip platform including managers, interfaces, and their configurations",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_service_dependencies",
                    "description": "Get dependencies for a specific service including internal and external dependencies",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "service_name": {
                                "type": "string",
                                "description": "Name of the service to analyze dependencies for"
                            }
                        },
                        "required": ["service_name"]
                    }
                },
                {
                    "name": "analyze_config_files",
                    "description": "Analyze configuration files in the project including .env, YAML, JSON, Python configs, and Docker files",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "target_path": {
                                "type": "string",
                                "description": "Specific path to analyze (defaults to project root)"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "get_config_summary",
                    "description": "Get a high-level summary of all configuration in the project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_docker_info",
                    "description": "Get comprehensive Docker analysis including containers, images, Compose files, and Dockerfiles",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "find_test_files",
                    "description": "Find test files mapping to source files or analyze overall test structure",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "target_file": {
                                "type": "string",
                                "description": "Specific source file to find tests for (optional)"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "analyze_dependencies",
                    "description": "Analyze project dependencies including Python packages, system requirements, and internal modules",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "analysis_type": {
                                "type": "string",
                                "enum": ["all", "python", "system", "internal"],
                                "description": "Type of dependency analysis to perform"
                            }
                        },
                        "required": []
                    }                },
                {
                    "name": "get_git_info",
                    "description": "Get git repository information including status, branches, commits, and remote info",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "info_type": {
                                "type": "string",
                                "enum": ["all", "status", "branches", "commits", "remote"],
                                "description": "Type of git information to retrieve"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "optimize_code",
                    "description": "AI-powered code optimization using local Ollama LLMs, integrates with VS Code problems panel and Sourcery suggestions",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to optimize"
                            },
                            "problems": {
                                "type": "array",
                                "description": "List of problems from VS Code diagnostics (optional)"
                            }
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
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to refactor"
                            },
                            "target_scope": {
                                "type": "string",
                                "enum": ["function", "class", "method", "file"],
                                "description": "Scope of refactoring"
                            },
                            "target_name": {
                                "type": "string",
                                "description": "Name of the specific function/class/method to refactor (optional)"
                            }
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
                            "file_path": {
                                "type": "string",
                                "description": "Path to the Python file to generate tests for"
                            },
                            "test_types": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["unit", "integration", "edge", "error"]},
                                "description": "Types of tests to generate"
                            },
                            "coverage_target": {
                                "type": "number",
                                "description": "Target coverage percentage (0.0-1.0)"
                            },
                            "include_fixtures": {
                                "type": "boolean",
                                "description": "Whether to generate pytest fixtures"
                            },
                            "include_mocks": {
                                "type": "boolean",
                                "description": "Whether to include mock suggestions"
                            }
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
                            "file_path": {
                                "type": "string",
                                "description": "Path to the Python file to document"
                            },
                            "doc_types": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["docstrings", "readme", "api", "tutorial"]},
                                "description": "Types of documentation to generate"
                            },
                            "style": {
                                "type": "string",
                                "enum": ["google", "numpy", "sphinx"],
                                "description": "Docstring style"
                            },
                            "include_examples": {
                                "type": "boolean",
                                "description": "Whether to include code examples"
                            },
                            "include_type_hints": {
                                "type": "boolean",
                                "description": "Whether to include type hint documentation"
                            }
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
                            "diff_content": {
                                "type": "string",
                                "description": "Git diff content to review (optional, will get from git if not provided)"
                            },
                            "file_paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific files to review (if not using git diff)"
                            },
                            "review_types": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["quality", "security", "style", "performance"]},
                                "description": "Types of review to perform"
                            },
                            "severity_threshold": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Minimum severity level to report"
                            }
                        },
                        "required": []
                    }
                },
                # Tier 4 Infrastructure Analysis Tools
                {
                    "name": "discover_api_endpoints",
                    "description": "Discover and analyze API endpoints across different frameworks (Flask, FastAPI, Django, Express.js, etc.)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "framework": {
                                "type": "string",
                                "enum": ["flask", "fastapi", "django", "express", "nextjs", "spring"],
                                "description": "Specific framework to analyze (optional, analyzes all if not specified)"
                            }
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
                            "database_type": {
                                "type": "string",
                                "enum": ["sqlite", "postgresql", "mysql", "mongodb", "django_orm", "sqlalchemy"],
                                "description": "Specific database type to analyze (optional, analyzes all if not specified)"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "analyze_logs",
                    "description": "Analyze application logs, error patterns, and performance metrics",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "log_type": {
                                "type": "string",
                                "enum": ["error", "access", "application", "system"],
                                "description": "Specific log type to analyze (optional, analyzes all if not specified)"
                            },
                            "time_range": {
                                "type": "object",
                                "properties": {
                                    "start": {"type": "string", "description": "Start time (ISO format)"},
                                    "end": {"type": "string", "description": "End time (ISO format)"}
                                },
                                "description": "Time range filter for log analysis"
                            }
                        },
                        "required": []
                    }
                }
            ]
        }
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution."""
        async def _generate_project_tree():
            root_path = arguments.get("root_path", self.project_root)
            ignore_patterns = arguments.get("ignore_patterns", ["*.pyc", "__pycache__", ".git"])
            max_depth = arguments.get("max_depth")
            tree_gen = ProjectTreeGenerator(
                root_path=root_path,
                ignore_patterns=ignore_patterns,
                max_depth=max_depth
            )
            result = tree_gen.generate()
            return {"content": [{"type": "text", "text": result}]}

        async def _analyze_python_file():
            file_path = arguments["file_path"]
            if not Path(file_path).is_absolute():
                file_path = str(Path(self.project_root) / file_path)
            result = self.code_analyzer.analyze_python_file(file_path)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _get_project_overview():
            result = self.code_analyzer.get_project_overview()
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _search_code():
            query = arguments["query"]
            file_type = arguments.get("file_type", "py")
            result = self.code_analyzer.search_code(query, file_type)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _find_python_files():
            directory = arguments.get("directory")
            result = self.code_analyzer.find_python_files(directory)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _discover_services():
            result = self.service_discovery.discover_services()
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _get_service_dependencies():
            service_name = arguments["service_name"]
            result = self.service_discovery.get_service_dependencies(service_name)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _analyze_config_files():
            target_path = arguments.get("target_path")
            result = self.config_analyzer.analyze_config_files(target_path)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _get_config_summary():
            result = self.config_analyzer.get_config_summary()
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _get_docker_info():
            result = self.docker_analyzer.get_docker_info()
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _find_test_files():
            target_file = arguments.get("target_file")
            result = self.test_mapper.find_test_files(target_file)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _analyze_dependencies():
            analysis_type = arguments.get("analysis_type", "all")
            result = self.dependency_analyzer.analyze_dependencies(analysis_type)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _get_git_info():
            info_type = arguments.get("info_type", "all")
            result = self.git_analyzer.get_git_info(info_type)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _optimize_code():
            file_path = arguments["file_path"]
            problems = arguments.get("problems")
            result = self.ai_code_optimizer.optimize_code(file_path, problems)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _smart_refactor():
            file_path = arguments["file_path"]
            target_scope = arguments.get("target_scope", "file")
            target_name = arguments.get("target_name")
            result = self.ai_smart_refactorer.analyze_refactoring_opportunities(file_path, target_scope)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _generate_tests():
            file_path = arguments["file_path"]
            test_types = arguments.get("test_types")
            coverage_target = arguments.get("coverage_target", 0.9)
            include_fixtures = arguments.get("include_fixtures", True)
            include_mocks = arguments.get("include_mocks", True)
            result = await self.ai_test_generator.generate_tests(
                file_path, test_types, coverage_target, include_fixtures, include_mocks
            )
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _write_docs():
            file_path = arguments["file_path"]
            doc_types = arguments.get("doc_types")
            style = arguments.get("style", "google")
            include_examples = arguments.get("include_examples", True)
            include_type_hints = arguments.get("include_type_hints", True)
            result = await self.ai_documentation_writer.write_docs(
                file_path, doc_types, style, include_examples, include_type_hints
            )
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _review_code():
            diff_content = arguments.get("diff_content")
            file_paths = arguments.get("file_paths")
            review_types = arguments.get("review_types")
            severity_threshold = arguments.get("severity_threshold", "medium")
            result = await self.ai_code_review_assistant.review_code(
                diff_content, file_paths, review_types, severity_threshold
            )
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _discover_api_endpoints():
            framework = arguments.get("framework")
            result = self.api_endpoint_discovery.discover_endpoints(framework)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _analyze_database_schemas():
            database_type = arguments.get("database_type")
            result = self.database_schema_analysis.analyze_schemas(database_type)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        async def _analyze_logs():
            log_type = arguments.get("log_type")
            time_range = arguments.get("time_range")
            result = self.log_analysis.analyze_logs(log_type, time_range)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        tool_map = {
            "generate_project_tree": _generate_project_tree,
            "analyze_python_file": _analyze_python_file,
            "get_project_overview": _get_project_overview,
            "search_code": _search_code,
            "find_python_files": _find_python_files,
            "discover_services": _discover_services,
            "get_service_dependencies": _get_service_dependencies,
            "analyze_config_files": _analyze_config_files,
            "get_config_summary": _get_config_summary,
            "get_docker_info": _get_docker_info,
            "find_test_files": _find_test_files,
            "analyze_dependencies": _analyze_dependencies,
            "get_git_info": _get_git_info,
            "optimize_code": _optimize_code,
            "smart_refactor": _smart_refactor,
            "generate_tests": _generate_tests,
            "write_docs": _write_docs,
            "review_code": _review_code,
            "discover_api_endpoints": _discover_api_endpoints,
            "analyze_database_schemas": _analyze_database_schemas,
            "analyze_logs": _analyze_logs,
        }

        try:
            handler = tool_map.get(name)
            if handler is None:
                return {"error": f"Unknown tool: {name}"}
            result = await handler()
            return result
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}


async def main():
    """Main MCP server loop."""
    server = BitingLipMCPServer()
    
    while True:
        try:
            # Read a line from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            # Parse the JSON-RPC message
            try:
                request = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            
            # Handle the request
            if request.get("method") == "tools/list":
                response = await server.handle_list_tools()
                result = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": response
                }
            elif request.get("method") == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                response = await server.handle_call_tool(tool_name, arguments)
                result = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": response
                }
            else:
                result = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": "Method not found"
                    }
                }
            
            # Send the response
            print(json.dumps(result))
            sys.stdout.flush()
        
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
