"""
Memory System Package - Modular AI Memory System

A sophisticated PostgreSQL-based memory system for AI assistants with semantic search,
emotional context tracking, and enhanced capabilities for persona evolution and
self-reflection.
"""

from .main import MemorySystem
from .core import MemorySystemBase, EmbeddingVector
from .database import DatabaseManager
from .embeddings import EmbeddingManager  
from .enhanced import EnhancedMemoryCapabilities

__all__ = [
    'MemorySystem',
    'MemorySystemBase', 
    'EmbeddingVector',
    'DatabaseManager',
    'EmbeddingManager',
    'EnhancedMemoryCapabilities'
]

__version__ = "2.0.0"
