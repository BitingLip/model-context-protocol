#!/usr/bin/env python3
"""
Memory System Main Orchestrator
"""
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

try:
    from .core import MemorySystemBase
    from .database import DatabaseManager
    from .embeddings import EmbeddingManager  
    from .enhanced import EnhancedMemoryCapabilities
except ImportError:
    # Fallback for direct execution
    from core import MemorySystemBase
    from database import DatabaseManager
    from embeddings import EmbeddingManager  
    from enhanced import EnhancedMemoryCapabilities


class MemorySystem(MemorySystemBase):
    """Main memory system orchestrator."""
    
    def __init__(self, project_root: Optional[str] = None, embedding_model: str = "all-MiniLM-L6-v2"):
        super().__init__(project_root, embedding_model)
        
        # Initialize component managers
        self.database_manager = DatabaseManager(project_root, embedding_model)
        self.embedding_manager = EmbeddingManager(project_root, embedding_model)
        self.enhanced_capabilities = EnhancedMemoryCapabilities(project_root, embedding_model)
        
        # Session management
        self.session_id = self._generate_session_id()

    def store_memory(self, memory_type: str, content: Union[str, Dict[str, Any]], 
                     title: Optional[str] = None, importance: float = 0.5,
                     emotional_context: Optional[Dict[str, Any]] = None,
                     tags: Optional[List[str]] = None,
                     expires_in_days: Optional[int] = None) -> Dict[str, Any]:
        """Store a new memory."""
        if not self.database_manager.connection_pool:
            return {"success": False, "error": "Database not available"}
        
        try:
            # Prepare data
            content_json = content if isinstance(content, dict) else {"text": content}
            emotional_context = emotional_context or {}
            tags = tags or []
            expires_at = None
            if expires_in_days:
                expires_at = datetime.now() + timedelta(days=expires_in_days)
            
            # Generate embedding
            content_text = self.embedding_manager.prepare_content_for_embedding(content_json)
            if title:
                content_text = f"{title}: {content_text}"
            embedding = self.embedding_manager.generate_embedding(content_text)
            
            # Store in database (serialize JSON objects)
            memory_id = self.database_manager.execute_insert(
                """INSERT INTO memories (project_id, session_id, memory_type, title, content,
                   importance_score, emotional_context, tags, embedding, expires_at) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;""",
                (self.current_project_id, self.session_id, memory_type, title,
                 json.dumps(content_json), importance, json.dumps(emotional_context), 
                 tags, embedding, expires_at)
            )
            
            if memory_id:
                self.logger.info(f"Stored memory {memory_id}")
                return {"success": True, "memory_id": memory_id, "has_embedding": embedding is not None}
            else:
                return {"success": False, "error": "Failed to store memory"}
                
        except Exception as e:
            self.logger.error(f"Error storing memory: {e}")
            return {"success": False, "error": str(e)}

    def recall_memories(self, query: Optional[str] = None, memory_type: Optional[str] = None,
                        importance_threshold: float = 0.0, limit: int = 10,
                        project_id: Optional[str] = None, 
                        include_other_projects: bool = False) -> List[Dict[str, Any]]:
        """Recall memories with optional semantic search."""
        if not self.database_manager.connection_pool:
            return []
        
        try:
            # Build WHERE conditions
            where_conditions = []
            params = []
            
            if not include_other_projects:
                where_conditions.append("project_id = %s")
                params.append(project_id or self.current_project_id)
                
            if memory_type:
                where_conditions.append("memory_type = %s")
                params.append(memory_type)
                
            if importance_threshold > 0:
                where_conditions.append("importance_score >= %s")
                params.append(importance_threshold)
                
            where_conditions.append("(expires_at IS NULL OR expires_at > %s)")
            params.append(datetime.now())
            
            if not where_conditions:
                where_conditions = ["1=1"]
            
            # Try semantic search first
            if query and self.embedding_manager.embedding_model:
                query_embedding = self.embedding_manager.generate_embedding(query)
                if query_embedding:
                    search_sql, execution_params = self.embedding_manager.build_semantic_search_query(
                        where_conditions, params, query_embedding, limit)
                    results = self.database_manager.execute_query(search_sql, tuple(execution_params))
                    if results:
                        memory_ids = [memory['id'] for memory in results]
                        self.enhanced_capabilities.log_memory_access(
                            memory_ids, "semantic_search", database_manager=self.database_manager)
                        return results
            
            # Fallback to text search or simple query
            if query:
                search_sql, execution_params = self.embedding_manager.build_text_search_query(
                    where_conditions, params, query, limit)
            else:
                search_sql = f"""SELECT id, project_id, session_id, memory_type, title,
                                content, importance_score, emotional_context, tags,
                                created_at, updated_at FROM memories
                                WHERE {' AND '.join(where_conditions)}
                                ORDER BY importance_score DESC, created_at DESC LIMIT %s;"""
                execution_params = params + [limit]
            
            results = self.database_manager.execute_query(search_sql, tuple(execution_params))
            
            if results:
                memory_ids = [memory['id'] for memory in results]
                self.enhanced_capabilities.log_memory_access(
                    memory_ids, "recall", database_manager=self.database_manager)
            
            return results or []            
        except Exception as e:
            self.logger.error(f"Error recalling memories: {e}")
            return []

    def recall_memories_weighted(self, **kwargs) -> List[Dict[str, Any]]:
        """Enhanced recall with weighted scoring."""
        # Since the enhanced module doesn't have this method, implement basic weighted recall
        try:
            # Extract weight parameters
            importance_weight = kwargs.pop('importance_weight', 0.4)
            recency_weight = kwargs.pop('recency_weight', 0.3)
            relevance_weight = kwargs.pop('relevance_weight', 0.3)
            
            # Call base recall method without weight parameters
            memories = self.recall_memories(**kwargs)
            
            # Apply basic weighting
            for memory in memories:
                # Calculate composite score
                importance_score = memory.get('importance_score', 0.5) * importance_weight
                
                # Recency score (newer = higher)
                created_at = memory.get('created_at')
                if created_at:
                    days_old = (datetime.now() - created_at).days
                    recency_score = max(0, 1 - (days_old / 365)) * recency_weight
                else:
                    recency_score = 0
                
                # Relevance score (if semantic search was used, this is already factored in)
                relevance_score = memory.get('similarity_score', 0.5) * relevance_weight
                
                memory['composite_score'] = importance_score + recency_score + relevance_score
            
            # Sort by composite score
            memories.sort(key=lambda x: x.get('composite_score', 0), reverse=True)
            return memories
            
        except Exception as e:
            self.logger.error(f"Error in weighted recall: {e}")
            return []
    
    def update_memory(self, memory_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing memory."""
        if not self.database_manager.connection_pool:
            return {"success": False, "error": "Database not available"}
        
        try:
            # Build update fields dynamically
            update_fields = []
            params = []
            
            if 'content' in kwargs:
                content = kwargs['content']
                content_json = content if isinstance(content, dict) else {"text": content}
                update_fields.append("content = %s")
                params.append(json.dumps(content_json))
                
                # Regenerate embedding if content changed
                if self.embedding_manager.embedding_model:
                    content_text = self.embedding_manager.prepare_content_for_embedding(content_json)
                    if 'title' in kwargs:
                        content_text = f"{kwargs['title']}: {content_text}"
                    embedding = self.embedding_manager.generate_embedding(content_text)
                    if embedding:
                        update_fields.append("embedding = %s")
                        params.append(embedding)
            
            if 'title' in kwargs:
                update_fields.append("title = %s")
                params.append(kwargs['title'])
            
            if 'importance' in kwargs:
                update_fields.append("importance_score = %s")
                params.append(kwargs['importance'])
            
            if 'emotional_context' in kwargs:
                update_fields.append("emotional_context = %s")
                params.append(json.dumps(kwargs['emotional_context']))
            
            if 'add_tags' in kwargs:
                # Get current tags and merge
                current = self.database_manager.get_memory_by_id(memory_id)
                if current:
                    current_tags = current.get('tags', [])
                    new_tags = list(set(current_tags + kwargs['add_tags']))
                    update_fields.append("tags = %s")
                    params.append(new_tags)
            
            if not update_fields:
                return {"success": False, "error": "No fields to update"}
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(memory_id)
            
            sql = f"UPDATE memories SET {', '.join(update_fields)} WHERE id = %s"
            rows_affected = self.database_manager.execute_query(sql, tuple(params))
            
            return {"success": True, "rows_affected": len(rows_affected) if rows_affected else 0}
            
        except Exception as e:
            self.logger.error(f"Error updating memory: {e}")
            return {"success": False, "error": str(e)}
    
    def store_persona_memory(self, **kwargs) -> Dict[str, Any]:
        """Store persona memory - delegate to enhanced capabilities."""
        return self.enhanced_capabilities.store_persona_memory(
            database_manager=self.database_manager, **kwargs
        )
    
    def get_current_persona(self, **kwargs) -> Dict[str, Any]:
        """Get current persona - delegate to enhanced capabilities.""" 
        return self.enhanced_capabilities.get_current_persona(
            database_manager=self.database_manager, **kwargs
        )
    
    def generate_self_reflection(self, **kwargs) -> Dict[str, Any]:
        """Generate self reflection - delegate to enhanced capabilities."""
        return self.enhanced_capabilities.generate_self_reflection(
            database_manager=self.database_manager, **kwargs
        )
    
    def apply_forgetting_curve(self, **kwargs) -> Dict[str, Any]:
        """Apply forgetting curve - delegate to enhanced capabilities."""
        return self.enhanced_capabilities.apply_forgetting_curve(
            database_manager=self.database_manager, **kwargs
        )
    
    def get_persona_evolution_summary(self, **kwargs) -> Dict[str, Any]:
        """Get persona evolution summary - delegate to enhanced capabilities."""
        return self.enhanced_capabilities.get_persona_evolution_summary(
            database_manager=self.database_manager, **kwargs
        )
    
    def reflect_on_interaction(self, **kwargs) -> Dict[str, Any]:
        """Reflect on interaction - delegate to enhanced capabilities."""
        return self.enhanced_capabilities.reflect_on_interaction(
            database_manager=self.database_manager, **kwargs
        )
    
    def get_emotional_insights(self, days_back: int = 30) -> Dict[str, Any]:
        """Get emotional insights - delegate to enhanced capabilities."""
        return self.enhanced_capabilities.get_emotional_insights(
            days_back, database_manager=self.database_manager
        )
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get memory summary from database."""
        if not self.database_manager.connection_pool:
            return {"total_memories": 0, "error": "Database not available"}
        
        try:
            stats = self.database_manager.get_database_stats()
            return {
                "total_memories": stats.get("total_memories", 0),
                "by_type": stats.get("memories_by_type", {}),
                "by_importance": stats.get("memories_by_importance", {}),
                "project_id": self.current_project_id
            }
        except Exception as e:
            self.logger.error(f"Error getting memory summary: {e}")
            return {"total_memories": 0, "error": str(e)}
    
    def cleanup_expired_memories(self, **kwargs) -> Dict[str, Any]:
        """Cleanup expired memories - delegate to database manager."""
        try:
            count = self.database_manager.cleanup_expired_memories()
            return {"success": True, "deleted_count": count}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_embeddings_for_existing_memories(self, **kwargs) -> Dict[str, Any]:
        """Update embeddings for existing memories."""
        if not self.database_manager.connection_pool or not self.embedding_manager.embedding_model:
            return {"success": False, "error": "Database or embedding model not available"}
        
        try:
            batch_size = kwargs.get('batch_size', 100)
            force_update = kwargs.get('force_update', False)
            
            # Get memories that need embedding updates
            where_clause = "WHERE embedding IS NULL" if not force_update else ""
            memories = self.database_manager.execute_query(
                f"SELECT id, title, content FROM memories {where_clause} LIMIT %s",
                (batch_size,)
            )
            
            if not memories:
                return {"success": True, "updated_count": 0, "message": "No memories need embedding updates"}
            
            updated_count = 0
            for memory in memories:
                try:
                    content_json = json.loads(memory['content']) if isinstance(memory['content'], str) else memory['content']
                    content_text = self.embedding_manager.prepare_content_for_embedding(content_json)
                    if memory['title']:
                        content_text = f"{memory['title']}: {content_text}"
                    
                    embedding = self.embedding_manager.generate_embedding(content_text)
                    if embedding:
                        self.database_manager.update_memory_embedding(memory['id'], embedding)
                        updated_count += 1
                        
                except Exception as e:
                    self.logger.warning(f"Failed to update embedding for memory {memory['id']}: {e}")
                    continue
            
            return {
                "success": True, 
                "updated_count": updated_count,
                "total_processed": len(memories)
            }
            
        except Exception as e:
            self.logger.error(f"Error updating embeddings: {e}")
            return {"success": False, "error": str(e)}    # Properties for MCP tool compatibility - removed project_root property since it's already an attribute    @property 
    def connection_pool(self):
        """Get database connection pool."""
        return getattr(self.database_manager, 'connection_pool', None)