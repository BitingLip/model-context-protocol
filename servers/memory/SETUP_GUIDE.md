# Memory MCP Server Setup Guide

This guide provides detailed instructions for setting up the Memory MCP Server, including database configuration, dependencies, and troubleshooting tips.

## Prerequisites

- Python 3.8+ (Python 3.12 recommended)
- PostgreSQL 12+ (PostgreSQL 14+ recommended)
- pgvector extension for PostgreSQL

## Quick Start

The easiest way to set up the Memory MCP Server is to use the provided setup script:

```bash
python setup/setup.py
```

This script will:
1. Check PostgreSQL installation and compatibility
2. Install required Python dependencies
3. Create and configure the memory.env file
4. Set up the database and required extensions
5. Create necessary database tables
6. Test the memory system functionality
7. Update embeddings for existing memories (if any)

## Manual Setup

### 1. Install PostgreSQL and Extensions

#### Windows

1. Download PostgreSQL from [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)
2. Run the installer and follow the prompts
3. Remember the password you set for the `postgres` user
4. Install pgvector using Stack Builder (included with PostgreSQL) or build from source:
   - [pgvector Installation Guide](https://github.com/pgvector/pgvector#installation)

#### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Install pgvector
git clone https://github.com/pgvector/pgvector
cd pgvector
make
sudo make install
```

### 2. Create Database and User

```sql
-- Connect as postgres user
CREATE DATABASE memory_system;
CREATE USER ai_assistant WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE memory_system TO ai_assistant;

-- Connect to memory_system database
\c memory_system

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Configure Environment

1. Copy the example configuration file:
   ```bash
   cp config/memory.env.example config/memory.env
   ```

2. Edit `memory.env` with your database credentials:
   ```dotenv
   MEMORY_DB_HOST=localhost
   MEMORY_DB_PORT=5432
   MEMORY_DB_NAME=memory_system
   MEMORY_DB_USER=ai_assistant
   MEMORY_DB_PASSWORD=your_secure_password
   ```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the Server

```bash
python server.py
```

## Advanced Configuration

### Embedding Model

By default, the system uses the `all-MiniLM-L6-v2` model for embeddings. You can configure a different model in `memory.env`:

```dotenv
EMBEDDING_MODEL=all-mpnet-base-v2
EMBEDDING_BATCH_SIZE=16
```

Available models:
- `all-MiniLM-L6-v2` (Default, fast, 384 dimensions)
- `all-mpnet-base-v2` (Better quality, 768 dimensions)
- `all-MiniLM-L12-v2` (Balanced performance)

### Vector Indexing

If using pgvectorscale, you can configure the index type and parameters:

```dotenv
VECTOR_INDEX_TYPE=hnsw
VECTOR_INDEX_PARAMS={"m": 16, "ef_construction": 64}
```

Available index types:
- `hnsw` (Hierarchical Navigable Small World, recommended)
- `ivfflat` (Inverted File with Flat Compression)
- `diskann` (Disk-based Approximate Nearest Neighbor)

## Troubleshooting

### Database Connection Issues

1. **Connection refused**
   - Verify PostgreSQL is running: `pg_isready`
   - Check host/port in `memory.env`
   - Ensure firewall allows connections to PostgreSQL port

2. **Authentication failed**
   - Verify username and password in `memory.env`
   - Check PostgreSQL's `pg_hba.conf` authentication settings

3. **Database does not exist**
   - Create the database manually: `CREATE DATABASE memory_system;`

4. **Permission denied when creating extensions**
   - Connect as superuser: `sudo -u postgres psql`
   - Create extension: `CREATE EXTENSION vector;`

### Embedding Model Issues

1. **ImportError: No module named 'sentence_transformers'**
   - Install the package: `pip install sentence-transformers>=2.0.0`

2. **CUDA not available**
   - For GPU acceleration: `pip install torch==2.0.0+cu118 -f https://download.pytorch.org/whl/torch_stable.html`

3. **Model download fails**
   - Check internet connection
   - Try different model: `EMBEDDING_MODEL=all-MiniLM-L6-v2`

### Common Error Messages

1. **"Error: psycopg2 module not found"**
   - Run: `pip install psycopg2-binary>=2.9.0`

2. **"pgvector extension is not available"**
   - Install pgvector: [Installation Guide](https://github.com/pgvector/pgvector#installation)

3. **"Could not create vector extension"**
   - Connect as PostgreSQL superuser and run: `CREATE EXTENSION vector;`

## Setup Script Options

The setup script (`setup.py`) supports several command-line arguments:

- `--force` - Force setup even if already configured
- `--skip-db-create` - Skip database creation and schema setup
- `--skip-python-deps` - Skip Python dependencies installation
- `--skip-embeddings-update` - Skip updating embeddings for existing memories

## Database Schema

The Memory MCP Server uses the following database tables:

1. `memories` - Core memory storage with embedding vectors
2. `memory_relationships` - Connections between related memories
3. `emotional_reflections` - Emotional context data
4. `persona_memories` - AI identity evolution tracking
5. `self_reflections` - Self-assessment records 
6. `memory_access_log` - Access patterns for forgetting algorithm

## Performance Optimization

For large-scale deployments:

1. **Connection Pooling**
   - The system uses built-in connection pooling (1-20 connections)
   - For higher loads, consider using pgBouncer

2. **Vector Indexing**
   - Install pgvectorscale for improved vector search performance
   - Configure optimal index parameters based on your data size

3. **Memory Usage**
   - Monitor RAM usage when loading embedding models
   - Consider using smaller models for resource-constrained environments

## Contact and Support

For issues or questions:
- File an issue in the GitHub repository
- Contact the development team at support@bitinglip.ai
