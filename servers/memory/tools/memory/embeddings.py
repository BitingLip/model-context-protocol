#!/usr/bin/env python3
"""
Memory System Embedding Manager - Semantic search and embedding generation
"""
import logging
from typing import Any, Dict, List, Optional, Union

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

from .core import MemorySystemBase, EmbeddingVector


class EmbeddingManager(MemorySystemBase):
    """Handles embedding generation and semantic search operations."""
    
    def __init__(self, project_root: Optional[str] = None, embedding_model: str = "all-MiniLM-L6-v2"):
        super().__init__(project_root, embedding_model)

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text content."""
        if not self.embedding_model or not EMBEDDING_AVAILABLE:
            return None
        
        try:
            # Extract text content if it's structured
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

    def prepare_content_for_embedding(self, content: Union[str, Dict[str, Any]]) -> str:
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

    def build_semantic_search_query(self, where_conditions: List[str], params: List[Any], 
                                   query_embedding: List[float], limit: int) -> tuple[str, List[Any]]:
        """Build SQL query for semantic search with embedding similarity."""
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
        """
        
        # CRITICAL: Parameters must match SQL order: embedding (in SELECT), base WHERE params, limit
        execution_params = [EmbeddingVector(query_embedding)] + params + [limit]
        
        return search_sql, execution_params

    def build_text_search_query(self, where_conditions: List[str], params: List[Any], 
                               query: str, limit: int) -> tuple[str, List[Any]]:
        """Build SQL query for text-based search fallback."""
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
        
        return search_sql, params

    def update_embeddings_for_memories(self, memories: List[Dict[str, Any]], 
                                     database_manager) -> Dict[str, Any]:
        """Update embeddings for a batch of memories."""
        if not self.embedding_model:
            return {"success": False, "error": "Embedding model not available"}

        try:
            updated_count = 0
            processed_count = 0
            skipped_count = 0
            error_count = 0

            for memory in memories:
                processed_count += 1
                
                try:
                    # Generate embedding for content
                    content_text = self.prepare_content_for_embedding(memory['content'])
                    if memory.get('title'):
                        content_text = f"{memory['title']}: {content_text}"

                    embedding = self.generate_embedding(content_text)
                    if embedding:
                        # Update memory with embedding using database manager
                        success = database_manager.update_memory_embedding(memory['id'], embedding)
                        if success:
                            updated_count += 1
                        else:
                            error_count += 1
                    else:
                        skipped_count += 1
                        self.logger.warning(f"Failed to generate embedding for memory {memory['id']}")
                        
                except Exception as e:
                    error_count += 1
                    self.logger.error(f"Error processing memory {memory['id']}: {e}")

            self.logger.info(f"Embedding update complete: {updated_count} updated, {skipped_count} skipped, {error_count} errors")
            
            return {
                "success": True,
                "processed": processed_count,
                "updated": updated_count,
                "skipped": skipped_count,
                "errors": error_count
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update embeddings: {e}")
            return {"success": False, "error": str(e)}

    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about embedding availability and performance."""
        return {
            "embedding_available": EMBEDDING_AVAILABLE,
            "model_loaded": self.embedding_model is not None,
            "model_name": "all-MiniLM-L6-v2" if self.embedding_model else None,
            "embedding_dimension": self.embedding_dim,
            "numpy_available": NUMPY_AVAILABLE
        }
