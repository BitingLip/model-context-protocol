#!/usr/bin/env python3
"""
Simple test to update embeddings for existing memories using the enhanced memory system.
"""

import sys
import os

# Add the memory server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tools.memory_system import MemorySystem
    
    print("🚀 Initializing enhanced memory system...")
    memory_system = MemorySystem()
    
    if memory_system.embedding_model is None:
        print("❌ Embedding model not available")
        sys.exit(1)
    
    print(f"✅ Embedding model loaded: {memory_system.embedding_dim}D")
    
    print("\n📝 Updating embeddings for existing memories...")
    result = memory_system.update_embeddings_for_existing_memories()
    
    print(f"✅ Embedding update complete!")
    print(f"   - Processed: {result['processed']}")
    print(f"   - Updated: {result['updated']}")
    print(f"   - Skipped: {result['skipped']}")
    print(f"   - Errors: {result['errors']}")
    
    # Test semantic search
    print(f"\n🔍 Testing semantic search...")
    
    test_query = "task manager database integration postgresql"
    memories = memory_system.recall_memories(query=test_query, limit=3)
    
    print(f"Query: '{test_query}'")
    print(f"Found {len(memories)} memories:")
    
    for i, memory in enumerate(memories, 1):
        title = memory.get('title', 'No title')
        mem_type = memory.get('memory_type', 'Unknown')
        relevance = memory.get('relevance_score', 'N/A')
        
        print(f"  {i}. [{mem_type}] {title}")
        print(f"     Relevance: {relevance}")
    
    print("\n🎉 Enhanced memory system test completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("The enhanced memory system may need dependency installation")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
