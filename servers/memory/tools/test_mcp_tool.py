#!/usr/bin/env python3
"""
Test MCP Tool with Modular Memory System
"""

def test_mcp_tool():
    """Test the MCP tool with the refactored memory system."""
    try:
        print("Testing MCP Tool with modular memory system...")
        
        # Test importing the memory package
        from memory import MemorySystem
        print("✓ Memory package imported successfully")
        
        # Test importing the MCP tool
        from memory_mcp_tool import MemoryMCPTool
        print("✓ MCP Tool imported successfully")
        
        # Test initializing the MCP tool
        tool = MemoryMCPTool(".")
        print("✓ MCP Tool initialized successfully")
        
        # Test basic operations
        result = tool.store_memory(
            memory_type="test",
            content="Test memory for MCP tool",
            title="MCP Test",
            importance=0.7
        )
        print(f"✓ Store memory result: {result}")
        
        # Test recall
        memories = tool.recall_memories(query="test", limit=5)
        print(f"✓ Recall memories result: {len(memories)} memories found")        # Test get stats  
        stats = tool.get_project_context()
        print(f"✓ Project context: {list(stats.keys())}")
        
        print("\n🎉 All MCP Tool tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_mcp_tool()
