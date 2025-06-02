#!/usr/bin/env python3
"""
Test script for enhanced memory system with semantic search capabilities.
"""

import sys
import os
import logging

# Add the memory server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.memory_system import MemorySystem

def test_memory_system():
    """Test the enhanced memory system functionality."""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting Enhanced Memory System Test")
    
    # Initialize memory system
    logger.info("Initializing memory system...")
    memory_system = MemorySystem()
    
    # Check connection
    if memory_system.connection_pool is None:
        logger.error("❌ Failed to connect to database")
        return False
    
    logger.info("✅ Successfully connected to memory database")
    
    # Check embedding model
    if memory_system.embedding_model is None:
        logger.warning("⚠️ Embedding model not loaded - semantic search unavailable")
        return False
    
    logger.info(f"✅ Embedding model loaded: {memory_system.embedding_dim}D embeddings")
    
    # Test 1: Update embeddings for existing memories
    logger.info("\n📝 Test 1: Updating embeddings for existing memories...")
    
    try:
        results = memory_system.update_embeddings_for_existing_memories()
        logger.info(f"✅ Updated embeddings for {results['updated']} memories")
        logger.info(f"   - Processed: {results['processed']}")
        logger.info(f"   - Skipped: {results['skipped']}")
        logger.info(f"   - Errors: {results['errors']}")
        
        if results['errors'] > 0:
            logger.warning("⚠️ Some errors occurred during embedding update")
        
    except Exception as e:
        logger.error(f"❌ Failed to update embeddings: {e}")
        return False
    
    # Test 2: Store a new memory with automatic embedding
    logger.info("\n📝 Test 2: Storing new memory with automatic embedding...")
    
    try:
        test_memory = {
            "memory_type": "test_semantic_search",
            "content": {
                "title": "Semantic Search Test",
                "description": "This is a test memory for semantic search functionality",
                "technical_details": "Using sentence-transformers with all-MiniLM-L6-v2 model",
                "performance": "Expected 28x improvement with pgvectorscale",
                "keywords": ["embedding", "vector", "similarity", "search", "AI", "memory"]
            },
            "importance": 0.8,
            "tags": ["test", "semantic_search", "embedding"]
        }
        
        memory_id = memory_system.store_memory(**test_memory)
        logger.info(f"✅ Stored test memory with ID: {memory_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to store test memory: {e}")
        return False
    
    # Test 3: Semantic search queries
    logger.info("\n📝 Test 3: Testing semantic search functionality...")
    
    test_queries = [
        "How do I improve memory performance?",
        "vector embeddings and similarity search",
        "AI memory storage techniques",
        "database optimization strategies",
        "pgvectorscale benefits"
    ]
    
    for i, query in enumerate(test_queries, 1):
        try:
            logger.info(f"\n🔍 Query {i}: '{query}'")
            
            # Semantic search
            memories = memory_system.recall_memories(query=query, limit=3)
            
            if memories:
                logger.info(f"   Found {len(memories)} relevant memories:")
                for j, memory in enumerate(memories, 1):
                    relevance = memory.get('relevance_score', 'N/A')
                    importance = memory.get('importance_score', 'N/A')
                    title = memory.get('title', 'No title')
                    mem_type = memory.get('memory_type', 'Unknown')
                    
                    logger.info(f"     {j}. [{mem_type}] {title}")
                    logger.info(f"        Relevance: {relevance}, Importance: {importance}")
            else:
                logger.info("   No memories found")
                
        except Exception as e:
            logger.error(f"❌ Query {i} failed: {e}")
    
    # Test 4: Compare with text search
    logger.info("\n📝 Test 4: Comparing semantic vs text search...")
    
    try:
        test_query = "memory optimization"
        
        # Force text search by temporarily disabling embedding model
        original_model = memory_system.embedding_model
        memory_system.embedding_model = None
        
        text_results = memory_system.recall_memories(query=test_query, limit=3)
        logger.info(f"   Text search found: {len(text_results)} memories")
        
        # Restore embedding model for semantic search
        memory_system.embedding_model = original_model
        
        semantic_results = memory_system.recall_memories(query=test_query, limit=3)
        logger.info(f"   Semantic search found: {len(semantic_results)} memories")
        
        if len(semantic_results) > 0 and len(text_results) > 0:
            logger.info("   Results comparison:")
            logger.info("     Semantic search (top result):")
            top_semantic = semantic_results[0]
            logger.info(f"       - {top_semantic.get('memory_type', 'N/A')}: {top_semantic.get('title', 'No title')}")
            logger.info(f"       - Relevance: {top_semantic.get('relevance_score', 'N/A')}")
            
            logger.info("     Text search (top result):")
            top_text = text_results[0]
            logger.info(f"       - {top_text.get('memory_type', 'N/A')}: {top_text.get('title', 'No title')}")
        
    except Exception as e:
        logger.error(f"❌ Comparison test failed: {e}")
    
    # Test 5: Weighted recall
    logger.info("\n📝 Test 5: Testing weighted memory recall...")
    
    try:
        weighted_results = memory_system.recall_memories_weighted(
            query="database performance optimization",
            limit=5,
            importance_weight=0.4,
            relevance_weight=0.4,
            recency_weight=0.2
        )
        
        logger.info(f"   Weighted search found: {len(weighted_results)} memories")
        for i, memory in enumerate(weighted_results, 1):
            title = memory.get('title', 'No title')
            weighted_score = memory.get('weighted_score', 'N/A')
            logger.info(f"     {i}. {title} (Score: {weighted_score})")
            
    except Exception as e:
        logger.error(f"❌ Weighted recall test failed: {e}")
    
    logger.info("\n🎉 Enhanced Memory System Test Complete!")
    logger.info("\n💡 Next Steps:")
    logger.info("   1. Install pgvectorscale for 28x performance improvement")
    logger.info("   2. Create optimized indices for large-scale deployment")
    logger.info("   3. Consider pgai integration for automated pipelines")
    
    return True

if __name__ == "__main__":
    success = test_memory_system()
    sys.exit(0 if success else 1)
