"""
Configuration file analysis tools for the Biting Lip platform.
"""

import os
import json
import yaml
import configparser
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import re


class ConfigAnalyzer:
    """Analyze configuration files in the Biting Lip platform."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
    
    def analyze_config_files(self, target_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze configuration files in the project.
        
        Args:
            target_path: Specific path to analyze, defaults to project root
            
        Returns:
            Dict containing analysis of all configuration files found.
        """
        search_path = Path(target_path) if target_path else self.project_root
        
        config_analysis = {
            "environment_files": self._analyze_env_files(search_path),
            "yaml_configs": self._analyze_yaml_files(search_path),
            "json_configs": self._analyze_json_files(search_path),
            "python_configs": self._analyze_python_configs(search_path),
            "docker_configs": self._analyze_docker_configs(search_path),
            "service_configs": self._analyze_service_configs(),
            "summary": {}
        }
        
        # Generate summary
        total_files = sum(
            len(config_analysis[category]) 
            for category in config_analysis 
            if isinstance(config_analysis[category], dict) and category != "summary"
        )
        
        config_analysis["summary"] = {
            "total_config_files": total_files,
            "environment_files": len(config_analysis["environment_files"]),
            "yaml_files": len(config_analysis["yaml_configs"]),
            "json_files": len(config_analysis["json_configs"]),
            "python_configs": len(config_analysis["python_configs"]),
            "docker_configs": len(config_analysis["docker_configs"]),
            "service_configs": len(config_analysis["service_configs"])
        }
        
        return config_analysis
    
    def _analyze_env_files(self, search_path: Path) -> Dict[str, Any]:
        """Analyze .env files in the project."""
        env_files = {}
        
        # Find all .env files
        for env_file in search_path.rglob("*.env"):
            if env_file.is_file():
                rel_path = str(env_file.relative_to(self.project_root))
                env_files[rel_path] = self._parse_env_file(env_file)
        
        return env_files
    
    def _analyze_yaml_files(self, search_path: Path) -> Dict[str, Any]:
        """Analyze YAML configuration files."""
        yaml_files = {}
        
        # Find YAML files (excluding docker-compose files which are handled separately)
        for yaml_file in search_path.rglob("*.yml"):
            if yaml_file.is_file() and "docker-compose" not in yaml_file.name:
                rel_path = str(yaml_file.relative_to(self.project_root))
                yaml_files[rel_path] = self._parse_yaml_file(yaml_file)
        
        for yaml_file in search_path.rglob("*.yaml"):
            if yaml_file.is_file() and "docker-compose" not in yaml_file.name:
                rel_path = str(yaml_file.relative_to(self.project_root))
                yaml_files[rel_path] = self._parse_yaml_file(yaml_file)
        
        return yaml_files
    
    def _analyze_json_files(self, search_path: Path) -> Dict[str, Any]:
        """Analyze JSON configuration files."""
        json_files = {}
        
        # Common config file names
        config_patterns = [
            "*.config.json", "config.json", "settings.json", 
            "mcp_config.json", "tsconfig.json", "package.json"
        ]
        
        for pattern in config_patterns:
            for json_file in search_path.rglob(pattern):
                if json_file.is_file():
                    rel_path = str(json_file.relative_to(self.project_root))
                    json_files[rel_path] = self._parse_json_file(json_file)
        
        return json_files
    
    def _analyze_python_configs(self, search_path: Path) -> Dict[str, Any]:
        """Analyze Python configuration files."""
        python_configs = {}
        
        # Look for common Python config files
        config_files = [
            "config.py", "settings.py", "central_config.py", 
            "config_validator.py", "service_discovery.py"
        ]
        
        for config_file in config_files:
            for py_file in search_path.rglob(config_file):
                if py_file.is_file():
                    rel_path = str(py_file.relative_to(self.project_root))
                    python_configs[rel_path] = self._analyze_python_config_file(py_file)
        
        return python_configs
    
    def _analyze_docker_configs(self, search_path: Path) -> Dict[str, Any]:
        """Analyze Docker-related configuration files."""
        docker_configs = {}
        
        # Find Docker files
        for docker_file in search_path.rglob("docker-compose*.yml"):
            if docker_file.is_file():
                rel_path = str(docker_file.relative_to(self.project_root))
                docker_configs[rel_path] = self._parse_docker_compose(docker_file)
        
        for docker_file in search_path.rglob("Dockerfile*"):
            if docker_file.is_file():
                rel_path = str(docker_file.relative_to(self.project_root))
                docker_configs[rel_path] = self._parse_dockerfile(docker_file)
        
        return docker_configs
    
    def _analyze_service_configs(self) -> Dict[str, Any]:
        """Analyze service-specific configuration files."""
        service_configs = {}
        
        services_config_dir = self.config_dir / "services"
        if services_config_dir.exists():
            for service_file in services_config_dir.glob("*.env"):
                service_name = service_file.stem
                service_configs[service_name] = self._parse_env_file(service_file)
        
        return service_configs
    
    def _parse_env_file(self, env_file: Path) -> Dict[str, Any]:
        """Parse an environment file."""
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            variables = {}
            comments = []
            sections = []
            
            current_section = None
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                if not line:
                    continue
                elif line.startswith('#'):
                    comment = line[1:].strip()
                    if comment.isupper() and all(c not in comment for c in ['=', ' ']):
                        # Likely a section header
                        current_section = comment
                        sections.append(comment)
                    else:
                        comments.append(comment)
                elif '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    
                    var_info = {
                        "value": value,
                        "line": line_num,
                        "section": current_section
                    }
                    
                    # Try to infer variable type
                    if value.lower() in ('true', 'false'):
                        var_info["type"] = "boolean"
                    elif value.isdigit():
                        var_info["type"] = "integer"
                    elif self._is_url(value):
                        var_info["type"] = "url"
                    elif self._is_path(value):
                        var_info["type"] = "path"
                    else:
                        var_info["type"] = "string"
                    
                    variables[key] = var_info
            
            return {
                "type": "environment",
                "variables": variables,
                "sections": sections,
                "comments": comments,
                "variable_count": len(variables)
            }
        
        except Exception as e:
            return {"error": f"Failed to parse {env_file}: {str(e)}"}
    
    def _parse_yaml_file(self, yaml_file: Path) -> Dict[str, Any]:
        """Parse a YAML configuration file."""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            return {
                "type": "yaml",
                "content": content,
                "keys": list(content.keys()) if isinstance(content, dict) else [],
                "structure": self._analyze_yaml_structure(content)
            }
        
        except Exception as e:
            return {"error": f"Failed to parse {yaml_file}: {str(e)}"}
    
    def _parse_json_file(self, json_file: Path) -> Dict[str, Any]:
        """Parse a JSON configuration file."""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            analysis = {
                "type": "json",
                "content": content,
                "keys": list(content.keys()) if isinstance(content, dict) else [],
            }
            
            # Special handling for specific file types
            if json_file.name == "package.json":
                analysis["package_info"] = self._analyze_package_json(content)
            elif json_file.name == "tsconfig.json":
                analysis["typescript_config"] = self._analyze_tsconfig(content)
            elif "mcp" in json_file.name:
                analysis["mcp_config"] = self._analyze_mcp_config(content)
            
            return analysis
        
        except Exception as e:
            return {"error": f"Failed to parse {json_file}: {str(e)}"}
    
    def _analyze_python_config_file(self, py_file: Path) -> Dict[str, Any]:
        """Analyze a Python configuration file."""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract configuration variables and classes
            config_vars = self._extract_config_variables(content)
            classes = self._extract_classes(content)
            imports = self._extract_imports(content)
            
            return {
                "type": "python_config",
                "config_variables": config_vars,
                "classes": classes,
                "imports": imports,
                "has_config_class": any("config" in cls.lower() for cls in classes)
            }
        
        except Exception as e:
            return {"error": f"Failed to analyze {py_file}: {str(e)}"}
    
    def _parse_docker_compose(self, compose_file: Path) -> Dict[str, Any]:
        """Parse a Docker Compose file."""
        try:
            with open(compose_file, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            services = content.get('services', {})
            
            return {
                "type": "docker_compose",
                "version": content.get('version'),
                "services": list(services.keys()),
                "service_count": len(services),
                "networks": list(content.get('networks', {}).keys()),
                "volumes": list(content.get('volumes', {}).keys()),
                "ports": self._extract_compose_ports(services),
                "environment_vars": self._extract_compose_env_vars(services)
            }
        
        except Exception as e:
            return {"error": f"Failed to parse {compose_file}: {str(e)}"}
    
    def _parse_dockerfile(self, dockerfile: Path) -> Dict[str, Any]:
        """Parse a Dockerfile."""
        try:
            with open(dockerfile, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            instructions = []
            base_image = None
            exposed_ports = []
            env_vars = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(None, 1)
                if len(parts) >= 1:
                    instruction = parts[0].upper()
                    value = parts[1] if len(parts) > 1 else ""
                    
                    instructions.append(instruction)
                    
                    if instruction == "FROM" and not base_image:
                        base_image = value
                    elif instruction == "EXPOSE":
                        exposed_ports.extend(value.split())
                    elif instruction == "ENV":
                        env_vars.append(value)
            
            return {
                "type": "dockerfile",
                "base_image": base_image,
                "instructions": instructions,
                "exposed_ports": exposed_ports,
                "environment_variables": env_vars,
                "instruction_count": len(instructions)
            }
        
        except Exception as e:
            return {"error": f"Failed to parse {dockerfile}: {str(e)}"}
    
    def _analyze_yaml_structure(self, content: Any, depth: int = 0) -> Dict[str, Any]:
        """Analyze the structure of YAML content."""
        if depth > 5:  # Prevent infinite recursion
            return {"type": "truncated", "reason": "max_depth_reached"}
        
        if isinstance(content, dict):
            return {
                "type": "object",
                "keys": list(content.keys()),
                "key_count": len(content)
            }
        elif isinstance(content, list):
            return {
                "type": "array",
                "length": len(content),
                "item_types": list(set(type(item).__name__ for item in content[:10]))
            }
        else:
            return {
                "type": type(content).__name__,
                "value": content if len(str(content)) < 100 else str(content)[:100] + "..."
            }
    
    def _analyze_package_json(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze package.json specific content."""
        return {
            "name": content.get("name"),
            "version": content.get("version"),
            "dependencies": list(content.get("dependencies", {}).keys()),
            "dev_dependencies": list(content.get("devDependencies", {}).keys()),
            "scripts": list(content.get("scripts", {}).keys())
        }
    
    def _analyze_tsconfig(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze tsconfig.json specific content."""
        compiler_options = content.get("compilerOptions", {})
        return {
            "target": compiler_options.get("target"),
            "module": compiler_options.get("module"),
            "lib": compiler_options.get("lib", []),
            "include": content.get("include", []),
            "exclude": content.get("exclude", [])
        }
    
    def _analyze_mcp_config(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze MCP configuration content."""
        servers = content.get("mcpServers", {})
        return {
            "server_count": len(servers),
            "servers": list(servers.keys()),
            "server_configs": {
                name: {
                    "command": config.get("command"),
                    "args": config.get("args", []),
                    "cwd": config.get("cwd")
                }
                for name, config in servers.items()
            }
        }
    
    def _extract_config_variables(self, content: str) -> List[str]:
        """Extract configuration variable assignments from Python code."""
        # Simple regex to find variable assignments
        var_pattern = r'^([A-Z_][A-Z0-9_]*)\s*=\s*'
        variables = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                match = re.match(var_pattern, line)
                if match:
                    variables.append(match.group(1))
        
        return variables
    
    def _extract_classes(self, content: str) -> List[str]:
        """Extract class names from Python code."""
        class_pattern = r'^class\s+(\w+)(?:\([^)]*\))?:'
        classes = []
        
        for line in content.split('\n'):
            line = line.strip()
            match = re.match(class_pattern, line)
            if match:
                classes.append(match.group(1))
        
        return classes
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from Python code."""
        import_pattern = r'^(?:from\s+\S+\s+)?import\s+(.+)'
        imports = []
        
        for line in content.split('\n'):
            line = line.strip()
            match = re.match(import_pattern, line)
            if match:
                imports.append(line)
        
        return imports
    
    def _extract_compose_ports(self, services: Dict[str, Any]) -> List[str]:
        """Extract port mappings from Docker Compose services."""
        ports = []
        for service_name, service_config in services.items():
            if 'ports' in service_config:
                for port in service_config['ports']:
                    ports.append(f"{service_name}: {port}")
        return ports
    
    def _extract_compose_env_vars(self, services: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract environment variables from Docker Compose services."""
        env_vars = {}
        for service_name, service_config in services.items():
            service_env = []
            if 'environment' in service_config:
                env = service_config['environment']
                if isinstance(env, list):
                    service_env.extend(env)
                elif isinstance(env, dict):
                    service_env.extend([f"{k}={v}" for k, v in env.items()])
            if service_env:
                env_vars[service_name] = service_env
        return env_vars
    
    def _is_url(self, value: str) -> bool:
        """Check if a value looks like a URL."""
        return value.startswith(('http://', 'https://', 'ftp://', 'ws://', 'wss://'))
    
    def _is_path(self, value: str) -> bool:
        """Check if a value looks like a file path."""
        return '/' in value or '\\' in value or value.startswith('./')
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a high-level summary of all configuration in the project."""
        analysis = self.analyze_config_files()
        
        summary = {
            "total_config_files": analysis["summary"]["total_config_files"],
            "config_types": {
                "environment": analysis["summary"]["environment_files"],
                "yaml": analysis["summary"]["yaml_files"], 
                "json": analysis["summary"]["json_files"],
                "python": analysis["summary"]["python_configs"],
                "docker": analysis["summary"]["docker_configs"],
                "services": analysis["summary"]["service_configs"]
            },
            "key_configs": {},
            "potential_issues": []
        }
        
        # Identify key configuration files
        if analysis["service_configs"]:
            summary["key_configs"]["services"] = list(analysis["service_configs"].keys())
        
        if analysis["environment_files"]:
            summary["key_configs"]["environments"] = [
                path for path in analysis["environment_files"].keys()
                if "environment" in path
            ]
        
        # Look for potential configuration issues
        if analysis["summary"]["total_config_files"] == 0:
            summary["potential_issues"].append("No configuration files found")
        
        return summary
