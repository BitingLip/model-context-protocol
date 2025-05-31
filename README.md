# Biting Lip MCP Server

Model Context Protocol (MCP) server providing handy tools for AI agents working with the Biting Lip AI platform.

## Overview

This MCP server provides a collection of tools designed to help AI agents understand and work with the Biting Lip project structure. It includes tools for:

- **Project Structure Analysis**: Generate visual tree representations of directories
- **Code Analysis**: Extract information from Python files including classes, functions, imports
- **Code Search**: Search for patterns across the codebase
- **File Discovery**: Find Python files and analyze project structure

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
