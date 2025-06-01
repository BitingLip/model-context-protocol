"""
Code analysis tools for the Biting Lip MCP server.
"""

import os
import ast
import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class CodeAnalyzer:
    """Analyze code files in the Biting Lip project."""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        
    def analyze_python_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file and extract structure information."""
        def is_method(node, class_nodes):
            # Helper to check if a function node is a method of any class node
            for class_node in class_nodes:
                if node in class_node.body:
                    return True
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            analysis = {
                'file_path': file_path,
                'classes': [],
                'functions': [],
                'imports': [],
                'constants': [],
                'docstring': ast.get_docstring(tree)
            }

            class_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                        'docstring': ast.get_docstring(node)
                    })
                elif isinstance(node, ast.FunctionDef) and not is_method(node, class_nodes):
                    # This is a top-level function (not a method)
                    analysis['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node)
                    })

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append({
                                'type': 'import',
                                'name': alias.name,
                                'alias': alias.asname
                            })
                    else:
                        for alias in node.names:
                            analysis['imports'].append({
                                'type': 'from',
                                'module': node.module,
                                'name': alias.name,
                                'alias': alias.asname
                            })

                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():                            analysis['constants'].append({
                                'name': target.id,
                                'line': node.lineno
                            })

            return analysis

        except Exception as e:
            return {
                'error': f"Error analyzing {file_path}: {str(e)}",
                'file_path': file_path
            }
            
    def find_python_files(self, directory: Optional[str] = None) -> List[str]:
        """Find all Python files in the project."""
        search_dir = directory or self.project_root
        python_files = []
        
        for root, dirs, files in os.walk(search_dir):
            # Skip common ignore directories that can cause infinite loops or are not relevant
            dirs[:] = [d for d in dirs if d not in [
                '__pycache__', '.git', 'node_modules', 'cache', 'downloads',
                '.vscode', '.idea', 'venv', 'env', '.env', 'dist', 'build',
                '.pytest_cache', '.mypy_cache', '.coverage'
            ]]
            
            python_files.extend(
                [os.path.join(root, file) for file in files if file.endswith('.py')]
            )
                    
        return python_files
        
    def get_project_overview(self) -> Dict[str, Any]:
        """Get a comprehensive overview of the project structure."""
        python_files = self.find_python_files()
        
        overview = {
            'total_python_files': len(python_files),
            'files': [],
            'total_classes': 0,
            'total_functions': 0,
            'modules': {}
        }
        
        for file_path in python_files:
            analysis = self.analyze_python_file(file_path)
            if 'error' not in analysis:
                overview['files'].append(analysis)
                overview['total_classes'] += len(analysis['classes'])
                overview['total_functions'] += len(analysis['functions'])
                  # Organize by module
                rel_path = os.path.relpath(file_path, self.project_root)
                module_parts = rel_path.replace('\\', '/').split('/')
                if module_parts[0] not in overview['modules']:
                    overview['modules'][module_parts[0]] = []
                overview['modules'][module_parts[0]].append(rel_path)
                
        return overview
        
    def search_code(self, query: str, file_type: str = 'py') -> List[Dict[str, Any]]:
        """Search for code patterns in the project."""
        results = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip common ignore directories that can cause infinite loops or are not relevant
            dirs[:] = [d for d in dirs if d not in [
                '__pycache__', '.git', 'node_modules', 'cache', 'downloads',
                '.vscode', '.idea', 'venv', 'env', '.env', 'dist', 'build',
                '.pytest_cache', '.mypy_cache', '.coverage'
            ]]
            
            for file in files:
                if file.endswith(f'.{file_type}'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            
                        matches = [
                            {
                                'file': file_path,
                                'line_number': i + 1,
                                'line_content': line.strip(),
                                'context': {
                                    'before': lines[max(0, i-2):i],
                                    'after': lines[i+1:min(len(lines), i+3)]
                                }
                            }
                            for i, line in enumerate(lines)
                            if query.lower() in line.lower()
                        ]
                        results.extend(matches)
                    except Exception:
                        continue
                        
        return results
    
    def get_project_summary(self, max_files: int = 20, include_details: bool = False) -> Dict[str, Any]:
        """Get a lightweight project summary to avoid MCP protocol issues."""
        python_files = self.find_python_files()
        
        summary = {
            'total_python_files': len(python_files),
            'files_analyzed': min(max_files, len(python_files)),
            'total_classes': 0,
            'total_functions': 0,
            'modules': {},
            'top_files': []
        }
        
        # Analyze only a subset of files to keep response size manageable
        files_to_analyze = python_files[:max_files]
        
        for file_path in files_to_analyze:
            analysis = self.analyze_python_file(file_path)
            if 'error' not in analysis:
                summary['total_classes'] += len(analysis['classes'])
                summary['total_functions'] += len(analysis['functions'])
                
                # Organize by module
                rel_path = os.path.relpath(file_path, self.project_root)
                module_parts = rel_path.replace('\\', '/').split('/')
                if module_parts[0] not in summary['modules']:
                    summary['modules'][module_parts[0]] = []
                summary['modules'][module_parts[0]].append(rel_path)
                
                # Add lightweight file info
                file_summary = {
                    'file_path': rel_path,
                    'classes_count': len(analysis['classes']),
                    'functions_count': len(analysis['functions']),
                    'imports_count': len(analysis['imports'])
                }
                
                # Include detailed analysis only if requested and size permits
                if include_details and len(str(summary)) < 50000:  # Keep under 50KB
                    file_summary['classes'] = [{'name': c['name'], 'line': c['line']} for c in analysis['classes']]
                    file_summary['functions'] = [{'name': f['name'], 'line': f['line']} for f in analysis['functions']]
                
                summary['top_files'].append(file_summary)
        
        # Add warning if there are more files
        if len(python_files) > max_files:
            summary['note'] = f"Showing {max_files} of {len(python_files)} files. Use get_project_overview_paginated for more."
        
        return summary

    def get_project_overview_paginated(self, page: int = 0, files_per_page: int = 10) -> Dict[str, Any]:
        """Get paginated project overview to handle large projects."""
        python_files = self.find_python_files()
        start_idx = page * files_per_page
        end_idx = start_idx + files_per_page
        
        page_files = python_files[start_idx:end_idx]
        
        overview = {
            'pagination': {
                'page': page,
                'files_per_page': files_per_page,
                'total_files': len(python_files),
                'total_pages': (len(python_files) + files_per_page - 1) // files_per_page,
                'has_next': end_idx < len(python_files),
                'has_previous': page > 0
            },
            'files': [],
            'page_stats': {
                'classes': 0,
                'functions': 0
            }
        }
        
        for file_path in page_files:
            analysis = self.analyze_python_file(file_path)
            if 'error' not in analysis:
                overview['files'].append(analysis)
                overview['page_stats']['classes'] += len(analysis['classes'])
                overview['page_stats']['functions'] += len(analysis['functions'])
        
        return overview
