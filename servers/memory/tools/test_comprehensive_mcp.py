#!/usr/bin/env python3
"""
Comprehensive MCP Tool Test with Modular Memory System
"""

def comprehensive_mcp_test():
    """Comprehensive test of MCP tool with all features."""
    print("🚀 Comprehensive MCP Tool Test with Modular Memory System\n")
    
    try:
        from memory_mcp_tool import MemoryMCPTool
        
        # Initialize tool
        tool = MemoryMCPTool(".")
        print("✓ MCP Tool initialized successfully")
        
        # Test 1: Store different types of memories
        print("\n📝 Test 1: Storing different memory types")
        
        # Store a code insight
        result1 = tool.store_memory(
            memory_type="code_insight",
            content="Successfully refactored monolithic memory system into modular architecture",
            title="Memory System Refactoring",
            importance=0.9,
            tags=["refactoring", "architecture", "memory"],
            emotional_context={"satisfaction": 0.8, "accomplishment": 0.9}
        )
        print(f"  ✓ Code insight stored: {result1.get('memory_id')}")
        
        # Store a user preference
        result2 = tool.store_memory(
            memory_type="user_preference",
            content={"preferred_style": "modular", "focus": "maintainability"},
            title="User Coding Preferences",
            importance=0.7,
            tags=["preferences", "coding"]
        )
        print(f"  ✓ User preference stored: {result2.get('memory_id')}")
        
        # Test 2: Recall memories with different methods
        print("\n🔍 Test 2: Memory recall tests")
        
        # Semantic search
        semantic_results = tool.recall_memories(
            query="refactoring modular architecture",
            limit=5
        )
        print(f"  ✓ Semantic search found: {len(semantic_results)} memories")
        
        # Type-based search
        code_memories = tool.recall_memories(
            memory_type="code_insight",
            limit=5
        )
        print(f"  ✓ Code insights found: {len(code_memories)} memories")
        
        # Weighted recall
        weighted_results = tool.recall_memories_weighted(
            query="memory system",
            importance_weight=0.5,
            recency_weight=0.3,
            relevance_weight=0.2,
            limit=3
        )
        print(f"  ✓ Weighted recall found: {len(weighted_results)} memories")
        
        # Test 3: Advanced features
        print("\n🧠 Test 3: Advanced memory features")
        
        # Memory summary
        summary = tool.get_memory_summary()
        print(f"  ✓ Memory summary: {summary.get('total_memories', 0)} total memories")
        
        # Emotional insights
        emotional = tool.get_emotional_insights(days_back=7)
        print(f"  ✓ Emotional insights: {len(emotional.get('insights', []))} insights")
        
        # Project context
        context = tool.get_project_context()
        print(f"  ✓ Project context: {context.get('project_id', 'unknown')}")
        
        # Test 4: System maintenance
        print("\n🔧 Test 4: System maintenance")
        
        # Update embeddings
        update_result = tool.update_embeddings_for_existing_memories(
            batch_size=10,
            force_update=False
        )
        print(f"  ✓ Embedding update: {update_result.get('updated_count', 0)} memories updated")
        
        # Cleanup expired memories
        cleanup_result = tool.cleanup_expired_memories()
        print(f"  ✓ Cleanup: {cleanup_result.get('deleted_count', 0)} expired memories removed")
        
        print("\n🎉 Comprehensive MCP Tool test completed successfully!")
        print(f"Total memories in system: {summary.get('total_memories', 0)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    comprehensive_mcp_test()
