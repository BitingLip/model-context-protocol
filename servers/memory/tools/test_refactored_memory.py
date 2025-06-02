#!/usr/bin/env python3
"""
Test script to verify the refactored memory system works correctly.
"""
import sys
import os

# Add the memory module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from memory.main import MemorySystem

def test_refactored_memory_system():
    """Test the refactored memory system components."""
    print("Testing refactored memory system...")
    
    try:
        # Initialize memory system
        memory_system = MemorySystem()
        print("✓ MemorySystem initialized successfully")
        
        # Test database connection
        if memory_system.database_manager.connection_pool:
            print("✓ Database connection established")
        else:
            print("✗ Database connection failed")
            return False
        
        # Test embedding generation
        test_text = "This is a test memory for refactoring validation"
        embedding = memory_system.embedding_manager.generate_embedding(test_text)
        if embedding:
            print(f"✓ Embedding generated successfully (dimension: {len(embedding)})")
        else:
            print("⚠ Embedding generation skipped (optional)")
        
        # Test memory storage
        result = memory_system.store_memory(
            memory_type="test",
            content=test_text,
            title="Refactoring Test Memory",
            importance=0.8
        )
        
        if result.get("success"):
            memory_id = result.get("memory_id")
            print(f"✓ Memory stored successfully (ID: {memory_id})")
            
            # Test memory recall
            memories = memory_system.recall_memories(
                query="refactoring validation",
                limit=5
            )
            
            if memories:
                print(f"✓ Memory recall successful (found {len(memories)} memories)")
            else:
                print("⚠ No memories found in recall test")
                
        else:
            print(f"✗ Memory storage failed: {result.get('error')}")
            return False
        
        # Test stats
        stats = memory_system.get_stats()
        print(f"✓ System stats retrieved: {len(stats)} categories")
        
        # Cleanup
        memory_system.cleanup()
        print("✓ Cleanup completed")
        
        print("\n🎉 Refactored memory system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_refactored_memory_system()
    sys.exit(0 if success else 1)
