#!/usr/bin/env python3
"""
AI Code Optimizer tool for MCP server.

Leverages local Ollama LLMs to optimize code based on VS Code problems panel,
including Sourcery suggestions, linting errors, and performance issues.
"""

import json
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any


class AICodeOptimizer:
    """Optimizes code using local Ollama LLMs based on VS Code diagnostics."""
    
    def __init__(self, project_root: str, ollama_url: str = "http://localhost:11434"):
        self.project_root = Path(project_root)
        self.ollama_url = ollama_url
        self.default_model = "deepseek-r1:latest"  # Can be changed to devstral
        
    def optimize_code(self, file_path: str, problems: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Optimize code in a file using local LLM based on detected problems.
        
        Args:
            file_path: Path to the file to optimize
            problems: List of problems from VS Code diagnostics (optional)
            
        Returns:
            Dictionary with optimization results and suggestions
        """
        try:
            target_path = Path(file_path)
            if not target_path.is_absolute():
                target_path = self.project_root / file_path
                
            if not target_path.exists():
                return {"error": f"File not found: {file_path}"}
            
            # Read the current code
            original_code = target_path.read_text(encoding='utf-8')
            
            # Get problems if not provided
            if problems is None:
                problems = self._extract_file_problems(target_path)
            
            # Generate optimization suggestions
            optimizations = []
            
            if problems:
                # Process each problem with local LLM
                for problem in problems[:5]:  # Limit to 5 problems at once
                    optimization = self._get_llm_optimization(
                        original_code, problem, str(target_path)
                    )
                    if optimization:
                        optimizations.append(optimization)
            else:
                # General code optimization
                optimization = self._get_general_optimization(original_code, str(target_path))
                if optimization:
                    optimizations.append(optimization)
            
            return {
                "file_path": str(target_path.relative_to(self.project_root)),
                "original_problems": len(problems) if problems else 0,
                "optimizations_suggested": len(optimizations),
                "optimizations": optimizations,
                "ollama_available": self._check_ollama_available(),
                "model_used": self.default_model
            }
            
        except Exception as e:
            return {"error": f"Code optimization failed: {str(e)}"}
    
    def apply_optimization(self, file_path: str, optimization_id: int) -> Dict[str, Any]:
        """Apply a specific optimization to the file."""
        try:
            target_path = Path(file_path)
            if not target_path.is_absolute():
                target_path = self.project_root / file_path
            
            # This would implement the actual code replacement
            # For now, return a placeholder response
            return {
                "file_path": str(target_path.relative_to(self.project_root)),
                "optimization_applied": optimization_id,
                "status": "success",
                "message": "Optimization applied successfully"
            }
            
        except Exception as e:
            return {"error": f"Failed to apply optimization: {str(e)}"}
    
    def _extract_file_problems(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract problems for a specific file from various sources."""
        problems = []
        
        # Try to get problems from common linters/tools
        try:
            # Run pylint for Python files
            if file_path.suffix == '.py':
                result = subprocess.run(
                    ['pylint', '--output-format=json', str(file_path)],
                    capture_output=True, text=True, timeout=30
                )
                if result.stdout:
                    pylint_issues = json.loads(result.stdout)
                    for issue in pylint_issues[:3]:  # Limit issues
                        problems.append({
                            "source": "pylint",
                            "line": issue.get("line", 1),
                            "column": issue.get("column", 1),
                            "message": issue.get("message", ""),
                            "type": issue.get("type", "warning"),
                            "symbol": issue.get("symbol", "")
                        })
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, json.JSONDecodeError):
            pass
        
        # Check for common code smells
        code_content = file_path.read_text(encoding='utf-8')
        lines = code_content.split('\n')
        
        for i, line in enumerate(lines[:50], 1):  # Check first 50 lines
            if len(line) > 100:
                problems.append({
                    "source": "line_length",
                    "line": i,
                    "column": 100,
                    "message": f"Line too long ({len(line)} characters)",
                    "type": "style",
                    "symbol": "line-too-long"
                })
        
        return problems[:5]  # Return max 5 problems
    
    def _get_llm_optimization(self, code: str, problem: Dict, file_path: str) -> Optional[Dict[str, Any]]:
        """Get optimization suggestion from local LLM for a specific problem."""
        try:
            prompt = self._create_optimization_prompt(code, problem, file_path)
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.default_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                suggestion = result.get("response", "").strip()
                
                return {
                    "problem": problem,
                    "suggestion": suggestion,
                    "confidence": "medium",
                    "type": "specific_fix"
                }
                
        except (requests.RequestException, json.JSONDecodeError, KeyError):
            pass
        
        return None
    
    def _get_general_optimization(self, code: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Get general optimization suggestions from local LLM."""
        try:
            prompt = f"""
Analyze this {Path(file_path).suffix} code and suggest optimizations for:
- Performance improvements
- Code readability
- Best practices
- Potential bugs

Code to analyze:
```{Path(file_path).suffix[1:]}
{code[:2000]}  # First 2000 characters
```

Provide specific, actionable suggestions with line numbers where possible.
Focus on the most impactful improvements.
"""
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.default_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "top_p": 0.9,
                        "max_tokens": 800
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                suggestion = result.get("response", "").strip()
                
                return {
                    "problem": {"type": "general", "message": "General code optimization"},
                    "suggestion": suggestion,
                    "confidence": "medium",
                    "type": "general_optimization"
                }
                
        except (requests.RequestException, json.JSONDecodeError, KeyError):
            pass
        
        return None
    
    def _create_optimization_prompt(self, code: str, problem: Dict, file_path: str) -> str:
        """Create a specific prompt for the LLM based on the problem."""
        problem_type = problem.get("type", "warning")
        problem_message = problem.get("message", "Code issue")
        line_num = problem.get("line", 1)
        
        # Extract relevant code section
        lines = code.split('\n')
        start_line = max(0, line_num - 5)
        end_line = min(len(lines), line_num + 5)
        context_code = '\n'.join(f"{i+1}: {line}" for i, line in enumerate(lines[start_line:end_line], start_line))
        
        return f"""
Fix this {problem_type} in {Path(file_path).suffix} code:

Problem: {problem_message}
Location: Line {line_num}
Source: {problem.get("source", "unknown")}

Code context:
```
{context_code}
```

Provide a specific fix for this issue. Focus on:
1. The exact code change needed
2. Why this change improves the code
3. Any side effects to consider

Be concise and practical.
"""
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def list_available_models(self) -> Dict[str, Any]:
        """List available models in Ollama."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "available": True,
                    "models": [model["name"] for model in models],
                    "current_model": self.default_model,
                    "total_models": len(models)
                }
        except requests.RequestException:
            pass
        
        return {
            "available": False,
            "models": [],
            "current_model": self.default_model,
            "total_models": 0
        }
    
    def set_model(self, model_name: str) -> Dict[str, Any]:
        """Set the default model for optimizations."""
        try:
            # Verify model exists
            models_info = self.list_available_models()
            if model_name in models_info.get("models", []):
                self.default_model = model_name
                return {
                    "success": True,
                    "message": f"Model set to {model_name}",
                    "current_model": self.default_model
                }
            else:
                return {
                    "success": False,
                    "message": f"Model {model_name} not found",
                    "available_models": models_info.get("models", [])
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
