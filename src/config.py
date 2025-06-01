"""
Configuration for AI-powered development tools.

This module contains configuration settings for the Tier 3 AI tools
that integrate with local Ollama LLM instances.
"""

# Ollama Configuration for AI Development Tools
OLLAMA_CONFIG = {
    "url": "http://localhost:11434",
    "model": "deepseek-r1:8b",  # Default model, can be changed to devstral or other models
    "timeout": 30,
    "fallback_model": "devstral:latest",
    "models": {
        "code_optimization": "deepseek-r1:8b",
        "refactoring": "devstral:latest", 
        "test_generation": "deepseek-r1:8b",
        "documentation": "devstral:latest",
        "code_review": "deepseek-r1:8b"
    }
}

# VS Code Integration Settings
VSCODE_CONFIG = {
    "problems_panel_integration": True,
    "sourcery_integration": True,
    "auto_fix_suggestions": False,  # Whether to auto-apply safe fixes
    "notification_level": "info"  # none, error, warning, info, verbose
}

# AI Tool Behavior Settings
AI_TOOL_CONFIG = {
    "max_file_size": 100000,  # Maximum file size to process (bytes)
    "max_complexity": 50,     # Maximum cyclomatic complexity to analyze
    "confidence_threshold": 0.7,  # Minimum confidence for suggestions
    "cache_results": True,    # Cache AI responses for performance
    "cache_ttl": 3600        # Cache time-to-live in seconds
}
