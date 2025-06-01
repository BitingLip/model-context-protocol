# Memory System Documentation

## Overview

The Biting Lip MCP Memory System provides persistent memory capabilities for AI assistants, enabling continuity across conversations and emotional context tracking.

## Features

- **PostgreSQL Backend**: Robust, scalable storage with pgvector support
- **Emotional Context**: Track mood and emotional patterns over time
- **Project-Aware**: Organize memories by project and session
- **Semantic Search**: Advanced retrieval using vector embeddings (future)
- **Automatic Cleanup**: Configurable memory expiration and archiving

## Memory Tools

### Core Memory Operations

1. **`store_memory`** - Store new memories with emotional context
2. **`recall_memories`** - Search and retrieve relevant memories
3. **`update_memory`** - Modify existing memories
4. **`reflect_on_interaction`** - Store emotional reflections

### Analysis and Management

5. **`get_memory_summary`** - Get memory statistics overview
6. **`get_emotional_insights`** - Analyze emotional patterns
7. **`cleanup_expired_memories`** - Remove expired memories
8. **`get_project_context`** - Get current project/memory context

## Database Schema

### Tables

- **`memories`** - Core memory storage with content, importance, tags
- **`memory_relationships`** - Links between related memories
- **`emotional_reflections`** - Emotional context and mood tracking

### Features

- **pgvector extension** for semantic search (future)
- **Automatic timestamps** for creation and updates
- **Project isolation** with configurable cross-project access
- **Session tracking** for conversation continuity

## Configuration

### Environment Variables

```bash
MEMORY_DB_HOST=localhost
MEMORY_DB_PORT=5432
MEMORY_DB_NAME=ai_memory
MEMORY_DB_USER=postgres
MEMORY_DB_PASSWORD=postgres
```

### Connection Pooling

- Automatic connection pool management
- Fallback to in-memory storage if database unavailable
- Graceful degradation with logging

## Usage Examples

### Storing Memories

```python
memory_system.store_memory(
    memory_type="code_insight",
    content="Discovered that using connection pooling improves performance",
    title="Connection Pooling Insight",
    importance=0.8,
    emotional_context={"satisfaction": "high", "confidence": "increased"},
    tags=["performance", "database", "optimization"]
)
```

### Recalling Memories

```python
memories = memory_system.recall_memories(
    query="database performance",
    memory_type="code_insight",
    importance_threshold=0.7,
    limit=10
)
```

### Emotional Reflection

```python
memory_system.reflect_on_interaction(
    reflection_type="problem_solving",
    content={
        "challenge": "Complex debugging session",
        "approach": "Systematic analysis with user collaboration",
        "outcome": "Successful resolution and learning"
    },
    mood_score=0.8
)
```

## Architecture

The memory system is designed with:

- **Modular architecture** - Easy to extend and modify
- **Error handling** - Graceful fallbacks and logging
- **Performance optimization** - Connection pooling and efficient queries
- **Security considerations** - Parameterized queries, input validation
- **Future-ready** - pgvector integration for semantic search

## Integration

The memory system integrates with:

- **MCP Server** - All tools exposed through Model Context Protocol
- **VS Code** - Available as tools in Copilot and other AI assistants
- **Project Analysis** - Contextual memory storage during code analysis
- **Emotional AI** - Mood tracking and emotional intelligence

## Maintenance

### Regular Tasks

- Monitor memory growth and clean up expired entries
- Analyze emotional patterns for insights
- Backup important memories and relationships
- Update vector embeddings (when semantic search is enabled)

### Troubleshooting

- Check PostgreSQL connection and permissions
- Verify environment variables are set correctly
- Review logs for connection or query errors
- Test fallback mode if database is unavailable
