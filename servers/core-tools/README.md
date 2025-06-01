# Core Tools MCP Server

Project analysis and infrastructure tools for comprehensive project understanding and management.

## Features

- 17 specialized project analysis tools
- Configuration file analysis
- Database schema discovery
- API endpoint mapping
- Docker and Git integration
- Dependency analysis

## Tools

- `mcp_biting-lip-co_analyze_config_files` - Analyze configuration files (env, YAML, JSON, Docker)
- `mcp_biting-lip-co_analyze_database_schemas` - Analyze database schemas across different systems
- `mcp_biting-lip-co_analyze_dependencies` - Analyze project dependencies and requirements
- `mcp_biting-lip-co_analyze_logs` - Analyze application logs and error patterns
- `mcp_biting-lip-co_analyze_python_file` - Extract classes, functions, imports from Python files
- `mcp_biting-lip-co_discover_api_endpoints` - Discover API endpoints across frameworks
- `mcp_biting-lip-co_discover_services` - Discover and analyze all platform services
- `mcp_biting-lip-co_find_python_files` - Find all Python files in directories
- `mcp_biting-lip-co_find_test_files` - Find test files mapping to source files
- `mcp_biting-lip-co_generate_project_tree` - Generate visual project tree structure
- `mcp_biting-lip-co_get_config_summary` - Get high-level configuration summary
- `mcp_biting-lip-co_get_docker_info` - Comprehensive Docker analysis
- `mcp_biting-lip-co_get_git_info` - Git repository information and status
- `mcp_biting-lip-co_get_project_overview` - Lightweight project overview
- `mcp_biting-lip-co_get_project_overview_paginated` - Paginated project overview for large projects
- `mcp_biting-lip-co_get_service_dependencies` - Get dependencies for specific services
- `mcp_biting-lip-co_search_code` - Search for code patterns in the project

## Usage

```bash
python server.py
```

## Requirements

- Python 3.8+
- Docker (for Docker analysis tools)
- Git (for Git analysis tools)
- Project access permissions

## Configuration

The server automatically discovers project structure and adapts to different frameworks and configurations.
