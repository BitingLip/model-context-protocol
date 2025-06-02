#!/usr/bin/env python3
"""
Memory System Core - Base classes and configuration
"""
import os
import logging
import hashlib
import contextlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Database imports with fallback
try:
    import psycopg2
    import psycopg2.pool
    from psycopg2.extras import RealDictCursor, Json
    from psycopg2.extensions import AsIs
    POSTGRES_AVAILABLE = True
except ImportError:
    psycopg2 = None
    RealDictCursor = None
    Json = None
    POSTGRES_AVAILABLE = False

# Embedding support
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    EMBEDDING_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False


class EmbeddingVector:
    """Wrapper class for embedding vectors that need to be converted to pgvector format."""
    def __init__(self, vector):
        if np and isinstance(vector, np.ndarray):
            self.vector = vector.tolist()
        else:
            self.vector = vector


def _adapt_embedding_vector(embedding_vector):
    """Convert an EmbeddingVector into a pgvector-literal string."""
    arr = embedding_vector.vector
    inner = ",".join(str(float(x)) for x in arr)
    literal = f"'[{inner}]'::vector"
    return AsIs(literal)


# Register adapter only for our EmbeddingVector class
if POSTGRES_AVAILABLE:
    psycopg2.extensions.register_adapter(EmbeddingVector, _adapt_embedding_vector)


class MemorySystemBase:
    """Base class for memory system with core configuration and utilities."""
    
    def __init__(self, project_root: Optional[str] = None, embedding_model: str = "all-MiniLM-L6-v2"):
        # Logging setup
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Project configuration
        self.project_root = project_root or os.getcwd()
        self.current_project_id = self._detect_project_id()
        self.session_id = self._generate_session_id()
        
        # Embedding configuration
        self.embedding_model = None
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        self._initialize_embedding_model(embedding_model)
        
        # Database configuration
        try:
            self.db_config = self._load_db_config()
            self.connection_pool: Optional[Any] = None
            self.fallback_storage: Dict[int, Dict[str, Any]] = {}
        except ValueError as e:
            self.logger.warning(f"Database configuration failed: {e}")
            self.db_config = {}
            self.connection_pool = None
            self.fallback_storage: Dict[int, Dict[str, Any]] = {}
    
    def _initialize_embedding_model(self, embedding_model: str) -> None:
        """Initialize the embedding model."""
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
    
    def _load_db_config(self) -> Dict[str, str]:
        """Load PostgreSQL configuration from environment or config file."""
        self._load_env_file()
        
        # Get required config values
        host = os.getenv('MEMORY_DB_HOST', 'localhost')
        port = os.getenv('MEMORY_DB_PORT', '5432')
        database = os.getenv('MEMORY_DB_NAME', 'memory_system')
        user = os.getenv('MEMORY_DB_USER')
        password = os.getenv('MEMORY_DB_PASSWORD')
        
        # Validate required credentials
        if not user or not password:
            self.logger.error("Database credentials not found in environment variables or config file")
            self.logger.info("Please set MEMORY_DB_USER and MEMORY_DB_PASSWORD in interfaces/model-context-protocol/config/mcp-memory.env")
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
            # Find the project root (5 levels up from this file)
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent.parent.parent.parent
            
            # Look in interfaces/model-context-protocol/config
            env_file = project_root / "interfaces" / "model-context-protocol" / "config" / "mcp-memory.env"
            
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                self.logger.info(f"Loaded config from {env_file}")
            else:
                self.logger.warning(f"Config file not found: {env_file}")
        except Exception as e:
            self.logger.warning(f"Failed to load config file: {e}")
    
    def _detect_project_id(self) -> str:
        """Detect current project based on directory structure and git repo."""
        with contextlib.suppress(Exception):
            # Try to get git repo name
            if os.path.exists(os.path.join(self.project_root, '.git')):
                git_config = os.path.join(self.project_root, '.git', 'config')
                if os.path.exists(git_config):
                    with open(git_config, 'r') as f:
                        for line in f:
                            if 'url =' in line and '.git' in line:
                                return line.split('/')[-1].replace('.git', '').strip()
        
        # Fallback to directory name
        return Path(self.project_root).name
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID for this conversation."""
        timestamp = datetime.now().isoformat()
        project_hash = hashlib.md5(self.project_root.encode()).hexdigest()[:8]
        return f"{self.current_project_id}_{project_hash}_{timestamp}"
    
    def _safe_json(self, data: Any) -> Any:
        """Safely convert data to JSON format for database storage."""
        return Json(data) if (POSTGRES_AVAILABLE and Json) else data
    
    def __del__(self) -> None:
        """Clean up database connections."""
        if self.connection_pool:
            try:
                self.connection_pool.closeall()
            except Exception:
                pass
