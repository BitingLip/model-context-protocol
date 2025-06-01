#!/usr/bin/env python3
"""
Demo script for Tier 3 AI-powered development tools in the Biting Lip MCP server.

This script demonstrates the capabilities of the new AI tools that leverage 
local Ollama LLMs for:
- Code optimization (VS Code problems panel integration)
- Smart refactoring suggestions 
- Test generation
- Documentation writing
- Code review assistance

Prerequisites:
- Ollama running locally with models like deepseek-r1:8b or devstral
- Python 3.8+
- Dependencies from requirements.txt
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the src directory to the path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from tools.ai_code_optimizer import AICodeOptimizer
from tools.ai_smart_refactorer import AISmartRefactorer
from tools.ai_test_generator import AITestGenerator
from tools.ai_documentation_writer import AIDocumentationWriter
from tools.ai_code_review_assistant import AICodeReviewAssistant


def print_section(title: str, content: str = None):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    if content:
        print(content)


def print_result(result: dict, truncate: bool = True):
    """Print a formatted result."""
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    if "success" in result and result["success"]:
        print("✅ Success!")
    
    # Print key information
    if "ai_model" in result:
        print(f"🤖 AI Model: {result['ai_model']}")
    
    if "metadata" in result:
        metadata = result["metadata"]
        for key, value in metadata.items():
            if isinstance(value, (int, float, str, bool)):
                print(f"📊 {key}: {value}")
    
    # Print results (truncated for readability)
    result_copy = result.copy()
    if truncate:
        # Remove large content fields for demo
        for key in ["generated_docs", "test_file_content", "optimization_suggestions"]:
            if key in result_copy:
                content = result_copy[key]
                if isinstance(content, str) and len(content) > 200:
                    result_copy[key] = content[:200] + "... [truncated]"
                elif isinstance(content, dict):
                    for subkey, subcontent in content.items():
                        if isinstance(subcontent, str) and len(subcontent) > 200:
                            content[subkey] = subcontent[:200] + "... [truncated]"
    
    print("\n📋 Result Summary:")
    print(json.dumps(result_copy, indent=2))


async def demo_ai_code_optimizer():
    """Demo the AI Code Optimizer tool."""
    print_section("🔧 AI Code Optimizer", 
                 "Integrates with VS Code problems panel and Sourcery suggestions")
    
    project_root = str(Path(__file__).parent.parent.parent.parent)
    optimizer = AICodeOptimizer(project_root)
    
    # Use this demo file as an example
    demo_file = __file__
    
    # Demo with mock problems (simulating VS Code diagnostics)
    mock_problems = [
        {
            "severity": "warning",
            "message": "Line too long (85 > 79 characters)",
            "line": 25,
            "source": "flake8"
        },
        {
            "severity": "info", 
            "message": "Use f-string instead of string concatenation",
            "line": 45,
            "source": "sourcery"
        }
    ]
    
    print(f"🔍 Analyzing file: {demo_file}")
    print(f"📋 Mock problems: {len(mock_problems)} issues detected")
    
    result = optimizer.optimize_code(demo_file, mock_problems)
    print_result(result)


async def demo_ai_smart_refactorer():
    """Demo the AI Smart Refactorer tool."""
    print_section("🔄 AI Smart Refactorer",
                 "Intelligent code refactoring suggestions using AST analysis")
    
    project_root = str(Path(__file__).parent.parent.parent.parent)
    refactorer = AISmartRefactorer(project_root)
    
    # Use this demo file as an example
    demo_file = __file__
    
    print(f"🔍 Analyzing file: {demo_file}")
    print("🎯 Scope: file-level analysis")
    
    result = refactorer.analyze_refactoring_opportunities(demo_file, "file")
    print_result(result)


async def demo_ai_test_generator():
    """Demo the AI Test Generator tool."""
    print_section("🧪 AI Test Generator",
                 "Automatic test generation with pytest fixtures and mocks")
    
    test_generator = AITestGenerator()
    
    # Use this demo file as an example
    demo_file = __file__
    
    print(f"🔍 Generating tests for: {demo_file}")
    print("📋 Test types: unit, integration, edge cases, error conditions")
    
    result = await test_generator.generate_tests(
        demo_file,
        test_types=["unit", "edge", "error"],
        coverage_target=0.8,
        include_fixtures=True,
        include_mocks=True
    )
    print_result(result)


async def demo_ai_documentation_writer():
    """Demo the AI Documentation Writer tool."""
    print_section("📚 AI Documentation Writer",
                 "Comprehensive documentation generation including docstrings, README, API docs")
    
    doc_writer = AIDocumentationWriter()
    
    # Use this demo file as an example
    demo_file = __file__
    
    print(f"🔍 Generating documentation for: {demo_file}")
    print("📋 Doc types: docstrings, README, API documentation")
    
    result = await doc_writer.write_docs(
        demo_file,
        doc_types=["docstrings", "readme", "api"],
        style="google",
        include_examples=True,
        include_type_hints=True
    )
    print_result(result)


async def demo_ai_code_review_assistant():
    """Demo the AI Code Review Assistant tool."""
    print_section("👀 AI Code Review Assistant",
                 "Comprehensive code review with security, quality, style, and performance analysis")
    
    reviewer = AICodeReviewAssistant()
    
    print("🔍 Performing code review on recent changes")
    print("📋 Review types: quality, security, style, performance")
    
    # Demo with file-based review (since we might not have git changes)
    demo_file = __file__
    
    result = await reviewer.review_code(
        file_paths=[demo_file],
        review_types=["quality", "security", "style", "performance"],
        severity_threshold="low"
    )
    print_result(result)


def check_ollama_availability():
    """Check if Ollama is available."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama is running with {len(models)} models available")
            for model in models[:3]:  # Show first 3 models
                print(f"   - {model.get('name', 'Unknown')}")
            if len(models) > 3:
                print(f"   ... and {len(models) - 3} more")
            return True
        else:
            print("❌ Ollama is running but API is not responding properly")
            return False
    except Exception as e:
        print(f"❌ Ollama is not available: {e}")
        print("Please start Ollama with: ollama serve")
        print("And ensure you have models like: ollama pull deepseek-r1:8b")
        return False


async def main():
    """Run the comprehensive demo of Tier 3 AI tools."""
    print_section("🚀 Biting Lip MCP Server - Tier 3 AI Tools Demo",
                 "Leveraging local Ollama LLMs for AI-assisted development")
    
    # Check prerequisites
    print_section("🔧 Prerequisites Check")
    
    ollama_available = check_ollama_availability()
    
    if not ollama_available:
        print("\n⚠️  Warning: Ollama is not available. The demo will show the tool interfaces")
        print("but AI-generated content will be mock responses.")
        input("\nPress Enter to continue with the demo...")
    
    # Run all demos
    demos = [
        ("🔧 AI Code Optimizer", demo_ai_code_optimizer),
        ("🔄 AI Smart Refactorer", demo_ai_smart_refactorer),
        ("🧪 AI Test Generator", demo_ai_test_generator),
        ("📚 AI Documentation Writer", demo_ai_documentation_writer),
        ("👀 AI Code Review Assistant", demo_ai_code_review_assistant),
    ]
    
    for demo_name, demo_func in demos:
        try:
            await demo_func()
            input(f"\n✅ {demo_name} demo completed. Press Enter to continue...")
        except Exception as e:
            print(f"❌ Error in {demo_name}: {e}")
            input("Press Enter to continue...")
    
    print_section("🎉 Demo Complete!",
                 """All Tier 3 AI tools have been demonstrated. These tools provide:

🔧 Code Optimization: VS Code problems panel integration with AI-powered fixes
🔄 Smart Refactoring: Intelligent code restructuring suggestions  
🧪 Test Generation: Automatic pytest test creation with fixtures and mocks
📚 Documentation: Comprehensive docs including docstrings, README, and API docs
👀 Code Review: Git diff analysis with security, quality, and style feedback

The MCP server now provides 18 total tools:
- 9 Tier 1 tools (project analysis, service discovery, etc.)
- 4 Tier 2 tools (Docker, git, dependencies, test mapping)
- 5 Tier 3 tools (AI-powered development assistance)

Next steps:
1. Ensure Ollama is running with appropriate models
2. Integrate with your VS Code workflow
3. Use with git hooks for automated code review
4. Customize AI models for specific use cases""")


if __name__ == "__main__":
    asyncio.run(main())
