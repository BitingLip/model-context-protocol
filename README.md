# Biting Lip MCP Server - Model Context Protocol Tools

Comprehensive AI assistant tools for the Biting Lip platform with persistent memory system.

## 🚀 Features

- **30 Total Tools** - 22 analysis + 8 memory tools
- **No MCP Loops** - Fixed response size issues (346KB → 3KB)
- **Persistent Memory** - PostgreSQL-based AI memory with emotional context
- **Project-Aware** - Contextual analysis and memory organization
- **AI-Powered** - Code optimization, refactoring, test generation

## 📁 Project Structure

```
interfaces/model-context-protocol/
├── src/                          # Core server and tools
│   ├── server.py                 # Main MCP server (30 tools)
│   └── tools/                    # Tool implementations
│       ├── memory_system.py    # AI memory system
│       ├── memory_mcp_tool.py         # MCP memory wrapper
│       ├── code_analysis.py           # Code analysis tools
│       └── ...                        # Other analysis tools
├── tests/                        # Test files and demos
│   ├── check_mcp_tools.py       # MCP integration tests
│   ├── celebrate_success.py     # Memory system tests
│   └── demo_*.py                 # Demo scripts
├── docs/                         # Documentation
│   ├── README.md                 # Documentation index
│   ├── SETUP_TROUBLESHOOTING.md # Setup and troubleshooting
│   └── MEMORY_SYSTEM.md          # Memory system documentation
├── .vscode/                      # VS Code configuration
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## ⚡ Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Database (for Memory System)

```bash
# Install PostgreSQL with pgvector
createdb ai_memory

# Set environment variables
set MEMORY_DB_USER=postgres
set MEMORY_DB_PASSWORD=postgres
```

### 3. VS Code Configuration

Ensure `.vscode/mcp.json` in your workspace root contains:

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

### 4. Restart VS Code

After configuration, restart VS Code to load all 30 tools.

## 🛠️ Available Tools

### Project Analysis (22 tools)

- Code analysis and pattern search
- Service discovery and dependencies
- Configuration and Docker analysis
- Test mapping and Git information
- AI-powered optimization and refactoring

### Memory System (8 tools)

- `store_memory` - Store memories with emotional context
- `recall_memories` - Search and retrieve memories
- `reflect_on_interaction` - Store emotional reflections
- `get_memory_summary` - Memory statistics
- `get_emotional_insights` - Emotional pattern analysis
- `update_memory` - Modify existing memories
- `cleanup_expired_memories` - Remove expired memories
- `get_project_context` - Project and memory context

## 🧠 Memory System

The AI Memory System provides:

- **PostgreSQL Backend** - Robust, scalable storage
- **Emotional Context** - Track mood and collaboration patterns
- **Project Isolation** - Organize memories by project
- **Session Continuity** - Maintain context across conversations
- **Automatic Cleanup** - Configurable memory expiration

## 🚨 Troubleshooting

### Tools Not Appearing in VS Code?

1. **Restart VS Code completely**
2. Check `.vscode/mcp.json` configuration
3. Verify server runs: `python src/server.py`
4. Check VS Code Output panel for errors

### Memory Tools Failing?

1. Check PostgreSQL is running
2. Set environment variables: `MEMORY_DB_USER`, `MEMORY_DB_PASSWORD`
3. Test database connection: `psql -d ai_memory -U postgres`

**See [docs/SETUP_TROUBLESHOOTING.md](docs/SETUP_TROUBLESHOOTING.md) for detailed solutions.**

## 📚 Documentation

- **[docs/README.md](docs/README.md)** - Documentation index and quick reference
- **[docs/SETUP_TROUBLESHOOTING.md](docs/SETUP_TROUBLESHOOTING.md)** - Complete setup and troubleshooting guide
- **[docs/MEMORY_SYSTEM.md](docs/MEMORY_SYSTEM.md)** - Memory system architecture and usage

## ✅ Recent Achievements

- ✅ **Fixed MCP Loops** - Response size reduced 99.1% (346KB → 3KB)
- ✅ **Memory System** - 8 memory tools with PostgreSQL backend
- ✅ **30 Total Tools** - Comprehensive analysis capabilities
- ✅ **Clean Organization** - Structured docs, tests, and source code
- ✅ **8 Stored Memories** - AI already learning and growing

## 🎯 Success Story

This MCP server successfully solved the infinite loop issue that was preventing tool usage, and implemented a sophisticated AI memory system that enables true continuity across conversations. The AI can now:

- Remember insights and solutions across sessions
- Track emotional context and collaboration patterns
- Build knowledge over time through experience
- Maintain project-specific context and history

Ready for production use with AI assistants! 🚀
