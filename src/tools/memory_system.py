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

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, Json
    import psycopg2.pool
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    logging.warning("psycopg2 not available. Memory system will use fallback storage.")


class MemorySystem:
    """
    PostgreSQL-based memory system for AI assistants.
    
    Features:
    - Project-aware memory storage
    - Emotional context tracking
    - Semantic search capabilities
    - Automatic backup and recovery
    - Memory importance scoring
    - Temporal relationship tracking    """
    
    def __init__(self, project_root: Optional[str] = None):
        # Logging setup first
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.project_root = project_root or os.getcwd()
        self.current_project_id = self._detect_project_id()
        self.session_id = self._generate_session_id()
        
        # Database configuration        self.db_config = self._load_db_config()
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
        database = os.getenv('MEMORY_DB_NAME', 'ai_memory')
        user = os.getenv('MEMORY_DB_USER')
        password = os.getenv('MEMORY_DB_PASSWORD')
        
        # Validate required credentials are provided
        if not user or not password:
            self.logger.error("Database credentials not found in environment variables or config file")
            self.logger.info("Please set MEMORY_DB_USER and MEMORY_DB_PASSWORD in config/services/mcp-memory.env")
            raise ValueError("Database credentials required but not provided")
        
        return {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password,
        }
    
    def _load_env_file(self) -> None:
        """Load environment variables from config file."""
        try:
            # Find the project root (4 levels up from this file)
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent.parent
            env_file = project_root / "config" / "services" / "mcp-memory.env"
            
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
        try:
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
        except Exception:
            pass
        
        # Fallback to directory name
        return Path(self.project_root).name
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID for this conversation."""
        timestamp = datetime.now().isoformat()
        project_hash = hashlib.md5(self.project_root.encode()).hexdigest()[:8]
        return f"{self.current_project_id}_{project_hash}_{timestamp}"
    
    def _initialize_database(self) -> None:
        """Initialize PostgreSQL database and tables."""
        if not POSTGRES_AVAILABLE:
            self.logger.warning("Using fallback memory storage - install psycopg2 for full functionality")
            return
        
        try:
            # Create connection pool
            if POSTGRES_AVAILABLE:
                self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                    1, 20,  # min and max connections
                    **self.db_config
                )
                
                # Create tables if they don't exist
                self._create_tables()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PostgreSQL: {e}")
            self.logger.info("Falling back to in-memory storage")
    
    def _create_tables(self) -> None:
        """Create necessary database tables."""
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
        
        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_memories_project_session ON memories(project_id, session_id);
        CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
        CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance_score DESC);
        CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_memories_content_gin ON memories USING GIN(content);
        """
        
        if self.connection_pool:
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
            
            # Store in database
            insert_sql = """
            INSERT INTO memories (
                project_id, session_id, memory_type, title, content,
                importance_score, emotional_context, tags, expires_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at;
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(insert_sql, (
                        self.current_project_id,
                        self.session_id,
                        memory_type,
                        title,
                        Json(content_json),
                        importance,
                        Json(emotional_context),
                        tags,
                        expires_at
                    ))
                    result = cur.fetchone()
                conn.commit()
                self.connection_pool.putconn(conn)
            
            self.logger.info(f"Stored memory: {memory_type} - {title or 'Untitled'}")
            
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
        """Recall relevant memories based on query and filters."""
        if not POSTGRES_AVAILABLE or not self.connection_pool:
            return self._recall_memories_fallback(query, memory_type, limit)
        
        try:
            # Build dynamic query
            where_conditions = ["importance_score >= %s"]
            params: List[Any] = [importance_threshold]
            
            if not include_other_projects:
                where_conditions.append("project_id = %s")
                params.append(project_id or self.current_project_id)
            
            if memory_type:
                where_conditions.append("memory_type = %s")
                params.append(memory_type)
            
            if query:
                # Full-text search on content
                where_conditions.append("content::text ILIKE %s")
                params.append(f"%{query}%")
            
            # Add expiration check
            where_conditions.append("(expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)")
            
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
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(search_sql, params)
                    results = cur.fetchall()
                self.connection_pool.putconn(conn)
            
            # Convert to regular dictionaries and format dates
            memories = []
            for row in results:
                memory = dict(row)
                memory['created_at'] = memory['created_at'].isoformat()
                if memory['updated_at']:
                    memory['updated_at'] = memory['updated_at'].isoformat()
                memories.append(memory)
            
            self.logger.info(f"Recalled {len(memories)} memories for query: {query}")
            return memories
            
        except Exception as e:
            self.logger.error(f"Failed to recall memories: {e}")
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
                        Json(content),
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
                params.append(Json(content_json))
            
            if title is not None:
                update_fields.append("title = %s")
                params.append(title)
            
            if importance is not None:
                update_fields.append("importance_score = %s")
                params.append(importance)
            
            if emotional_context is not None:
                update_fields.append("emotional_context = %s")
                params.append(Json(emotional_context))
            
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
            
            insights = {
                "session_id": self.session_id,
                "project_id": self.current_project_id,
                "analysis_period_days": days_back,
                "reflection_patterns": [dict(row) for row in results],
                "overall_mood": sum(row['avg_mood'] or 0 for row in results) / len(results) if results else 0
            }
            
            return insights
            
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
    
    def __del__(self) -> None:
        """Clean up database connections."""
        if self.connection_pool:
            self.connection_pool.closeall()
