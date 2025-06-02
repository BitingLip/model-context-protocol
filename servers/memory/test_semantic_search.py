#!/usr/bin/env python3
"""
Test script to verify semantic search functionality with the custom pgvector adapter.
"""

import sys
import os
from pathlib import Path

# Add the tools directory to the path
sys.path.insert(0, str(Path(__file__).parent / "tools"))

from memory_system import MemorySystem

def test_semantic_search():
    """Test semantic search functionality."""
    print("Testing semantic search with custom pgvector adapter...")
    
    # Initialize memory system
    memory_system = MemorySystem()
    print(f"Memory system initialized. Embedding model available: {memory_system.embedding_model is not None}")
    print(f"PostgreSQL available: {memory_system.connection_pool is not None}")
    
    if not memory_system.connection_pool:
        print("ERROR: No database connection available")
        return False
    
    if not memory_system.embedding_model:
        print("ERROR: No embedding model available")
        return False
    
    # Test 1: Basic recall without query (should work)
    print("\n=== Test 1: Basic recall without query ===")
    basic_memories = memory_system.recall_memories(limit=3)
    print(f"Basic recall returned {len(basic_memories)} memories")
    for i, mem in enumerate(basic_memories[:2]):  # Show first 2
        print(f"  {i+1}. {mem.get('title', 'No title')}: {mem.get('memory_type', 'Unknown type')}")
    
    # Test 2: Semantic search with query (this should now work with the adapter)
    print("\n=== Test 2: Semantic search with query ===")
    test_queries = ["debug logging test", "task management", "configuration"]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        semantic_memories = memory_system.recall_memories(query=query, limit=3)
        print(f"Semantic search returned {len(semantic_memories)} memories")
        
        for i, mem in enumerate(semantic_memories):
            relevance = mem.get('relevance_score', 'N/A')
            print(f"  {i+1}. {mem.get('title', 'No title')} (relevance: {relevance})")
            print(f"     Type: {mem.get('memory_type', 'Unknown')}")
        
        if len(semantic_memories) > 0 and 'relevance_score' in semantic_memories[0]:
            print(f"✅ Semantic search working! Found {len(semantic_memories)} memories with relevance scores")
            return True
        elif len(semantic_memories) > 0:
            print(f"⚠️  Found memories but no relevance scores - may be using text fallback")
        else:
            print(f"❌ No memories found for query: '{query}'")
    
    return False

if __name__ == "__main__":
    success = test_semantic_search()
    if success:
        print("\n🎉 SUCCESS: Semantic search is working with the custom pgvector adapter!")
    else:
        print("\n❌ FAILED: Semantic search is not working properly")
    
    sys.exit(0 if success else 1)
