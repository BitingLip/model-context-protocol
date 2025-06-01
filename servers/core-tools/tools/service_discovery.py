"""
Service discovery and analysis tools for the Biting Lip platform.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


class ServiceDiscovery:
    """Discover and analyze services in the Biting Lip platform."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.managers_dir = self.project_root / "managers"
        self.interfaces_dir = self.project_root / "interfaces"
    
    def discover_services(self) -> Dict[str, Any]:
        """
        Discover all services in the platform.
        
        Returns:
            Dict containing service information including managers, interfaces, and their configurations.
        """
        services = {
            "managers": self._discover_managers(),
            "interfaces": self._discover_interfaces(),
            "config_services": self._discover_config_services(),
            "summary": {}
        }
        
        # Generate summary
        total_services = len(services["managers"]) + len(services["interfaces"])
        services["summary"] = {
            "total_services": total_services,
            "manager_count": len(services["managers"]),
            "interface_count": len(services["interfaces"]),
            "config_files_found": sum(len(s.get("config_files", [])) for s in services["managers"].values())
        }
        
        return services
    
    def _discover_managers(self) -> Dict[str, Any]:
        """Discover manager services."""
        managers = {}
        
        if not self.managers_dir.exists():
            return managers
        
        for manager_dir in self.managers_dir.iterdir():
            if manager_dir.is_dir() and not manager_dir.name.startswith('.'):
                manager_info = self._analyze_manager_service(manager_dir)
                if manager_info:
                    managers[manager_dir.name] = manager_info
        
        return managers
    
    def _discover_interfaces(self) -> Dict[str, Any]:
        """Discover interface services."""
        interfaces = {}
        
        if not self.interfaces_dir.exists():
            return interfaces
        
        for interface_dir in self.interfaces_dir.iterdir():
            if interface_dir.is_dir() and not interface_dir.name.startswith('.'):
                interface_info = self._analyze_interface_service(interface_dir)
                if interface_info:
                    interfaces[interface_dir.name] = interface_info
        
        return interfaces
    
    def _discover_config_services(self) -> Dict[str, Any]:
        """Discover configuration-related services."""
        config_dir = self.project_root / "config"
        config_services = {}
        
        if config_dir.exists():
            config_services["central_config"] = {
                "type": "configuration_service",
                "path": str(config_dir),
                "files": [f.name for f in config_dir.iterdir() if f.is_file()],
                "subdirectories": [d.name for d in config_dir.iterdir() if d.is_dir()]
            }
        
        return config_services
    
    def _analyze_manager_service(self, manager_dir: Path) -> Optional[Dict[str, Any]]:
        """Analyze a manager service directory."""
        service_info = {
            "type": "manager",
            "path": str(manager_dir),
            "files": [],
            "config_files": [],
            "docker_files": [],
            "python_files": [],
            "dependencies": [],
            "ports": [],
            "environment_vars": []
        }
        
        # Scan files in the manager directory
        for file_path in manager_dir.rglob("*"):
            if file_path.is_file():
                file_name = file_path.name.lower()
                relative_path = str(file_path.relative_to(manager_dir))
                
                service_info["files"].append(relative_path)
                
                # Categorize files
                if file_name.endswith(('.yml', '.yaml')):
                    service_info["config_files"].append(relative_path)
                    if 'docker-compose' in file_name:
                        service_info["docker_files"].append(relative_path)
                        # Extract port information from docker-compose
                        ports = self._extract_ports_from_compose(file_path)
                        service_info["ports"].extend(ports)
                elif file_name.endswith('.py'):
                    service_info["python_files"].append(relative_path)
                elif file_name in ('dockerfile', 'dockerfile.dev', 'dockerfile.prod'):
                    service_info["docker_files"].append(relative_path)
                elif file_name.endswith(('.env', '.conf', '.config', '.json')):
                    service_info["config_files"].append(relative_path)
                elif file_name in ('requirements.txt', 'package.json', 'pyproject.toml'):
                    service_info["dependencies"].append(relative_path)
        
        return service_info if service_info["files"] else None
    
    def _analyze_interface_service(self, interface_dir: Path) -> Optional[Dict[str, Any]]:
        """Analyze an interface service directory."""
        service_info = {
            "type": "interface",
            "path": str(interface_dir),
            "files": [],
            "config_files": [],
            "frontend_files": [],
            "backend_files": [],
            "dependencies": [],
            "technology": self._detect_interface_technology(interface_dir)
        }
        
        # Scan files in the interface directory
        for file_path in interface_dir.rglob("*"):
            if file_path.is_file():
                file_name = file_path.name.lower()
                relative_path = str(file_path.relative_to(interface_dir))
                
                service_info["files"].append(relative_path)
                
                # Categorize files
                if file_name.endswith(('.ts', '.tsx', '.js', '.jsx', '.html', '.css', '.vue')):
                    service_info["frontend_files"].append(relative_path)
                elif file_name.endswith('.py'):
                    service_info["backend_files"].append(relative_path)
                elif file_name.endswith(('.json', '.yml', '.yaml', '.env', '.config')):
                    service_info["config_files"].append(relative_path)
                elif file_name in ('requirements.txt', 'package.json', 'pyproject.toml'):
                    service_info["dependencies"].append(relative_path)
        
        return service_info if service_info["files"] else None
    
    def _detect_interface_technology(self, interface_dir: Path) -> List[str]:
        """Detect the technology stack used in an interface."""
        technologies = []
        
        # Check for common files        # Check for common files
        files_in_dir = [f.name.lower() for f in interface_dir.iterdir() if f.is_file()]
        
        if 'package.json' in files_in_dir:
            technologies.append('Node.js')
        if 'vite.config.ts' in files_in_dir or 'vite.config.js' in files_in_dir:
            technologies.append('Vite')
        if 'tailwind.config.js' in files_in_dir:
            technologies.append('Tailwind CSS')
        if 'tsconfig.json' in files_in_dir:
            technologies.append('TypeScript')
        if 'pyproject.toml' in files_in_dir or 'requirements.txt' in files_in_dir:
            technologies.append('Python')
        if any(f.name.endswith('.vue') for f in interface_dir.rglob("*.vue")):
            technologies.append('Vue.js')
        if any(f.name.endswith(('.tsx', '.jsx')) for f in interface_dir.rglob("*")):
            technologies.append('React')
        
        return technologies
    
    def _extract_ports_from_compose(self, compose_file: Path) -> List[str]:
        """Extract port mappings from docker-compose file."""
        ports = []
        try:
            with open(compose_file, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
                
            if content and 'services' in content:
                for service_name, service_config in content['services'].items():
                    if 'ports' in service_config:
                        for port_mapping in service_config['ports']:
                            ports.append(f"{service_name}: {port_mapping}")
        except Exception:
            # If we can't parse the YAML, try regex for port patterns
            try:
                with open(compose_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    port_matches = re.findall(r'ports:\s*\n\s*-\s*["\']?(\d+:\d+)["\']?', content)
                    ports.extend(port_matches)
            except Exception:
                pass
        
        return ports
    
    def get_service_dependencies(self, service_name: str) -> Dict[str, Any]:
        """Get dependencies for a specific service."""
        services = self.discover_services()
        
        # Look in both managers and interfaces
        all_services = {**services["managers"], **services["interfaces"]}
        
        if service_name not in all_services:
            return {"error": f"Service '{service_name}' not found"}
        
        service_info = all_services[service_name]
        dependencies = {
            "internal_dependencies": [],
            "external_dependencies": [],
            "config_dependencies": []
        }
        
        # Analyze dependency files
        service_path = Path(service_info["path"])
        for dep_file in service_info.get("dependencies", []):
            dep_path = service_path / dep_file
            if dep_path.exists():
                if dep_file == "requirements.txt":
                    dependencies["external_dependencies"].extend(
                        self._parse_requirements_file(dep_path)
                    )
                elif dep_file == "package.json":
                    dependencies["external_dependencies"].extend(
                        self._parse_package_json(dep_path)
                    )
        
        # Look for references to other services in config files
        for config_file in service_info.get("config_files", []):
            config_path = service_path / config_file
            if config_path.exists():
                internal_deps = self._find_service_references(config_path, list(all_services.keys()))
                dependencies["internal_dependencies"].extend(internal_deps)
        
        return dependencies
    
    def _parse_requirements_file(self, req_file: Path) -> List[str]:
        """Parse Python requirements file."""
        try:
            with open(req_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            requirements = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove version specifiers
                    package = re.split(r'[>=<!=]', line)[0].strip()
                    if package:
                        requirements.append(package)
            
            return requirements
        except Exception:
            return []
    
    def _parse_package_json(self, package_file: Path) -> List[str]:
        """Parse Node.js package.json file."""
        try:
            with open(package_file, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            dependencies = []
            for dep_type in ['dependencies', 'devDependencies']:
                if dep_type in package_data:
                    dependencies.extend(package_data[dep_type].keys())
            
            return dependencies
        except Exception:
            return []
    
    def _find_service_references(self, config_file: Path, service_names: List[str]) -> List[str]:
        """Find references to other services in config files."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            references = []
            for service_name in service_names:
                if service_name.lower() in content:
                    references.append(service_name)
            
            return references
        except Exception:
            return []
