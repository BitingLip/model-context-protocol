"""
Project tree tool for the Biting Lip MCP server.
Provides functionality to visualize project directory structures.
"""

import os
import fnmatch
from contextlib import suppress
from typing import List, Optional


class ProjectTreeGenerator:
    """Generate visual tree structures of project directories."""
    
    def __init__(self, root_path: str, ignore_patterns: Optional[List[str]] = None, 
                 max_depth: Optional[int] = None):
        self.root_path = root_path
        self.ignore_patterns = ignore_patterns or []
        self.max_depth = max_depth
        self.ignored_folders = ['node_modules', '.git', '__pycache__', '.vscode', 'cache']
        
        # File extensions considered runnable
        self.runnable_exts = ('.py', '.sh', '.bat', '.ps1', '.exe', '.com', '.cmd')
        
    def _should_ignore(self, item_name: str, item_path: str) -> bool:
        """Check if an item should be ignored based on patterns."""
        # Check folder ignore list
        if os.path.isdir(item_path) and item_name in self.ignored_folders:
            return True
            
        # Check custom ignore patterns
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(item_name, pattern):
                return True
                
        return False
        
    def _load_gitignore_patterns(self, path: str) -> List[str]:
        """Load patterns from .gitignore file."""
        patterns = []
        gi_path = os.path.join(path, '.gitignore')
        if os.path.isfile(gi_path):
            with suppress(OSError):
                with open(gi_path) as gi:
                    for line in gi:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line.rstrip('/'))
        return patterns
        
    def _build_tree(self, path: str, indent_prefix: str = '', 
                   is_last_item: bool = True, current_depth: int = 0) -> str:
        """Build tree structure recursively."""
        if self.max_depth and current_depth >= self.max_depth:
            return ""
            
        # Load .gitignore patterns
        gitignore_patterns = self._load_gitignore_patterns(path)
        
        try:
            items = sorted(os.listdir(path), 
                          key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
        except OSError as e:
            return f"Error accessing {path}: {e}\n"
            
        tree_output = ""
        
        for i, item_name in enumerate(items):
            item_path = os.path.join(path, item_name)
            
            # Skip ignored items
            if self._should_ignore(item_name, item_path):
                continue
                
            is_last = (i == len(items) - 1)
            
            # Determine connector and child prefix
            connector = '└── ' if is_last else '├── '
            if indent_prefix == '':
                line_prefix = connector
                child_indent_prefix = '    ' if is_last else '│   '
            else:
                line_prefix = indent_prefix + connector
                child_indent_prefix = indent_prefix + ('    ' if is_last else '│   ')
                
            # Add markers for special files
            marker = ""
            if any(fnmatch.fnmatch(item_name, pat) for pat in gitignore_patterns):
                marker = " [ignored]"
            elif os.path.isfile(item_path) and item_name.lower().endswith(self.runnable_exts):
                marker = " [executable]"
                
            tree_output += f"{line_prefix}{item_name}{marker}\n"
            
            # Recurse into directories
            if os.path.isdir(item_path):
                tree_output += self._build_tree(item_path, child_indent_prefix, 
                                              is_last, current_depth + 1)
                
        return tree_output
        
    def generate(self) -> str:
        """Generate the complete project tree."""
        if not os.path.exists(self.root_path):
            return f"Error: Path '{self.root_path}' does not exist."
            
        # Start with root directory name
        root_name = os.path.basename(self.root_path) or self.root_path
        tree_output = f"{root_name}\n"
        
        # Generate tree structure
        tree_output += self._build_tree(self.root_path)
        
        return tree_output


def generate_project_tree(root_path: str, ignore_patterns: Optional[List[str]] = None,
                         max_depth: Optional[int] = None) -> str:
    """Convenience function to generate a project tree."""
    generator = ProjectTreeGenerator(root_path, ignore_patterns, max_depth)
    return generator.generate()
