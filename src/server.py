"""
Biting Lip MCP Server - Main server implementation.
Provides handy tools for AI agents working with the Biting Lip platform.
"""

import asyncio
import json
import logging
from typing import Any, Sequence

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# Import our tools
from tools.project_tree import ProjectTreeGenerator
from tools.code_analysis import CodeAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the server
app = Server("biting-lip-mcp")

# Global analyzer instance (will be set during initialization)
analyzer = None


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools for the Biting Lip MCP server."""
    return [
        types.Tool(
            name="generate_project_tree",
            description="Generate a visual tree structure of a project directory with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "root_path": {
                        "type": "string",
                        "description": "Root directory path to analyze"
                    },
                    "ignore_patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Patterns to ignore (e.g., '*.pyc', '__pycache__')"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum depth to traverse (optional)"
                    }
                },
                "required": ["root_path"]
            }
        ),
        types.Tool(
            name="analyze_python_file",
            description="Analyze a Python file and extract classes, functions, imports, and constants",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the Python file to analyze"
                    }
                },
                "required": ["file_path"]
            }
        ),
        types.Tool(
            name="get_project_overview",
            description="Get a comprehensive overview of the Python project structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_root": {
                        "type": "string",
                        "description": "Root directory of the project (optional, uses current working directory if not provided)"
                    }
                }
            }
        ),
        types.Tool(
            name="search_code",
            description="Search for code patterns in the project",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string"
                    },
                    "file_type": {
                        "type": "string",
                        "description": "File extension to search in (default: 'py')",
                        "default": "py"
                    },
                    "project_root": {
                        "type": "string",
                        "description": "Root directory to search in (optional)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="find_python_files",
            description="Find all Python files in a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in (optional, uses project root if not provided)"
                    }
                }
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls."""
    try:
        if name == "generate_project_tree":
            root_path = arguments.get("root_path")
            ignore_patterns = arguments.get("ignore_patterns", [])
            max_depth = arguments.get("max_depth")
            
            generator = ProjectTreeGenerator(
                root_path=root_path,
                ignore_patterns=ignore_patterns,
                max_depth=max_depth
            )
            
            tree_output = generator.generate()
            
            return [
                types.TextContent(
                    type="text",
                    text=tree_output
                )
            ]
            
        elif name == "analyze_python_file":
            file_path = arguments.get("file_path")
            
            # Use global analyzer or create a temporary one
            temp_analyzer = analyzer or CodeAnalyzer(".")
            analysis = temp_analyzer.analyze_python_file(file_path)
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(analysis, indent=2)
                )
            ]
            
        elif name == "get_project_overview":
            project_root = arguments.get("project_root", ".")
            
            temp_analyzer = CodeAnalyzer(project_root)
            overview = temp_analyzer.get_project_overview()
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(overview, indent=2)
                )
            ]
            
        elif name == "search_code":
            query = arguments.get("query")
            file_type = arguments.get("file_type", "py")
            project_root = arguments.get("project_root", ".")
            
            temp_analyzer = CodeAnalyzer(project_root)
            results = temp_analyzer.search_code(query, file_type)
            
            # Format results for better readability
            if results:
                output = f"Found {len(results)} matches for '{query}':\n\n"
                for i, result in enumerate(results[:20]):  # Limit to first 20 results
                    output += f"{i+1}. {result['file']}:{result['line_number']}\n"
                    output += f"   {result['line_content']}\n\n"
                if len(results) > 20:
                    output += f"... and {len(results) - 20} more matches"
            else:
                output = f"No matches found for '{query}'"
            
            return [
                types.TextContent(
                    type="text",
                    text=output
                )
            ]
            
        elif name == "find_python_files":
            directory = arguments.get("directory")
            
            temp_analyzer = analyzer or CodeAnalyzer(".")
            python_files = temp_analyzer.find_python_files(directory)
            
            output = f"Found {len(python_files)} Python files:\n\n"
            for file in python_files:
                output += f"- {file}\n"
            
            return [
                types.TextContent(
                    type="text",
                    text=output
                )
            ]
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [
            types.TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}"
            )
        ]


async def main():
    """Main function to run the MCP server."""
    global analyzer
    
    # Initialize the analyzer with current working directory
    analyzer = CodeAnalyzer(".")
    
    logger.info("Starting Biting Lip MCP Server...")
    
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="biting-lip-mcp",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    logger.info("Biting Lip MCP Server - Starting...")
    asyncio.run(main())
