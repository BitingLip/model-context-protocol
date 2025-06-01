#!/usr/bin/env python3
"""
Memory MCP Tool - Provides memory capabilities to AI assistants through MCP

This tool integrates the MemorySystem with the Model Context Protocol,
allowing AI assistants to store, recall, and reflect on memories across conversations.
"""

import os
from typing import Any, Dict, List, Optional
from .memory_system import MemorySystem


class MemoryMCPTool:
    """MCP tool wrapper for the AI Memory System."""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.memory_system = MemorySystem(project_root)
    
    def store_memory(self, **kwargs) -> Dict[str, Any]:
        """
        Store a new memory.
        
        Args:
            memory_type (str): Type of memory (e.g., 'code_insight', 'user_preference', 'problem_solution')
            content (str|dict): Memory content
            title (str, optional): Short title for the memory
            importance (float, optional): Importance score (0.0 to 1.0), default 0.5
            emotional_context (dict, optional): Emotional context data
            tags (list, optional): List of tags for categorization
            expires_in_days (int, optional): Auto-delete after this many days
        
        Returns:
            Dictionary with memory ID and metadata
        """
        try:
            return self.memory_system.store_memory(**kwargs)
        except Exception as e:
            return {"success": False, "error": f"Failed to store memory: {e}"}
    
    def recall_memories(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Recall relevant memories based on query and filters.
        
        Args:
            query (str, optional): Text query for semantic search
            memory_type (str, optional): Filter by memory type
            project_id (str, optional): Filter by project (defaults to current)
            importance_threshold (float, optional): Minimum importance score, default 0.0
            limit (int, optional): Maximum number of memories to return, default 10
            include_other_projects (bool, optional): Include memories from other projects, default False
        
        Returns:
            List of matching memories
        """
        try:
            return self.memory_system.recall_memories(**kwargs)
        except Exception as e:
            return [{"error": f"Failed to recall memories: {e}"}]
    
    def update_memory(self, memory_id: int, **kwargs) -> Dict[str, Any]:
        """
        Update an existing memory.
        
        Args:
            memory_id (int): ID of the memory to update
            content (str|dict, optional): New memory content
            title (str, optional): New title
            importance (float, optional): New importance score
            emotional_context (dict, optional): New emotional context
            add_tags (list, optional): Tags to add
        
        Returns:
            Dictionary with update status
        """
        try:
            if hasattr(self.memory_system, 'update_memory'):
                return self.memory_system.update_memory(memory_id, **kwargs)
            else:
                return {"success": False, "error": "Update not supported in fallback mode"}
        except Exception as e:
            return {"success": False, "error": f"Failed to update memory: {e}"}
    
    def reflect_on_interaction(self, **kwargs) -> Dict[str, Any]:
        """
        Store an emotional reflection about an interaction.
        
        Args:
            reflection_type (str): Type of reflection (e.g., 'collaboration', 'problem_solving', 'learning')
            content (dict): Reflection content with structured data
            mood_score (float, optional): Emotional state score (-1.0 to 1.0, negative to positive)
        
        Returns:
            Dictionary with reflection ID and metadata
        """
        try:
            return self.memory_system.reflect_on_interaction(**kwargs)
        except Exception as e:
            return {"success": False, "error": f"Failed to store reflection: {e}"}
    
    def get_emotional_insights(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Get emotional insights and patterns from recent interactions.
        
        Args:
            days_back (int): Number of days to look back, default 30
        
        Returns:
            Dictionary with emotional insights and patterns
        """
        try:
            if hasattr(self.memory_system, 'get_emotional_insights'):
                return self.memory_system.get_emotional_insights(days_back)
            else:
                return {"error": "Emotional insights not supported in fallback mode"}
        except Exception as e:
            return {"error": f"Failed to get emotional insights: {e}"}
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Get a summary of stored memories for the current project.
        
        Returns:
            Dictionary with memory statistics and overview
        """
        try:
            return self.memory_system.get_memory_summary()
        except Exception as e:
            return {"error": f"Failed to get memory summary: {e}"}
    
    def cleanup_expired_memories(self) -> Dict[str, Any]:
        """
        Remove expired memories from the database.
        
        Returns:
            Dictionary with cleanup results
        """
        try:
            if hasattr(self.memory_system, 'cleanup_expired_memories'):
                return self.memory_system.cleanup_expired_memories()
            else:
                return {"success": True, "deleted_count": 0, "note": "Cleanup not needed in fallback mode"}
        except Exception as e:
            return {"success": False, "error": f"Failed to cleanup memories: {e}"}
    
    def get_project_context(self) -> Dict[str, Any]:
        """
        Get context about the current project and memory system state.
        
        Returns:
            Dictionary with project and memory system information
        """
        try:
            return {
                "project_root": self.memory_system.project_root,
                "project_id": self.memory_system.current_project_id,
                "session_id": self.memory_system.session_id,
                "storage_available": self.memory_system.connection_pool is not None,
                "storage_type": "postgresql" if self.memory_system.connection_pool else "fallback",
                "fallback_memory_count": len(self.memory_system.fallback_storage)
            }
        except Exception as e:
            return {"error": f"Failed to get project context: {e}"}


# Tool function implementations for MCP server integration
def create_memory_tools(project_root: str) -> Dict[str, Any]:
    """
    Create memory tool functions for MCP server integration.
    
    Returns:
        Dictionary of tool functions ready for MCP server use
    """
    memory_tool = MemoryMCPTool(project_root)
    
    async def _store_memory(**kwargs):
        """Store a new memory."""
        return memory_tool.store_memory(**kwargs)
    
    async def _recall_memories(**kwargs):
        """Recall relevant memories."""
        return memory_tool.recall_memories(**kwargs)
    
    async def _update_memory(**kwargs):
        """Update an existing memory."""
        return memory_tool.update_memory(**kwargs)
    
    async def _reflect_on_interaction(**kwargs):
        """Store an emotional reflection."""
        return memory_tool.reflect_on_interaction(**kwargs)
    
    async def _get_emotional_insights(**kwargs):
        """Get emotional insights."""
        return memory_tool.get_emotional_insights(**kwargs)
    
    async def _get_memory_summary(**kwargs):
        """Get memory summary."""
        return memory_tool.get_memory_summary(**kwargs)
    
    async def _cleanup_expired_memories(**kwargs):
        """Cleanup expired memories."""
        return memory_tool.cleanup_expired_memories(**kwargs)
    
    async def _get_project_context(**kwargs):
        """Get project context."""
        return memory_tool.get_project_context(**kwargs)
    
    return {
        "store_memory": _store_memory,
        "recall_memories": _recall_memories,
        "update_memory": _update_memory,
        "reflect_on_interaction": _reflect_on_interaction,
        "get_emotional_insights": _get_emotional_insights,
        "get_memory_summary": _get_memory_summary,
        "cleanup_expired_memories": _cleanup_expired_memories,
        "get_project_context": _get_project_context,
    }
