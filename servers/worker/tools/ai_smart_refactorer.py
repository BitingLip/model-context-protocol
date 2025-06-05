#!/usr/bin/env python3
"""
AI Smart Refactoring tool for MCP server.

Leverages local Ollama LLMs to suggest intelligent refactoring opportunities
based on code analysis and best practices.
"""

import json
import requests
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class AISmartRefactorer:
    """Suggests intelligent refactoring using local Ollama LLMs."""
    
    def __init__(self, project_root: str, ollama_url: str = "http://localhost:11434"):
        self.project_root = Path(project_root)
        self.ollama_url = ollama_url
        self.default_model = "deepseek-r1:latest"
        
    def analyze_refactoring_opportunities(self, file_path: str, scope: str = "file") -> Dict[str, Any]:
        """
        Analyze code for refactoring opportunities.
        
        Args:
            file_path: Path to the file to analyze
            scope: Analysis scope ('file', 'function', 'class')
            
        Returns:
            Dictionary with refactoring suggestions
        """
        try:
            target_path = Path(file_path)
            if not target_path.is_absolute():
                target_path = self.project_root / file_path
                
            if not target_path.exists():
                return {"error": f"File not found: {file_path}"}
            
            code_content = target_path.read_text(encoding='utf-8')
            
            # Analyze code structure
            analysis = self._analyze_code_structure(code_content, target_path)
            
            # Get LLM suggestions
            refactoring_suggestions = []
            
            # Check for common refactoring patterns
            suggestions = self._detect_refactoring_patterns(code_content, analysis)
            
            # Get AI-powered suggestions
            ai_suggestions = self._get_ai_refactoring_suggestions(code_content, target_path, scope)
            
            if ai_suggestions:
                suggestions.extend(ai_suggestions)
            
            return {
                "file_path": str(target_path.relative_to(self.project_root)),
                "analysis": analysis,
                "refactoring_opportunities": len(suggestions),
                "suggestions": suggestions,
                "scope": scope,
                "ollama_available": self._check_ollama_available()
            }
            
        except Exception as e:
            return {"error": f"Refactoring analysis failed: {str(e)}"}
    
    def extract_function(self, file_path: str, start_line: int, end_line: int, function_name: str) -> Dict[str, Any]:
        """Extract code block into a new function."""
        try:
            target_path = Path(file_path)
            if not target_path.is_absolute():
                target_path = self.project_root / file_path
            
            code_content = target_path.read_text(encoding='utf-8')
            lines = code_content.split('\n')
            
            # Extract the code block
            extracted_code = '\n'.join(lines[start_line-1:end_line])
            
            # Use LLM to create proper function extraction
            extraction_result = self._get_function_extraction_suggestion(
                code_content, extracted_code, function_name, start_line, end_line
            )
            
            return {
                "file_path": str(target_path.relative_to(self.project_root)),
                "extracted_function": extraction_result,
                "original_lines": f"{start_line}-{end_line}",
                "function_name": function_name
            }
            
        except Exception as e:
            return {"error": f"Function extraction failed: {str(e)}"}
    
    def improve_naming(self, file_path: str, target_type: str = "all") -> Dict[str, Any]:
        """Suggest better names for variables, functions, and classes."""
        try:
            target_path = Path(file_path)
            if not target_path.is_absolute():
                target_path = self.project_root / file_path
            
            code_content = target_path.read_text(encoding='utf-8')
            
            # Parse code to find naming candidates
            naming_analysis = self._analyze_naming_opportunities(code_content, target_type)
            
            # Get AI suggestions for better names
            ai_naming_suggestions = self._get_ai_naming_suggestions(code_content, naming_analysis)
            
            return {
                "file_path": str(target_path.relative_to(self.project_root)),
                "naming_analysis": naming_analysis,
                "ai_suggestions": ai_naming_suggestions,
                "target_type": target_type
            }
            
        except Exception as e:
            return {"error": f"Naming analysis failed: {str(e)}"}
    
    def reduce_complexity(self, file_path: str, threshold: int = 10) -> Dict[str, Any]:
        """Suggest ways to reduce cyclomatic complexity."""
        try:
            target_path = Path(file_path)
            if not target_path.is_absolute():
                target_path = self.project_root / file_path
            
            code_content = target_path.read_text(encoding='utf-8')
            
            # Analyze complexity
            complexity_analysis = self._analyze_complexity(code_content, threshold)
            
            # Get AI suggestions for complexity reduction
            complexity_suggestions = self._get_complexity_reduction_suggestions(
                code_content, complexity_analysis
            )
            
            return {
                "file_path": str(target_path.relative_to(self.project_root)),
                "complexity_analysis": complexity_analysis,
                "suggestions": complexity_suggestions,
                "threshold": threshold
            }
            
        except Exception as e:
            return {"error": f"Complexity analysis failed: {str(e)}"}
    
    def _analyze_code_structure(self, code: str, file_path: Path) -> Dict[str, Any]:
        """Analyze the basic structure of the code."""
        analysis = {
            "total_lines": len(code.split('\n')),
            "functions": [],
            "classes": [],
            "imports": [],
            "complexity_issues": []
        }
        
        try:
            if file_path.suffix == '.py':
                tree = ast.parse(code)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        analysis["functions"].append({
                            "name": node.name,
                            "line": node.lineno,
                            "args_count": len(node.args.args),
                            "lines": self._count_function_lines(node)
                        })
                    elif isinstance(node, ast.ClassDef):
                        analysis["classes"].append({
                            "name": node.name,
                            "line": node.lineno,
                            "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                        })
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        analysis["imports"].append({
                            "line": node.lineno,
                            "module": getattr(node, 'module', None) or 'multiple'
                        })
        except SyntaxError:
            analysis["syntax_error"] = True
        
        return analysis
    
    def _detect_refactoring_patterns(self, code: str, analysis: Dict) -> List[Dict[str, Any]]:
        """Detect common refactoring patterns."""
        # Long functions
        suggestions = [
            {
                "type": "extract_method",
                "target": func["name"],
                "line": func["line"],
                "description": f"Function '{func['name']}' is {func['lines']} lines long. Consider breaking it down.",
                "priority": "medium"
            }
            for func in analysis.get("functions", [])
            if func.get("lines", 0) > 50
        ]
        
        # Too many parameters
        for func in analysis.get("functions", []):
            if func.get("args_count", 0) > 5:
                suggestions.append({
                    "type": "parameter_object",
                    "target": func["name"],
                    "line": func["line"],
                    "description": f"Function '{func['name']}' has {func['args_count']} parameters. Consider using a parameter object.",
                    "priority": "low"
                })
        
        # Duplicate code detection (simple pattern)
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if len(line.strip()) > 20:  # Only check substantial lines
                occurrences = [j for j, other_line in enumerate(lines) if other_line.strip() == line.strip()]
                if len(occurrences) > 2:
                    suggestions.append({
                        "type": "extract_constant",
                        "target": f"{line.strip()[:50]}...",
                        "line": i + 1,
                        "description": f"Duplicate code found on lines {occurrences}",
                        "priority": "medium"
                    })
                    break  # Only report first occurrence
        
        return suggestions
    
    def _get_ai_refactoring_suggestions(self, code: str, file_path: Path, scope: str) -> List[Dict[str, Any]]:
        """Get AI-powered refactoring suggestions."""
        try:
            prompt = f"""
Analyze this {file_path.suffix} code and suggest specific refactoring improvements:

Scope: {scope}
Code to analyze:
```{file_path.suffix[1:]}
{code[:3000]}  # First 3000 characters
```

Suggest refactoring opportunities focusing on:
1. Extract Method - breaking down long functions
2. Extract Class - grouping related functionality  
3. Rename - improving variable/function names
4. Simplify Conditionals - reducing complex if/else chains
5. Remove Duplication - eliminating repeated code

For each suggestion, provide:
- Type of refactoring
- Specific location (line number if possible)
- Brief description of the improvement
- Priority (high/medium/low)

Format as JSON array of suggestions.
"""
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.default_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "max_tokens": 1200
                    }
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                suggestion_text = result.get("response", "").strip()
                
                # Try to parse JSON from the response
                try:
                    # Extract JSON from response if it's wrapped in other text
                    json_match = re.search(r'\[.*\]', suggestion_text, re.DOTALL)
                    if json_match:
                        suggestions = json.loads(json_match.group())
                        return suggestions
                except json.JSONDecodeError:
                    pass
                
                # If JSON parsing fails, create a single suggestion with the text
                return [{
                    "type": "general_refactoring",
                    "target": "file",
                    "line": 1,
                    "description": suggestion_text[:500],
                    "priority": "medium"
                }]
                
        except (requests.RequestException, json.JSONDecodeError, KeyError):
            pass
        
        return []
    
    def _get_function_extraction_suggestion(self, full_code: str, extracted_code: str, 
                                          function_name: str, start_line: int, end_line: int) -> Dict[str, Any]:
        """Get AI suggestion for function extraction."""
        try:
            prompt = f"""
Help extract this code block into a well-designed function:

Original context (lines around {start_line}-{end_line}):
```python
{full_code[max(0, (start_line-10)*50):(end_line+5)*50]}
```

Code to extract:
```python
{extracted_code}
```

Proposed function name: {function_name}

Please provide:
1. The extracted function with proper parameters and return value
2. The replacement call in the original location  
3. Any imports or dependencies needed
4. Brief explanation of the refactoring

Format the response as a clear code example.
"""
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.default_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2, "max_tokens": 800}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "suggestion": result.get("response", "").strip(),
                    "confidence": "medium"
                }
                
        except (requests.RequestException, json.JSONDecodeError):
            pass
        
        return {"suggestion": "AI suggestion unavailable", "confidence": "low"}
    
    def _analyze_naming_opportunities(self, code: str, target_type: str) -> Dict[str, Any]:
        """Analyze naming opportunities in the code."""
        opportunities = {"variables": [], "functions": [], "classes": []}
        
        import contextlib
        with contextlib.suppress(SyntaxError):
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if target_type in {"all", "variables"} and isinstance(node, ast.Name):
                    name = node.id
                    if len(name) <= 2 or name.lower() in {'data', 'info', 'temp', 'tmp'}:
                        opportunities["variables"].append({
                            "name": name,
                            "line": node.lineno,
                            "reason": "Too short or generic"
                        })
                
                elif target_type in ["all", "functions"] and isinstance(node, ast.FunctionDef):
                    name = node.name
                    if not name.startswith('_') and (len(name) <= 3 or name.lower() in ['process', 'handle']):
                        opportunities["functions"].append({
                            "name": name,
                            "line": node.lineno,
                            "reason": "Too generic or short"
                        })
                
                elif target_type in ["all", "classes"] and isinstance(node, ast.ClassDef):
                    name = node.name
                    if not name[0].isupper() or name.lower() in ['data', 'info', 'manager']:
                        opportunities["classes"].append({
                            "name": name,
                            "line": node.lineno,
                            "reason": "Not following naming convention or too generic"
                        })
        
        return opportunities
    
    def _get_ai_naming_suggestions(self, code: str, naming_analysis: Dict) -> Dict[str, Any]:
        """Get AI suggestions for better naming."""
        if not any(naming_analysis.values()):
            return {"suggestions": "No naming improvements needed"}
        
        try:
            prompt = f"""
Suggest better names for these code elements:

Code context:
```python
{code[:2000]}
```

Elements to rename:
{json.dumps(naming_analysis, indent=2)}

For each element, suggest:
1. A better, more descriptive name
2. Brief reason for the suggestion
3. Context where this name would be used

Focus on clarity, convention, and domain-specific meaning.
"""
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.default_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "max_tokens": 1000}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {"suggestions": result.get("response", "").strip()}
                
        except (requests.RequestException, json.JSONDecodeError):
            pass
        
        return {"suggestions": "AI naming suggestions unavailable"}
    
    def _analyze_complexity(self, code: str, threshold: int) -> Dict[str, Any]:
        """Analyze cyclomatic complexity of functions."""
        complex_functions = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    if complexity > threshold:
                        complex_functions.append({
                            "name": node.name,
                            "line": node.lineno,
                            "complexity": complexity,
                            "threshold_exceeded": complexity - threshold
                        })
        
        except SyntaxError:
            pass
        
        return {"complex_functions": complex_functions, "threshold": threshold}
    
    def _get_complexity_reduction_suggestions(self, code: str, complexity_analysis: Dict) -> List[Dict[str, Any]]:
        """Get AI suggestions for reducing complexity."""
        complex_functions = complexity_analysis.get("complex_functions", [])
        if not complex_functions:
            return []
        
        suggestions = []
        
        for func in complex_functions[:3]:  # Limit to 3 most complex functions
            try:
                prompt = f"""
This function has high cyclomatic complexity ({func['complexity']}):

Function: {func['name']} (line {func['line']})

Code context:
```python
{code}
```

Suggest specific ways to reduce complexity:
1. Extract methods
2. Simplify conditionals
3. Use polymorphism instead of if/else chains
4. Apply strategy pattern

Provide concrete, actionable suggestions.
"""
                
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.default_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.3, "max_tokens": 800}
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    suggestions.append({
                        "function": func["name"],
                        "complexity": func["complexity"],
                        "suggestions": result.get("response", "").strip()
                    })
                    
            except (requests.RequestException, json.JSONDecodeError):
                suggestions.append({
                    "function": func["name"],
                    "complexity": func["complexity"],
                    "suggestions": "AI suggestions unavailable"
                })
        
        return suggestions
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Decision points increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _count_function_lines(self, node: ast.FunctionDef) -> int:
        """Count lines in a function node."""
        if hasattr(node, 'end_lineno') and node.end_lineno:
            return node.end_lineno - node.lineno + 1
        return 10  # Default estimate
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
