# Biting Lip MCP Server Documentation

Welcome to the Biting Lip Model Context Protocol (MCP) Server documentation. This directory contains comprehensive guides for setup, usage, and troubleshooting.

## 📚 Documentation Index

### 🚀 [Setup & Troubleshooting](SETUP_TROUBLESHOOTING.md)

Complete guide for:

- Installation and configuration
- VS Code integration
- Common issues and solutions
- Performance optimization
- Development guidelines

### 🧠 [Memory System](MEMORY_SYSTEM.md)

In-depth coverage of the AI Memory System:

- PostgreSQL-based persistent memory
- Emotional context tracking
- Memory tools and operations
- Database schema and architecture
- Usage examples and best practices

## 🛠️ Quick Reference

### Available Tools (30 total)

- **22 Project Analysis Tools** - Code analysis, service discovery, configuration analysis
- **8 Memory System Tools** - Persistent memory with emotional context

### Key Features

- **No More MCP Loops** - Fixed with lightweight responses
- **Persistent AI Memory** - PostgreSQL backend with emotional tracking
- **Project-Aware** - Contextual analysis and memory organization
- **AI-Powered** - Code optimization, refactoring, test generation, documentation
- **Comprehensive** - Full platform analysis from code to infrastructure

### Configuration

```json
// .vscode/mcp.json (workspace root)
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

## 🔧 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup PostgreSQL (for memory system)
createdb ai_memory
export MEMORY_DB_USER=postgres
export MEMORY_DB_PASSWORD=postgres

# 3. Test server
python src/server.py

# 4. Restart VS Code to load tools
```

## 🎯 Use Cases

### For Developers

- **Code Analysis** - Understand complex codebases quickly
- **Refactoring** - AI-powered suggestions and optimization
- **Testing** - Automated test generation and coverage analysis
- **Documentation** - Generate comprehensive docs with examples

### For AI Assistants

- **Persistent Memory** - Remember conversations and insights across sessions
- **Emotional Context** - Track collaboration patterns and mood
- **Project Continuity** - Maintain context within and across projects
- **Learning** - Build knowledge over time through experience

### For DevOps

- **Infrastructure Analysis** - Docker, database, and service discovery
- **Configuration Management** - Analyze and validate configs across environments
- **Log Analysis** - Pattern detection and error tracking
- **Dependency Mapping** - Understand service relationships and dependencies

## 🚨 Troubleshooting Quick Fixes

### Tools Not Appearing?

1. Restart VS Code completely
2. Check `.vscode/mcp.json` configuration
3. Verify server runs: `python src/server.py`

### Memory Tools Failing?

1. Check PostgreSQL is running
2. Set environment variables: `MEMORY_DB_USER`, `MEMORY_DB_PASSWORD`
3. Test database: `psql -d ai_memory -U postgres`

### Performance Issues?

1. Use `get_project_overview` with `max_files` parameter
2. Use pagination for large projects
3. Regular memory cleanup with `cleanup_expired_memories`

## 📈 What's New

### Recent Improvements

- ✅ **Fixed MCP Loops** - Responses reduced from 346KB to 3KB
- ✅ **Memory System** - 8 new tools for persistent AI memory
- ✅ **PostgreSQL Backend** - Robust storage with emotional context
- ✅ **30 Total Tools** - Comprehensive analysis and memory capabilities
- ✅ **Better Organization** - Clean structure with docs and tests

### Breaking Changes

- `get_project_overview` now returns lightweight summary by default
- Use `get_project_overview_paginated` for detailed analysis of large projects
- Memory tools require PostgreSQL setup (falls back gracefully)

## 🤝 Contributing

### Adding Documentation

1. Create new `.md` files in this directory
2. Update this README with links
3. Follow existing formatting conventions
4. Include practical examples and troubleshooting

### Reporting Issues

Include:

- VS Code version and MCP extension
- Server logs and error messages
- Configuration files (`.vscode/mcp.json`)
- Steps to reproduce

## 📊 Success Metrics

The MCP server has achieved:

- **Zero Loop Issues** - Stable, responsive operation
- **30 Comprehensive Tools** - Full platform coverage
- **Persistent Memory** - AI continuity across sessions
- **8 Stored Memories** - Already learning and growing
- **99.1% Size Reduction** - From 346KB to 3KB responses

Ready for production use with AI assistants! 🚀
