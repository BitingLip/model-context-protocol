#!/usr/bin/env python3
"""
Git information tool for MCP server.

Provides functionality to analyze git repository state including
branch information, commit history, and project status.
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any


class GitAnalyzer:
    """Analyzes git repository information."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
    
    def get_git_info(self, info_type: str = "all") -> Dict[str, Any]:
        """
        Get git repository information.
        
        Args:
            info_type: Type of info - 'all', 'status', 'branches', 'commits', 'remote'
            
        Returns:
            Dictionary with git information
        """
        try:
            if not self._is_git_repo():
                return {
                    "error": "Not a git repository",
                    "is_git_repo": False
                }
            
            if info_type == "status":
                return self._get_git_status()
            elif info_type == "branches":
                return self._get_branch_info()
            elif info_type == "commits":
                return self._get_commit_history()
            elif info_type == "remote":
                return self._get_remote_info()
            else:
                return self._get_all_git_info()
        except Exception as e:
            return {
                "error": f"Failed to get git info: {str(e)}",
                "is_git_repo": False
            }
    
    def _is_git_repo(self) -> bool:
        """Check if the project is a git repository."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_all_git_info(self) -> Dict[str, Any]:
        """Get comprehensive git repository information."""
        status = self._get_git_status()
        branches = self._get_branch_info()
        commits = self._get_commit_history(limit=10)
        remote = self._get_remote_info()
        
        return {
            "is_git_repo": True,
            "status": status,
            "branches": branches,
            "recent_commits": commits,
            "remote": remote,
            "summary": {
                "current_branch": status.get("current_branch"),
                "total_branches": len(branches.get("all_branches", [])),
                "modified_files": len(status.get("modified_files", [])),
                "untracked_files": len(status.get("untracked_files", [])),
                "has_remote": bool(remote.get("remotes"))
            }
        }
    
    def _get_git_status(self) -> Dict[str, Any]:
        """Get git status information."""
        try:
            # Get current branch
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            
            # Get status --porcelain for machine-readable output
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            modified_files = []
            untracked_files = []
            staged_files = []
            
            if status_result.returncode == 0:
                for line in status_result.stdout.strip().split('\n'):
                    if line:
                        status_code = line[:2]
                        file_path = line[3:]
                        
                        if status_code[0] in ['M', 'A', 'D', 'R', 'C']:
                            staged_files.append({
                                "file": file_path,
                                "status": self._parse_status_code(status_code[0])
                            })
                        
                        if status_code[1] == 'M':
                            modified_files.append(file_path)
                        elif status_code == '??':
                            untracked_files.append(file_path)
            
            # Get last commit info
            last_commit = self._get_last_commit()
            
            # Check if there are any commits
            has_commits = self._has_commits()
            
            return {
                "current_branch": current_branch,
                "modified_files": modified_files,
                "untracked_files": untracked_files,
                "staged_files": staged_files,
                "is_clean": not modified_files and not untracked_files and not staged_files,
                "last_commit": last_commit,
                "has_commits": has_commits
            }
            
        except Exception as e:
            return {"error": f"Failed to get git status: {str(e)}"}
    
    def _get_branch_info(self) -> Dict[str, Any]:
        """Get git branch information."""
        try:
            # Get all branches
            branch_result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            local_branches = []
            remote_branches = []
            current_branch = None
            
            if branch_result.returncode == 0:
                for line in branch_result.stdout.strip().split('\n'):
                    if (line := line.strip()):
                        if line.startswith('* '):
                            current_branch = line[2:]
                            local_branches.append(current_branch)
                        elif line.startswith('remotes/'):
                            remote_branches.append(line[8:])  # Remove 'remotes/' prefix
                        else:
                            local_branches.append(line)
            
            # Get branch tracking info
            tracking_info = {}
            for branch in local_branches:
                if branch and branch != current_branch:
                    try:
                        tracking_result = subprocess.run(
                            ['git', 'rev-list', '--count', '--left-right', f'{branch}...origin/{branch}'],
                            cwd=self.project_root,
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if tracking_result.returncode == 0:
                            ahead_behind = tracking_result.stdout.strip().split('\t')
                            if len(ahead_behind) == 2:
                                tracking_info[branch] = {
                                    "ahead": int(ahead_behind[0]),
                                    "behind": int(ahead_behind[1])
                                }
                    except Exception:
                        continue
            
            return {
                "current_branch": current_branch,
                "local_branches": local_branches,
                "remote_branches": remote_branches,
                "all_branches": local_branches + remote_branches,
                "tracking_info": tracking_info
            }
            
        except Exception as e:
            return {"error": f"Failed to get branch info: {str(e)}"}
    
    def _get_commit_history(self, limit: int = 20) -> Dict[str, Any]:
        """Get git commit history."""
        try:
            # Get commit log with formatting
            log_result = subprocess.run(
                ['git', 'log', f'-{limit}', '--pretty=format:%H|%an|%ae|%ad|%s', '--date=iso'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            commits = []
            if log_result.returncode == 0:
                for line in log_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|', 4)
                        if len(parts) == 5:
                            commits.append({
                                "hash": parts[0][:8],  # Short hash
                                "full_hash": parts[0],
                                "author": parts[1],
                                "email": parts[2],
                                "date": parts[3],
                                "message": parts[4]
                            })
            
            # Get commit statistics
            stats = self._get_commit_stats()
            
            return {
                "commits": commits,
                "total_shown": len(commits),
                "stats": stats
            }
            
        except Exception as e:
            return {"error": f"Failed to get commit history: {str(e)}"}
    
    def _get_remote_info(self) -> Dict[str, Any]:
        """Get git remote information."""
        try:
            # Get remotes
            remote_result = subprocess.run(
                ['git', 'remote', '-v'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            remotes = {}
            if remote_result.returncode == 0:
                for line in remote_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if len(parts) >= 3:
                            name = parts[0]
                            url = parts[1]
                            operation = parts[2].strip('()')
                            
                            if name not in remotes:
                                remotes[name] = {}
                            remotes[name][operation] = url
            
            # Get remote tracking branch info
            tracking_branch = None
            from contextlib import suppress
            with suppress(Exception):
                tracking_result = subprocess.run(
                    ['git', 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if tracking_result.returncode == 0:
                    tracking_branch = tracking_result.stdout.strip()
            
            return {
                "remotes": remotes,
                "tracking_branch": tracking_branch,
                "has_origin": "origin" in remotes
            }
            
        except Exception as e:
            return {"error": f"Failed to get remote info: {str(e)}"}
    
    def _get_last_commit(self) -> Optional[Dict[str, Any]]:
        """Get information about the last commit."""
        from contextlib import suppress
        with suppress(Exception):
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%H|%an|%ae|%ad|%s', '--date=iso'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split('|', 4)
                if len(parts) == 5:
                    return {
                        "hash": parts[0][:8],
                        "full_hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    }
        return None
    
    def _has_commits(self) -> bool:
        """Check if the repository has any commits."""
        try:
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0 and result.stdout.strip() != '0'
        except Exception:
            return False
    
    def _get_commit_stats(self) -> Dict[str, Any]:
        """Get commit statistics."""
        try:
            # Total commit count
            count_result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            total_commits = int(count_result.stdout.strip()) if count_result.returncode == 0 else 0
            
            # Contributors
            contributors_result = subprocess.run(
                ['git', 'shortlog', '-sn', '--all'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            contributors = []
            if contributors_result.returncode == 0:
                for line in contributors_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.strip().split('\t', 1)
                        if len(parts) == 2:
                            contributors.append({
                                "commits": int(parts[0]),
                                "name": parts[1]
                            })
            
            return {
                "total_commits": total_commits,
                "contributors": contributors,
                "total_contributors": len(contributors)
            }
            
        except Exception:
            return {
                "total_commits": 0,
                "contributors": [],
                "total_contributors": 0
            }
    
    def _parse_status_code(self, code: str) -> str:
        """Parse git status code to human-readable string."""
        status_map = {
            'M': 'modified',
            'A': 'added',
            'D': 'deleted',
            'R': 'renamed',
            'C': 'copied',
            'U': 'updated',
            '?': 'untracked'
        }
        return status_map.get(code, 'unknown')
