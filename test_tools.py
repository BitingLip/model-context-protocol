#!/usr/bin/env python3
"""
Test script for the Biting Lip MCP tools.
"""

import sys
import os

# Add the tools directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'tools'))

from project_tree import ProjectTreeGenerator, generate_project_tree
from code_analysis import CodeAnalyzer


def test_project_tree():
    """Test the project tree generator."""
    print("=" * 60)
    print("TESTING PROJECT TREE GENERATOR")
    print("=" * 60)
    
    # Test with the current MCP directory
    mcp_dir = os.path.dirname(__file__)
    
    print(f"Generating tree for: {mcp_dir}")
    print("-" * 40)
    
    # Test basic generation
    tree = generate_project_tree(mcp_dir)
    print(tree)
    
    print("\n" + "-" * 40)
    print("Testing with max depth = 2")
    print("-" * 40)
    
    # Test with max depth
    tree_limited = generate_project_tree(mcp_dir, max_depth=2)
    print(tree_limited)
    
    print("\n" + "-" * 40)
    print("Testing with ignore patterns")
    print("-" * 40)
    
    # Test with ignore patterns
    tree_filtered = generate_project_tree(mcp_dir, ignore_patterns=['*.pyc', '__pycache__'])
    print(tree_filtered)


def test_code_analyzer():
    """Test the code analyzer."""
    print("\n" + "=" * 60)
    print("TESTING CODE ANALYZER")
    print("=" * 60)
    
    # Test with the current MCP directory
    mcp_dir = os.path.dirname(__file__)
    analyzer = CodeAnalyzer(mcp_dir)
    
    print(f"Analyzing code in: {mcp_dir}")
    print("-" * 40)
    
    # Find Python files
    python_files = analyzer.find_python_files()
    print(f"Found {len(python_files)} Python files:")
    for file in python_files:
        print(f"  - {os.path.relpath(file, mcp_dir)}")
    
    print("\n" + "-" * 40)
    print("Project Overview:")
    print("-" * 40)
    
    # Get project overview
    overview = analyzer.get_project_overview()
    print(f"Total Python files: {overview['total_python_files']}")
    print(f"Total classes: {overview['total_classes']}")
    print(f"Total functions: {overview['total_functions']}")
    print(f"Modules: {list(overview['modules'].keys())}")
    
    # Analyze first Python file if any exist
    if python_files:
        print(f"\n" + "-" * 40)
        print(f"Detailed analysis of: {os.path.basename(python_files[0])}")
        print("-" * 40)
        
        analysis = analyzer.analyze_python_file(python_files[0])
        if 'error' not in analysis:
            print(f"Classes: {[c['name'] for c in analysis['classes']]}")
            print(f"Functions: {[f['name'] for f in analysis['functions']]}")
            print(f"Imports: {len(analysis['imports'])}")
            print(f"Constants: {[c['name'] for c in analysis['constants']]}")
            if analysis['docstring']:
                print(f"Module docstring: {analysis['docstring'][:100]}...")
        else:
            print(f"Error: {analysis['error']}")
    
    print("\n" + "-" * 40)
    print("Search test - looking for 'class':")
    print("-" * 40)
    
    # Test search functionality
    search_results = analyzer.search_code('class')
    print(f"Found {len(search_results)} matches")
    for i, result in enumerate(search_results[:3]):  # Show first 3 results
        rel_path = os.path.relpath(result['file'], mcp_dir)
        print(f"  {i+1}. {rel_path}:{result['line_number']} - {result['line_content']}")


if __name__ == "__main__":
    try:
        test_project_tree()
        test_code_analyzer()
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
