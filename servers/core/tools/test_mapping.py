#!/usr/bin/env python3
"""
Test file mapping tool for MCP server.

Provides functionality to map source files to their corresponding test files
and understand the testing structure of the project.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any


class TestMapper:
    """Maps source files to test files and analyzes test structure."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.test_patterns = [
            r'test_.*\.py$',
            r'.*_test\.py$',
            r'.*\.test\.py$',
            r'test.*\.py$',
            r'.*_tests\.py$',
            r'.*\.tests\.py$',
        ]
        self.test_directories = [
            'test', 'tests', 'testing', '__tests__',
            'spec', 'specs', '__spec__'
        ]
    
    def find_test_files(self, target_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Find test files mapping to source files.
        
        Args:
            target_file: Specific source file to find tests for (optional)
            
        Returns:
            Dictionary with test mapping information
        """
        try:
            if target_file:
                return self._find_tests_for_file(target_file)
            else:
                return self._find_all_test_mappings()
        except Exception as e:
            return {
                "error": f"Failed to find test files: {str(e)}",
                "test_files": [],
                "mappings": {}
            }
    
    def _find_tests_for_file(self, target_file: str) -> Dict[str, Any]:
        """Find test files for a specific source file."""
        target_path = Path(target_file)
        if not target_path.is_absolute():
            target_path = self.project_root / target_file
        
        if not target_path.exists():
            return {
                "error": f"Target file not found: {target_file}",
                "target_file": str(target_path),
                "test_files": [],
                "possible_test_locations": []
            }
        
        test_files = []
        possible_locations = []
        
        # Generate possible test file names
        base_name = target_path.stem
        extension = target_path.suffix
        
        possible_names = [
            f"test_{base_name}{extension}",
            f"{base_name}_test{extension}",
            f"{base_name}.test{extension}",
            f"test_{base_name.lower()}{extension}",
            f"{base_name.lower()}_test{extension}"
        ]
        
        # Look in same directory
        for name in possible_names:
            test_file = target_path.parent / name
            if test_file.exists():
                test_files.append({
                    "path": str(test_file),
                    "relative_path": str(test_file.relative_to(self.project_root)),
                    "type": "same_directory",
                    "confidence": "high"
                })
        
        # Look in test directories safely
        test_dirs = self._safe_find_directories(self.project_root, "test")
        test_dirs.extend(self._safe_find_directories(self.project_root, "tests"))
        
        for test_dir in test_dirs:
            for name in possible_names:
                test_file = test_dir / name
                if test_file.exists():
                    test_files.append({
                        "path": str(test_file),
                        "relative_path": str(test_file.relative_to(self.project_root)),
                        "type": "test_directory",
                        "confidence": "medium"
                    })
                else:
                    possible_locations.append(str(test_file))
        
        # Look for tests that import or reference the target file
        referenced_tests = self._find_tests_by_reference(target_path)
        test_files.extend(referenced_tests)
        
        return {
            "target_file": str(target_path.relative_to(self.project_root)),
            "test_files": test_files,
            "possible_test_locations": possible_locations,
            "total_tests_found": len(test_files)
        }
    
    def _find_all_test_mappings(self) -> Dict[str, Any]:
        """Find comprehensive test mappings for the entire project."""
        test_files = []
        source_to_tests = {}
        test_structure = {}
        
        # Find all test files using safe search
        all_py_files = self._safe_find_files(self.project_root, "*.py")
        
        # Filter to actual test files
        actual_test_files = []
        for file_path in all_py_files:
            if any(re.match(pattern, file_path.name) for pattern in self.test_patterns):
                relative_path = str(file_path.relative_to(self.project_root))
                test_info = {
                    "path": str(file_path),
                    "relative_path": relative_path,
                    "name": file_path.name,
                    "directory": str(file_path.parent.relative_to(self.project_root)),
                    "size": file_path.stat().st_size if file_path.exists() else 0,
                    "imports": self._extract_imports(file_path),
                    "test_functions": self._extract_test_functions(file_path)
                }
                actual_test_files.append(test_info)
        
        # Analyze test directory structure
        for test_dir_name in self.test_directories:
            test_dirs = self._safe_find_directories(self.project_root, test_dir_name)
            for test_dir in test_dirs:
                relative_dir = str(test_dir.relative_to(self.project_root))
                test_files_in_dir = self._safe_find_test_files_in_dir(test_dir)
                
                test_structure[relative_dir] = {
                    "path": str(test_dir),
                    "test_count": len(test_files_in_dir),
                    "test_files": [str(f.relative_to(self.project_root)) for f in test_files_in_dir],
                    "subdirectories": [
                        str(d.relative_to(self.project_root)) 
                        for d in test_dir.iterdir() if d.is_dir() and not self._should_skip_directory(d)
                    ]
                }
        
        # Try to map tests to source files
        for test_file in actual_test_files:
            potential_sources = self._find_source_for_test(test_file)
            for source in potential_sources:
                if source not in source_to_tests:
                    source_to_tests[source] = []
                source_to_tests[source].append(test_file["relative_path"])
        
        return {
            "test_files": actual_test_files,
            "test_structure": test_structure,
            "source_to_tests_mapping": source_to_tests,
            "total_test_files": len(actual_test_files),
            "test_directories": len(test_structure)
        }
    
    def _find_tests_by_reference(self, target_path: Path) -> List[Dict[str, Any]]:
        """Find tests that reference the target file."""
        referenced_tests = []
        target_module = self._path_to_module_name(target_path)
        
        # Search all Python files for imports or references using safe search
        py_files = self._safe_find_files(self.project_root, "*.py")
        for py_file in py_files:
            if any(re.match(pattern, py_file.name) for pattern in self.test_patterns):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    if target_module in content or target_path.stem in content:
                        referenced_tests.append({
                            "path": str(py_file),
                            "relative_path": str(py_file.relative_to(self.project_root)),
                            "type": "reference_found",
                            "confidence": "low"
                        })
                except Exception:
                    continue
        
        return referenced_tests
    
    def _safe_find_files(self, root_path: Path, pattern: str = "*.py", max_depth: int = 5) -> List[Path]:
        """Safely find files by pattern with depth limits and exclusions."""
        found_files = []
        
        def _search_directory(directory: Path, current_depth: int):
            if current_depth > max_depth:
                return
            try:
                for item in directory.iterdir():
                    if item.is_file():
                        if pattern == "*.py" and item.suffix == '.py':
                            found_files.append(item)
                        elif item.name == pattern:
                            found_files.append(item)
                    elif item.is_dir() and not self._should_skip_directory(item):
                        _search_directory(item, current_depth + 1)
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass
        
        _search_directory(root_path, 0)
        return found_files
    
    def _safe_find_directories(self, root_path: Path, dir_name: str, max_depth: int = 5) -> List[Path]:
        """Safely find directories by name with depth limits and exclusions."""
        found_dirs = []
        
        def _search_directory(directory: Path, current_depth: int):
            if current_depth > max_depth:
                return
            
            try:
                for item in directory.iterdir():
                    if item.is_dir():
                        if item.name == dir_name:
                            found_dirs.append(item)
                        elif not self._should_skip_directory(item):
                            _search_directory(item, current_depth + 1)
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass
        
        _search_directory(root_path, 0)
        return found_dirs
    
    def _safe_find_test_files_in_dir(self, test_dir: Path, max_depth: int = 3) -> List[Path]:
        """Safely find test files in a directory with depth limits."""
        test_files = []
        
        def _search_directory(directory: Path, current_depth: int):
            if current_depth > max_depth:
                return
            
            try:
                for item in directory.iterdir():
                    if item.is_file() and item.suffix == '.py':
                        if any(re.match(pattern, item.name) for pattern in self.test_patterns):
                            test_files.append(item)
                    elif item.is_dir() and not self._should_skip_directory(item):
                        _search_directory(item, current_depth + 1)
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass
        
        _search_directory(test_dir, 0)
        return test_files
    
    def _should_skip_directory(self, directory: Path) -> bool:
        """Check if a directory should be skipped during traversal."""
        skip_patterns = {
            '__pycache__', '.git', '.vscode', 'node_modules', '.pytest_cache',
            '.tox', '.coverage', 'dist', 'build', '.egg-info', '.mypy_cache',
            'cache', 'downloads', '.env', 'venv', 'env'
        }
        return directory.name in skip_patterns or directory.name.startswith('.')
    
    def _find_source_for_test(self, test_file: Dict[str, Any]) -> List[str]:
        """Find potential source files for a test file."""
        potential_sources = []
        test_name = test_file["name"]
        
        # Extract base name from test file
        base_name = None
        for pattern in self.test_patterns:
            match = re.match(pattern.replace('.*', '(.*)').replace('$', ''), test_name)
            if match:
                base_name = match.group(1)
                break
        
        if not base_name:
            return potential_sources
        
        # Look for corresponding source files
        possible_names = [
            f"{base_name}.py",
            f"{base_name.lower()}.py",
            f"{base_name.title()}.py"
        ]
        
        for name in possible_names:
            # Use safe file finding instead of rglob to prevent infinite recursion
            source_files = self._safe_find_files(self.project_root, name)
            for source_file in source_files:
                # Skip if it's in a test directory
                if not any(test_dir in str(source_file) for test_dir in self.test_directories):
                    potential_sources.append(str(source_file.relative_to(self.project_root)))
        
        return potential_sources
    
    def _extract_imports(self, file_path: Path) -> List[str]:
        """Extract import statements from a Python file."""
        imports = []
        try:
            content = file_path.read_text(encoding='utf-8')
            import_lines = [
                line.strip() for line in content.split('\n') 
                if line.strip().startswith(('import ', 'from '))
            ]
            imports = import_lines[:10]  # Limit to first 10 imports
        except Exception:
            pass
        return imports
    
    def _extract_test_functions(self, file_path: Path) -> List[str]:
        """Extract test function names from a test file."""
        test_functions = []
        try:
            content = file_path.read_text(encoding='utf-8')
            # Find functions that start with 'test_' or 'test'
            function_pattern = r'def\s+(test\w*)\s*\('
            matches = re.findall(function_pattern, content)
            test_functions = matches[:20]  # Limit to first 20 functions
        except Exception:
            pass
        return test_functions
    
    def _path_to_module_name(self, file_path: Path) -> str:
        """Convert file path to Python module name."""
        relative_path = file_path.relative_to(self.project_root)
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        return '.'.join(module_parts)
