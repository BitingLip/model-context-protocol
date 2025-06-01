#!/usr/bin/env python3
"""
Dependency analysis tool for MCP server.

Provides functionality to analyze project dependencies including
Python packages, system requirements, and inter-module dependencies.
"""

import ast
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Any


class DependencyAnalyzer:
    """Analyzes project dependencies and requirements."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.requirement_files = [
            'requirements.txt', 'requirements-dev.txt', 'requirements-test.txt',
            'dev-requirements.txt', 'test-requirements.txt', 'pyproject.toml',
            'setup.py', 'setup.cfg', 'Pipfile', 'poetry.lock', 'environment.yml'
        ]
    
    def analyze_dependencies(self, analysis_type: str = "all") -> Dict[str, Any]:
        """
        Analyze project dependencies.
        
        Args:
            analysis_type: Type of analysis - 'all', 'python', 'system', 'internal'
            
        Returns:
            Dictionary with dependency analysis results
        """
        try:
            if analysis_type == "python":
                return self._analyze_python_dependencies()
            elif analysis_type == "system":
                return self._analyze_system_dependencies()
            elif analysis_type == "internal":
                return self._analyze_internal_dependencies()
            else:
                return self._analyze_all_dependencies()
        except Exception as e:
            return {
                "error": f"Failed to analyze dependencies: {str(e)}",
                "dependencies": {}
            }
    
    def _analyze_all_dependencies(self) -> Dict[str, Any]:
        """Perform comprehensive dependency analysis."""
        python_deps = self._analyze_python_dependencies()
        system_deps = self._analyze_system_dependencies()
        internal_deps = self._analyze_internal_dependencies()
        
        return {
            "python_dependencies": python_deps,
            "system_dependencies": system_deps,
            "internal_dependencies": internal_deps,
            "summary": {
                "total_python_packages": len(python_deps.get("packages", {})),
                "total_requirement_files": len(python_deps.get("requirement_files", [])),
                "total_internal_modules": len(internal_deps.get("modules", {})),
                "has_docker": system_deps.get("docker", {}).get("available", False),
                "has_git": system_deps.get("git", {}).get("available", False)
            }
        }
    
    def _analyze_python_dependencies(self) -> Dict[str, Any]:
        """Analyze Python package dependencies."""
        packages = {}
        requirement_files = []
        conflicts = []
        
        # Find and parse requirement files
        for req_file in self.requirement_files:
            req_paths = list(self.project_root.rglob(req_file))
            for req_path in req_paths:
                try:
                    file_info = self._parse_requirement_file(req_path)
                    requirement_files.append(file_info)
                    
                    # Merge packages and detect conflicts
                    for pkg_name, pkg_info in file_info.get("packages", {}).items():
                        if pkg_name in packages:
                            existing_version = packages[pkg_name].get("version")
                            new_version = pkg_info.get("version")
                            if existing_version != new_version:
                                conflicts.append({
                                    "package": pkg_name,
                                    "file1": packages[pkg_name].get("source_file"),
                                    "version1": existing_version,
                                    "file2": str(req_path.relative_to(self.project_root)),
                                    "version2": new_version
                                })
                        packages[pkg_name] = pkg_info
                except Exception as e:
                    requirement_files.append({
                        "file": str(req_path.relative_to(self.project_root)),
                        "error": str(e),
                        "packages": {}
                    })
        
        # Analyze installed packages (if pip is available)
        installed_packages = self._get_installed_packages()
        
        # Find imported packages in code
        imported_packages = self._find_imported_packages()
        
        return {
            "packages": packages,
            "requirement_files": requirement_files,
            "installed_packages": installed_packages,
            "imported_packages": imported_packages,
            "conflicts": conflicts,
            "missing_packages": self._find_missing_packages(packages, imported_packages),
            "unused_packages": self._find_unused_packages(packages, imported_packages)
        }
    
    def _analyze_system_dependencies(self) -> Dict[str, Any]:
        """Analyze system-level dependencies."""
        system_info = {}
        
        # Check Python version
        try:
            result = subprocess.run(['python', '--version'], 
                                   capture_output=True, text=True, timeout=10)
            system_info["python"] = {
                "available": result.returncode == 0,
                "version": result.stdout.strip() if result.returncode == 0 else None,
                "error": result.stderr.strip() if result.returncode != 0 else None
            }
        except Exception as e:
            system_info["python"] = {"available": False, "error": str(e)}
        
        # Check Docker
        try:
            result = subprocess.run(['docker', '--version'], 
                                   capture_output=True, text=True, timeout=10)
            system_info["docker"] = {
                "available": result.returncode == 0,
                "version": result.stdout.strip() if result.returncode == 0 else None,
                "error": result.stderr.strip() if result.returncode != 0 else None
            }
        except Exception as e:
            system_info["docker"] = {"available": False, "error": str(e)}
        
        # Check Git
        try:
            result = subprocess.run(['git', '--version'], 
                                   capture_output=True, text=True, timeout=10)
            system_info["git"] = {
                "available": result.returncode == 0,
                "version": result.stdout.strip() if result.returncode == 0 else None,
                "error": result.stderr.strip() if result.returncode != 0 else None
            }
        except Exception as e:
            system_info["git"] = {"available": False, "error": str(e)}
        
        # Check Node.js (for GUI components)
        try:
            result = subprocess.run(['node', '--version'], 
                                   capture_output=True, text=True, timeout=10)
            system_info["nodejs"] = {
                "available": result.returncode == 0,
                "version": result.stdout.strip() if result.returncode == 0 else None,
                "error": result.stderr.strip() if result.returncode != 0 else None
            }
        except Exception as e:
            system_info["nodejs"] = {"available": False, "error": str(e)}
        
        # Check npm
        try:
            result = subprocess.run(['npm', '--version'], 
                                   capture_output=True, text=True, timeout=10)
            system_info["npm"] = {
                "available": result.returncode == 0,
                "version": result.stdout.strip() if result.returncode == 0 else None,
                "error": result.stderr.strip() if result.returncode != 0 else None
            }
        except Exception as e:
            system_info["npm"] = {"available": False, "error": str(e)}
        
        return system_info
    
    def _analyze_internal_dependencies(self) -> Dict[str, Any]:
        """Analyze internal module dependencies."""
        modules = {}
        dependency_graph = {}
        circular_dependencies = []
        
        # Find all Python files
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            try:
                relative_path = str(py_file.relative_to(self.project_root))
                module_name = self._path_to_module_name(py_file)
                
                imports = self._extract_imports_from_file(py_file)
                internal_imports = self._filter_internal_imports(imports)
                
                modules[module_name] = {
                    "file_path": relative_path,
                    "imports": internal_imports,
                    "import_count": len(internal_imports),
                    "size": py_file.stat().st_size
                }
                
                dependency_graph[module_name] = internal_imports
                
            except Exception:
                continue
        
        # Detect circular dependencies
        circular_dependencies = self._detect_circular_dependencies(dependency_graph)
        
        # Calculate dependency metrics
        dependency_metrics = self._calculate_dependency_metrics(modules, dependency_graph)
        
        return {
            "modules": modules,
            "dependency_graph": dependency_graph,
            "circular_dependencies": circular_dependencies,
            "metrics": dependency_metrics
        }
    
    def _parse_requirement_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a requirements file."""
        packages = {}
        
        if file_path.name == "pyproject.toml":
            return self._parse_pyproject_toml(file_path)
        elif file_path.name in ["setup.py", "setup.cfg"]:
            return self._parse_setup_file(file_path)
        else:
            # Standard requirements.txt format
            try:
                content = file_path.read_text(encoding='utf-8')
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        pkg_info = self._parse_requirement_line(line)
                        if pkg_info:
                            pkg_info["source_file"] = str(file_path.relative_to(self.project_root))
                            packages[pkg_info["name"]] = pkg_info
            except Exception as e:
                return {
                    "file": str(file_path.relative_to(self.project_root)),
                    "error": str(e),
                    "packages": {}
                }
        
        return {
            "file": str(file_path.relative_to(self.project_root)),
            "packages": packages,
            "total_packages": len(packages)
        }
    
    def _parse_pyproject_toml(self, file_path: Path) -> Dict[str, Any]:
        """Parse pyproject.toml file."""
        packages = {}
        try:
            try:
                import tomllib
            except ImportError:
                # Python < 3.11, try tomli
                try:
                    import tomli as tomllib
                except ImportError:
                    return {
                        "file": str(file_path.relative_to(self.project_root)),
                        "packages": {},
                        "total_packages": 0,
                        "error": "TOML library not available"
                    }
            
            content = file_path.read_text(encoding='utf-8')
            data = tomllib.loads(content)
            
            # Handle poetry dependencies
            if "tool" in data and "poetry" in data["tool"] and "dependencies" in data["tool"]["poetry"]:
                deps = data["tool"]["poetry"]["dependencies"]
                for name, version in deps.items():
                    if name != "python":  # Skip Python version requirement
                        packages[name] = {
                            "name": name,
                            "version": str(version),
                            "type": "poetry",
                            "source_file": str(file_path.relative_to(self.project_root))
                        }
            
            # Handle project dependencies
            if "project" in data and "dependencies" in data["project"]:
                deps = data["project"]["dependencies"]
                for dep in deps:
                    pkg_info = self._parse_requirement_line(dep)
                    if pkg_info:
                        pkg_info["source_file"] = str(file_path.relative_to(self.project_root))
                        packages[pkg_info["name"]] = pkg_info
                        
        except Exception:
            # Fall back to basic parsing
            pass
        
        return {
            "file": str(file_path.relative_to(self.project_root)),
            "packages": packages,
            "total_packages": len(packages)
        }
    
    def _parse_setup_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse setup.py or setup.cfg file."""
        packages = {}
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Look for install_requires or requirements
            requires_pattern = r'(?:install_requires|requires)\s*=\s*\[(.*?)\]'
            matches = re.findall(requires_pattern, content, re.DOTALL)
            
            for match in matches:
                # Extract individual requirements
                req_lines = re.findall(r'["\']([^"\']+)["\']', match)
                for req_line in req_lines:
                    pkg_info = self._parse_requirement_line(req_line)
                    if pkg_info:
                        pkg_info["source_file"] = str(file_path.relative_to(self.project_root))
                        packages[pkg_info["name"]] = pkg_info
                        
        except Exception:
            pass
        
        return {
            "file": str(file_path.relative_to(self.project_root)),
            "packages": packages,
            "total_packages": len(packages)
        }
    
    def _parse_requirement_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single requirement line."""
        # Handle various requirement formats
        line = line.strip()
        if not line or line.startswith('#'):
            return None
        
        # Remove comments
        if '#' in line:
            line = line.split('#')[0].strip()
        
        # Parse package name and version
        version_operators = ['==', '>=', '<=', '>', '<', '!=', '~=']
        name = line
        version = None
        operator = None
        
        for op in version_operators:
            if op in line:
                parts = line.split(op, 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    version = parts[1].strip()
                    operator = op
                    break
        
        # Handle extras
        if '[' in name:
            name = name.split('[')[0]
        
        return {
            "name": name.lower(),
            "version": version,
            "operator": operator,
            "original_line": line
        }
    
    def _get_installed_packages(self) -> Dict[str, Any]:
        """Get list of installed Python packages."""
        try:
            result = subprocess.run(['pip', 'list', '--format=json'], 
                                   capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return {pkg["name"].lower(): pkg["version"] for pkg in packages}
        except Exception:
            pass
        return {}
    
    def _find_imported_packages(self) -> Dict[str, Any]:
        """Find packages imported in Python code."""
        imported = {}
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                imports = self._extract_imports_from_file(py_file)
                for imp in imports:
                    # Extract top-level package name
                    top_level = imp.split('.')[0]
                    if top_level not in imported:
                        imported[top_level] = []
                    imported[top_level].append({
                        "file": str(py_file.relative_to(self.project_root)),
                        "import": imp
                    })
            except Exception:
                continue
        
        return imported
    
    def _extract_imports_from_file(self, file_path: Path) -> List[str]:
        """Extract imports from a Python file using AST."""
        imports = []
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception:
            # Fall back to regex parsing
            try:
                content = file_path.read_text(encoding='utf-8')
                import_patterns = [
                    r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
                    r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import'
                ]
                for pattern in import_patterns:
                    matches = re.findall(pattern, content, re.MULTILINE)
                    imports.extend(matches)
            except Exception:
                pass
        
        return imports
    
    def _filter_internal_imports(self, imports: List[str]) -> List[str]:
        """Filter imports to only include internal project modules."""
        internal = []
        for imp in imports:
            # Check if import corresponds to a file in the project
            potential_paths = [
                self.project_root / f"{imp.replace('.', os.sep)}.py",
                self.project_root / imp.replace('.', os.sep) / "__init__.py"
            ]
            if any(path.exists() for path in potential_paths):
                internal.append(imp)
        return internal
    
    def _detect_circular_dependencies(self, dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies in the dependency graph."""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in dependency_graph.get(node, []):
                dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
        
        for node in dependency_graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _calculate_dependency_metrics(self, modules: Dict[str, Any], 
                                     dependency_graph: Dict[str, List[str]]) -> Dict[str, Any]:
        """Calculate dependency metrics."""
        total_modules = len(modules)
        total_dependencies = sum(len(deps) for deps in dependency_graph.values())
        
        # Find modules with most dependencies
        most_dependent = sorted(
            [(module, len(deps)) for module, deps in dependency_graph.items()],
            key=lambda x: x[1], reverse=True
        )[:10]
        
        # Find modules that are most depended upon
        dependency_count = {}
        for deps in dependency_graph.values():
            for dep in deps:
                dependency_count[dep] = dependency_count.get(dep, 0) + 1
        
        most_depended_upon = sorted(
            dependency_count.items(),
            key=lambda x: x[1], reverse=True
        )[:10]
        
        return {
            "total_modules": total_modules,
            "total_internal_dependencies": total_dependencies,
            "average_dependencies_per_module": total_dependencies / total_modules if total_modules > 0 else 0,
            "modules_with_most_dependencies": most_dependent,
            "most_depended_upon_modules": most_depended_upon
        }
    
    def _find_missing_packages(self, required: Dict[str, Any], 
                              imported: Dict[str, Any]) -> List[str]:
        """Find packages that are imported but not in requirements."""
        required_names = set(required.keys())
        imported_names = set(imported.keys())
        
        # Common packages that don't need to be in requirements
        builtin_packages = {
            'os', 'sys', 'json', 'datetime', 'time', 're', 'math', 'random',
            'collections', 'itertools', 'functools', 'pathlib', 'typing',
            'logging', 'unittest', 'ast', 'subprocess', 'threading'
        }
        
        missing = []
        for pkg in imported_names:
            if pkg not in required_names and pkg not in builtin_packages:
                missing.append(pkg)
        
        return missing
    
    def _find_unused_packages(self, required: Dict[str, Any], 
                             imported: Dict[str, Any]) -> List[str]:
        """Find packages in requirements but not imported."""
        required_names = set(required.keys())
        imported_names = set(imported.keys())
        
        unused = []
        for pkg in required_names:
            if pkg not in imported_names:
                unused.append(pkg)
        
        return unused
    
    def _path_to_module_name(self, file_path: Path) -> str:
        """Convert file path to Python module name."""
        relative_path = file_path.relative_to(self.project_root)
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        return '.'.join(module_parts)
