# Biting Lip MCP Server

Model Context Protocol (MCP) server providing handy tools for AI agents working with the Biting Lip AI platform.

## Overview

This MCP server provides a collection of tools designed to help AI agents understand and work with the Biting Lip project structure. It includes tools for:

**Tier 1 Tools (Core Analysis):**

- **Project Structure Analysis**: Generate visual tree representations of directories
- **Code Analysis**: Extract information from Python files including classes, functions, imports
- **Code Search**: Search for patterns across the codebase
- **File Discovery**: Find Python files and analyze project structure
- **Service Discovery**: Discover and analyze all services in the Biting Lip platform
- **Configuration Analysis**: Analyze configuration files and summarize project configuration

**Tier 2 Tools (Development Workflow):**

- **Docker Analysis**: Comprehensive Docker system analysis including containers, images, and Compose files
- **Test File Mapping**: Find and map test files to source files with intelligent matching
- **Dependency Analysis**: Analyze Python packages, system requirements, and internal module dependencies
- **Git Information**: Repository status, branch information, commit history, and remote configuration

**Tier 3 Tools (AI-Assisted Development):**

- **AI Code Optimization**: Local Ollama LLM-powered code optimization with VS Code problems panel integration
- **AI Smart Refactoring**: Intelligent refactoring suggestions using AST analysis and AI
- **AI Test Generation**: Automated test generation with pytest fixtures, mocks, and comprehensive scenarios
- **AI Documentation Writing**: Multi-format documentation generation (docstrings, README, API docs)
- **AI Code Review**: Comprehensive code review with security, quality, style, and performance analysis

Total: **18 powerful tools** for comprehensive project analysis, development workflow support, and AI-assisted development.

## Tools Available

### 1. `generate_project_tree`

Generate a visual tree structure of a project directory with optional filtering.

**Parameters:**

- `root_path` (required): Root directory path to analyze
- `ignore_patterns` (optional): Array of patterns to ignore (e.g., `["*.pyc", "__pycache__"]`)
- `max_depth` (optional): Maximum depth to traverse

**Example:**

```json
{
  "tool": "generate_project_tree",
  "arguments": {
    "root_path": "/path/to/project",
    "ignore_patterns": ["*.pyc", "__pycache__", ".git"],
    "max_depth": 3
  }
}
```

### 2. `analyze_python_file`

Analyze a Python file and extract classes, functions, imports, and constants.

**Parameters:**

- `file_path` (required): Path to the Python file to analyze

**Example:**

```json
{
  "tool": "analyze_python_file",
  "arguments": {
    "file_path": "/path/to/file.py"
  }
}
```

### 3. `get_project_overview`

Get a comprehensive overview of the Python project structure.

**Parameters:**

- `project_root` (optional): Root directory of the project

**Example:**

```json
{
  "tool": "get_project_overview",
  "arguments": {
    "project_root": "/path/to/project"
  }
}
```

### 4. `search_code`

Search for code patterns in the project.

**Parameters:**

- `query` (required): Search query string
- `file_type` (optional): File extension to search in (default: "py")
- `project_root` (optional): Root directory to search in

**Example:**

```json
{
  "tool": "search_code",
  "arguments": {
    "query": "class TaskManager",
    "file_type": "py"
  }
}
```

### 5. `find_python_files`

Find all Python files in a directory.

**Parameters:**

- `directory` (optional): Directory to search in

**Example:**

```json
{
  "tool": "find_python_files",
  "arguments": {
    "directory": "/path/to/search"
  }
}
```

### 6. `discover_services`

Discover and analyze all services in the Biting Lip platform including managers, interfaces, and their configurations.

**Parameters:**

- None required

**Example:**

```json
{
  "tool": "discover_services",
  "arguments": {}
}
```

**Returns:**

- Summary of all services (managers, interfaces, config services)
- Service types, file counts, ports, technologies used
- Docker configurations and dependencies

### 7. `get_service_dependencies`

Get dependencies for a specific service including internal and external dependencies.

**Parameters:**

- `service_name` (required): Name of the service to analyze dependencies for

**Example:**

```json
{
  "tool": "get_service_dependencies",
  "arguments": {
    "service_name": "cluster-manager"
  }
}
```

**Returns:**

- Internal dependencies (references to other services)
- External dependencies (Python packages, Node modules)
- Configuration dependencies

### 8. `analyze_config_files`

Analyze configuration files in the project including .env, YAML, JSON, Python configs, and Docker files.

**Parameters:**

- `target_path` (optional): Specific path to analyze (defaults to project root)

**Example:**

```json
{
  "tool": "analyze_config_files",
  "arguments": {
    "target_path": "/path/to/config/directory"
  }
}
```

**Returns:**

- Categorized analysis of all config file types
- Environment variables with type detection
- Docker service configurations with ports and environment
- Python config analysis with classes and imports
- JSON/YAML structure analysis

### 9. `get_config_summary`

Get a high-level summary of all configuration in the project.

**Parameters:**

- None required

**Example:**

```json
{
  "tool": "get_config_summary",
  "arguments": {}
}
```

**Returns:**

- Overview of config file counts by type
- Key configuration identification
- Potential configuration issues

## Tier 2 Development Tools

The following tools provide advanced development workflow support:

### 10. `get_docker_info`

Get comprehensive Docker analysis including containers, images, Compose files, and Dockerfiles.

**Parameters:**

- None required

**Example:**

```json
{
  "tool": "get_docker_info",
  "arguments": {}
}
```

**Returns:**

- Docker system availability and version
- Running and stopped containers with status
- Available Docker images
- Docker Compose file analysis with services and ports
- Dockerfile analysis with instructions and base images

### 11. `find_test_files`

Find test files mapping to source files or analyze overall test structure.

**Parameters:**

- `target_file` (optional): Specific source file to find tests for

**Example:**

```json
{
  "tool": "find_test_files",
  "arguments": {
    "target_file": "src/server.py"
  }
}
```

**Returns:**

- Test file mappings with confidence levels
- Test directory structure analysis
- Test function extraction
- Import analysis for test files

### 12. `analyze_dependencies`

Analyze project dependencies including Python packages, system requirements, and internal modules.

**Parameters:**

- `analysis_type` (optional): "all", "python", "system", or "internal" (defaults to "all")

**Example:**

```json
{
  "tool": "analyze_dependencies",
  "arguments": {
    "analysis_type": "python"
  }
}
```

**Returns:**

- Python package dependencies from requirements files
- System dependency availability (Docker, Git, Node.js)
- Internal module dependency graph
- Dependency conflicts and missing packages
- Circular dependency detection

### 13. `get_git_info`

Get git repository information including status, branches, commits, and remote info.

**Parameters:**

- `info_type` (optional): "all", "status", "branches", "commits", or "remote" (defaults to "all")

**Example:**

```json
{
  "tool": "get_git_info",
  "arguments": {
    "info_type": "status"
  }
}
```

**Returns:**

- Git repository status and branch information
- Recent commit history with authors and messages
- Remote repository configuration
- Modified and untracked files
- Branch tracking information

### 14. `optimize_code`

AI-powered code optimization using local Ollama LLMs with VS Code problems panel integration.

**Parameters:**

- `file_path` (required): Path to the code file to optimize
- `problems` (optional): Array of VS Code problems/diagnostics to address

**Example:**

```json
{
  "tool": "optimize_code",
  "arguments": {
    "file_path": "src/module.py",
    "problems": [
      {
        "severity": "warning",
        "message": "Line too long",
        "line": 25,
        "source": "flake8"
      }
    ]
  }
}
```

### 15. `smart_refactor`

AI-powered intelligent code refactoring suggestions using AST analysis and local Ollama LLMs.

**Parameters:**

- `file_path` (required): Path to the file to analyze for refactoring
- `target_scope` (optional): Scope of analysis ("file", "function", "class")
- `target_name` (optional): Specific function/class name to focus on

**Example:**

```json
{
  "tool": "smart_refactor",
  "arguments": {
    "file_path": "src/module.py",
    "target_scope": "function",
    "target_name": "complex_function"
  }
}
```

### 16. `generate_tests`

AI-powered automated test generation using local Ollama LLMs with pytest fixtures and mocks.

**Parameters:**

- `source_file` (required): Path to the source file to generate tests for
- `test_types` (optional): Array of test types ("unit", "integration", "edge", "error")
- `coverage_target` (optional): Target coverage percentage (0.0-1.0)

**Example:**

```json
{
  "tool": "generate_tests",
  "arguments": {
    "source_file": "src/module.py",
    "test_types": ["unit", "edge", "error"],
    "coverage_target": 0.85
  }
}
```

### 17. `write_docs`

AI-powered comprehensive documentation generation using local Ollama LLMs.

**Parameters:**

- `source_file` (required): Path to the source file to document
- `doc_types` (optional): Array of documentation types ("docstrings", "readme", "api")
- `style` (optional): Documentation style ("google", "numpy", "sphinx")

**Example:**

```json
{
  "tool": "write_docs",
  "arguments": {
    "source_file": "src/module.py",
    "doc_types": ["docstrings", "readme"],
    "style": "google"
  }
}
```

### 18. `review_code`

AI-powered comprehensive code review using local Ollama LLMs with git diff analysis.

**Parameters:**

- `target_path` (optional): Specific file/directory to review (defaults to git changes)
- `review_types` (optional): Array of review types ("quality", "security", "style", "performance")
- `severity_threshold` (optional): Minimum severity to report ("low", "medium", "high")

**Example:**

```json
{
  "tool": "review_code",
  "arguments": {
    "target_path": "src/",
    "review_types": ["quality", "security"],
    "severity_threshold": "medium"
  }
}
```

## AI Tools Requirements

The Tier 3 AI tools require:

- **Ollama** running locally with appropriate models (e.g., `deepseek-r1:8b`, `devstral`)
- Models can be pulled using: `ollama pull deepseek-r1:8b`
- Configure model preferences in `src/config.py`
- Tools gracefully fallback when AI services are unavailable

## Installation

1. Clone this repository as a submodule:

```bash
git submodule add https://github.com/BitingLip/model-context-protocol.git interfaces/model-context-protocol
```

2. Install dependencies:

```bash
cd interfaces/model-context-protocol
pip install -r requirements.txt
```

3. Test the installation:

```bash
python test_server.py
python test_tools.py
```

## VS Code Configuration

To use this MCP server with VS Code, add the following to your VS Code settings or use the provided `mcp_config.json`:

```json
{
  "mcpServers": {
    "biting-lip-tools": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "${workspaceFolder}/interfaces/model-context-protocol"
    }
  }
}
```

## Running the Server

### Standalone Mode

```bash
python src/server.py
```

### As MCP Server

The server is designed to be run through the MCP protocol via stdio transport. When configured in VS Code or other MCP-compatible environments, it will be automatically started when needed.

## Development

### Project Structure

```
model-context-protocol/
├── src/
│   ├── server.py           # Main MCP server
│   ├── tools/
│   │   ├── project_tree.py # Project tree generation
│   │   └── code_analysis.py # Code analysis tools
│   └── handlers/           # Future tool handlers
├── test_server.py          # Server functionality tests
├── test_tools.py           # Individual tool tests
├── mcp_config.json         # VS Code MCP configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Adding New Tools

1. Create a new tool module in `src/tools/`
2. Add the tool definition to `handle_list_tools()` in `server.py`
3. Add the tool handler to `handle_call_tool()` in `server.py`
4. Add tests for your tool

### Testing

Run the test suite:

```bash
python test_server.py    # Test server functionality
python test_tools.py     # Test individual tools
```

## Contributing

This MCP server is part of the Biting Lip AI platform. Contributions should follow the project's coding standards and include appropriate tests.

## License

See the LICENSE file in the project root for license information.
MCP interface for Agentic development
