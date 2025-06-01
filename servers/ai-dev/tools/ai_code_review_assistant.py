"""
AI Code Review Assistant Tool

This tool leverages local Ollama LLMs to perform comprehensive code reviews on git diffs
and changes. It analyzes code quality, identifies potential issues, suggests improvements,
and provides constructive feedback following best practices.

Features:
- Git diff analysis and change detection
- Code quality assessment (maintainability, readability, performance)
- Security vulnerability detection
- Best practices enforcement
- Automated code style and convention checking
- Integration with local Ollama models (Devstral, DeepSeek R1)
- Detailed review reports with actionable suggestions
"""

import ast
import json
import logging
import os
import re
import subprocess
import requests
from contextlib import suppress
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)


class AICodeReviewAssistant:
    """AI-powered code review assistant using local Ollama LLMs."""
    
    def __init__(self):
        # Use default Ollama configuration
        self.ollama_url = "http://localhost:11434"
        self.model = "deepseek-r1:8b"
        self.timeout = 30
        
    async def review_code(
        self,
        diff_content: Optional[str] = None,
        file_paths: Optional[List[str]] = None,
        review_types: Optional[List[str]] = None,
        severity_threshold: str = "medium"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive code review on git changes or specific files.
        
        Args:
            diff_content: Git diff content to review (if not provided, will get from git)
            file_paths: Specific files to review (if not using git diff)
            review_types: Types of review to perform (quality, security, style, performance)
            severity_threshold: Minimum severity level to report (low, medium, high, critical)
            
        Returns:
            Dictionary containing review results and recommendations
        """
        try:
            # Default review types
            if review_types is None:
                review_types = ["quality", "security", "style", "performance"]
            
            # Get diff content if not provided
            if diff_content is None and file_paths is None:
                diff_content = self._get_git_diff()
            elif file_paths:
                diff_content = self._create_file_diff(file_paths)
            
            if not diff_content:
                return {"error": "No changes found to review"}
            
            # Parse diff and extract changes
            changes = self._parse_diff(diff_content)
            
            # Analyze changes for different review aspects
            review_results = {}
            
            if "quality" in review_types:
                review_results["quality"] = await self._review_code_quality(changes)
            
            if "security" in review_types:
                review_results["security"] = await self._review_security(changes)
            
            if "style" in review_types:
                review_results["style"] = await self._review_code_style(changes)
            
            if "performance" in review_types:
                review_results["performance"] = await self._review_performance(changes)
            
            # Generate overall assessment
            overall_assessment = self._generate_overall_assessment(
                review_results, severity_threshold
            )
            
            # Create action plan
            action_plan = self._create_action_plan(review_results, severity_threshold)
            
            return {
                "success": True,
                "review_results": review_results,
                "overall_assessment": overall_assessment,
                "action_plan": action_plan,
                "changes_analyzed": len(changes),
                "ai_model": self.model,
                "metadata": {
                    "review_types": review_types,
                    "severity_threshold": severity_threshold,
                    "files_reviewed": list(set(change.get("file", "") for change in changes))
                }
            }
            
        except Exception as e:
            logger.error(f"Error during code review: {e}")
            return {"error": f"Code review failed: {str(e)}"}
    
    def _get_git_diff(self) -> str:
        """Get git diff for staged/unstaged changes."""
        try:
            # Try to get staged changes first
            result = subprocess.run(
                ["git", "diff", "--cached"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.stdout.strip():
                return result.stdout
            
            # If no staged changes, get unstaged changes
            result = subprocess.run(
                ["git", "diff"],
                capture_output=True,
                text=True,
                check=False
            )
            
            return result.stdout
            
        except Exception as e:
            logger.error(f"Failed to get git diff: {e}")
            return ""
    
    def _create_file_diff(self, file_paths: List[str]) -> str:
        """Create a pseudo-diff from file contents."""
        diff_content = ""
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    diff_content += f"--- a/{file_path}\n"
                    diff_content += f"+++ b/{file_path}\n"
                    
                    for i, line in enumerate(content.splitlines(), 1):
                        diff_content += f"+{i}: {line}\n"
                    
                    diff_content += "\n"
                    
                except Exception as e:
                    logger.error(f"Failed to read file {file_path}: {e}")
        
        return diff_content
    
    def _parse_diff(self, diff_content: str) -> List[Dict[str, Any]]:
        """Parse git diff content into structured changes."""
        changes = []
        current_file = None
        current_hunk = []
        
        for line in diff_content.splitlines():
            if line.startswith("--- a/") or line.startswith("--- /dev/null"):
                current_file = line[6:] if line.startswith("--- a/") else None
            elif line.startswith("+++ b/"):
                current_file = line[6:]
            elif line.startswith("@@"):
                if current_hunk and current_file:
                    changes.append({
                        "file": current_file,
                        "type": "modification",
                        "lines": current_hunk.copy()
                    })
                current_hunk = []
            elif line.startswith(("+", "-", " ")):
                current_hunk.append({
                    "type": "added" if line.startswith("+") else "removed" if line.startswith("-") else "context",
                    "content": line[1:],
                    "line_number": len(current_hunk) + 1
                })
        
        # Add final hunk
        if current_hunk and current_file:
            changes.append({
                "file": current_file,
                "type": "modification",
                "lines": current_hunk
            })
        
        return changes
    
    async def _review_code_quality(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Review code quality aspects."""
        try:
            # Extract added/modified code
            code_changes = []
            for change in changes:
                added_lines = [
                    line["content"] for line in change.get("lines", [])
                    if line["type"] == "added"
                ]
                if added_lines:
                    code_changes.append({
                        "file": change["file"],
                        "code": "\n".join(added_lines)
                    })
            
            if not code_changes:
                return {"issues": [], "suggestions": []}
            
            # Prepare code for AI review
            code_for_review = "\n\n".join([
                f"File: {change['file']}\n{change['code']}"
                for change in code_changes
            ])
            
            prompt = f"""
            Review the following code changes for quality issues:
            
            {code_for_review}
            
            Analyze for:
            1. Code complexity and readability
            2. Function/method design and single responsibility
            3. Variable naming and conventions
            4. Error handling and edge cases
            5. Code duplication and DRY principle
            6. Documentation and comments
            7. Maintainability concerns
            
            Provide specific, actionable feedback in JSON format:
            {{
                "issues": [
                    {{
                        "severity": "high|medium|low",
                        "category": "complexity|naming|structure|documentation",
                        "file": "filename",
                        "line": "line_number_if_applicable",
                        "description": "Specific issue description",
                        "suggestion": "How to fix this issue"
                    }}
                ],
                "overall_score": "score_out_of_10",
                "summary": "Overall quality assessment"
            }}
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
                ai_response = result.get("response", "{}")
                
                # Try to parse JSON response
                try:
                    return json.loads(ai_response)
                except json.JSONDecodeError:
                    # Fallback if AI doesn't return valid JSON
                    return {
                        "issues": [{"description": "AI review completed but response format was invalid"}],
                        "summary": ai_response[:500]  # First 500 chars
                    }
            else:
                return {"error": "AI service unavailable"}
                
        except Exception as e:
            logger.error(f"Code quality review failed: {e}")
            return {"error": f"Quality review error: {str(e)}"}
    
    async def _review_security(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Review security aspects of code changes."""
        try:
            security_patterns = {
                "sql_injection": [
                    r"execute\s*\(\s*[\"'].*%.*[\"']",
                    r"\.format\s*\(",
                    r"f[\"'].*\{.*\}.*[\"'].*execute"
                ],
                "hardcoded_secrets": [
                    r"password\s*=\s*[\"'][^\"']+[\"']",
                    r"api_key\s*=\s*[\"'][^\"']+[\"']",
                    r"secret\s*=\s*[\"'][^\"']+[\"']",
                    r"token\s*=\s*[\"'][^\"']+[\"']"
                ],
                "unsafe_deserialize": [
                    r"pickle\.loads?",
                    r"eval\s*\(",
                    r"exec\s*\("
                ],
                "path_traversal": [
                    r"open\s*\(\s*.*\+",
                    r"\.\./"
                ]
            }
            
            security_issues = []
            
            for change in changes:
                file_name = change["file"]
                for line in change.get("lines", []):
                    if line["type"] == "added":
                        content = line["content"]
                        
                        # Check for security patterns
                        for vulnerability_type, patterns in security_patterns.items():
                            for pattern in patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    security_issues.append({
                                        "severity": "high",
                                        "category": "security",
                                        "vulnerability_type": vulnerability_type,
                                        "file": file_name,
                                        "line": line["line_number"],
                                        "description": f"Potential {vulnerability_type.replace('_', ' ')} vulnerability",
                                        "code": content.strip(),
                                        "suggestion": self._get_security_suggestion(vulnerability_type)
                                    })
            
            return {
                "issues": security_issues,
                "vulnerabilities_found": len(security_issues),
                "security_score": max(0, 10 - len(security_issues) * 2)
            }
            
        except Exception as e:
            logger.error(f"Security review failed: {e}")
            return {"error": f"Security review error: {str(e)}"}
    
    async def _review_code_style(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Review code style and conventions."""
        try:
            style_issues = []
            
            for change in changes:
                file_name = change["file"]
                if not file_name.endswith('.py'):
                    continue
                
                for line in change.get("lines", []):
                    if line["type"] == "added":
                        content = line["content"]
                        line_num = line["line_number"]
                        
                        # Check various style issues
                        issues = self._check_style_issues(content, file_name, line_num)
                        style_issues.extend(issues)
            
            return {
                "issues": style_issues,
                "style_score": max(0, 10 - len(style_issues) * 0.5),
                "conventions_checked": ["PEP8", "naming", "imports", "whitespace"]
            }
            
        except Exception as e:
            logger.error(f"Style review failed: {e}")
            return {"error": f"Style review error: {str(e)}"}
    
    async def _review_performance(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Review performance aspects of code changes."""
        try:
            performance_issues = []
            
            performance_patterns = {
                "inefficient_loop": [
                    r"for.*in.*range\(len\(",
                    r"while.*len\("
                ],
                "repeated_computation": [
                    r"for.*in.*:.*\..*\(",
                    r"while.*:.*\..*\("
                ],
                "memory_inefficient": [
                    r"\[\].*for.*in",  # List comprehension that could be generator
                    r"\.append\(.*for.*in"  # Append in loop
                ]
            }
            
            for change in changes:
                file_name = change["file"]
                for line in change.get("lines", []):
                    if line["type"] == "added":
                        content = line["content"]
                        
                        # Check for performance anti-patterns
                        for issue_type, patterns in performance_patterns.items():
                            for pattern in patterns:
                                if re.search(pattern, content):
                                    performance_issues.append({
                                        "severity": "medium",
                                        "category": "performance",
                                        "issue_type": issue_type,
                                        "file": file_name,
                                        "line": line["line_number"],
                                        "description": f"Potential {issue_type.replace('_', ' ')} issue",
                                        "code": content.strip(),
                                        "suggestion": self._get_performance_suggestion(issue_type)
                                    })
            
            return {
                "issues": performance_issues,
                "performance_score": max(0, 10 - len(performance_issues))
            }
            
        except Exception as e:
            logger.error(f"Performance review failed: {e}")
            return {"error": f"Performance review error: {str(e)}"}
    
    def _check_style_issues(self, content: str, file_name: str, line_num: int) -> List[Dict[str, Any]]:
        """Check for code style issues in a line."""
        issues = []
        
        # Line length
        if len(content) > 88:  # PEP8 recommends 79, but 88 is common
            issues.append({
                "severity": "low",
                "category": "style",
                "issue_type": "line_length",
                "file": file_name,
                "line": line_num,
                "description": f"Line too long ({len(content)} characters)",
                "suggestion": "Break line into multiple lines or shorten variable names"
            })
        
        # Trailing whitespace
        if content.endswith(' ') or content.endswith('\t'):
            issues.append({
                "severity": "low",
                "category": "style",
                "issue_type": "trailing_whitespace",
                "file": file_name,
                "line": line_num,
                "description": "Trailing whitespace",
                "suggestion": "Remove trailing whitespace"
            })
        
        # Mixed tabs and spaces
        if '\t' in content and '    ' in content:
            issues.append({
                "severity": "medium",
                "category": "style",
                "issue_type": "mixed_indentation",
                "file": file_name,
                "line": line_num,
                "description": "Mixed tabs and spaces",
                "suggestion": "Use only spaces for indentation (4 spaces per level)"
            })
        
        # Variable naming (basic check)
        import_match = re.search(r'^\s*import\s+([A-Z])', content)
        if import_match:
            issues.append({
                "severity": "low",
                "category": "style",
                "issue_type": "import_naming",
                "file": file_name,
                "line": line_num,
                "description": "Module import should be lowercase",
                "suggestion": "Use lowercase module names"
            })
        
        return issues
    
    def _get_security_suggestion(self, vulnerability_type: str) -> str:
        """Get security improvement suggestion."""
        suggestions = {
            "sql_injection": "Use parameterized queries or ORM methods instead of string formatting",
            "hardcoded_secrets": "Move secrets to environment variables or secure configuration",
            "unsafe_deserialize": "Use safe alternatives like json.loads() or validate input",
            "path_traversal": "Validate and sanitize file paths, use os.path.join()"
        }
        return suggestions.get(vulnerability_type, "Review this potential security issue")
    
    def _get_performance_suggestion(self, issue_type: str) -> str:
        """Get performance improvement suggestion."""
        suggestions = {
            "inefficient_loop": "Use enumerate() or direct iteration instead of range(len())",
            "repeated_computation": "Cache the result outside the loop",
            "memory_inefficient": "Consider using generators or more efficient data structures"
        }
        return suggestions.get(issue_type, "Consider optimizing this code for better performance")
    
    def _generate_overall_assessment(
        self, 
        review_results: Dict[str, Any], 
        severity_threshold: str
    ) -> Dict[str, Any]:
        """Generate overall code review assessment."""
        all_issues = []
        total_score = 0
        score_count = 0
        
        # Collect all issues
        for review_type, results in review_results.items():
            if "issues" in results:
                all_issues.extend(results["issues"])
            
            # Collect scores
            if "score" in results:
                total_score += results["score"]
                score_count += 1
            elif f"{review_type}_score" in results:
                total_score += results[f"{review_type}_score"]
                score_count += 1
        
        # Filter by severity threshold
        severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        threshold_level = severity_order.get(severity_threshold, 1)
        
        filtered_issues = [
            issue for issue in all_issues
            if severity_order.get(issue.get("severity", "medium"), 1) >= threshold_level
        ]
        
        # Calculate overall score
        overall_score = round(total_score / max(score_count, 1), 1)
        
        # Determine approval status
        critical_issues = [i for i in filtered_issues if i.get("severity") == "critical"]
        high_issues = [i for i in filtered_issues if i.get("severity") == "high"]
        
        if critical_issues:
            approval = "blocked"
        elif len(high_issues) > 3:
            approval = "needs_work"
        elif overall_score >= 8:
            approval = "approved"
        elif overall_score >= 6:
            approval = "approved_with_comments"
        else:
            approval = "needs_work"
        
        return {
            "overall_score": overall_score,
            "approval_status": approval,
            "total_issues": len(all_issues),
            "filtered_issues": len(filtered_issues),
            "critical_issues": len(critical_issues),
            "high_issues": len(high_issues),
            "recommendation": self._get_approval_recommendation(approval, filtered_issues)
        }
    
    def _create_action_plan(
        self, 
        review_results: Dict[str, Any], 
        severity_threshold: str
    ) -> List[Dict[str, Any]]:
        """Create actionable plan for addressing review issues."""
        actions = []
        
        # Collect all issues
        all_issues = []
        for results in review_results.values():
            if "issues" in results:
                all_issues.extend(results["issues"])
        
        # Group by severity
        critical_issues = [i for i in all_issues if i.get("severity") == "critical"]
        high_issues = [i for i in all_issues if i.get("severity") == "high"]
        medium_issues = [i for i in all_issues if i.get("severity") == "medium"]
        
        # Create prioritized actions
        if critical_issues:
            actions.append({
                "priority": "immediate",
                "title": "Fix Critical Security Issues",
                "description": f"Address {len(critical_issues)} critical security vulnerabilities",
                "issues": critical_issues[:3],  # Show top 3
                "estimated_effort": "high"
            })
        
        if high_issues:
            actions.append({
                "priority": "high",
                "title": "Resolve High-Priority Issues",
                "description": f"Address {len(high_issues)} high-priority code quality issues",
                "issues": high_issues[:5],  # Show top 5
                "estimated_effort": "medium"
            })
        
        if len(medium_issues) > 5:
            actions.append({
                "priority": "medium",
                "title": "Code Style and Minor Improvements",
                "description": f"Address {len(medium_issues)} style and minor quality issues",
                "issues": medium_issues[:3],  # Show top 3
                "estimated_effort": "low"
            })
        
        return actions
    
    def _get_approval_recommendation(self, approval_status: str, issues: List[Dict[str, Any]]) -> str:
        """Get recommendation based on approval status."""
        recommendations = {
            "approved": "Code looks good! Ready to merge.",
            "approved_with_comments": "Code is acceptable but consider addressing the noted issues in future PRs.",
            "needs_work": "Several issues need to be addressed before merging.",
            "blocked": "Critical issues must be fixed before this can be merged."
        }
        
        base_rec = recommendations.get(approval_status, "Review completed.")
        
        if issues:
            issue_count = len(issues)
            base_rec += f" {issue_count} issue{'s' if issue_count != 1 else ''} found."
        
        return base_rec
