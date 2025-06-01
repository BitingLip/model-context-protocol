# Biting Lip MCP Tools - Quick Reference

## Available Tools (21 total)

### Tier 1: Project Analysis Tools

1. **generate_project_tree** - Generate visual tree structure of project directory
2. **analyze_code** - Comprehensive code analysis and quality metrics
3. **discover_services** - Discover running services and their configurations
4. **analyze_config** - Analyze configuration files and settings
5. **analyze_docker** - Docker and containerization analysis
6. **analyze_dependencies** - Dependency analysis and conflict detection
7. **map_tests** - Test mapping and coverage analysis
8. **analyze_git** - Git repository analysis and history

### Tier 2: Infrastructure Discovery Tools

9. **discover_api_endpoints** - API endpoint discovery and documentation
10. **analyze_database_schema** - Database schema analysis
11. **analyze_logs** - Log file analysis and pattern detection

### Tier 3: AI-Powered Development Tools

12. **optimize_code** - AI-powered code optimization using local Ollama LLMs
13. **smart_refactor** - Intelligent code refactoring suggestions
14. **generate_tests** - AI-powered test generation
15. **generate_documentation** - Automated documentation generation
16. **review_code** - AI-powered code review and suggestions

### Tier 4: Advanced Analysis Tools

17. **analyze_performance** - Performance bottleneck analysis
18. **analyze_security** - Security vulnerability scanning
19. **analyze_architecture** - Architecture pattern analysis
20. **analyze_metrics** - Code metrics and quality assessment
21. **generate_insights** - Project insights and recommendations

## Usage Examples

### Basic Commands

```
@mcp list tools
@mcp call generate_project_tree
@mcp call analyze_code --file_path="src/main.py"
```

### AI-Powered Analysis

```
@mcp call optimize_code --file_path="src/performance.py"
@mcp call smart_refactor --file_path="src/legacy.py" --target_scope="function"
@mcp call generate_tests --file_path="src/utils.py" --test_types=["unit", "edge"]
```

### Infrastructure Analysis

```
@mcp call discover_services
@mcp call analyze_docker
@mcp call discover_api_endpoints --base_url="http://localhost:8000"
```

## Server Status

- ✅ Server Running: `full_mcp_server.py`
- ✅ Tools Available: 21
- ✅ GitHub Copilot Integration: Active
- ✅ Local Ollama Integration: Enabled
