"""
AI Documentation Writer Tool

This tool leverages local Ollama LLMs to automatically generate comprehensive documentation
for Python code. It analyzes code structure, extracts meaningful information, and creates
various types of documentation including docstrings, README sections, API documentation,
and inline comments.

Features:
- AST-based code analysis for documentation extraction
- Multiple documentation formats: docstrings, README, API docs, tutorials
- Google, NumPy, and Sphinx docstring styles
- Automatic type hint analysis and documentation
- Integration with local Ollama models (Devstral, DeepSeek R1)
- Documentation quality assessment and improvement suggestions
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

logger = logging.getLogger(__name__)


class AIDocumentationWriter:
    """AI-powered documentation generator using local Ollama LLMs."""
    
    def __init__(self):
        # Use default Ollama configuration
        self.ollama_url = "http://localhost:11434"
        self.model = "deepseek-r1:8b"
        self.timeout = 30
        
    async def write_docs(
        self,
        file_path: str,
        doc_types: Optional[List[str]] = None,
        style: str = "google",
        include_examples: bool = True,
        include_type_hints: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive documentation for a Python file.
        
        Args:
            file_path: Path to the Python file to document
            doc_types: List of documentation types to generate (docstrings, readme, api, tutorial)
            style: Docstring style (google, numpy, sphinx)
            include_examples: Whether to include code examples
            include_type_hints: Whether to include type hint documentation
            
        Returns:
            Dictionary containing generated documentation and metadata
        """
        try:
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}
            
            # Default documentation types
            if doc_types is None:
                doc_types = ["docstrings", "readme", "api"]
            
            # Read and analyze the source code
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Perform code analysis
            analysis = self._analyze_code_for_docs(source_code)
            
            # Generate different types of documentation
            generated_docs = {}
            
            if "docstrings" in doc_types:
                generated_docs["docstrings"] = await self._generate_docstrings(
                    source_code, analysis, style, include_examples, include_type_hints
                )
            
            if "readme" in doc_types:
                generated_docs["readme"] = await self._generate_readme(
                    source_code, analysis, file_path
                )
            
            if "api" in doc_types:
                generated_docs["api"] = await self._generate_api_docs(
                    source_code, analysis, file_path
                )
            
            if "tutorial" in doc_types:
                generated_docs["tutorial"] = await self._generate_tutorial(
                    source_code, analysis, file_path
                )
            
            # Generate improvement suggestions
            quality_assessment = self._assess_documentation_quality(analysis)
            
            return {
                "success": True,
                "source_file": file_path,
                "generated_docs": generated_docs,
                "quality_assessment": quality_assessment,
                "ai_model": self.model,
                "metadata": {
                    "functions_analyzed": len(analysis.get("functions", [])),
                    "classes_analyzed": len(analysis.get("classes", [])),
                    "doc_types": doc_types,
                    "style": style,
                    "analysis": analysis
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
            return {"error": f"Documentation generation failed: {str(e)}"}
    
    def _analyze_code_for_docs(self, code: str) -> Dict[str, Any]:
        """Analyze Python code to extract documentation-relevant information."""
        analysis = {
            "module_docstring": None,
            "functions": [],
            "classes": [],
            "imports": [],
            "constants": [],
            "global_vars": [],
            "complexity_metrics": {},
            "type_hints": {}
        }
        
        with suppress(SyntaxError):
            tree = ast.parse(code)
            
            # Extract module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr) and 
                isinstance(tree.body[0].value, ast.Constant) and 
                isinstance(tree.body[0].value.value, str)):
                analysis["module_docstring"] = tree.body[0].value.value
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._analyze_function_for_docs(node)
                    analysis["functions"].append(func_info)
                    
                elif isinstance(node, ast.ClassDef):
                    class_info = self._analyze_class_for_docs(node)
                    analysis["classes"].append(class_info)
                    
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_info = self._analyze_import(node)
                    analysis["imports"].append(import_info)
                    
                elif isinstance(node, ast.Assign):
                    self._analyze_assignment(node, analysis)
        
        return analysis
    
    def _analyze_function_for_docs(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Analyze a function for documentation generation."""
        return {
            "name": node.name,
            "args": self._extract_function_args(node),
            "returns": self._extract_return_annotation(node),
            "docstring": ast.get_docstring(node),
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            "complexity": self._calculate_complexity(node),
            "raises_exceptions": self._find_raised_exceptions(node),
            "calls_external": self._find_external_calls(node),
            "line_number": node.lineno,
            "is_public": not node.name.startswith('_'),
            "type_annotations": self._extract_type_annotations(node)
        }
    
    def _analyze_class_for_docs(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze a class for documentation generation."""
        methods = []
        properties = []
        class_vars = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._analyze_function_for_docs(item)
                method_info["is_property"] = any(
                    self._get_decorator_name(d) == "property" 
                    for d in item.decorator_list
                )
                method_info["is_classmethod"] = any(
                    self._get_decorator_name(d) == "classmethod"
                    for d in item.decorator_list
                )
                method_info["is_staticmethod"] = any(
                    self._get_decorator_name(d) == "staticmethod"
                    for d in item.decorator_list
                )
                
                if method_info["is_property"]:
                    properties.append(method_info)
                else:
                    methods.append(method_info)
                    
            elif isinstance(item, ast.Assign):
                # Class variables
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_vars.append({
                            "name": target.id,
                            "annotation": getattr(item, 'annotation', None),
                            "value": self._extract_value(item.value)
                        })
        
        return {
            "name": node.name,
            "methods": methods,
            "properties": properties,
            "class_vars": class_vars,
            "bases": [self._get_base_name(base) for base in node.bases],
            "docstring": ast.get_docstring(node),
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            "line_number": node.lineno,
            "is_public": not node.name.startswith('_')
        }
    
    def _extract_function_args(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function arguments with type annotations."""
        args = []
        
        # Regular arguments
        for i, arg in enumerate(node.args.args):
            arg_info = {
                "name": arg.arg,
                "annotation": self._extract_annotation(arg.annotation),
                "default": None,
                "kind": "positional"
            }
            
            # Check for default values
            defaults_offset = len(node.args.args) - len(node.args.defaults)
            if i >= defaults_offset:
                default_idx = i - defaults_offset
                arg_info["default"] = self._extract_value(node.args.defaults[default_idx])
            
            args.append(arg_info)
        
        # *args
        if node.args.vararg:
            args.append({
                "name": node.args.vararg.arg,
                "annotation": self._extract_annotation(node.args.vararg.annotation),
                "kind": "vararg"
            })
        
        # **kwargs
        if node.args.kwarg:
            args.append({
                "name": node.args.kwarg.arg,
                "annotation": self._extract_annotation(node.args.kwarg.annotation),
                "kind": "kwarg"
            })
        
        return args
    
    async def _generate_docstrings(
        self, 
        source_code: str, 
        analysis: Dict[str, Any], 
        style: str,
        include_examples: bool,
        include_type_hints: bool
    ) -> Dict[str, Any]:
        """Generate docstrings for functions and classes."""
        try:
            prompt = f"""
            Generate comprehensive {style}-style docstrings for the following Python code.
            
            Code to document:
            ```python
            {source_code}
            ```
            
            Code analysis:
            - Functions: {json.dumps([f['name'] for f in analysis.get('functions', [])], indent=2)}
            - Classes: {json.dumps([c['name'] for c in analysis.get('classes', [])], indent=2)}
            
            Requirements:
            1. Use {style} docstring style (Google/NumPy/Sphinx)
            2. Include parameter descriptions with types
            3. Include return value descriptions
            4. Document raised exceptions
            5. {'Include usage examples' if include_examples else 'No examples needed'}
            6. {'Include type hint documentation' if include_type_hints else 'Skip type hints'}
            7. Keep docstrings concise but comprehensive
            8. Use proper formatting and indentation
            
            For each function/class, provide:
            - Brief description
            - Parameters (with types and descriptions)
            - Returns (type and description)
            - Raises (exceptions that may be raised)
            - Examples (if requested)
            
            Return the complete code with added docstrings.
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
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "content": result.get("response", "# Docstring generation failed"),
                    "style": style,
                    "functions_documented": len(analysis.get("functions", [])),
                    "classes_documented": len(analysis.get("classes", []))
                }
            else:
                return {"error": "AI service unavailable"}
                
        except Exception as e:
            logger.error(f"Docstring generation failed: {e}")
            return {"error": f"Docstring generation error: {str(e)}"}
    
    async def _generate_readme(self, source_code: str, analysis: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Generate README documentation."""
        try:
            module_name = Path(file_path).stem
            
            prompt = f"""
            Generate a comprehensive README.md file for the Python module '{module_name}'.
            
            Code to document:
            ```python
            {source_code}
            ```
            
            Module analysis:
            - Module: {module_name}
            - Functions: {[f['name'] for f in analysis.get('functions', [])]}
            - Classes: {[c['name'] for c in analysis.get('classes', [])]}
            - Dependencies: {[imp['modules'] if imp['type'] == 'import' else f"{imp['module']}.{imp['names']}" for imp in analysis.get('imports', [])]}
            
            Create a README with these sections:
            1. # Module Name - Brief description
            2. ## Features - Key capabilities
            3. ## Installation - How to install/use
            4. ## Quick Start - Basic usage examples
            5. ## API Reference - Main functions/classes
            6. ## Examples - Detailed usage examples
            7. ## Dependencies - Required packages
            8. ## License - License information
            
            Make it professional, clear, and user-friendly.
            Include code examples and practical use cases.
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
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "content": result.get("response", "# README generation failed"),
                    "module_name": module_name,
                    "sections": ["overview", "features", "installation", "usage", "api", "examples"]
                }
            else:
                return {"error": "AI service unavailable"}
                
        except Exception as e:
            logger.error(f"README generation failed: {e}")
            return {"error": f"README generation error: {str(e)}"}
    
    async def _generate_api_docs(self, source_code: str, analysis: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Generate API documentation."""
        try:
            prompt = f"""
            Generate comprehensive API documentation for this Python module.
            
            Code:
            ```python
            {source_code}
            ```
            
            Create structured API documentation with:
            
            ## Classes
            For each class:
            - Class description and purpose
            - Constructor parameters
            - Public methods with signatures
            - Properties and attributes
            - Usage examples
            
            ## Functions
            For each function:
            - Function signature with type hints
            - Parameter descriptions
            - Return value description
            - Example usage
            - Notes about exceptions
            
            ## Constants and Variables
            - Module-level constants
            - Configuration variables
            - Default values
            
            Format as clean, structured documentation suitable for API reference.
            Include type information and be precise about behavior.
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
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "content": result.get("response", "# API documentation generation failed"),
                    "functions_count": len(analysis.get("functions", [])),
                    "classes_count": len(analysis.get("classes", []))
                }
            else:
                return {"error": "AI service unavailable"}
                
        except Exception as e:
            logger.error(f"API documentation generation failed: {e}")
            return {"error": f"API documentation error: {str(e)}"}
    
    async def _generate_tutorial(self, source_code: str, analysis: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Generate tutorial documentation."""
        try:
            module_name = Path(file_path).stem
            
            prompt = f"""
            Create a step-by-step tutorial for using the '{module_name}' Python module.
            
            Code:
            ```python
            {source_code}
            ```
            
            Create a beginner-friendly tutorial with:
            
            # Getting Started with {module_name}
            
            ## Step 1: Basic Setup
            - Import statements
            - Basic configuration
            
            ## Step 2: Core Concepts
            - Key classes and functions
            - Basic usage patterns
            
            ## Step 3: Common Use Cases
            - Practical examples
            - Real-world scenarios
            
            ## Step 4: Advanced Features
            - Advanced functionality
            - Customization options
            
            ## Step 5: Best Practices
            - Tips and recommendations
            - Common pitfalls to avoid
            
            Make it educational, with progressive examples from simple to complex.
            Include explanations of why certain approaches are used.
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
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "content": result.get("response", "# Tutorial generation failed"),
                    "module_name": module_name,
                    "difficulty": "beginner-to-advanced"
                }
            else:
                return {"error": "AI service unavailable"}
                
        except Exception as e:
            logger.error(f"Tutorial generation failed: {e}")
            return {"error": f"Tutorial generation error: {str(e)}"}
    
    def _assess_documentation_quality(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of existing documentation."""
        assessment = {
            "score": 0.0,
            "issues": [],
            "suggestions": [],
            "coverage": {}
        }
        
        total_items = 0
        documented_items = 0
        
        # Check module docstring
        if analysis.get("module_docstring"):
            documented_items += 1
        else:
            assessment["issues"].append("Missing module docstring")
            assessment["suggestions"].append("Add a module-level docstring explaining the purpose")
        total_items += 1
        
        # Check function documentation
        functions = analysis.get("functions", [])
        total_items += len(functions)
        for func in functions:
            if func.get("docstring"):
                documented_items += 1
            else:
                if func["is_public"]:
                    assessment["issues"].append(f"Function '{func['name']}' missing docstring")
                    assessment["suggestions"].append(f"Add docstring to function '{func['name']}'")
        
        # Check class documentation
        classes = analysis.get("classes", [])
        total_items += len(classes)
        for cls in classes:
            if cls.get("docstring"):
                documented_items += 1
            else:
                if cls["is_public"]:
                    assessment["issues"].append(f"Class '{cls['name']}' missing docstring")
                    assessment["suggestions"].append(f"Add docstring to class '{cls['name']}'")
            
            # Check method documentation
            for method in cls.get("methods", []):
                total_items += 1
                if method.get("docstring"):
                    documented_items += 1
                else:
                    if method["is_public"]:
                        assessment["issues"].append(f"Method '{cls['name']}.{method['name']}' missing docstring")
        
        # Calculate coverage
        coverage = documented_items / max(total_items, 1)
        assessment["score"] = round(coverage, 2)
        assessment["coverage"] = {
            "total_items": total_items,
            "documented_items": documented_items,
            "percentage": round(coverage * 100, 1)
        }
        
        # Quality suggestions
        if coverage < 0.5:
            assessment["suggestions"].append("Consider documenting all public functions and classes")
        if coverage < 0.8:
            assessment["suggestions"].append("Add examples to complex functions")
        
        return assessment
    
    # Helper methods for AST analysis
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
    
    def _analyze_assignment(self, node: ast.Assign, analysis: Dict[str, Any]) -> None:
        """Analyze assignment statements for constants and variables."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                if name.isupper():  # Convention for constants
                    analysis["constants"].append({
                        "name": name,
                        "value": self._extract_value(node.value),
                        "annotation": getattr(node, 'annotation', None)
                    })
                else:
                    analysis["global_vars"].append({
                        "name": name,
                        "value": self._extract_value(node.value),
                        "annotation": getattr(node, 'annotation', None)
                    })
    
    def _extract_annotation(self, annotation: Optional[ast.AST]) -> Optional[str]:
        """Extract type annotation as string."""
        if annotation is None:
            return None
        
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Attribute):
            return f"{annotation.value.id}.{annotation.attr}"
        else:
            return str(annotation)
    
    def _extract_return_annotation(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation."""
        return self._extract_annotation(node.returns)
    
    def _extract_type_annotations(self, node: ast.FunctionDef) -> Dict[str, str]:
        """Extract all type annotations from a function."""
        annotations = {}
        
        # Arguments
        for arg in node.args.args:
            if arg.annotation:
                annotations[arg.arg] = self._extract_annotation(arg.annotation)
        
        # Return type
        if node.returns:
            annotations["return"] = self._extract_annotation(node.returns)
        
        return annotations
    
    def _extract_value(self, node: ast.AST) -> str:
        """Extract value from AST node as string."""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.List):
            return f"[{', '.join(self._extract_value(item) for item in node.elts)}]"
        elif isinstance(node, ast.Dict):
            items = []
            for k, v in zip(node.keys, node.values):
                items.append(f"{self._extract_value(k)}: {self._extract_value(v)}")
            return f"{{{', '.join(items)}}}"
        else:
            return str(node)
    
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
        """Calculate cyclomatic complexity."""
        complexity = 1
        
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
