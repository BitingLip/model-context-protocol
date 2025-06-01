#!/usr/bin/env python3
"""
Store memory about the loop issue investigation
"""
import os
import sys
from pathlib import Path

# Add the src directory to the path
script_dir = Path(__file__).parent
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

from tools.memory_system_fixed import MemorySystem

def store_loop_investigation():
    """Store findings about the loop issue."""
    print("🔍 Storing Loop Investigation Findings...")
    
    # Set up environment
    os.environ.setdefault('MEMORY_DB_USER', 'postgres')
    os.environ.setdefault('MEMORY_DB_PASSWORD', 'postgres')
    
    # Initialize memory system
    project_root = str(Path(__file__).parent.parent.parent)
    memory = MemorySystem(project_root)
    
    # Store the loop investigation findings
    memory.store_memory(
        memory_type="debugging_insight",
        content={
            "issue": "get_project_overview tool causing infinite loops",
            "investigation_findings": [
                "Method found in src/tools/code_analysis.py line 112",
                "get_project_overview() analyzes Python files and creates comprehensive overview",
                "Potential issue: inconsistent indentation at line 125 could cause parsing errors",
                "Method calls analyze_python_file() for each Python file found",
                "Returns dictionary with total_python_files, files, total_classes, total_functions, modules",
                "User temporarily disabled custom MCP tools to stop loops"
            ],
            "next_steps": [
                "Test get_project_overview directly to see response format",
                "Check if response format causes MCP loop",
                "Fix any indentation issues in code_analysis.py",
                "Re-enable MCP tools once fixed"
            ],
            "current_status": "Memory system working, investigating original loop cause"
        },
        title="Loop Investigation - get_project_overview",
        importance=0.9,
        emotional_context={
            "detective_work": "methodical investigation",
            "progress": "significant - memory system implemented"
        },
        tags=["debugging", "loops", "get_project_overview", "code_analysis", "mcp_tools"]
    )
    
    print("✅ Loop investigation findings stored in memory")
    
    # Recall what we know about loops
    print("\n🧠 Recalling what we know about loops...")
    loop_memories = memory.recall_memories(
        memory_type="debugging_insight",
        limit=5
    )
    
    for mem in loop_memories:
        print(f"   📝 {mem['title']}")
        print(f"      Investigation: {len(mem['content']['investigation_findings'])} findings")
    
    print(f"\n💾 Total memories about this collaboration: {memory.get_memory_summary()['total_memories']}")

if __name__ == "__main__":
    store_loop_investigation()
