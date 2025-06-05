"""
AI Test Generator Tool

This tool leverages local Ollama LLMs to automatically generate comprehensive unit tests
for Python code. It analyzes code structure, identifies test scenarios, and creates
pytest-compatible test files with proper fixtures, mocks, and edge cases.

Features:
- AST-based code analysis for test case identification
- Multiple test types: unit, integration, edge cases, error conditions
- Pytest fixtures and parameterized tests generation
- Mock integration for external dependencies
- Test coverage analysis and suggestions
- Integration with local Ollama models (Devstral, DeepSeek R1)
"""

import ast
import json
import logging
import os
import re
import requests
from contextlib import suppress
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Import configuration directly
try:
    from ..config import OLLAMA_CONFIG
except ImportError:
    # Fallback configuration if import fails
    OLLAMA_CONFIG = {
        "url": "http://localhost:11434",
        "model": "deepseek-r1:8b",
        "timeout": 30
    }

logger = logging.getLogger(__name__)


class AITestGenerator:
    """AI-powered test generator using local Ollama LLMs."""
    
    def __init__(self):
        self.ollama_url = OLLAMA_CONFIG.get("url", "http://localhost:11434")
        self.model = OLLAMA_CONFIG.get("model", "deepseek-r1:8b")
        self.timeout = OLLAMA_CONFIG.get("timeout", 30)
        
    async def generate_tests(
        self,
        file_path: str,
        test_types: Optional[List[str]] = None,
        coverage_target: float = 0.9,
        include_fixtures: bool = True,
        include_mocks: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive unit tests for a Python file.
        
        Args:
            file_path: Path to the Python file to generate tests for
            test_types: List of test types to generate (unit, integration, edge, error)
            coverage_target: Target code coverage percentage (0.0-1.0)
            include_fixtures: Whether to generate pytest fixtures
            include_mocks: Whether to include mock suggestions
            
        Returns:
            Dictionary containing generated tests and metadata
        """
        try:
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}
            
            # Default test types
            test_types = test_types if test_types is not None else ["unit", "integration", "edge", "error"]
            
            # Read and analyze the source code
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Perform code analysis
            analysis = self._analyze_code_for_testing(source_code)
            
            # Generate test scenarios
            test_scenarios = self._identify_test_scenarios(analysis, test_types)
            
            # Generate AI-powered test code
            ai_generated_tests = await self._generate_ai_tests(
                source_code, analysis, test_scenarios, file_path
            )
            
            # Generate fixtures if requested
            fixtures = []
            if include_fixtures:
                fixtures = await self._generate_fixtures(analysis)
            
            # Generate mock suggestions if requested
            mock_suggestions = []
            if include_mocks:
                mock_suggestions = await self._generate_mock_suggestions(analysis)
            
            # Calculate coverage estimation
            coverage_estimation = self._estimate_coverage(analysis, test_scenarios)
            
            # Create test file structure
            test_file_content = self._create_test_file(
                ai_generated_tests, fixtures, mock_suggestions, file_path
            )
            
            return {
                "success": True,
                "source_file": file_path,
                "test_file_content": test_file_content,
                "test_scenarios": test_scenarios,
                "fixtures": fixtures,
                "mock_suggestions": mock_suggestions,
                "coverage_estimation": coverage_estimation,
                "ai_model": self.model,
                "metadata": {
                    "functions_analyzed": len(analysis.get("functions", [])),
                    "classes_analyzed": len(analysis.get("classes", [])),
                    "test_types": test_types,
                    "coverage_target": coverage_target
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating tests: {e}")
            return {"error": f"Test generation failed: {str(e)}"}
    
    def _analyze_code_for_testing(self, code: str) -> Dict[str, Any]:
        """Analyze Python code to identify testable components."""
        analysis = {
            "functions": [],
            "classes": [],
            "imports": [],
            "global_vars": [],
            "complexity_metrics": {},
            "dependencies": []
        }
        
        with suppress(SyntaxError):
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._analyze_function(node)
                    analysis["functions"].append(func_info)
                    
                elif isinstance(node, ast.ClassDef):
                    class_info = self._analyze_class(node)
                    analysis["classes"].append(class_info)
                    
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_info = self._analyze_import(node)
                    analysis["imports"].append(import_info)
                    
                elif isinstance(node, ast.Assign):
                    if isinstance(node.targets[0], ast.Name):
                        analysis["global_vars"].append(node.targets[0].id)
        
        return analysis
    
    def _analyze_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Analyze a function for test generation."""
        return {
            "name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "returns": self._extract_return_type(node),
            "docstring": ast.get_docstring(node),
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            "complexity": self._calculate_complexity(node),
            "raises_exceptions": self._find_raised_exceptions(node),
            "calls_external": self._find_external_calls(node)
        }
    
    def _analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze a class for test generation."""
        methods = []
        properties = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name.startswith('test_'):
                    continue  # Skip existing test methods
                method_info = self._analyze_function(item)
                method_info["is_property"] = any(
                    self._get_decorator_name(d) == "property" 
                    for d in item.decorator_list
                )
                if method_info["is_property"]:
                    properties.append(method_info)
                else:
                    methods.append(method_info)
        
        return {
            "name": node.name,
            "methods": methods,
            "properties": properties,
            "bases": [self._get_base_name(base) for base in node.bases],
            "docstring": ast.get_docstring(node),
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list]
        }
    
    def _analyze_import(self, node: ast.AST) -> Dict[str, Any]:
        """Analyze an import statement."""
        if isinstance(node, ast.Import):
            return {
                "type": "import",
                "modules": [alias.name for alias in node.names]
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                "type": "from_import",
                "module": node.module,
                "names": [alias.name for alias in node.names]
            }
        return {}
    
    def _identify_test_scenarios(self, analysis: Dict[str, Any], test_types: List[str]) -> List[Dict[str, Any]]:
        """Identify test scenarios based on code analysis."""
        scenarios = []
        
        # Function test scenarios
        for func in analysis.get("functions", []):
            if "unit" in test_types:
                scenarios.append({
                    "type": "unit",
                    "target": func["name"],
                    "target_type": "function",
                    "scenario": "normal_execution",
                    "description": f"Test {func['name']} with valid inputs"
                })
            
            if "edge" in test_types:
                scenarios.extend(self._generate_edge_case_scenarios(func))
            
            if "error" in test_types:
                scenarios.extend(self._generate_error_scenarios(func))
        
        # Class test scenarios
        for cls in analysis.get("classes", []):
            if "unit" in test_types:
                scenarios.append({
                    "type": "unit",
                    "target": cls["name"],
                    "target_type": "class",
                    "scenario": "initialization",
                    "description": f"Test {cls['name']} initialization"
                })
                
                scenarios.extend([
                    {
                        "type": "unit",
                        "target": f"{cls['name']}.{method['name']}",
                        "target_type": "method",
                        "scenario": "normal_execution",
                        "description": f"Test {method['name']} method"
                    }
                    for method in cls["methods"]
                ])
        
        return scenarios
    
    def _generate_edge_case_scenarios(self, func: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate edge case test scenarios for a function."""
        return [
            {
                "type": "edge",
                "target": func["name"],
                "target_type": "function",
                "scenario": "empty_inputs",
                "description": f"Test {func['name']} with empty/None inputs"
            },
            *(
                [{
                    "type": "edge",
                    "target": func["name"],
                    "target_type": "function",
                    "scenario": "boundary_values",
                    "description": f"Test {func['name']} with boundary values (0, -1, max)"
                }] if any(arg in func["args"] for arg in ["size", "count", "length", "index"]) else []
            )
        ]
    
    def _generate_error_scenarios(self, func: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate error condition test scenarios."""
        # Type errors and value errors
        scenarios = [
            {
                "type": "error",
                "target": func["name"],
                "target_type": "function",
                "scenario": "type_error",
                "description": f"Test {func['name']} with wrong argument types"
            },
            {
                "type": "error",
                "target": func["name"],
                "target_type": "function",
                "scenario": "value_error",
                "description": f"Test {func['name']} with invalid argument values"
            }
        ]
        
        # Custom exceptions
        scenarios.extend([
            {
                "type": "error",
                "target": func["name"],
                "target_type": "function",
                "scenario": f"raises_{exception.lower()}",
                "description": f"Test {func['name']} raises {exception}"
            }
            for exception in func.get("raises_exceptions", [])
        ])
        
        return scenarios
    
    async def _generate_ai_tests(
        self, 
        source_code: str, 
        analysis: Dict[str, Any], 
        scenarios: List[Dict[str, Any]],
        file_path: str
    ) -> str:
        """Generate test code using AI."""
        try:
            prompt = f"""
            Generate comprehensive pytest unit tests for the following Python code.
            
            Source file: {file_path}
            
            Code to test:
            ```python
            {source_code}
            ```
            
            Code analysis:
            - Functions: {[f['name'] for f in analysis.get('functions', [])]}
            - Classes: {[c['name'] for c in analysis.get('classes', [])]}
            - Dependencies: {analysis.get('imports', [])}
            
            Test scenarios to cover:
            {json.dumps(scenarios, indent=2)}
            
            Requirements:
            1. Generate pytest-compatible test functions
            2. Use proper test naming conventions (test_*)
            3. Include docstrings for test functions
            4. Use parameterized tests where appropriate
            5. Include assertions with descriptive messages
            6. Handle edge cases and error conditions
            7. Use appropriate pytest fixtures
            8. Include setup/teardown when needed
            
            Return only the test code, no explanations.
            """
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                return "# AI service unavailable"
            result = response.json()
            return result.get("response", "# AI test generation failed")
                
        except Exception as e:
            logger.error(f"AI test generation failed: {e}")
            return f"# AI test generation error: {str(e)}"
    
    async def _generate_fixtures(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate pytest fixtures based on code analysis."""
        # Sample data fixtures
        fixtures = [
            {
                "name": f"sample_{cls['name'].lower()}",
                "scope": "function",
                "description": f"Sample {cls['name']} instance for testing",
                "code": f"@pytest.fixture\ndef sample_{cls['name'].lower()}():\n    return {cls['name']}()"
            }
            for cls in analysis.get("classes", [])
        ]
        
        # Mock fixtures for external dependencies
        external_deps = {dep for func in analysis.get("functions", []) for dep in func.get("calls_external", [])}
        
        fixtures += [
            {
                "name": f"mock_{dep.lower()}",
                "scope": "function", 
                "description": f"Mock for {dep} dependency",
                "code": f"@pytest.fixture\ndef mock_{dep.lower()}():\n    return Mock(spec={dep})"
            }
            for dep in external_deps
        ]
        
        return fixtures
    
    async def _generate_mock_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mock suggestions for external dependencies."""

        db_keywords = {"database", "db", "sql", "query", "connection"}
        http_keywords = {"request", "api", "http", "fetch", "get", "post"}

        db_suggestions = [
            {
                "type": "database",
                "target": func["name"],
                "suggestion": "Mock database connections and queries",
                "library": "unittest.mock or pytest-mock"
            }
            for func in analysis.get("functions", [])
            if any(keyword in func["name"].lower() for keyword in db_keywords)
        ]

        http_suggestions = [
            {
                "type": "http",
                "target": func["name"],
                "suggestion": "Mock HTTP requests and responses",
                "library": "responses or httpx_mock"
            }
            for func in analysis.get("functions", [])
            if any(keyword in func["name"].lower() for keyword in http_keywords)
        ]

        return db_suggestions + http_suggestions
    
    def _estimate_coverage(self, analysis: Dict[str, Any], scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate test coverage based on generated scenarios."""
        total_functions = len(analysis.get("functions", []))
        total_methods = sum(len(cls.get("methods", [])) for cls in analysis.get("classes", []))
        total_testable = total_functions + total_methods
        
        covered_targets = set()
        for scenario in scenarios:
            covered_targets.add(scenario["target"])
        
        coverage = len(covered_targets) / max(total_testable, 1)
        
        return {
            "estimated_coverage": round(coverage, 2),
            "total_testable_units": total_testable,
            "covered_units": len(covered_targets),
            "uncovered_units": total_testable - len(covered_targets)
        }
    
    def _create_test_file(
        self, 
        ai_tests: str, 
        fixtures: List[Dict[str, Any]], 
        mock_suggestions: List[Dict[str, Any]], 
        source_file: str
    ) -> str:
        """Create the complete test file content."""
        source_name = Path(source_file).stem
        
        header = f'''"""
Tests for {source_name}.py

Auto-generated by AI Test Generator using {self.model}
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add source directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from {source_name} import *


'''
        
        # Add fixtures
        fixtures_code = "\n\n".join([
            f"# {fixture['description']}\n{fixture['code']}"
            for fixture in fixtures
        ])
        
        # Add mock suggestions as comments
        mock_comments = "\n".join([
            f"# {suggestion['type'].upper()} MOCK: {suggestion['suggestion']} ({suggestion['library']})"
            for suggestion in mock_suggestions
        ])
        
        return f"{header}\n# FIXTURES\n{fixtures_code}\n\n# MOCK SUGGESTIONS\n{mock_comments}\n\n# GENERATED TESTS\n{ai_tests}"
    
    # Helper methods for AST analysis
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation if present."""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        return None
    
    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Get decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        return str(decorator)
    
    def _get_base_name(self, base: ast.AST) -> str:
        """Get base class name from AST node."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return str(base)
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _find_raised_exceptions(self, node: ast.FunctionDef) -> List[str]:
        """Find exceptions raised by a function."""
        exceptions = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Raise) and child.exc:
                if isinstance(child.exc, ast.Name):
                    exceptions.append(child.exc.id)
                elif isinstance(child.exc, ast.Call) and isinstance(child.exc.func, ast.Name):
                    exceptions.append(child.exc.func.id)
        
        return exceptions
    
    def _find_external_calls(self, node: ast.FunctionDef) -> List[str]:
        """Find external function/method calls."""
        calls = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        
        return list(set(calls))
