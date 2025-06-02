#!/usr/bin/env python3
"""Test semantic search against the project with embeddings"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from memory_system import MemorySystem

def test_semantic_search():
    print("Testing semantic search against biting-lip project...")
    
    # Initialize memory system
    memory_system = MemorySystem()
    
    # Test semantic search against the project with embeddings
    print("\n=== Testing semantic search (biting-lip project) ===")
    results = memory_system.recall_memories(
        query="debug logging test", 
        project_id="biting-lip",  # Use the project with embeddings
        limit=5
    )
    
    print(f"Results: {len(results)} memories found")
    for i, memory in enumerate(results):
        content = memory.get('content', {})
        if isinstance(content, dict):
            content_text = content.get('text', str(content))
        else:
            content_text = str(content)
        
        print(f"{i+1}. {memory.get('title', 'No title')}")
        print(f"   Content: {content_text[:150]}...")
        print(f"   Type: {memory.get('memory_type', 'unknown')}")
        if 'relevance_score' in memory:
            print(f"   Relevance: {memory['relevance_score']:.4f}")
        print()
    
    # Also test a different query
    print("\n=== Testing different query ===")
    results2 = memory_system.recall_memories(
        query="memory system", 
        project_id="biting-lip",
        limit=3
    )
    
    print(f"Results for 'memory system': {len(results2)} memories found")
    for i, memory in enumerate(results2):
        if 'relevance_score' in memory:
            print(f"{i+1}. Relevance: {memory['relevance_score']:.4f} - {memory.get('title', 'No title')}")

if __name__ == "__main__":
    test_semantic_search()
