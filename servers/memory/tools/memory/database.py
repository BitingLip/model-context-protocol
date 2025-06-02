#!/usr/bin/env python3
"""
Memory System Database Manager - Database operations and schema management
"""
import logging
import contextlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

try:
    import psycopg2
    import psycopg2.pool
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    psycopg2 = None
    RealDictCursor = None
    POSTGRES_AVAILABLE = False

from .core import MemorySystemBase, EmbeddingVector


class DatabaseManager(MemorySystemBase):
    """Handles all database operations for the memory system."""
    
    def __init__(self, project_root: Optional[str] = None, embedding_model: str = "all-MiniLM-L6-v2"):
        super().__init__(project_root, embedding_model)
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize PostgreSQL database and tables."""
        if not POSTGRES_AVAILABLE or not psycopg2:
            self.logger.warning("PostgreSQL not available. Using fallback storage.")
            return

        if not self.db_config:
            self.logger.warning("Database configuration not available. Using fallback storage.")
            return

        try:
            # Create connection pool
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20,  # min/max connections
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            
            # Test connection and create tables
            with self.connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")  # Test connection
                self.connection_pool.putconn(conn)
            
            self._create_tables()
            self.logger.info(f"Connected to PostgreSQL database: {self.db_config['database']}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            self.connection_pool = None

    def _create_tables(self) -> None:
        """Create necessary database tables."""
        if not self.connection_pool:
            return

        create_sql = """
        CREATE EXTENSION IF NOT EXISTS vector;
        
        -- Main memories table
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
        
        -- Memory relationships table
        CREATE TABLE IF NOT EXISTS memory_relationships (
            id SERIAL PRIMARY KEY,
            source_memory_id INTEGER REFERENCES memories(id),
            target_memory_id INTEGER REFERENCES memories(id),
            relationship_type VARCHAR(100),
            strength FLOAT DEFAULT 0.5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Emotional reflections table
        CREATE TABLE IF NOT EXISTS emotional_reflections (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            project_id VARCHAR(255) NOT NULL,
            reflection_type VARCHAR(100),
            content JSONB NOT NULL,
            mood_score FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Persona evolution table
        CREATE TABLE IF NOT EXISTS persona_memories (
            id SERIAL PRIMARY KEY,
            ai_instance_id VARCHAR(255) NOT NULL DEFAULT 'default',
            persona_type VARCHAR(100) NOT NULL,
            attribute_name VARCHAR(255) NOT NULL,
            current_value JSONB NOT NULL,
            confidence_score FLOAT DEFAULT 0.5,
            evidence_count INTEGER DEFAULT 1,
            first_observed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            growth_trajectory JSONB DEFAULT '[]'
        );
        
        -- Self-reflections table (Reflexion capability)
        CREATE TABLE IF NOT EXISTS self_reflections (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            project_id VARCHAR(255) NOT NULL,
            reflection_trigger VARCHAR(100),
            situation_summary TEXT,
            what_went_well TEXT,
            what_could_improve TEXT,
            lessons_learned TEXT,
            confidence_in_analysis FLOAT DEFAULT 0.5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Memory access patterns (for forgetting algorithm)
        CREATE TABLE IF NOT EXISTS memory_access_log (
            id SERIAL PRIMARY KEY,
            memory_id INTEGER REFERENCES memories(id) ON DELETE CASCADE,
            accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            access_context VARCHAR(100),
            relevance_score FLOAT DEFAULT 0.5
        );
        
        -- Performance indexes
        CREATE INDEX IF NOT EXISTS idx_memories_project_session ON memories(project_id, session_id);
        CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
        CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance_score DESC);
        CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_memories_content_gin ON memories USING GIN(content);
        CREATE INDEX IF NOT EXISTS idx_memories_composite_score ON memories(importance_score DESC, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_persona_ai_type ON persona_memories(ai_instance_id, persona_type);
        CREATE INDEX IF NOT EXISTS idx_persona_attribute ON persona_memories(attribute_name);
        CREATE INDEX IF NOT EXISTS idx_reflections_session ON self_reflections(session_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_access_log_memory_time ON memory_access_log(memory_id, accessed_at DESC);
        """
        
        try:
            with self.connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_sql)
                conn.commit()
                self.connection_pool.putconn(conn)
        except Exception as e:
            self.logger.error(f"Failed to create tables: {e}")

    def execute_query(self, sql: str, params: Optional[tuple] = None, fetch: bool = True) -> Optional[List[Dict[str, Any]]]:
        """Execute a database query safely."""
        if not self.connection_pool:
            return None

        try:
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(sql, params or ())
                    results = cur.fetchall() if fetch else None
                conn.commit()
                self.connection_pool.putconn(conn)
            return [dict(row) for row in results] if results else []
        except Exception as e:
            self.logger.error(f"Database query failed: {e}")
            return None

    def execute_insert(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Execute an INSERT query and return the inserted row."""
        if not self.connection_pool:
            return None

        try:
            with self.connection_pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(sql, params or ())
                    result = cur.fetchone()
                conn.commit()
                self.connection_pool.putconn(conn)
            return dict(result) if result else None
        except Exception as e:
            self.logger.error(f"Database insert failed: {e}")
            return None

    def get_memory_by_id(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory by ID."""
        sql = "SELECT * FROM memories WHERE id = %s"
        results = self.execute_query(sql, (memory_id,))
        return results[0] if results else None

    def get_memories_by_project(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all memories for a specific project."""
        sql = """
        SELECT * FROM memories 
        WHERE project_id = %s 
          AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        ORDER BY created_at DESC 
        LIMIT %s
        """
        return self.execute_query(sql, (project_id, limit)) or []

    def cleanup_expired_memories(self) -> int:
        """Remove expired memories and return count of deleted records."""
        if not self.connection_pool:
            return 0

        try:
            sql = "DELETE FROM memories WHERE expires_at <= CURRENT_TIMESTAMP"
            with self.connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    deleted_count = cur.rowcount
                conn.commit()
                self.connection_pool.putconn(conn)
            return deleted_count
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired memories: {e}")
            return 0

    def log_memory_access(self, memory_ids: List[int], access_context: str, relevance_score: float = 0.5) -> None:
        """Log memory access for forgetting algorithm."""
        if not self.connection_pool or not memory_ids:
            return

        try:
            insert_sql = """
            INSERT INTO memory_access_log (memory_id, access_context, relevance_score)
            VALUES (%s, %s, %s)
            """
            
            with self.connection_pool.getconn() as conn:
                with conn.cursor() as cur:
                    for memory_id in memory_ids:
                        cur.execute(insert_sql, (memory_id, access_context, relevance_score))
                conn.commit()
                self.connection_pool.putconn(conn)
                
        except Exception as e:
            self.logger.debug(f"Failed to log memory access: {e}")  # Non-critical, use debug level

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if not self.connection_pool:
            return {"error": "Database not available"}

        stats_sql = """
        SELECT 
            'memories' as table_name,
            COUNT(*) as total_count,
            COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as with_embeddings,
            COUNT(CASE WHEN expires_at IS NOT NULL AND expires_at <= CURRENT_TIMESTAMP THEN 1 END) as expired
        FROM memories
        UNION ALL
        SELECT 
            'persona_memories' as table_name,
            COUNT(*) as total_count,
            0 as with_embeddings,
            0 as expired
        FROM persona_memories
        UNION ALL
        SELECT 
            'self_reflections' as table_name,
            COUNT(*) as total_count,
            0 as with_embeddings,
            0 as expired
        FROM self_reflections
        """
        
        results = self.execute_query(stats_sql)
        return {"tables": results} if results else {"error": "Failed to get stats"}

    def update_memory_embedding(self, memory_id: int, embedding: List[float]) -> bool:
        """Update the embedding vector for a specific memory."""
        try:
            update_sql = """
            UPDATE memories 
            SET embedding = %s, updated_at = %s
            WHERE id = %s;
            """
            
            result = self.execute_query(
                update_sql, 
                (EmbeddingVector(embedding), datetime.now(), memory_id)
            )
            
            return result is not None
            
        except Exception as e:
            self.logger.error(f"Failed to update embedding for memory {memory_id}: {e}")
            return False

    def __del__(self) -> None:
        """Clean up database connections."""
        if self.connection_pool:
            with contextlib.suppress(Exception):
                self.connection_pool.closeall()
