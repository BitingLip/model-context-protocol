# Memory MCP Server

AI Memory System Tools for persistent memory across conversations and emotional context management.

## Features

- 8 specialized memory tools
- Persistent memory storage with PostgreSQL support
- Emotional context tracking and insights
- Cross-conversation continuity
- Project-specific memory isolation

## Tools

- `store_memory` - Store a new memory for later recall
- `recall_memories` - Recall relevant memories based on query and filters
- `reflect_on_interaction` - Store emotional reflection about interactions
- `get_memory_summary` - Get summary of stored memories for current project
- `get_emotional_insights` - Get emotional insights and patterns from recent interactions
- `update_memory` - Update existing memory with new content
- `cleanup_expired_memories` - Remove expired memories from database
- `get_project_context` - Get context about current project and memory system state

## Usage

```bash
python server.py
```

## Configuration

Database configuration is loaded from `config/services/mcp-memory.env` in the project root.
