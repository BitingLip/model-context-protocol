#!/usr/bin/env python3
"""
Demo script showcasing the Tier 2 development workflow tools.
"""

import sys
import os
import asyncio
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from server import BitingLipMCPServer


async def demo_tier2_tools():
    """Demonstrate the new Tier 2 development workflow tools."""
    print("=" * 70)
    print("BITING LIP MCP SERVER - TIER 2 TOOLS DEMONSTRATION")
    print("=" * 70)
    
    server = BitingLipMCPServer()
    
    # Docker Analysis Demo
    print("\n🐳 DOCKER ANALYSIS")
    print("-" * 50)
    
    try:
        docker_result = await server.handle_call_tool("get_docker_info", {})
        docker_data = json.loads(docker_result["content"][0]["text"])
        
        print(f"Docker Available: {docker_data.get('docker_available', 'Unknown')}")
        print(f"Containers Found: {len(docker_data.get('containers', []))}")
        print(f"Images Found: {len(docker_data.get('images', []))}")
        print(f"Compose Files: {len(docker_data.get('compose_files', []))}")
        print(f"Dockerfiles: {len(docker_data.get('dockerfiles', []))}")
        
        if docker_data.get('compose_files'):
            print("\nCompose Files:")
            for compose in docker_data['compose_files'][:3]:
                print(f"  📄 {compose.get('relative_path', 'Unknown')}")
                if compose.get('services'):
                    print(f"     Services: {', '.join(compose['services'].keys())}")
    except Exception as e:
        print(f"❌ Docker analysis failed: {e}")
    
    # Test File Mapping Demo
    print("\n🧪 TEST FILE MAPPING")
    print("-" * 50)
    
    try:
        test_result = await server.handle_call_tool("find_test_files", {})
        test_data = json.loads(test_result["content"][0]["text"])
        
        print(f"Total Test Files: {test_data.get('total_test_files', 0)}")
        print(f"Test Directories: {test_data.get('test_directories', 0)}")
        
        if test_data.get('test_files'):
            print("\nSample Test Files:")
            for test_file in test_data['test_files'][:5]:
                print(f"  🧪 {test_file.get('relative_path', 'Unknown')}")
                if test_file.get('test_functions'):
                    print(f"     Functions: {len(test_file['test_functions'])}")
        
        # Test with specific file
        print("\n   Testing specific file mapping...")
        specific_result = await server.handle_call_tool("find_test_files", {"target_file": "src/server.py"})
        specific_data = json.loads(specific_result["content"][0]["text"])
        print(f"   Tests for server.py: {specific_data.get('total_tests_found', 0)}")
    except Exception as e:
        print(f"❌ Test mapping failed: {e}")
    
    # Dependency Analysis Demo
    print("\n📦 DEPENDENCY ANALYSIS")
    print("-" * 50)
    
    try:
        # Python dependencies
        dep_result = await server.handle_call_tool("analyze_dependencies", {"analysis_type": "python"})
        dep_data = json.loads(dep_result["content"][0]["text"])
        
        print(f"Python Packages: {len(dep_data.get('packages', {}))}")
        print(f"Requirement Files: {len(dep_data.get('requirement_files', []))}")
        print(f"Conflicts Found: {len(dep_data.get('conflicts', []))}")
        print(f"Missing Packages: {len(dep_data.get('missing_packages', []))}")
        
        # System dependencies
        sys_result = await server.handle_call_tool("analyze_dependencies", {"analysis_type": "system"})
        sys_data = json.loads(sys_result["content"][0]["text"])
        
        print("\nSystem Dependencies:")
        for tool, info in sys_data.items():
            if isinstance(info, dict):
                status = "✅" if info.get('available') else "❌"
                version = info.get('version', 'N/A')
                print(f"  {status} {tool.capitalize()}: {version}")
    except Exception as e:
        print(f"❌ Dependency analysis failed: {e}")
    
    # Git Analysis Demo
    print("\n🔄 GIT REPOSITORY ANALYSIS")
    print("-" * 50)
    
    try:
        git_result = await server.handle_call_tool("get_git_info", {"info_type": "all"})
        git_data = json.loads(git_result["content"][0]["text"])
        
        if git_data.get('error'):
            print(f"❌ {git_data['error']}")
        else:
            print(f"Git Repository: ✅")
            if git_data.get('summary'):
                summary = git_data['summary']
                print(f"Current Branch: {summary.get('current_branch', 'Unknown')}")
                print(f"Total Branches: {summary.get('total_branches', 0)}")
                print(f"Modified Files: {summary.get('modified_files', 0)}")
                print(f"Untracked Files: {summary.get('untracked_files', 0)}")
                print(f"Has Remote: {'✅' if summary.get('has_remote') else '❌'}")
                
            if git_data.get('recent_commits'):
                commits = git_data['recent_commits'].get('commits', [])
                if commits:
                    print(f"\nRecent Commits ({len(commits)}):")
                    for commit in commits[:3]:
                        print(f"  📝 {commit.get('hash', 'Unknown')}: {commit.get('message', 'No message')[:50]}...")
    except Exception as e:
        print(f"❌ Git analysis failed: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("TIER 2 TOOLS DEMONSTRATION COMPLETE")
    print("=" * 70)
    
    tools_info = await server.handle_list_tools()
    total_tools = len(tools_info["tools"])
    tier1_tools = 9  # First 9 tools are Tier 1
    tier2_tools = total_tools - tier1_tools
    
    print(f"📊 Total Tools Available: {total_tools}")
    print(f"   🔧 Tier 1 (Core Analysis): {tier1_tools}")
    print(f"   🚀 Tier 2 (Development Workflow): {tier2_tools}")
    print("\n✨ The Biting Lip MCP Server is ready for advanced AI agent workflows!")


if __name__ == "__main__":
    asyncio.run(demo_tier2_tools())
