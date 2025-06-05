# Enhanced AI Memory MCP Server

Advanced AI Memory System with persona evolution, weighted retrieval, reflexion capabilities, and intelligent forgetting mechanisms.

## Features

- **14 Specialized Memory Tools** - Complete memory management suite
- **Persona Evolution Layer** - AI self-identity that grows over time
- **Enhanced Weighted Retrieval** - Importance + recency + relevance scoring
- **Reflexion Capability** - Automatic self-assessment and learning
- **Forgetting Mechanism** - Memory decay to prevent information overload
- **Persistent Storage** - PostgreSQL support with emotional context tracking
- **Cross-Conversation Continuity** - Project-specific memory isolation

## Installation and Setup

### Quick Setup

The easiest way to set up the Memory MCP Server is to use the provided setup script:

```bash
python setup/setup.py
```

This script will guide you through the entire setup process with clear instructions and helpful error messages.

#### Setup Options

- `--force` - Force setup even if already configured
- `--skip-db-create` - Skip database creation and schema setup
- `--skip-python-deps` - Skip Python dependencies installation
- `--skip-embeddings-update` - Skip updating embeddings for existing memories

#### What the Setup Script Does

1. Checks PostgreSQL installation and compatibility
2. Installs required Python dependencies
3. Creates and configures the memory.env file
4. Sets up the database and required extensions
5. Creates necessary database tables
6. Tests the memory system functionality
7. Updates embeddings for existing memories (if any)

### Manual Setup

If you prefer manual setup, or need to troubleshoot specific issues:

1. Copy `config/memory.env.example` to `config/memory.env`
2. Edit `memory.env` with your PostgreSQL credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Ensure PostgreSQL is running with pgvector extension installed
5. Run the server: `python server.py`

### Detailed Setup Guide

For comprehensive installation instructions, advanced configuration options, and troubleshooting tips, see the [detailed setup guide](SETUP_GUIDE.md).

## Core Tools

### Basic Memory Operations

- `store_memory` - Store a new memory for later recall
- `recall_memories` - Basic recall with semantic search and filters
- `update_memory` - Update existing memory with new content
- `get_memory_summary` - Get summary of stored memories for current project
- `cleanup_expired_memories` - Remove expired memories from database
- `get_project_context` - Get context about current project and memory system state

### Enhanced Memory Capabilities

- `recall_memories_weighted` - **NEW**: Enhanced retrieval using composite scoring (α*relevance + β*importance + γ\*recency)
- `store_persona_memory` - **NEW**: Store/update AI persona characteristics with confidence tracking
- `get_current_persona` - **NEW**: Retrieve organized persona data for prompt context
- `generate_self_reflection` - **NEW**: Reflexion framework for self-assessment with database storage
- `apply_forgetting_curve` - **NEW**: Ebbinghaus forgetting curve implementation with decay
- `get_persona_evolution_summary` - **NEW**: Analyze persona changes over time with confidence trends

### Emotional Intelligence

- `reflect_on_interaction` - Store emotional reflection about interactions
- `get_emotional_insights` - Get emotional insights and patterns from recent interactions

## Usage

```bash
python server.py
```

## Configuration

Database configuration is loaded from `config/services/mcp-memory.env` in the project root.

## Enhanced Usage Examples

### Weighted Memory Retrieval

```python
# Enhanced retrieval with composite scoring
memories = memory_system.recall_memories_weighted(
    query="database optimization",
    limit=5,
    importance_weight=0.4,  # α: importance factor
    recency_weight=0.3,     # β: recency factor
    relevance_weight=0.3    # γ: relevance factor
)
# Returns memories scored by: α*importance + β*recency + γ*relevance
```

### Persona Evolution Layer

```python
# Store AI persona characteristics
memory_system.store_persona_memory(
    persona_type="skill",
    attribute="programming_languages",
    value=["Python", "JavaScript", "SQL"],
    confidence=0.8
)

# Retrieve current persona for prompt context
persona = memory_system.get_current_persona()
# Returns organized persona data by type (core_traits, preferences, skills)
```

### Self-Reflection Capability

```python
# Generate self-assessment reflection
reflection_id = memory_system.generate_self_reflection(
    reflection_type="learning_opportunity",
    content="Discovered importance of weighted scoring algorithms",
    context={"task": "memory_enhancement", "outcome": "successful"}
)
```

### Intelligent Forgetting

```python
# Apply Ebbinghaus forgetting curve
affected = memory_system.apply_forgetting_curve(
    min_age_hours=24,      # Only decay memories older than 1 day
    decay_factor=0.1,      # 10% decay rate
    access_boost=0.2,      # 20% boost for recently accessed
    dry_run=False          # Apply changes to database
)
```

## Advanced Configuration

### Weighted Retrieval Parameters

The enhanced retrieval system uses configurable weights for composite scoring:

- **importance_weight** (α): How much to weight stored importance scores (0.0-1.0)
- **recency_weight** (β): How much to weight memory recency (0.0-1.0)
- **relevance_weight** (γ): How much to weight semantic relevance (0.0-1.0)

_Note: Weights should sum to 1.0 for optimal results_

### Forgetting Curve Settings

Memory decay parameters based on Ebbinghaus research:

- **min_age_hours**: Minimum age before decay applies (default: 24)
- **decay_factor**: Base decay rate per time unit (default: 0.1)
- **access_boost**: Boost for recently accessed memories (default: 0.2)
- **max_decay**: Maximum decay to prevent total loss (default: 0.8)

### Database Schema

Enhanced schema includes:

- **memories** - Core memory storage with importance scoring
- **persona_memories** - AI identity evolution with confidence tracking
- **self_reflections** - Reflexion storage with metadata
- **memory_access_log** - Access patterns for forgetting algorithm
