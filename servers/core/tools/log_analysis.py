"""
Log Analysis Tool for Biting Lip MCP Server.

This tool analyzes application logs, error patterns, performance metrics,
and security events across different log formats and sources.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class LogAnalysis:
    """Analyzes application logs and patterns."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        
    def _get_filtered_files(self, pattern: str):
        """Get files matching pattern excluding common irrelevant directories."""
        excluded_dirs = {
            'node_modules', '.git', '__pycache__', '.pytest_cache', 'venv', 'env', 
            '.venv', '.env', 'build', 'dist', '.tox', 'site-packages', '.mypy_cache',
            '.cache', 'coverage', '.next'
        }
        
        for file_path in self.project_root.rglob(pattern):
            if all(excluded_dir not in file_path.parts for excluded_dir in excluded_dirs):
                yield file_path
        
    def analyze_logs(self, log_type: Optional[str] = None, time_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Analyze logs across the project.
        
        Args:
            log_type: Specific log type to analyze (error, access, application, system)
            time_range: Time range filter with 'start' and 'end' datetime strings
            
        Returns:
            Dictionary containing log analysis results
        """
        try:
            analysis = {
                "summary": {
                    "log_files_found": 0,
                    "total_entries": 0,
                    "error_count": 0,
                    "warning_count": 0,
                    "time_range_analyzed": {},
                    "log_types_found": []
                },
                "logs": {},
                "patterns": {
                    "errors": [],
                    "warnings": [],
                    "performance_issues": [],
                    "security_events": []
                },
                "analysis_metadata": {
                    "project_root": str(self.project_root),
                    "supported_formats": [
                        "apache", "nginx", "python", "nodejs", "django", "flask", "json", "syslog"
                    ]
                }
            }
            
            # Find and analyze log files
            log_files = self._find_log_files()
            
            for log_file in log_files:
                try:
                    if log_data := self._analyze_log_file(log_file, log_type, time_range):
                        file_key = str(log_file.relative_to(self.project_root))
                        analysis["logs"][file_key] = log_data
                        
                        # Update summary
                        analysis["summary"]["log_files_found"] += 1
                        analysis["summary"]["total_entries"] += log_data.get("entry_count", 0)
                        analysis["summary"]["error_count"] += log_data.get("error_count", 0)
                        analysis["summary"]["warning_count"] += log_data.get("warning_count", 0)
                        
                        # Collect patterns
                        self._collect_patterns(log_data, analysis["patterns"])
                        
                except Exception as e:
                    logger.warning(f"Error analyzing log file {log_file}: {e}")
            
            # Analyze patterns across all logs
            self._analyze_cross_log_patterns(analysis)
            
            # Calculate time range
            self._calculate_time_range(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing logs: {e}")
            return {"error": str(e)}
    
    def _find_log_files(self) -> List[Path]:
        """Find all log files in the project."""
        log_files = []
        
        # Common log file patterns
        log_patterns = [
            "*.log",
            "*.log.*",
            "logs/*.log",
            "logs/*.txt",
            "log/*.log",
            "**/access.log*",
            "**/error.log*",
            "**/application.log*",
            "**/debug.log*",
            "**/server.log*",
            "**/django*.log",
            "**/flask*.log",
            "**/gunicorn*.log",
            "**/nginx*.log",
            "**/apache*.log"
        ]
        
        for pattern in log_patterns:
            log_files.extend(
                [log_file for log_file in self._get_filtered_files(pattern)
                 if log_file.is_file() and log_file.stat().st_size > 0]
            )
        
        return list(set(log_files))  # Remove duplicates
    
    def _sample_log_file(self, log_file: Path, max_lines: int = 1000) -> List[str]:
        """Sample a large log file to analyze a portion of it."""
        try:
            # Get file size
            file_size = log_file.stat().st_size
            
            # For small files, just read everything
            if file_size < 1 * 1024 * 1024:  # 1MB
                return log_file.read_text(encoding='utf-8', errors='ignore').splitlines()
                
            # For large files, sample from beginning, middle and end
            lines = []
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                # Read first third of max_lines
                first_chunk = max_lines // 3
                lines.extend([f.readline().strip() for _ in range(first_chunk)])
                
                # Jump to middle
                from contextlib import suppress
                with suppress(Exception):
                    f.seek(int(file_size / 2))
                    # Read a line to align to line boundary
                    f.readline()
                    # Read middle third
                    lines.extend([f.readline().strip() for _ in range(first_chunk)])
                    
                # Jump to end minus a buffer
                with suppress(Exception):
                    f.seek(max(0, file_size - 50000))  # 50KB from end
                    # Read a line to align to line boundary
                    f.readline()
                    # Read end third
                    lines.extend([f.readline().strip() for _ in range(first_chunk)])
                    
            return [line for line in lines if line]  # Filter out empty lines
            
        except Exception as e:
            logger.warning(f"Error sampling log file {log_file}: {e}")
            return []
    
    def _analyze_log_file(self, log_file: Path, log_type: Optional[str] = None, 
                         time_range: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Analyze a single log file."""
        try:
            # Check file size first - skip files > 10MB
            file_size = log_file.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB
                logger.warning(f"Skipping large log file {log_file}: {file_size/1024/1024:.2f}MB")
                return {
                    "file_path": str(log_file.relative_to(self.project_root)),
                    "file_size": file_size,
                    "skipped": True,
                    "reason": "File too large",
                    "entry_count": 0,
                    "error_count": 0,
                    "warning_count": 0
                }
                
            # Determine log format
            log_format = self._detect_log_format(log_file)
            
            # Filter by log type if specified
            if log_type and not self._matches_log_type(log_file, log_format, log_type):
                return None
            
            log_data = {
                "file_path": str(log_file.relative_to(self.project_root)),
                "file_size": log_file.stat().st_size,
                "format": log_format,
                "entry_count": 0,
                "error_count": 0,
                "warning_count": 0,
                "info_count": 0,
                "entries": [],
                "error_patterns": [],
                "performance_metrics": {},
                "time_range": {}
            }
            
            # Parse log entries
            entries = self._parse_log_entries(log_file, log_format, time_range)
            
            # Analyze entries
            for entry in entries:
                log_data["entry_count"] += 1
                
                # Count by severity
                severity = entry.get("level", "unknown").lower()
                if severity in ["error", "err", "fatal", "critical"]:
                    log_data["error_count"] += 1
                elif severity in ["warning", "warn"]:
                    log_data["warning_count"] += 1
                elif severity in ["info", "information"]:
                    log_data["info_count"] += 1
                
                # Collect entry for detailed analysis
                if log_data["entry_count"] <= 100:  # Limit to avoid huge responses
                    log_data["entries"].append(entry)
            
            # Analyze patterns and metrics
            self._analyze_error_patterns(entries, log_data)
            self._analyze_performance_metrics(entries, log_data)
            self._calculate_entry_time_range(entries, log_data)
            
            return log_data
            
        except Exception as e:
            logger.warning(f"Error analyzing log file {log_file}: {e}")
            return None
    
    def _detect_log_format(self, log_file: Path) -> str:
        """Detect the format of a log file."""
        try:
            # Read first few lines to detect format
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                sample_lines = [f.readline().strip() for _ in range(5)]
            
            content = '\n'.join(sample_lines)
            
            # Check for common log formats
            if any('combined' in line.lower() or 'common' in line.lower() for line in sample_lines):
                return "apache"
            elif re.search(r'\d+\.\d+\.\d+\.\d+ - - \[', content):
                return "apache"
            elif re.search(r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', content):
                return "nginx"
            elif re.search(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', content):
                return "python"
            elif content.strip().startswith('{') and content.strip().endswith('}'):
                return "json"            
            elif re.search(r'DEBUG|INFO|WARNING|ERROR|CRITICAL', content):
                return "python"
            elif re.search(r'GET|POST|PUT|DELETE|HEAD|OPTIONS', content):
                return "access"
            else:
                return "generic"
                
        except Exception:
            return "unknown"
    
    def _matches_log_type(self, log_file: Path, log_format: str, log_type: str) -> bool:
        """Check if log file matches the specified type."""
        file_name = log_file.name.lower()
        
        type_patterns = {
            "error": ["error", "err", "exception"],
            "access": ["access", "request", "http"],
            "application": ["app", "application", "debug"],
            "system": ["system", "sys", "syslog"]
        }
        
        if log_type.lower() in type_patterns:
            patterns = type_patterns[log_type.lower()]
            return any(pattern in file_name for pattern in patterns)
        
        return True  # If unknown type, include all
    
    def _parse_log_entries(self, log_file: Path, log_format: str, 
                          time_range: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Parse log entries from a file."""
        entries = []
        
        try:
            # Use sampling for efficiency
            lines = self._sample_log_file(log_file, max_lines=2000)
            
            for line_num, line in enumerate(lines, 1):
                if not line:
                    continue
                
                if entry := self._parse_log_entry(line, log_format, line_num):
                    # Filter by time range if specified
                    if time_range and not self._entry_in_time_range(entry, time_range):
                        continue
                    
                    entries.append(entry)
                    
                    # Limit number of entries to avoid memory issues
                    if len(entries) >= 1000:
                        break
        
        except Exception as e:
            logger.warning(f"Error parsing log file {log_file}: {e}")
        
        return entries
    
    def _parse_log_entry(self, line: str, log_format: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single log entry."""
        entry = {
            "line_number": line_num,
            "raw": line,
            "timestamp": None,
            "level": "unknown",
            "message": line,
            "source": None
        }

        try:
            if log_format == "json":
                if (data := self._try_parse_json(line)):
                    entry = entry | {
                        "timestamp": data.get("timestamp") or data.get("time") or data.get("@timestamp"),
                        "level": data.get("level") or data.get("severity"),
                        "message": data.get("message") or data.get("msg"),
                        "source": data.get("source") or data.get("logger"),
                        "extra": {k: v for k, v in data.items()
                                  if k not in ["timestamp", "time", "@timestamp", "level", "severity", "message", "msg", "source", "logger"]}
                    }
                    return entry

            patterns = {
                "python": (
                    r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:,\d{3})?)\s*-\s*([^-]+)\s*-\s*(\w+)\s*-\s*(.+)$',
                    lambda m: {
                        "timestamp": m.group(1),
                        "source": m.group(2).strip(),
                        "level": m.group(3).strip(),
                        "message": m.group(4).strip()
                    }
                ),
                "apache": (
                    r'^(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\S+)',
                    lambda m: {
                        "ip": m.group(1),
                        "timestamp": m.group(2),
                        "method": m.group(3),
                        "url": m.group(4),
                        "protocol": m.group(5),
                        "status": int(m.group(6)),
                        "size": m.group(7),
                        "level": "info" if int(m.group(6)) < 400 else "error"
                    }
                ),
                "nginx": (
                    r'^(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (.+)',
                    lambda m: {
                        "timestamp": m.group(1),
                        "level": m.group(2),
                        "message": m.group(3)
                    }
                )
            }

            if log_format in patterns:
                pattern, updater = patterns[log_format]
                if (match := re.match(pattern, line)):
                    entry.update(updater(match))
                    return entry

            # Generic parsing - look for common patterns
            timestamp_patterns = [
                r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d{3})?)',
                r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})',
                r'(\w{3} \d{2} \d{2}:\d{2}:\d{2})'
            ]
            for pattern in timestamp_patterns:
                if (match := re.search(pattern, line)):
                    entry["timestamp"] = match.group(1)
                    break

            level_pattern = r'\b(DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL|TRACE)\b'
            if (level_match := re.search(level_pattern, line, re.IGNORECASE)):
                entry["level"] = level_match.group(1).upper()

            return entry

        except Exception as e:
            logger.debug(f"Error parsing log entry: {e}")
            return entry  # Return basic entry even if parsing fails

    def _try_parse_json(self, line: str) -> Optional[dict]:
        """Try to parse a line as JSON, suppressing errors."""
        from contextlib import suppress
        with suppress(Exception):
            return json.loads(line)
        return None
    
    def _entry_in_time_range(self, entry: Dict[str, Any], time_range: Dict[str, str]) -> bool:
        """Check if log entry falls within specified time range."""
        if not entry.get("timestamp"):
            return True  # Include entries without timestamps
        
        try:
            entry_time = entry["timestamp"]
            start_time = time_range.get("start")
            end_time = time_range.get("end")

            if (start_time and entry_time < start_time) or (end_time and entry_time > end_time):
                return False
            return True

        except Exception:
            return True  # Include entries if time parsing fails
    
    def _analyze_error_patterns(self, entries: List[Dict[str, Any]], log_data: Dict[str, Any]) -> None:
        """Analyze error patterns in log entries."""
        error_messages = [
            entry.get("message", "")
            for entry in entries
            if entry.get("level", "").lower() in ["error", "err", "fatal", "critical"]
        ]
        
        # Find common error patterns
        pattern_counts = Counter()
        
        for message in error_messages:
            # Extract patterns (simplified - would use more sophisticated pattern recognition)
            # Remove specific values like IDs, timestamps, etc.
            pattern = re.sub(r'\d+', 'N', message)
            pattern = re.sub(r'[a-f0-9]{8,}', 'HASH', pattern)
            pattern = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'IP', pattern)
            
            pattern_counts[pattern] += 1
        
        # Store top error patterns
        log_data["error_patterns"] = [
            {"pattern": pattern, "count": count}
            for pattern, count in pattern_counts.most_common(10)
        ]
    
    def _analyze_performance_metrics(self, entries: List[Dict[str, Any]], log_data: Dict[str, Any]) -> None:
        """Analyze performance metrics from log entries."""
        response_times = []
        status_codes = Counter()
        
        for entry in entries:
            # Extract response times (look for common patterns)
            message = entry.get("message", "")
            
            # Look for response time patterns
            time_patterns = [
                r'(\d+(?:\.\d+)?)ms',
                r'(\d+(?:\.\d+)?)s',
                r'time=(\d+(?:\.\d+)?)',
                r'duration=(\d+(?:\.\d+)?)'
            ]
            
            for pattern in time_patterns:
                if (match := re.search(pattern, message)):
                    try:
                        time_value = float(match[1])
                        response_times.append(time_value)
                        break
                    except ValueError:
                        continue
            
            # Count status codes
            if "status" in entry:
                status_codes[entry["status"]] += 1
        
        # Calculate performance metrics
        if response_times:
            log_data["performance_metrics"] = {
                "avg_response_time": sum(response_times) / len(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "response_time_samples": len(response_times)
            }
        
        if status_codes:
            log_data["status_code_distribution"] = dict(status_codes.most_common(10))
    
    def _calculate_entry_time_range(self, entries: List[Dict[str, Any]], log_data: Dict[str, Any]) -> None:
        """Calculate time range of log entries."""
        timestamps = [ts for entry in entries if (ts := entry.get("timestamp"))]
        
        if timestamps:
            log_data["time_range"] = {
                "start": min(timestamps),
                "end": max(timestamps),
                "total_entries": len(timestamps)
            }
    
    def _collect_patterns(self, log_data: Dict[str, Any], patterns: Dict[str, List]) -> None:
        """Collect patterns from log data for cross-log analysis."""
        # Collect error patterns
        if "error_patterns" in log_data:
            for pattern_info in log_data["error_patterns"]:
                patterns["errors"].append({
                    "file": log_data["file_path"],
                    "pattern": pattern_info["pattern"],
                    "count": pattern_info["count"]
                })
        
        # Collect performance issues
        perf_metrics = log_data.get("performance_metrics", {})
        if perf_metrics.get("max_response_time", 0) > 5000:  # > 5 seconds
            patterns["performance_issues"].append({
                "file": log_data["file_path"],
                "issue": "High response time",
                "max_time": perf_metrics["max_response_time"]
            })
    
    def _analyze_cross_log_patterns(self, analysis: Dict[str, Any]) -> None:
        """Analyze patterns across all log files."""
        # Find common errors across files
        error_patterns = defaultdict(list)
        
        for error in analysis["patterns"]["errors"]:
            error_patterns[error["pattern"]].append(error)
        
        # Find patterns that appear in multiple files
        cross_file_errors = [
            {
                "pattern": pattern,
                "files": list({occ["file"] for occ in occurrences}),
                "total_count": sum(occ["count"] for occ in occurrences)
            }
            for pattern, occurrences in error_patterns.items()
            if len({occ["file"] for occ in occurrences}) > 1
        ]
        
        analysis["patterns"]["cross_file_errors"] = cross_file_errors
    
    def _calculate_time_range(self, analysis: Dict[str, Any]) -> None:
        """Calculate overall time range across all logs."""
        all_start_times = []
        all_end_times = []
        
        for log_data in analysis["logs"].values():
            time_range = log_data.get("time_range", {})
            if time_range.get("start"):
                all_start_times.append(time_range["start"])
            if time_range.get("end"):
                all_end_times.append(time_range["end"])
        
        if all_start_times and all_end_times:
            analysis["summary"]["time_range_analyzed"] = {
                "start": min(all_start_times),
                "end": max(all_end_times)
            }
    
    def analyze_error_trends(self, hours: int = 24) -> Dict[str, Any]:
        """
        Analyze error trends over a specified time period.
        
        Args:
            hours: Number of hours to analyze (default: 24)
            
        Returns:
            Dictionary with error trend analysis
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            time_range = {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            }
            
            # Analyze logs with time filter
            log_analysis = self.analyze_logs(log_type="error", time_range=time_range)
            
            trend_analysis = {
                "time_period": f"{hours} hours",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "error_summary": {
                    "total_errors": log_analysis["summary"]["error_count"],
                    "files_with_errors": len([f for f in log_analysis["logs"].values() if f["error_count"] > 0]),
                },
                "top_error_patterns": [],
                "error_distribution": {}
            }
            
            # Collect all error patterns
            all_patterns = list(log_analysis["patterns"]["errors"])
            
            # Sort by count and get top patterns
            all_patterns.sort(key=lambda x: x["count"], reverse=True)
            trend_analysis["top_error_patterns"] = all_patterns[:10]
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing error trends: {e}")
            return {"error": str(e)}
    
    def search_logs(self, search_term: str, case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Search for specific terms across all log files.
        
        Args:
            search_term: Term to search for
            case_sensitive: Whether search should be case sensitive
            
        Returns:
            Dictionary with search results
        """
        try:
            search_results = {
                "search_term": search_term,
                "case_sensitive": case_sensitive,
                "matches": [],
                "summary": {
                    "total_matches": 0,
                    "files_with_matches": 0
                }
            }
            
            log_files = self._find_log_files()
            
            for log_file in log_files:
                if file_matches := self._search_in_file(log_file, search_term, case_sensitive):
                    search_results["matches"].append({
                        "file": str(log_file.relative_to(self.project_root)),
                        "matches": file_matches
                    })
                    search_results["summary"]["total_matches"] += len(file_matches)
                    search_results["summary"]["files_with_matches"] += 1
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching logs: {e}")
            return {"error": str(e)}
    
    def _search_in_file(self, log_file: Path, search_term: str, case_sensitive: bool) -> List[Dict[str, Any]]:
        """Search for term in a specific log file."""
        matches = []
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line_to_search = line if case_sensitive else line.lower()
                    term_to_search = search_term if case_sensitive else search_term.lower()
                    
                    if term_to_search in line_to_search:
                        matches.append({
                            "line_number": line_num,
                            "content": line.strip(),
                            "match_position": line_to_search.find(term_to_search)
                        })
                    
                    # Limit matches per file to avoid huge responses
                    if len(matches) >= 50:
                        break
        
        except Exception as e:
            logger.warning(f"Error searching in file {log_file}: {e}")
        
        return matches
