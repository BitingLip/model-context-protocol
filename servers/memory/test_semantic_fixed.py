#!/usr/bin/env python3
"""Test semantic search with fixed parameter ordering"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from memory_system import MemorySystem

def test_semantic_search():
    print("Testing semantic search with fixed parameter ordering...")
    
    # Initialize memory system
    memory_system = MemorySystem()
    
    # Test semantic search
    print("\n=== Testing semantic search ===")
    results = memory_system.recall_memories(query="debug logging test", limit=3)
    
    print(f"Results: {len(results)} memories found")
    for i, memory in enumerate(results):
        print(f"{i+1}. {memory.get('title', 'No title')}: {memory.get('content', '')[:100]}...")
        if 'relevance_score' in memory:
            print(f"   Relevance: {memory['relevance_score']:.4f}")
    
    # Test no query (should work)
    print("\n=== Testing basic recall (no query) ===")
    basic_results = memory_system.recall_memories(limit=3)
    print(f"Basic results: {len(basic_results)} memories found")

if __name__ == "__main__":
    test_semantic_search()
