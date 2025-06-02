#!/usr/bin/env python3
"""
AI Memory System - PostgreSQL-based persistent memory for AI assistants

Provides sophisticated memory storage, retrieval, and emotional context management
to enable true continuity in AI-human collaboration across projects and time.
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import asyncio
import logging
import contextlib

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, Json
    from psycopg2.extensions import AsIs
    import psycopg2.pool
    import psycopg2.extensions    # Import numpy for adapter
    try:
        import numpy as np
    except ImportError:
        np = None

    class EmbeddingVector:
        """Wrapper class for embedding vectors that need to be converted to pgvector format."""
        def __init__(self, vector):
            if np and isinstance(vector, np.ndarray):
                self.vector = vector.tolist()
            else:
                self.vector = list(vector)
    
    def _adapt_embedding_vector(embedding_vector):
        """Convert an EmbeddingVector into a pgvector-literal string."""
        arr = embedding_vector.vector
        inner = ",".join(str(float(x)) for x in arr)
        literal = f"'[{inner}]'::vector"
        return AsIs(literal)

    # Register adapter only for our EmbeddingVector class
    psycopg2.extensions.register_adapter(EmbeddingVector, _adapt_embedding_vector)

    POSTGRES_AVAILABLE = True
except ImportError:
    # Create dummy classes for type hints when psycopg2 is not available
    psycopg2 = None
    RealDictCursor = None
    Json = None
    POSTGRES_AVAILABLE = False
    logging.warning("psycopg2 not available. Memory system will use fallback storage.")

# Embedding generation support
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    EMBEDDING_AVAILABLE = False
    logging.warning("sentence-transformers not available. Semantic search will use fallback text matching.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False


class MemorySystem:
    """
    PostgreSQL-based memory system for AI assistants with semantic search capabilities.
    
    Features:
    - Project-aware memory storage
    - Emotional context tracking
    - Semantic search using pgvector embeddings
    - Automatic embedding generation
    - pgvectorscale optimization support
    - Memory importance scoring
    - Temporal relationship tracking
    """
    
    def __init__(self, project_root: Optional[str] = None, embedding_model: str = "all-MiniLM-L6-v2"):
        # Logging setup first
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.project_root = project_root or os.getcwd()
        self.current_project_id = self._detect_project_id()
        # Initialize embedding model if available
        self.embedding_model = None
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        if EMBEDDING_AVAILABLE and SentenceTransformer:
            try:
                self.embedding_model = SentenceTransformer(embedding_model)
                self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
                self.logger.info(f"Loaded embedding model: {embedding_model} (dim: {self.embedding_dim})")
            except Exception as e:
                self.logger.warning(f"Failed to load embedding model: {e}")
                self.embedding_model = None
        else:
            self.logger.warning("Semantic search disabled - install sentence-transformers for full functionality")
        # Session management
        self.session_id = self._generate_session_id()
        # Database configuration
        self.db_config = self._load_db_config()
        self.connection_pool: Optional[Any] = None
        self.fallback_storage: Dict[int, Dict[str, Any]] = {}
        
        # Initialize database
        self._initialize_database()
    
    def _load_db_config(self) -> Dict[str, str]:
        """Load PostgreSQL configuration from environment or config file."""
        # Try to load from config file first
        self._load_env_file()
          # Get required config values - no hardcoded credentials
        host = os.getenv('MEMORY_DB_HOST', 'localhost')
        port = os.getenv('MEMORY_DB_PORT', '5432')
        database = os.getenv('MEMORY_DB_NAME', 'memory_system')
        user = os.getenv('MEMORY_DB_USER')
        password = os.getenv('MEMORY_DB_PASSWORD')
          # Validate required credentials are provided
        if not user or not password:
            self.logger.error("Database credentials not found in environment variables or config file")
            self.logger.info("Please set MEMORY_DB_USER and MEMORY_DB_PASSWORD in interfaces/model-context-protocol/config/mcp-memory.env")
            raise ValueError("Database credentials required but not provided")
        
        return {            'host': host,            'port': port,
            'database': database,            'user': user,
            'password': password,
        }
    
    def _load_env_file(self) -> None:
        """Load environment variables from config file."""
        try:
            # Find the project root (5 levels up from this file)
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent.parent.parent
            
            # Look only in the new location in interfaces/model-context-protocol/config
            env_file = project_root / "interfaces" / "model-context-protocol" / "config" / "mcp-memory.env"
            
            if env_file.exists():
                # Simple .env file parser
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            # Only set if not already in environment
                            if key not in os.environ:
                                os.environ[key] = value
                self.logger.info(f"Loaded config from {env_file}")
            else:
                self.logger.info(f"Config file not found: {env_file}, using defaults")
        except Exception as e:
            self.logger.warning(f"Failed to load config file: {e}")
    
    def _detect_project_id(self) -> str:
        """Detect current project based on directory structure and git repo."""
        with contextlib.suppress(Exception):
            # Try to get git repo name
            if os.path.exists(os.path.join(self.project_root, '.git')):
                import subprocess
                result = subprocess.run(
                    ['git', 'remote', 'get-url', 'origin'],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    repo_url = result.stdout.strip()
                    return repo_url.split('/')[-1].replace('.git', '')
        
        # Fallback to directory name
        return Path(self.project_root).name
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID for this conversation."""
        timestamp = datetime.now().isoformat()
        project_hash = hashlib.md5(self.project_root.encode()).hexdigest()[:8]
        return f"{self.current_project_id}_{project_hash}_{timestamp}"
    
    def _initialize_database(self) -> None:
        """Initialize PostgreSQL database and tables."""
        if not POSTGRES_AVAILABLE or not psycopg2:
            self.logger.warning("Using fallback memory storage - install psycopg2 for full functionality")
            return
        
        try:
            # Create connection pool
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                1, 20,  # min and max connections
                **self.db_config
            )
            
            # Create tables if they don't exist
            self._create_tables()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PostgreSQL: {e}")
            self.logger.info("Falling back to in-memory storage")
    
    def _safe_json(self, data: Any) -> Any:
        """Safely convert data to JSON format for database storage."""
        return Json(data) if (POSTGRES_AVAILABLE and Json) else data
    
    def _create_tables(self) -> None:
        """Create necessary database tables."""
        if self.connection_pool:
            create_sql = """
            CREATE EXTENSION IF NOT EXISTS vector;
            
            CREATE TABLE IF NOT EXISTS memories (
                id SERIAL PRIMARY KEY,
                project_id VARCHAR(255) NOT NULL,
                session_id VARCHAR(255) NOT NULL,
                memory_type VARCHAR(100) NOT NULL,
                title VARCHAR(500),
                content JSONB NOT NULL,
                importance_score FLOAT DEFAULT 0.5,
                emotional_context JSONB DEFAULT '{}',
                tags TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                embedding VECTOR(384)
            );
            
            CREATE TABLE IF NOT EXISTS memory_relationships (
                id SERIAL PRIMARY KEY,
                source_memory_id INTEGER REFERENCES memories(id),
                target_memory_id INTEGER REFERENCES memories(id),
                relationship_type VARCHAR(100),
                strength FLOAT DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
              CREATE TABLE IF NOT EXISTS emotional_reflections (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                project_id VARCHAR(255) NOT NULL,
                reflection_type VARCHAR(100),
                content JSONB NOT NULL,
                mood_score FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- NEW: Persona Evolution Table
            CREATE TABLE IF NOT EXISTS persona_memories (
                id SERIAL PRIMARY KEY,
                ai_instance_id VARCHAR(255) NOT NULL DEFAULT 'default',
                persona_type VARCHAR(100) NOT NULL, -- 'core_trait', 'preference', 'skill', 'weakness', 'goal'
                attribute_name VARCHAR(255) NOT NULL,
                current_value JSONB NOT NULL,
                confidence_score FLOAT DEFAULT 0.5,
                evidence_count INTEGER DEFAULT 1,
                first_observed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                growth_trajectory JSONB DEFAULT '[]' -- track changes over time
            );
            
            -- NEW: Self-Reflections Table (Reflexion capability)
            CREATE TABLE IF NOT EXISTS self_reflections (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                project_id VARCHAR(255) NOT NULL,
                reflection_trigger VARCHAR(100), -- 'task_completion', 'error', 'feedback', 'periodic'
                situation_summary TEXT,
                what_went_well TEXT,
                what_could_improve TEXT,
                lessons_learned TEXT,
                confidence_in_analysis FLOAT DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- NEW: Memory Access Patterns (for forgetting algorithm)
            CREATE TABLE IF NOT EXISTS memory_access_log (
                id SERIAL PRIMARY KEY,
                memory_id INTEGER REFERENCES memories(id) ON DELETE CASCADE,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_context VARCHAR(100), -- 'retrieval', 'update', 'related_lookup'
                relevance_score FLOAT DEFAULT 0.5
            );
            
            -- Enhanced Indexes for performance
            CREATE INDEX IF NOT EXISTS idx_memories_project_session ON memories(project_id, session_id);
            CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
            CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance_score DESC);
            CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_memories_content_gin ON memories USING GIN(content);
            
            -- NEW: Indexes for enhanced retrieval
            CREATE INDEX IF NOT EXISTS idx_memories_composite_score ON memories(importance_score DESC, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_persona_ai_type ON persona_memories(ai_instance_id, persona_type);
            CREATE INDEX IF NOT EXISTS idx_persona_attribute ON persona_memories(attribute_name);
            CREATE INDEX IF NOT EXISTS idx_reflections_session ON self_reflections(session_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_access_log_memory_time ON memory_access_log(memory_id, accessed_at DESC);
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_sql)
                conn.commit()
                self.connection_pool.putconn(conn)
    
    def store_memory(
        self,
        memory_type: str,
        content: Union[str, Dict[str, Any]],
        title: Optional[str] = None,
        importance: float = 0.5,
        emotional_context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Store a new memory."""
        if not POSTGRES_AVAILABLE or not self.connection_pool:
            return self._store_memory_fallback(memory_type, content, title, importance)
        
        try:
            # Prepare data
            content_json = content if isinstance(content, dict) else {"text": content}
            emotional_context = emotional_context or {}
            tags = tags or []
            expires_at = None
            if expires_in_days:
                expires_at = datetime.now() + timedelta(days=expires_in_days)
            
            # Generate embedding for content
            content_text = self._prepare_content_for_embedding(content_json)
            if title:
                content_text = f"{title}: {content_text}"
            embedding = self._generate_embedding(content_text)
            
            # Store in database
            insert_sql = """
            INSERT INTO memories (
                project_id, session_id, memory_type, title, content,
                importance_score, emotional_context, tags, expires_at, embedding            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at;
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(insert_sql, (
                        self.current_project_id,
                        self.session_id,
                        memory_type,
                        title,
                        self._safe_json(content_json),
                        importance,
                        self._safe_json(emotional_context),
                        tags,
                        expires_at,
                        EmbeddingVector(embedding) if embedding else None
                    ))
                    result = cur.fetchone()
                conn.commit()
                self.connection_pool.putconn(conn)
            
            embedding_status = "with embedding" if embedding else "without embedding"
            self.logger.info(f"Stored memory: {memory_type} - {title or 'Untitled'} ({embedding_status})")
            
            return {
                "success": True,
                "memory_id": result['id'],
                "created_at": result['created_at'].isoformat(),
                "project_id": self.current_project_id,
                "session_id": self.session_id
            }            
        except Exception as e:
            self.logger.error(f"Failed to store memory: {e}")
            return {"success": False, "error": str(e)}
    
    def recall_memories(
        self,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        project_id: Optional[str] = None,
        importance_threshold: float = 0.0,
        limit: int = 10,
        include_other_projects: bool = False
    ) -> List[Dict[str, Any]]:
        """Recall relevant memories based on query and filters with semantic search."""
        if not POSTGRES_AVAILABLE or not self.connection_pool:
            return self._recall_memories_fallback(query, memory_type, limit)
        
        self.logger.info(f"Starting recall_memories: query='{query}', memory_type={memory_type}, limit={limit}")
        
        try:
            # Build base conditions
            where_conditions = ["importance_score >= %s"]
            params: List[Any] = [importance_threshold]
            
            if not include_other_projects:
                where_conditions.append("project_id = %s")
                params.append(project_id or self.current_project_id)
            
            if memory_type:
                where_conditions.append("memory_type = %s")
                params.append(memory_type)
              # Add expiration check
            where_conditions.append("(expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)")
            self.logger.debug(f"Base conditions: {where_conditions}, params: {params}")
            
            # Choose search strategy based on query and embedding availability
            if query and self.embedding_model:                # Generate embedding (Python list) for the query text
                query_embedding = self._generate_embedding(query)
                if query_embedding:
                    # Semantic search: embedding parameter goes FIRST (matches SQL order)
                    search_sql = f"""
                    SELECT 
                        id, project_id, session_id, memory_type, title,
                        content, importance_score, emotional_context, tags,
                        created_at, updated_at,
                        (1 - (embedding <=> %s)) * importance_score AS relevance_score
                    FROM memories
                    WHERE {' AND '.join(where_conditions)}
                      AND embedding IS NOT NULL
                    ORDER BY relevance_score DESC, created_at DESC
                    LIMIT %s;
                    """                    # CRITICAL: Parameters must match SQL order: embedding (in SELECT), base WHERE params, limit
                    execution_params = [EmbeddingVector(query_embedding)] + params + [limit]
                    self.logger.info(f"Using semantic search for query: '{query}'")
                else:
                    # If embedding generation failed, fall back to text search
                    where_conditions.append("(content::text ILIKE %s OR title ILIKE %s)")
                    search_param = f"%{query}%"
                    params.extend([search_param, search_param])
                    search_sql = f"""
                    SELECT 
                        id, project_id, session_id, memory_type, title,
                        content, importance_score, emotional_context, tags,
                        created_at, updated_at
                    FROM memories
                    WHERE {' AND '.join(where_conditions)}
                    ORDER BY importance_score DESC, created_at DESC
                    LIMIT %s;
                    """
                    params.append(limit)
                    execution_params = params
                    self.logger.info(f"Using text search fallback for query: '{query}'")
                    
            elif query:
                # Query provided but no embedding model - use text search
                self.logger.info("No embedding model available, using text search")
                where_conditions.append("(content::text ILIKE %s OR title ILIKE %s)")
                search_param = f"%{query}%"
                params.extend([search_param, search_param])
                
                search_sql = f"""
                SELECT 
                    id, project_id, session_id, memory_type, title,
                    content, importance_score, emotional_context, tags,
                    created_at, updated_at
                FROM memories
                WHERE {' AND '.join(where_conditions)}
                ORDER BY importance_score DESC, created_at DESC
                LIMIT %s;
                """
                
                params.append(limit)
                execution_params = params
                
            else:
                # No query - basic retrieval by importance and recency                self.logger.info("No query provided, retrieving recent memories by importance")
                search_sql = f"""
                SELECT 
                    id, project_id, session_id, memory_type, title,
                    content, importance_score, emotional_context, tags,
                    created_at, updated_at
                FROM memories
                WHERE {' AND '.join(where_conditions)}
                ORDER BY importance_score DESC, created_at DESC
                LIMIT %s;
                """
                
                params.append(limit)
                execution_params = params
            
            # Execute the query
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:                    # DEBUG (optional): log full SQL with parameters
                    self.logger.info(f"About to execute SQL with params: {[type(p).__name__ for p in execution_params]}")
                    try:
                        mogrified_sql = cur.mogrify(search_sql, execution_params)
                        self.logger.info(f"Mogrified SQL: {mogrified_sql.decode('utf-8')[:500]}...")
                    except Exception as debug_e:
                        self.logger.error(f"Could not mogrify SQL for debugging: {debug_e}")
                    
                    cur.execute(search_sql, execution_params)
                    results = cur.fetchall()
                    self.logger.info(f"Database returned {len(results)} results")
                self.connection_pool.putconn(conn)
            
            # Convert to regular dictionaries and format dates
            memories = []
            for row in results:
                memory = dict(row)
                memory['created_at'] = memory['created_at'].isoformat()
                if memory['updated_at']:
                    memory['updated_at'] = memory['updated_at'].isoformat()
                # Include relevance score if available
                if 'relevance_score' in memory:
                    memory['relevance_score'] = float(memory['relevance_score']) if memory['relevance_score'] else 0.0
                memories.append(memory)
            
            # Determine search type for logging
            search_type = "semantic" if query and self.embedding_model and 'relevance_score' in (memories[0] if memories else {}) else "text" if query else "standard"
            self.logger.info(f"Successfully recalled {len(memories)} memories using {search_type} search")
            
            return memories
            
        except Exception as e:
            import traceback
            self.logger.error(f"Failed to recall memories: {e}")
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            return []
    
    def reflect_on_interaction(
        self,
        reflection_type: str,
        content: Dict[str, Any],
        mood_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """Store an emotional reflection about an interaction."""
        if not POSTGRES_AVAILABLE or not self.connection_pool:
            return {"success": False, "error": "PostgreSQL not available"}
        
        try:
            insert_sql = """
            INSERT INTO emotional_reflections (
                session_id, project_id, reflection_type, content, mood_score
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id, created_at;
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(insert_sql, (
                        self.session_id,
                        self.current_project_id,
                        reflection_type,
                        self._safe_json(content),
                        mood_score
                    ))
                    result = cur.fetchone()
                conn.commit()
                self.connection_pool.putconn(conn)
            
            self.logger.info(f"Stored emotional reflection: {reflection_type}")
            
            return {
                "success": True,
                "reflection_id": result['id'],
                "created_at": result['created_at'].isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to store reflection: {e}")
            return {"success": False, "error": str(e)}
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of stored memories for the current project."""
        if not POSTGRES_AVAILABLE or not self.connection_pool:
            return {
                "total_memories": len(self.fallback_storage),
                "storage_type": "fallback",
                "project_id": self.current_project_id
            }
        
        try:
            summary_sql = """
            SELECT 
                memory_type,
                COUNT(*) as count,
                AVG(importance_score) as avg_importance,
                MAX(created_at) as latest_memory
            FROM memories
            WHERE project_id = %s
              AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
            GROUP BY memory_type
            ORDER BY count DESC;
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(summary_sql, (self.current_project_id,))
                    results = cur.fetchall()
                self.connection_pool.putconn(conn)
            
            total_memories = sum(row['count'] for row in results)
            
            return {
                "project_id": self.current_project_id,
                "session_id": self.session_id,
                "total_memories": total_memories,
                "memory_types": [
                    {
                        "type": row['memory_type'],
                        "count": row['count'],
                        "avg_importance": float(row['avg_importance']),
                        "latest": row['latest_memory'].isoformat()
                    }
                    for row in results
                ],
                "storage_type": "postgresql"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get memory summary: {e}")
            return {"error": str(e)}
    
    def update_memory(
        self,
        memory_id: int,
        content: Optional[Union[str, Dict[str, Any]]] = None,
        title: Optional[str] = None,
        importance: Optional[float] = None,
        emotional_context: Optional[Dict[str, Any]] = None,
        add_tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Update an existing memory."""
        if not POSTGRES_AVAILABLE or not self.connection_pool:
            return {"success": False, "error": "PostgreSQL not available"}
        
        try:
            update_fields = []
            params: List[Any] = []
            
            if content is not None:
                content_json = content if isinstance(content, dict) else {"text": content}
                update_fields.append("content = %s")
                params.append(self._safe_json(content_json))
            
            if title is not None:
                update_fields.append("title = %s")
                params.append(title)
            
            if importance is not None:
                update_fields.append("importance_score = %s")
                params.append(importance)
            
            if emotional_context is not None:
                update_fields.append("emotional_context = %s")
                params.append(self._safe_json(emotional_context))
            
            if add_tags:
                update_fields.append("tags = array_cat(tags, %s)")
                params.append(add_tags)
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(memory_id)
            
            update_sql = f"""
            UPDATE memories 
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, updated_at;
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(update_sql, params)
                    result = cur.fetchone()
                conn.commit()
                self.connection_pool.putconn(conn)
            
            if result:
                return {
                    "success": True,
                    "memory_id": result['id'],
                    "updated_at": result['updated_at'].isoformat()
                }
            else:
                return {"success": False, "error": "Memory not found"}
                
        except Exception as e:
            self.logger.error(f"Failed to update memory: {e}")
            return {"success": False, "error": str(e)}
    
    def get_emotional_insights(self, days_back: int = 30) -> Dict[str, Any]:
        """Get emotional insights and patterns from recent interactions."""
        if not POSTGRES_AVAILABLE or not self.connection_pool:
            return {"error": "PostgreSQL not available"}
        
        try:
            insights_sql = """
            SELECT 
                reflection_type,
                AVG(mood_score) as avg_mood,
                COUNT(*) as reflection_count,
                array_agg(DISTINCT content->>'topic') as topics
            FROM emotional_reflections
            WHERE session_id = %s 
              AND created_at > CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY reflection_type
            ORDER BY reflection_count DESC;
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(insights_sql, (self.session_id, days_back))
                    results = cur.fetchall()
                self.connection_pool.putconn(conn)
            
            return {
                "session_id": self.session_id,
                "project_id": self.current_project_id,
                "analysis_period_days": days_back,
                "reflection_patterns": [dict(row) for row in results],
                "overall_mood": sum(row['avg_mood'] or 0 for row in results) / len(results) if results else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get emotional insights: {e}")
            return {"error": str(e)}
    
    def cleanup_expired_memories(self) -> Dict[str, Any]:
        """Remove expired memories from the database."""
        if not POSTGRES_AVAILABLE or not self.connection_pool:
            return {"success": False, "error": "PostgreSQL not available"}
        
        try:
            cleanup_sql = """
            DELETE FROM memories 
            WHERE expires_at IS NOT NULL 
              AND expires_at <= CURRENT_TIMESTAMP
            RETURNING count(*);
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute(cleanup_sql)
                    deleted_count = cur.rowcount
                conn.commit()
                self.connection_pool.putconn(conn)
            
            self.logger.info(f"Cleaned up {deleted_count} expired memories")
            
            return {
                "success": True,
                "deleted_count": deleted_count
            }
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup memories: {e}")
            return {"success": False, "error": str(e)}

    # Fallback methods for when PostgreSQL is not available
    def _store_memory_fallback(
        self, 
        memory_type: str, 
        content: Union[str, Dict[str, Any]], 
        title: Optional[str], 
        importance: float
    ) -> Dict[str, Any]:
        """Fallback memory storage using in-memory dictionary."""
        memory_id = len(self.fallback_storage) + 1
        self.fallback_storage[memory_id] = {
            "id": memory_id,
            "project_id": self.current_project_id,
            "memory_type": memory_type,
            "title": title,
            "content": content,
            "importance": importance,
            "created_at": datetime.now().isoformat()
        }
        return {
            "success": True,
            "memory_id": memory_id,
            "storage_type": "fallback"
        }
    
    def _recall_memories_fallback(
        self, 
        query: Optional[str], 
        memory_type: Optional[str], 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Fallback memory recall using in-memory search."""
        results = []
        for memory in self.fallback_storage.values():
            if memory_type and memory["memory_type"] != memory_type:
                continue
            if query and query.lower() not in str(memory["content"]).lower():
                continue
            results.append(memory)
        # Sort by importance and limit
        results.sort(key=lambda x: x["importance"], reverse=True)
        return results[:limit]
    
    # ========== ENHANCED MEMORY CAPABILITIES ==========
    
    def recall_memories_weighted(
        self,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        project_id: Optional[str] = None,
        importance_threshold: float = 0.0,
        limit: int = 10,
        include_other_projects: bool = False,
        recency_weight: float = 0.3,
        importance_weight: float = 0.5,
        relevance_weight: float = 0.2
    ) -> List[Dict[str, Any]]:
        """
        Enhanced memory recall using weighted scoring (importance + recency + relevance).
        Based on Generative Agents research: score = α*relevance + β*importance + γ*recency
        """
        if not POSTGRES_AVAILABLE or not self.connection_pool:
            return self._recall_memories_fallback(query, memory_type, limit)
        
        try:
            # Build dynamic query with weighted scoring
            where_conditions = []
            params: List[Any] = []
            
            # Add query parameters for relevance scoring first
            params.extend([query, f"%{query}%" if query else None])
            
            # Add WHERE conditions and their parameters
            where_conditions.append("importance_score >= %s")
            params.append(importance_threshold)
            
            if not include_other_projects:
                where_conditions.append("project_id = %s")
                params.append(project_id or self.current_project_id)
            
            if memory_type:
                where_conditions.append("memory_type = %s")
                params.append(memory_type)
            
            # Add limit parameter
            params.append(limit)
            
            # Enhanced scoring query
            search_sql = f"""
            SELECT 
                id, project_id, session_id, memory_type, title,
                content, importance_score, emotional_context, tags,
                created_at, updated_at,
                -- Weighted composite score
                (
                    {importance_weight} * importance_score +
                    {recency_weight} * (1.0 - EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - created_at)) / (365.0 * 24 * 3600)) +
                    {relevance_weight} * CASE 
                        WHEN %s IS NOT NULL AND content::text ILIKE %s THEN 1.0 
                        ELSE 0.5 
                    END
                ) AS composite_score
            FROM memories
            WHERE {' AND '.join(where_conditions)}
                AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
            ORDER BY composite_score DESC, created_at DESC
            LIMIT %s;
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(search_sql, params)
                    results = cur.fetchall()
                self.connection_pool.putconn(conn)
            
            # Log access for forgetting algorithm
            if results:
                self._log_memory_access([row['id'] for row in results], 'weighted_retrieval')
            
            # Convert to regular dictionaries and format dates
            memories = []
            for row in results:
                memory = dict(row)
                memory['created_at'] = memory['created_at'].isoformat()
                if memory['updated_at']:
                    memory['updated_at'] = memory['updated_at'].isoformat()
                memory['composite_score'] = float(memory['composite_score'])
                memories.append(memory)
            
            self.logger.info(f"Weighted recall found {len(memories)} memories (weights: i={importance_weight}, r={recency_weight}, rel={relevance_weight})")
            return memories
            
        except Exception as e:
            self.logger.error(f"Failed weighted memory recall: {e}")
            return self.recall_memories(query, memory_type, project_id, importance_threshold, limit, include_other_projects)
    
    def store_persona_memory(
        self,
        persona_type: str,  # 'core_trait', 'preference', 'skill', 'weakness', 'goal'
        attribute_name: str,
        current_value: Union[str, Dict[str, Any]],
        confidence_score: float = 0.5,
        ai_instance_id: str = 'default'
    ) -> Dict[str, Any]:
        """
        Store or update AI persona characteristics for self-evolving identity.
        """
        if not POSTGRES_AVAILABLE or not self.connection_pool:
            return {"success": False, "error": "PostgreSQL not available"}
        
        try:
            value_json = current_value if isinstance(current_value, dict) else {"value": current_value}
            
            # Check if this persona attribute already exists
            check_sql = """
            SELECT id, confidence_score, evidence_count, growth_trajectory
            FROM persona_memories 
            WHERE ai_instance_id = %s AND persona_type = %s AND attribute_name = %s;
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(check_sql, (ai_instance_id, persona_type, attribute_name))
                    
                    if existing := cur.fetchone():
                        # Update existing persona memory with growth tracking
                        old_trajectory = existing['growth_trajectory'] or []
                        new_trajectory = old_trajectory + [{
                            "timestamp": datetime.now().isoformat(),
                            "previous_value": existing.get('current_value'),
                            "new_value": value_json,
                            "confidence_change": confidence_score - existing['confidence_score']
                        }]
                        
                        update_sql = """
                        UPDATE persona_memories 
                        SET current_value = %s, 
                            confidence_score = %s,
                            evidence_count = evidence_count + 1,
                            last_updated = CURRENT_TIMESTAMP,
                            growth_trajectory = %s
                        WHERE id = %s
                        RETURNING id;
                        """
                        cur.execute(update_sql, (
                            self._safe_json(value_json),
                            confidence_score,
                            self._safe_json(new_trajectory),
                            existing['id']
                        ))
                        result_id = cur.fetchone()['id']
                        action = "updated"
                    else:
                        # Insert new persona memory
                        insert_sql = """
                        INSERT INTO persona_memories (
                            ai_instance_id, persona_type, attribute_name, 
                            current_value, confidence_score
                        ) VALUES (%s, %s, %s, %s, %s)
                        RETURNING id;
                        """
                        cur.execute(insert_sql, (
                            ai_instance_id, persona_type, attribute_name,
                            self._safe_json(value_json), confidence_score
                        ))
                        result_id = cur.fetchone()['id']
                        action = "created"
                
                conn.commit()
                self.connection_pool.putconn(conn)
            
            self.logger.info(f"Persona memory {action}: {persona_type}.{attribute_name} = {current_value}")
            
            return {
                "success": True,
                "persona_id": result_id,
                "action": action,
                "ai_instance_id": ai_instance_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to store persona memory: {e}")
            return {"success": False, "error": str(e)}
    
    def get_current_persona(self, ai_instance_id: str = 'default') -> Dict[str, Any]:
        """
        Retrieve current AI persona for prompt context.
        """
        if not POSTGRES_AVAILABLE or not self.connection_pool:
            return {"persona": "Basic AI Assistant (fallback mode)"}
        
        try:
            persona_sql = """
            SELECT persona_type, attribute_name, current_value, confidence_score
            FROM persona_memories 
            WHERE ai_instance_id = %s 
            ORDER BY persona_type, confidence_score DESC;
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(persona_sql, (ai_instance_id,))
                    results = cur.fetchall()
                self.connection_pool.putconn(conn)
            
            # Organize by persona type
            persona = {
                "core_traits": {},
                "preferences": {},
                "skills": {},
                "weaknesses": {},
                "goals": {},
                "ai_instance_id": ai_instance_id
            }
            
            for row in results:
                category = row['persona_type'] + 's'  # pluralize
                if category in persona:
                    persona[category][row['attribute_name']] = {
                        "value": row['current_value'],
                        "confidence": row['confidence_score']
                    }
            
            return persona
            
        except Exception as e:
            self.logger.error(f"Failed to get persona: {e}")
            return {"error": str(e)}
    
    def generate_self_reflection(
        self,
        situation_summary: str,
        reflection_trigger: str = 'manual',
        project_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate and store self-reflection for continuous improvement (Reflexion capability).
        """
        if not POSTGRES_AVAILABLE or not self.connection_pool:
            return {"success": False, "error": "PostgreSQL not available"}
        
        try:
            # This would typically use an LLM to generate reflections
            # For now, we'll store the framework and can enhance with AI later
            
            reflection_prompts = {
                "what_went_well": f"Based on this situation: '{situation_summary}', what aspects went well?",
                "what_could_improve": f"What could be improved in handling: '{situation_summary}'?",
                "lessons_learned": f"What key lessons can be learned from: '{situation_summary}'?"
            }
            
            # Store the reflection structure (can be enhanced with LLM generation later)
            insert_sql = """
            INSERT INTO self_reflections (
                session_id, project_id, reflection_trigger, situation_summary,
                what_went_well, what_could_improve, lessons_learned, confidence_in_analysis
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at;
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(insert_sql, (
                        self.session_id,
                        project_context or self.current_project_id,
                        reflection_trigger,
                        situation_summary,
                        "Framework ready for AI analysis",  # Placeholder
                        "Framework ready for AI analysis",  # Placeholder  
                        "Framework ready for AI analysis",  # Placeholder
                        0.5  # Medium confidence until AI enhancement
                    ))
                    result = cur.fetchone()
                conn.commit()
                self.connection_pool.putconn(conn)
            
            self.logger.info(f"Self-reflection stored: {reflection_trigger} - {situation_summary[:50]}...")
            
            return {
                "success": True,
                "reflection_id": result['id'],
                "created_at": result['created_at'].isoformat(),
                "trigger": reflection_trigger,
                "note": "Framework ready - can be enhanced with LLM analysis"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate reflection: {e}")
            return {"success": False, "error": str(e)}
    
    def apply_forgetting_curve(self, decay_factor: float = 0.1) -> Dict[str, Any]:
        """
        Apply Ebbinghaus forgetting curve to reduce importance of old, unaccessed memories.
        """
        if not POSTGRES_AVAILABLE or not self.connection_pool:
            return {"success": False, "error": "PostgreSQL not available"}
        
        try:
            # Calculate decay based on age and access patterns
            decay_sql = """
            UPDATE memories 
            SET importance_score = GREATEST(0.1, importance_score * (1.0 - %s * 
                EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - 
                    COALESCE((
                        SELECT MAX(accessed_at) 
                        FROM memory_access_log 
                        WHERE memory_id = memories.id
                    ), created_at)
                )) / (30.0 * 24 * 3600)  -- 30 days in seconds
            ))
            WHERE importance_score > 0.1
                AND created_at < CURRENT_TIMESTAMP - INTERVAL '7 days';
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute(decay_sql, (decay_factor,))
                    affected_rows = cur.rowcount
                conn.commit()
                self.connection_pool.putconn(conn)
            
            self.logger.info(f"Applied forgetting curve to {affected_rows} memories")
            
            return {
                "success": True,
                "memories_decayed": affected_rows,
                "decay_factor": decay_factor
            }
            
        except Exception as e:
            self.logger.error(f"Failed to apply forgetting curve: {e}")
            return {"success": False, "error": str(e)}
    
    def _log_memory_access(self, memory_ids: List[int], access_context: str, relevance_score: float = 0.5) -> None:
        """Log memory access for forgetting algorithm."""
        if not POSTGRES_AVAILABLE or not self.connection_pool or not memory_ids:
            return
        
        try:
            insert_sql = """
            INSERT INTO memory_access_log (memory_id, access_context, relevance_score)
            VALUES (%s, %s, %s);
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    for memory_id in memory_ids:
                        cur.execute(insert_sql, (memory_id, access_context, relevance_score))
                conn.commit()
                self.connection_pool.putconn(conn)
                
        except Exception as e:
            self.logger.debug(f"Failed to log memory access: {e}")  # Non-critical, use debug level
    
    def get_persona_evolution_summary(self, days_back: int = 30, persona_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get summary of how the AI persona has evolved over time.
        
        Args:
            days_back: Number of days to analyze
            persona_type: Filter by specific persona type
            
        Returns:
            Dictionary with persona evolution insights and changes
        """
        if not POSTGRES_AVAILABLE or not self.connection_pool:
            return {"error": "PostgreSQL not available"}
        
        try:
            evolution_sql, params = self._get_persona_evolution_sql_and_params(days_back, persona_type)
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(evolution_sql, params)
                    results = cur.fetchall()
                self.connection_pool.putconn(conn)
            
            # Analyze evolution patterns
            evolution_summary = {
                "analysis_period_days": days_back,
                "total_attributes_tracked": len(results),
                "persona_types": {},
                "confidence_trends": {},
                "recent_changes": []
            }
            
            # Group by persona type and analyze trends
            for row in results:
                p_type = row['persona_type']
                if p_type not in evolution_summary["persona_types"]:
                    evolution_summary["persona_types"][p_type] = {
                        "attributes": {},
                        "average_confidence": 0.0,
                        "total_attributes": 0
                    }
                
                attr_name = row['attribute_name']
                evolution_summary["persona_types"][p_type]["attributes"][attr_name] = {
                    "current_value": row['current_value'],
                    "confidence": row['confidence_score'],
                    "growth_trajectory": row['growth_trajectory'],
                    "last_updated": row['last_updated'].isoformat() if row['last_updated'] else None
                }
                
                # Track recent changes
                if row['last_updated'] and (datetime.now() - row['last_updated']).days <= 7:
                    evolution_summary["recent_changes"].append({
                        "type": p_type,
                        "attribute": attr_name,
                        "updated": row['last_updated'].isoformat(),
                        "confidence": row['confidence_score']
                    })
            
            # Calculate averages
            for p_type, data in evolution_summary["persona_types"].items():
                if data["attributes"]:
                    confidences = [attr["confidence"] for attr in data["attributes"].values()]
                    data["average_confidence"] = sum(confidences) / len(confidences)
                    data["total_attributes"] = len(data["attributes"])
            
            return evolution_summary
            
        except Exception as e:
            self.logger.error(f"Failed to get persona evolution summary: {e}")
            return {"error": str(e)}

    def _get_persona_evolution_sql_and_params(self, days_back: int, persona_type: Optional[str] = None):
        """Helper to get SQL and params for persona evolution summary."""
        if persona_type:
            evolution_sql = """
            SELECT 
                persona_type,
                attribute_name,
                current_value,
                confidence_score,
                growth_trajectory,
                first_observed,
                last_updated
            FROM persona_memories 
            WHERE first_observed >= CURRENT_TIMESTAMP - INTERVAL %s
                AND persona_type = %s
            ORDER BY persona_type, attribute_name, last_updated DESC;
            """
            params = (f"{days_back} days", persona_type)
        else:
            evolution_sql = """
            SELECT 
                persona_type,
                attribute_name,
                current_value,
                confidence_score,
                growth_trajectory,
                first_observed,
                last_updated
            FROM persona_memories 
            WHERE first_observed >= CURRENT_TIMESTAMP - INTERVAL %s
            ORDER BY persona_type, attribute_name, last_updated DESC;
            """
            params = (f"{days_back} days",)
        return evolution_sql, params

    def _del__(self) -> None:
        """Clean up database connections."""
        if self.connection_pool:
            self.connection_pool.closeall()

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text content."""
        if not self.embedding_model or not EMBEDDING_AVAILABLE:
            return None
        
        try:            # Extract text content if it's structured
            if isinstance(text, dict):
                # Combine all text fields for embedding
                text_parts = []
                for key, value in text.items():
                    if isinstance(value, str):
                        text_parts.append(f"{key}: {value}")
                    elif isinstance(value, (list, dict)):
                        text_parts.append(f"{key}: {str(value)}")
                text = " ".join(text_parts)
            
            # Generate embedding
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            
            # Convert to list ensuring proper float type
            if NUMPY_AVAILABLE and hasattr(embedding, 'tolist'):
                return [float(x) for x in embedding.tolist()]
            elif hasattr(embedding, 'cpu'):
                return [float(x) for x in embedding.cpu().numpy().tolist()]
            elif hasattr(embedding, 'tolist'):
                return [float(x) for x in embedding.tolist()]
            else:
                return [float(x) for x in list(embedding)]
                
        except Exception as e:
            self.logger.warning(f"Failed to generate embedding: {e}")
            return None
    
    def _prepare_content_for_embedding(self, content: Union[str, Dict[str, Any]]) -> str:
        """Prepare content for embedding generation."""
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            # Extract text content from structured data
            text_parts = []
            
            # Handle common content structures
            if 'text' in content:
                text_parts.append(content['text'])
            if 'description' in content:
                text_parts.append(content['description'])
            if 'summary' in content:
                text_parts.append(content['summary'])
            if 'title' in content:
                text_parts.append(content['title'])
                
            # Include other string values
            for key, value in content.items():
                if key not in ['text', 'description', 'summary', 'title'] and isinstance(value, str):
                    text_parts.append(f"{key}: {value}")
                    
            return " ".join(text_parts) if text_parts else str(content)
        else:
            return str(content)
    
    def _get_memories_without_embeddings(self, batch_size: int) -> List[Dict[str, Any]]:
        """Helper to retrieve memories without embeddings."""
        if not self.connection_pool:
            return []
        with self.connection_pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, content, title 
                    FROM memories 
                    WHERE embedding IS NULL 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (batch_size,))
                memories = cur.fetchall()
            self.connection_pool.putconn(conn)
        return memories
    def update_embeddings_for_existing_memories(self, batch_size: int = 10) -> Dict[str, Any]:
        """Update embeddings for existing memories that don't have them."""
        if not POSTGRES_AVAILABLE or not self.connection_pool or not self.embedding_model:
            return {"success": False, "error": "PostgreSQL or embedding model not available"}

        try:
            if not (memories := self._get_memories_without_embeddings(batch_size)):
                return {"success": True, "updated": 0, "message": "All memories already have embeddings"}

            updated_count = 0
            for memory in memories:
                # Generate embedding for content
                content_text = self._prepare_content_for_embedding(memory['content'])
                if memory['title']:
                    content_text = f"{memory['title']}: {content_text}"

                embedding = self._generate_embedding(content_text)
                if embedding:
                    # Update memory with embedding
                    with self.connection_pool.getconn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE memories 
                                SET embedding = %s, updated_at = CURRENT_TIMESTAMP 
                                WHERE id = %s
                            """, (EmbeddingVector(embedding), memory['id']))
                        conn.commit()
                        self.connection_pool.putconn(conn)
                    updated_count += 1

            self.logger.info(f"Updated embeddings for {updated_count} memories")
            return {"success": True, "updated": updated_count}
            
        except Exception as e:
            self.logger.error(f"Failed to update embeddings: {e}")
            return {"success": False, "error": str(e)}
