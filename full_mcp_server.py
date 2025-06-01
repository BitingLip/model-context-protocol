#!/usr/bin/env python3
"""
Full Biting Lip MCP Server - All 21 Tools

Model Context Protocol server providing comprehensive tools for AI agents working with the Biting Lip AI platform.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add the src directory to the path for tool imports BEFORE importing tools
import os
import sys
from pathlib import Path

# Get the directory containing this script
script_dir = Path(__file__).parent
src_dir = script_dir / "src"

# Add both directories to the Python path
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(script_dir))

# Import all tool classes (Tier 1: Project Analysis)
from tools.project_tree import ProjectTreeGenerator  # type: ignore
from tools.code_analysis import CodeAnalyzer  # type: ignore
from tools.service_discovery import ServiceDiscovery  # type: ignore
from tools.config_analysis import ConfigAnalyzer  # type: ignore
from tools.docker_analysis import DockerAnalyzer  # type: ignore
from tools.test_mapping import TestMapper  # type: ignore
from tools.dependency_analysis import DependencyAnalyzer  # type: ignore
from tools.git_analysis import GitAnalyzer  # type: ignore
# Tier 3: AI-powered development tools
from tools.ai_code_optimizer import AICodeOptimizer  # type: ignore
from tools.ai_smart_refactorer import AISmartRefactorer  # type: ignore
from tools.ai_test_generator import AITestGenerator  # type: ignore
from tools.ai_documentation_writer import AIDocumentationWriter  # type: ignore
from tools.ai_code_review_assistant import AICodeReviewAssistant  # type: ignore
# Tier 4: Infrastructure analysis tools
from tools.api_endpoint_discovery import APIEndpointDiscovery  # type: ignore
from tools.database_schema_analysis import DatabaseSchemaAnalysis  # type: ignore
from tools.log_analysis import LogAnalysis  # type: ignore
# Memory System
from tools.memory_mcp_tool import MemoryMCPTool  # type: ignore


def get_project_root() -> str:
    """Get the Biting Lip project root directory (3 levels up from this file)."""
    return str(Path(__file__).parent.parent.parent.parent)


class FullBitingLipMCPServer:
    """Full MCP Server for Biting Lip project tools with all 21 specialized tools."""
    
    def __init__(self):
        self.name = "biting-lip-tools"
        self.version = "1.0.0"
        self.project_root = get_project_root()
        
        # Initialize all tool classes
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
        # Memory System
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
                "version": self.version
            }
        }
    
    async def handle_list_tools(self) -> Dict[str, Any]:
        """List all available tools."""
        return {
            "tools": [
                # Tier 1: Project Analysis Tools
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
                },                {
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
                # Tier 2: Service Discovery Tools
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
                {
                    "name": "get_docker_info",
                    "description": "Get comprehensive Docker analysis including containers, images, Compose files, and Dockerfiles",
                    "inputSchema": {"type": "object", "properties": {}, "required": []}
                },
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
                {
                    "name": "get_git_info",
                    "description": "Get git repository information including status, branches, commits, and remote info",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "info_type": {"type": "string", "enum": ["all", "status", "branches", "commits", "remote"], "description": "Type of git information to retrieve"}
                        },
                        "required": []
                    }                },
                # Tier 3: AI-Powered Development Tools
                {
                    "name": "optimize_code",
                    "description": "AI-powered code optimization using local Ollama LLMs, integrates with VS Code problems panel and Sourcery suggestions",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the file to optimize"},
                            "problems": {
                                "type": "array", 
                                "description": "List of problems from VS Code diagnostics (optional)",
                                "items": {"type": "string"}
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
                            "include_fixtures": {"type": "boolean", "description": "Whether to generate pytest fixtures"},
                            "include_mocks": {"type": "boolean", "description": "Whether to include mock suggestions"}
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
                            "diff_content": {"type": "string", "description": "Git diff content to review (optional, will get from git if not provided)"},
                            "file_paths": {"type": "array", "items": {"type": "string"}, "description": "Specific files to review (if not using git diff)"},
                            "review_types": {"type": "array", "items": {"type": "string", "enum": ["quality", "security", "style", "performance"]}, "description": "Types of review to perform"},
                            "severity_threshold": {"type": "string", "enum": ["low", "medium", "high", "critical"], "description": "Minimum severity level to report"}
                        },
                        "required": []
                    }
                },
                # Tier 4: Infrastructure Analysis Tools
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
                },                {
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
                },
                # Memory System Tools
                {
                    "name": "store_memory",
                    "description": "Store a new memory for later recall across conversations",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "memory_type": {"type": "string", "description": "Type of memory (e.g., 'code_insight', 'user_preference', 'problem_solution')"},
                            "content": {"type": ["string", "object"], "description": "Memory content (text or structured data)"},
                            "title": {"type": "string", "description": "Optional short title for the memory"},
                            "importance": {"type": "number", "minimum": 0.0, "maximum": 1.0, "description": "Importance score (0.0 to 1.0)"},
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
                            "importance_threshold": {"type": "number", "minimum": 0.0, "maximum": 1.0, "description": "Minimum importance score"},
                            "limit": {"type": "integer", "minimum": 1, "maximum": 100, "description": "Maximum number of memories to return"},
                            "include_other_projects": {"type": "boolean", "description": "Include memories from other projects"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "reflect_on_interaction",
                    "description": "Store an emotional reflection about an interaction for future learning",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "reflection_type": {"type": "string", "description": "Type of reflection (e.g., 'collaboration', 'problem_solving', 'learning')"},
                            "content": {"type": "object", "description": "Reflection content with structured data"},
                            "mood_score": {"type": "number", "minimum": -1.0, "maximum": 1.0, "description": "Emotional state score (-1.0 to 1.0, negative to positive)"}
                        },
                        "required": ["reflection_type", "content"]
                    }
                },
                {
                    "name": "get_memory_summary",
                    "description": "Get a summary of stored memories for the current project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },                {
                    "name": "get_emotional_insights",
                    "description": "Get emotional insights and patterns from recent interactions",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "days_back": {"type": "integer", "minimum": 1, "maximum": 365, "description": "Number of days to look back"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "update_memory",
                    "description": "Update an existing memory with new content",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "memory_id": {"type": "string", "description": "ID of the memory to update"},
                            "content": {"type": ["string", "object"], "description": "New memory content"},
                            "title": {"type": "string", "description": "Optional new title"},
                            "importance": {"type": "number", "minimum": 0.0, "maximum": 1.0, "description": "New importance score"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "New tags list"}
                        },
                        "required": ["memory_id"]
                    }
                },
                {
                    "name": "cleanup_expired_memories",
                    "description": "Remove expired memories from the database",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
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
        """Handle tool execution."""
        try:
            # Tier 1: Project Analysis Tools
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
                return {"content": [{"type": "text", "text": result}]}
            elif name == "analyze_python_file":
                file_path = arguments["file_path"]
                if not Path(file_path).is_absolute():
                    file_path = str(Path(self.project_root) / file_path)
                result = self.code_analyzer.analyze_python_file(file_path)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "get_project_overview":
                # Use lightweight summary to prevent MCP loops
                max_files = arguments.get("max_files", 20)
                include_details = arguments.get("include_details", False)
                result = self.code_analyzer.get_project_summary(max_files, include_details)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "get_project_overview_paginated":
                # Paginated overview for large projects
                page = arguments.get("page", 0)
                files_per_page = arguments.get("files_per_page", 10)
                result = self.code_analyzer.get_project_overview_paginated(page, files_per_page)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "search_code":
                query = arguments["query"]
                file_type = arguments.get("file_type", "py")
                result = self.code_analyzer.search_code(query, file_type)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "find_python_files":
                directory = arguments.get("directory")
                result = self.code_analyzer.find_python_files(directory)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            # Tier 2: Service Discovery Tools
            elif name == "discover_services":
                result = self.service_discovery.discover_services()
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "get_service_dependencies":
                service_name = arguments["service_name"]
                result = self.service_discovery.get_service_dependencies(service_name)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "analyze_config_files":
                target_path = arguments.get("target_path")
                result = self.config_analyzer.analyze_config_files(target_path)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "get_config_summary":
                result = self.config_analyzer.get_config_summary()
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "get_docker_info":
                result = self.docker_analyzer.get_docker_info()
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "find_test_files":
                target_file = arguments.get("target_file")
                result = self.test_mapper.find_test_files(target_file)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "analyze_dependencies":
                analysis_type = arguments.get("analysis_type", "all")
                result = self.dependency_analyzer.analyze_dependencies(analysis_type)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "get_git_info":
                info_type = arguments.get("info_type", "all")
                result = self.git_analyzer.get_git_info(info_type)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            # Tier 3: AI-Powered Development Tools
            elif name == "optimize_code":
                file_path = arguments["file_path"]
                problems = arguments.get("problems", [])
                result = await self.ai_code_optimizer.optimize_code(file_path, problems)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "smart_refactor":
                file_path = arguments["file_path"]
                target_scope = arguments.get("target_scope", "file")
                target_name = arguments.get("target_name")
                result = await self.ai_smart_refactorer.smart_refactor(file_path, target_scope, target_name)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "generate_tests":
                file_path = arguments["file_path"]
                test_types = arguments.get("test_types", ["unit"])
                coverage_target = arguments.get("coverage_target", 0.8)
                include_fixtures = arguments.get("include_fixtures", True)
                include_mocks = arguments.get("include_mocks", True)
                result = await self.ai_test_generator.generate_tests(
                    file_path, test_types, coverage_target, include_fixtures, include_mocks
                )
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "write_docs":
                file_path = arguments["file_path"]
                doc_types = arguments.get("doc_types", ["docstrings"])
                style = arguments.get("style", "google")
                include_examples = arguments.get("include_examples", True)
                include_type_hints = arguments.get("include_type_hints", True)
                result = await self.ai_documentation_writer.write_docs(
                    file_path, doc_types, style, include_examples, include_type_hints
                )
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "review_code":
                diff_content = arguments.get("diff_content")
                file_paths = arguments.get("file_paths", [])
                review_types = arguments.get("review_types", ["quality", "security", "style"])
                severity_threshold = arguments.get("severity_threshold", "medium")
                result = await self.ai_code_review_assistant.review_code(
                    diff_content, file_paths, review_types, severity_threshold
                )
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
              # Tier 4: Infrastructure Analysis Tools
            elif name == "discover_api_endpoints":
                framework = arguments.get("framework")
                result = self.api_endpoint_discovery.discover_api_endpoints(framework)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "analyze_database_schemas":
                database_type = arguments.get("database_type")
                result = self.database_schema_analysis.analyze_database_schemas(database_type)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "analyze_logs":
                log_type = arguments.get("log_type")
                time_range = arguments.get("time_range")
                result = self.log_analysis.analyze_logs(log_type, time_range)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
              # Memory System Tools
            elif name == "store_memory":
                result = self.memory_tool.store_memory(**arguments)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "recall_memories":
                result = self.memory_tool.recall_memories(**arguments)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "reflect_on_interaction":
                result = self.memory_tool.reflect_on_interaction(**arguments)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "get_memory_summary":
                result = self.memory_tool.get_memory_summary()
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "get_emotional_insights":
                days_back = arguments.get("days_back", 30)
                result = self.memory_tool.get_emotional_insights(days_back)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "update_memory":
                result = self.memory_tool.update_memory(**arguments)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "cleanup_expired_memories":
                result = self.memory_tool.cleanup_expired_memories()
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif name == "get_project_context":
                result = self.memory_tool.get_project_context()
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            else:
                raise ValueError(f"Unknown tool: {name}")
                
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error executing tool {name}: {str(e)}"}]}


async def main():
    """Main MCP server loop."""
    server = FullBitingLipMCPServer()
      # Send initial capabilities to stderr for debugging
    sys.stderr.write("Full Biting Lip MCP Server Starting (29 tools including 8 memory tools)...\n")
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
