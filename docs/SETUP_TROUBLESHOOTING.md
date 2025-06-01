# MCP Server Setup and Troubleshooting

## Overview

This document covers setup, configuration, and troubleshooting for the Biting Lip MCP (Model Context Protocol) Server.

## Quick Start

### 1. Installation

```bash
cd interfaces/model-context-protocol
pip install -r requirements.txt
```

### 2. Configuration

Edit `.vscode/mcp.json` in your workspace root:

```json
{
  "mcpServers": {
    "biting-lip-tools": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "${workspaceRoot}/interfaces/model-context-protocol",
      "env": {}
    }
  }
}
```

### 3. Database Setup (for Memory System)

```bash
# Install PostgreSQL with pgvector
# Create database
createdb ai_memory

# Set environment variables
export MEMORY_DB_USER=postgres
export MEMORY_DB_PASSWORD=postgres
```

### 4. Start Server

```bash
python src/server.py
```

## Available Tools

### Project Analysis Tools (22)

- `generate_project_tree` - Visual project structure
- `get_project_overview` - Lightweight project summary (fixed for MCP loops)
- `get_project_overview_paginated` - Paginated overview for large projects
- `analyze_python_file` - Python code analysis
- `search_code` - Code pattern search
- `find_python_files` - Python file discovery
- `discover_services` - Service discovery and analysis
- `get_service_dependencies` - Service dependency mapping
- `analyze_config_files` - Configuration analysis
- `get_config_summary` - Configuration overview
- `get_docker_info` - Docker container and image analysis
- `find_test_files` - Test file mapping
- `analyze_dependencies` - Dependency analysis
- `get_git_info` - Git repository information
- `optimize_code` - AI-powered code optimization
- `smart_refactor` - AI-powered refactoring suggestions
- `generate_tests` - AI-powered test generation
- `write_docs` - AI-powered documentation generation
- `review_code` - AI-powered code review
- `discover_api_endpoints` - API endpoint discovery
- `analyze_database_schemas` - Database schema analysis
- `analyze_logs` - Log analysis and pattern detection

### Memory System Tools (8)

- `store_memory` - Store new memories
- `recall_memories` - Search and retrieve memories
- `reflect_on_interaction` - Store emotional reflections
- `get_memory_summary` - Memory statistics
- `get_emotional_insights` - Emotional pattern analysis
- `update_memory` - Modify existing memories
- `cleanup_expired_memories` - Remove expired memories
- `get_project_context` - Project and memory context

## Troubleshooting

### Common Issues

#### 1. Tools Not Appearing in VS Code

**Symptoms**: Memory tools or other tools not visible in VS Code
**Solutions**:

- Restart VS Code completely
- Check `.vscode/mcp.json` configuration
- Verify server is running: `python src/server.py`
- Check VS Code Output panel for MCP errors
- Try "Developer: Reload Window" in VS Code

#### 2. MCP Loop Issues

**Symptoms**: VS Code becomes unresponsive when using tools
**Solutions**:

- Use `get_project_overview` instead of old `get_project_overview` (fixed)
- Use `get_project_overview_paginated` for large projects
- Check response sizes in server logs

#### 3. Memory System Database Issues

**Symptoms**: Memory tools fail or return errors
**Solutions**:

- Check PostgreSQL is running: `pg_ctl status`
- Verify environment variables are set
- Test database connection: `psql -d ai_memory -U postgres`
- Check logs for connection errors
- Fallback mode will activate if database unavailable

#### 4. Import Errors

**Symptoms**: Server fails to start with import errors
**Solutions**:

- Verify Python path includes `src` directory
- Check all dependencies installed: `pip install -r requirements.txt`
- Ensure PostgreSQL development headers installed
- Install psycopg2: `pip install psycopg2-binary`

### Testing Tools

#### Test Server Functionality

```bash
cd tests
python check_mcp_tools.py
```

#### Test Memory System

```bash
cd tests
python check_memory_tools.py
```

#### Test Integration

```bash
cd tests
python celebrate_success.py
```

### Configuration Files

#### VS Code MCP Configuration

Location: `.vscode/mcp.json` (workspace root)

```json
{
  "mcpServers": {
    "biting-lip-tools": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "${workspaceRoot}/interfaces/model-context-protocol",
      "env": {}
    }
  }
}
```

#### Environment Variables

```bash
# Memory System Database
MEMORY_DB_HOST=localhost
MEMORY_DB_PORT=5432
MEMORY_DB_NAME=ai_memory
MEMORY_DB_USER=postgres
MEMORY_DB_PASSWORD=postgres

# Ollama (for AI tools)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

### Logs and Debugging

#### Server Logs

The MCP server outputs logs to stderr:

```bash
python src/server.py 2> server.log
```

#### VS Code MCP Logs

Check VS Code Output panel → "MCP" channel for connection errors

#### Memory System Logs

Memory operations are logged with INFO level:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Performance Optimization

### Large Projects

- Use `get_project_overview` with `max_files` parameter
- Use `get_project_overview_paginated` for controlled data access
- Limit search results with appropriate filters

### Memory System

- Regular cleanup of expired memories
- Monitor database size and performance
- Use connection pooling (enabled by default)
- Consider indexing for large memory datasets

### AI Tools

- Configure Ollama model based on available resources
- Use appropriate timeouts for AI operations
- Cache AI responses when possible

## Development

### Adding New Tools

1. Create tool class in `src/tools/`
2. Add tool definition to `handle_list_tools()`
3. Add tool handler to `handle_call_tool()`
4. Update documentation and tests

### Testing

- Add unit tests in `tests/`
- Test MCP integration with VS Code
- Verify error handling and fallbacks
- Test with different project sizes and types
