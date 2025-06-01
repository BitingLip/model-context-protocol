"""
API Endpoint Discovery Tool for Biting Lip MCP Server.

This tool discovers and analyzes API endpoints across different frameworks
including Flask, FastAPI, Django, Express.js, and more.
"""

import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class APIEndpointDiscovery:
    """Discovers API endpoints in web applications."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        
    def _get_python_files(self):
        """Get Python files excluding common irrelevant directories."""
        excluded_dirs = {
            'node_modules', '.git', '__pycache__', '.pytest_cache', 
            'venv', 'env', '.venv', '.env', 'build', 'dist', 
            '.tox', 'site-packages', '.mypy_cache'
        }
        
        for py_file in self.project_root.rglob("*.py"):
            # Check if file is in excluded directory
            if all(excluded_dir not in py_file.parts for excluded_dir in excluded_dirs):
                yield py_file
            
    def _get_js_files(self):
        """Get JavaScript/TypeScript files excluding common irrelevant directories."""
        excluded_dirs = {
            'node_modules', '.git', '.next', 'build', 'dist',
            '.cache', 'coverage', '.nyc_output'
        }
        
        for js_file in self.project_root.rglob("*.js"):
            if all(excluded_dir not in js_file.parts for excluded_dir in excluded_dirs):
                yield js_file

        for ts_file in self.project_root.rglob("*.ts"):
            if all(excluded_dir not in ts_file.parts for excluded_dir in excluded_dirs):
                yield ts_file
    def discover_endpoints(self, framework: Optional[str] = None) -> Dict[str, Any]:
        """
        Discover API endpoints across the project.
        
        Args:
            framework: Specific framework to analyze (flask, fastapi, django, express, etc.)
            
        Returns:
            Dictionary containing discovered endpoints grouped by framework
        """
        try:
            endpoints = {
                "summary": {
                    "total_endpoints": 0,
                    "frameworks_detected": [],
                    "files_analyzed": 0
                },
                "endpoints": {},
                "analysis_metadata": {
                    "project_root": str(self.project_root),
                    "supported_frameworks": [
                        "flask", "fastapi", "django", "express", "nextjs", "spring"
                    ]
                }
            }
            
            # If framework specified, analyze only that framework
            if framework:
                if framework.lower() in ["flask", "fastapi", "django"]:
                    result = self._analyze_python_frameworks(framework.lower())
                elif framework.lower() in ["express", "nextjs"]:
                    result = self._analyze_javascript_frameworks(framework.lower())
                else:
                    result = {"endpoints": [], "files": []}
                
                endpoints["endpoints"][framework.lower()] = result
                endpoints["summary"]["frameworks_detected"] = [framework.lower()]
            else:
                # Discover all frameworks
                python_frameworks = self._analyze_python_frameworks()
                js_frameworks = self._analyze_javascript_frameworks()
                
                endpoints["endpoints"].update(python_frameworks)
                endpoints["endpoints"].update(js_frameworks)
                
                # Update summary
                detected_frameworks = [k for k, v in endpoints["endpoints"].items() 
                                     if v.get("endpoints")]
                endpoints["summary"]["frameworks_detected"] = detected_frameworks
            
            # Calculate totals
            total_endpoints = sum(
                len(fw_data.get("endpoints", [])) 
                for fw_data in endpoints["endpoints"].values()
            )
            total_files = sum(
                len(fw_data.get("files", [])) 
                for fw_data in endpoints["endpoints"].values()
            )
            
            endpoints["summary"]["total_endpoints"] = total_endpoints
            endpoints["summary"]["files_analyzed"] = total_files
            
            return endpoints
            
        except Exception as e:
            logger.error(f"Error discovering endpoints: {e}")
            return {
                "error": str(e),
                "summary": {"total_endpoints": 0, "frameworks_detected": [], "files_analyzed": 0},
                "endpoints": {}
            }
    
    def _analyze_python_frameworks(self, specific_framework: Optional[str] = None) -> Dict[str, Any]:
        """Analyze Python web frameworks (Flask, FastAPI, Django)."""
        frameworks_data = {}
        
        frameworks_to_check = [specific_framework] if specific_framework else ["flask", "fastapi", "django"]
        
        for framework in frameworks_to_check:
            if framework == "flask":
                frameworks_data["flask"] = self._analyze_flask()
            elif framework == "fastapi":
                frameworks_data["fastapi"] = self._analyze_fastapi()
            elif framework == "django":
                frameworks_data["django"] = self._analyze_django()
                
        return frameworks_data
    def _analyze_javascript_frameworks(self, specific_framework: Optional[str] = None) -> Dict[str, Any]:
        """Analyze JavaScript web frameworks (Express, Next.js)."""
        frameworks_data = {}
        
        frameworks_to_check = [specific_framework] if specific_framework else ["express", "nextjs"]
        
        for framework in frameworks_to_check:
            if framework == "express":
                frameworks_data["express"] = self._analyze_express()
            elif framework == "nextjs":
                frameworks_data["nextjs"] = self._analyze_nextjs()
                
        return frameworks_data
    
    def _analyze_flask(self) -> Dict[str, Any]:
        """Analyze Flask applications for API endpoints."""
        endpoints = []
        files_analyzed = []
        
        try:
            # Find Python files that might contain Flask apps
            for py_file in self._get_python_files():
                try:
                    content = py_file.read_text(encoding='utf-8')
                    
                    # Check if file contains Flask imports/usage
                    if any(pattern in content for pattern in [
                        "from flask import", "import flask", "Flask(__name__)", "app = Flask"
                    ]):
                        files_analyzed.append(str(py_file.relative_to(self.project_root)))
                        file_endpoints = self._extract_flask_endpoints(content, str(py_file))
                        endpoints.extend(file_endpoints)
                        
                except Exception as e:
                    logger.warning(f"Error analyzing Flask file {py_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in Flask analysis: {e}")
            
        return {
            "endpoints": endpoints,
            "files": files_analyzed,
            "framework_info": {
                "name": "Flask",
                "type": "Python Web Framework",
                "patterns_detected": ["@app.route", "@bp.route", "add_url_rule"]
            }
        }
    
    def _extract_flask_endpoints(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract Flask endpoints from file content."""
        endpoints = []
        
        try:
            # Parse the AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for Flask route decorators
                    for decorator in node.decorator_list:
                        if (route_info := self._parse_flask_decorator(decorator)):
                            endpoint = {
                                "path": route_info.get("path", "/"),
                                "methods": route_info.get("methods", ["GET"]),
                                "function_name": node.name,
                                "file": file_path,
                                "line": node.lineno,
                                "framework": "flask",
                                "parameters": [arg.arg for arg in node.args.args if arg.arg != "self"],
                                "docstring": ast.get_docstring(node)
                            }
                            endpoints.append(endpoint)
                            
        except Exception as e:
            logger.warning(f"Error parsing Flask AST: {e}")            # Fallback to regex parsing
            endpoints.extend(self._extract_flask_endpoints_regex(content, file_path))
            
        return endpoints
    
    def _parse_flask_decorator(self, decorator) -> Optional[Dict[str, Any]]:
        """Parse Flask route decorator."""
        try:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute) and decorator.func.attr == "route":
                route_info: Dict[str, Any] = {"methods": ["GET"]}
                  # Extract path (first argument)
                if decorator.args:
                    if isinstance(decorator.args[0], ast.Str):
                        route_info["path"] = decorator.args[0].s
                    elif isinstance(decorator.args[0], ast.Constant):
                        route_info["path"] = decorator.args[0].value
                  # Extract methods from keyword arguments
                for keyword in decorator.keywords:
                    if keyword.arg == "methods" and isinstance(keyword.value, ast.List):
                        route_info["methods"] = [
                            method.s if isinstance(method, ast.Str) else method.value
                            for method in keyword.value.elts
                            if isinstance(method, (ast.Str, ast.Constant))
                        ]
                
                return route_info
                        
        except Exception as e:
            logger.warning(f"Error parsing Flask decorator: {e}")
            
        return None
    
    def _extract_flask_endpoints_regex(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Fallback regex-based Flask endpoint extraction."""
        endpoints = []
        
        # Regex patterns for Flask routes
        route_pattern = r'@(?:app|bp|blueprint)\.route\([\'"]([^\'"]+)[\'"](?:.*?methods\s*=\s*\[([^\]]+)\])?.*?\)'
        
        for match in re.finditer(route_pattern, content, re.MULTILINE | re.DOTALL):
            path = match.group(1)
            methods_str = match.group(2)
            methods = ["GET"]
            
            if methods_str:
                methods = [m.strip().strip('\'"') for m in methods_str.split(',')]
            
            endpoints.append({
                "path": path,
                "methods": methods,
                "function_name": "unknown",
                "file": file_path,
                "line": 0,
                "framework": "flask",
                "parameters": [],
                "docstring": None
            })
            
        return endpoints
    
    def _analyze_fastapi(self) -> Dict[str, Any]:
        """Analyze FastAPI applications for API endpoints."""
        endpoints = []
        files_analyzed = []
        try:
            for py_file in self._get_python_files():
                try:
                    content = py_file.read_text(encoding='utf-8')
                    
                    if any(pattern in content for pattern in [
                        "from fastapi import", "import fastapi", "FastAPI()", "app = FastAPI"
                    ]):
                        files_analyzed.append(str(py_file.relative_to(self.project_root)))
                        file_endpoints = self._extract_fastapi_endpoints(content, str(py_file))
                        endpoints.extend(file_endpoints)
                        
                except Exception as e:
                    logger.warning(f"Error analyzing FastAPI file {py_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in FastAPI analysis: {e}")
            
        return {
            "endpoints": endpoints,
            "files": files_analyzed,
            "framework_info": {
                "name": "FastAPI",
                "type": "Python API Framework",
                "patterns_detected": ["@app.get", "@app.post", "@app.put", "@app.delete"]
            }
        }
    
    def _extract_fastapi_endpoints(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract FastAPI endpoints from file content."""
        endpoints = []
        
        # Regex patterns for FastAPI routes
        method_patterns = [
            (r'@(?:app|router)\.get\([\'"]([^\'"]+)[\'"].*?\)', "GET"),
            (r'@(?:app|router)\.post\([\'"]([^\'"]+)[\'"].*?\)', "POST"),
            (r'@(?:app|router)\.put\([\'"]([^\'"]+)[\'"].*?\)', "PUT"),
            (r'@(?:app|router)\.delete\([\'"]([^\'"]+)[\'"].*?\)', "DELETE"),
            (r'@(?:app|router)\.patch\([\'"]([^\'"]+)[\'"].*?\)', "PATCH"),
        ]
        
        for pattern, method in method_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                path = match.group(1)
                endpoints.append({
                    "path": path,
                    "methods": [method],
                    "function_name": "unknown",
                    "file": file_path,
                    "line": 0,
                    "framework": "fastapi",
                    "parameters": [],
                    "docstring": None
                })
                
        return endpoints
    
    def _analyze_django(self) -> Dict[str, Any]:
        """Analyze Django applications for URL patterns."""
        endpoints = []
        files_analyzed = []
        try:
            # Look for Django URLs patterns
            for py_file in self._get_python_files():
                # Skip non-urls.py files
                if not py_file.name.endswith('urls.py'):
                    continue
                try:
                    content = py_file.read_text(encoding='utf-8')
                    files_analyzed.append(str(py_file.relative_to(self.project_root)))
                    file_endpoints = self._extract_django_urls(content, str(py_file))
                    endpoints.extend(file_endpoints)
                    
                except Exception as e:
                    logger.warning(f"Error analyzing Django URLs file {py_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in Django analysis: {e}")
            
        return {
            "endpoints": endpoints,
            "files": files_analyzed,
            "framework_info": {
                "name": "Django",
                "type": "Python Web Framework",
                "patterns_detected": ["path(", "url(", "re_path("]
            }
        }
    
    def _extract_django_urls(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract Django URL patterns."""
        endpoints = []
        
        # Regex patterns for Django URL patterns
        url_patterns = [
            r'path\([\'"]([^\'"]+)[\'"]',
            r'url\(r[\'"]([^\'"]+)[\'"]',
            r're_path\(r[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in url_patterns:
            for match in re.finditer(pattern, content):
                path = match.group(1)
                endpoints.append({
                    "path": path,
                    "methods": ["GET", "POST"],  # Django views can handle multiple methods
                    "function_name": "unknown",
                    "file": file_path,
                    "line": 0,
                    "framework": "django",
                    "parameters": [],
                    "docstring": None
                })
                
        return endpoints
    
    def _analyze_express(self) -> Dict[str, Any]:
        """Analyze Express.js applications for API endpoints."""
        endpoints = []
        files_analyzed = []
        try:
            for js_file in self._get_js_files():
                try:
                    content = js_file.read_text(encoding='utf-8')
                    
                    if any(pattern in content for pattern in [
                        "express()", "require('express')", "from 'express'", "app.get", "app.post"
                    ]):
                        files_analyzed.append(str(js_file.relative_to(self.project_root)))
                        file_endpoints = self._extract_express_endpoints(content, str(js_file))
                        endpoints.extend(file_endpoints)
                        
                except Exception as e:
                    logger.warning(f"Error analyzing Express file {js_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in Express analysis: {e}")
            
        return {
            "endpoints": endpoints,
            "files": files_analyzed,
            "framework_info": {
                "name": "Express.js",
                "type": "Node.js Web Framework",
                "patterns_detected": ["app.get", "app.post", "app.put", "app.delete", "router."]
            }
        }
    
    def _extract_express_endpoints(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract Express.js endpoints."""
        endpoints = []
        
        # Regex patterns for Express routes
        method_patterns = [
            (r'(?:app|router)\.get\([\'"]([^\'"]+)[\'"]', "GET"),
            (r'(?:app|router)\.post\([\'"]([^\'"]+)[\'"]', "POST"),
            (r'(?:app|router)\.put\([\'"]([^\'"]+)[\'"]', "PUT"),
            (r'(?:app|router)\.delete\([\'"]([^\'"]+)[\'"]', "DELETE"),
            (r'(?:app|router)\.patch\([\'"]([^\'"]+)[\'"]', "PATCH"),
        ]
        
        for pattern, method in method_patterns:
            for match in re.finditer(pattern, content):
                path = match.group(1)
                endpoints.append({
                    "path": path,
                    "methods": [method],
                    "function_name": "unknown",
                    "file": file_path,
                    "line": 0,
                    "framework": "express",
                    "parameters": [],
                    "docstring": None
                })
                
        return endpoints
    
    def _analyze_nextjs(self) -> Dict[str, Any]:
        """Analyze Next.js API routes."""
        endpoints = []
        files_analyzed = []
        try:
            # Look for Next.js API routes in pages/api or app/api directories
            for js_file in self._get_js_files():
                # Check if file is in a Next.js API path pattern
                path_str = str(js_file.relative_to(self.project_root))                
                if (path_str.startswith('pages/api/') or 
                    (path_str.startswith('app/api/') and js_file.name in ('route.js', 'route.ts'))):
                    try:
                        content = js_file.read_text(encoding='utf-8')
                        files_analyzed.append(str(js_file.relative_to(self.project_root)))
                        file_endpoints = self._extract_nextjs_endpoints(content, str(js_file))
                        endpoints.extend(file_endpoints)
                        
                    except Exception as e:
                        logger.warning(f"Error analyzing Next.js file {js_file}: {e}")

        except Exception as e:
            logger.error(f"Error in Next.js analysis: {e}")
            
        return {
            "endpoints": endpoints,
            "files": files_analyzed,
            "framework_info": {
                "name": "Next.js",
                "type": "React Framework with API Routes",
                "patterns_detected": ["export default", "export async function GET", "export async function POST"]
            }
        }
    
    def _extract_nextjs_endpoints(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract Next.js API endpoints."""
        endpoints = []
        
        # Convert file path to API route
        api_path = file_path.replace("\\", "/")
        if "pages/api/" in api_path:
            route_path = api_path.split("pages/api/")[1].replace(".js", "").replace(".ts", "")
        elif "app/api/" in api_path:
            route_path = api_path.split("app/api/")[1].replace("/route.js", "").replace("/route.ts", "")
        else:
            route_path = "unknown"
            
        # Check for HTTP method exports
        methods = []
        if "export async function GET" in content or "export function GET" in content:
            methods.append("GET")
        if "export async function POST" in content or "export function POST" in content:
            methods.append("POST")
        if "export async function PUT" in content or "export function PUT" in content:
            methods.append("PUT")
        if "export async function DELETE" in content or "export function DELETE" in content:
            methods.append("DELETE")
        if "export default" in content and not methods:
            methods = ["GET", "POST"]  # Default handler can handle multiple methods
            
        if methods:
            endpoints.append({
                "path": f"/api/{route_path}",
                "methods": methods,
                "function_name": "api_handler",
                "file": file_path,
                "line": 0,
                "framework": "nextjs",
                "parameters": [],
                "docstring": None
            })
            
        return endpoints
    
    def analyze_endpoint_details(self, endpoint_path: str, framework: str) -> Dict[str, Any]:
        """Analyze specific endpoint in detail."""
        try:
            # Find the endpoint first
            all_endpoints = self.discover_endpoints(framework)
            
            target_endpoint = None
            for fw_name, fw_data in all_endpoints.get("endpoints", {}).items():
                if fw_name == framework.lower():
                    for endpoint in fw_data.get("endpoints", []):
                        if endpoint["path"] == endpoint_path:
                            target_endpoint = endpoint
                            break
                    break
            
            if not target_endpoint:
                return {"error": f"Endpoint {endpoint_path} not found in {framework}"}
            
            # Analyze the endpoint file for more details
            file_path = Path(target_endpoint["file"])
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                
                return {
                    "endpoint": target_endpoint,
                    "detailed_analysis": {
                        "security_considerations": self._analyze_endpoint_security(content),
                        "dependencies": self._analyze_endpoint_dependencies(content),
                        "middleware": self._analyze_endpoint_middleware(content, framework),
                        "parameters": self._analyze_endpoint_parameters(content, framework),
                        "response_format": self._analyze_response_format(content)
                    }
                }
            else:
                return {"error": f"File {target_endpoint['file']} not found"}
                
        except Exception as e:
            logger.error(f"Error analyzing endpoint details: {e}")
            return {"error": str(e)}
    
    def _analyze_endpoint_security(self, content: str) -> List[str]:
        """Analyze security patterns in endpoint."""
        # Check for authentication patterns
        auth_patterns = [
            ("authentication", ["@login_required", "authenticate", "jwt", "token", "auth"]),
            ("authorization", ["@permission_required", "authorize", "role", "permission"]),
            ("input_validation", ["validate", "sanitize", "escape", "request.form", "request.json"]),
            ("csrf_protection", ["csrf", "CSRFProtect", "csrf_token"]),
            ("rate_limiting", ["rate_limit", "throttle", "limit"])
        ]
        
        return [
            category
            for category, patterns in auth_patterns
            if any(pattern in content.lower() for pattern in patterns)
        ]
    
    def _analyze_endpoint_dependencies(self, content: str) -> List[str]:
        """Analyze dependencies used in endpoint."""
        dependencies = []
        
        # Extract import statements
        import_patterns = [
            r'import\s+([^\s;]+)',
            r'from\s+([^\s]+)\s+import',
            r'require\([\'"]([^\'"]+)[\'"]',
            r'import\s+[^from]*from\s+[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in import_patterns:
            dependencies.extend(re.findall(pattern, content))
            
        return list(set(dependencies))[:10]  # Limit to 10 most relevant
    
    def _analyze_endpoint_middleware(self, content: str, framework: str) -> List[str]:
        """Analyze middleware usage."""
        if framework == "flask":
            # Flask middleware patterns
            patterns = ["@app.before_request", "@app.after_request", "@app.errorhandler"]
        elif framework == "express":
            # Express middleware patterns  
            patterns = ["app.use", "middleware", "next()"]
        elif framework == "fastapi":
            # FastAPI middleware patterns
            patterns = ["@app.middleware", "Depends", "HTTPBearer"]
        else:
            patterns = ["middleware", "decorator"]

        return [pattern for pattern in patterns if pattern in content]
    
    def _analyze_endpoint_parameters(self, content: str, framework: str) -> Dict[str, Any]:
        """Analyze endpoint parameters."""
        parameters = {
            "query_params": [],
            "path_params": [],
            "body_params": [],
            "headers": []
        }
        
        # Extract parameter patterns based on framework
        if framework in {"flask", "fastapi"}:
            # Look for request.args, request.json, etc.
            if "request.args" in content:
                parameters["query_params"].append("request.args")
            if "request.json" in content:
                parameters["body_params"].append("request.json")
            if "request.headers" in content:
                parameters["headers"].append("request.headers")
        
        return parameters
    
    def _analyze_response_format(self, content: str) -> List[str]:
        """Analyze response format patterns."""
        format_patterns = [
            ("json", ["jsonify", "return json", ".json()", "response.json"]),
            ("html", ["render_template", "return render", "text/html"]),
            ("xml", ["xml", "text/xml", "application/xml"]),
            ("plain_text", ["text/plain", "return str"]),
            ("redirect", ["redirect", "302", "301"])
        ]
        return [
            format_name
            for format_name, patterns in format_patterns
            if any(pattern in content for pattern in patterns)
        ]
