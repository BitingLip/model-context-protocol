"""
Docker analysis tools for the Biting Lip platform.
"""

import os
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


class DockerAnalyzer:
    """Analyze Docker containers, images, and configurations in the Biting Lip platform."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
    
    def get_docker_info(self) -> Dict[str, Any]:
        """
        Get comprehensive Docker information including containers, images, and compose files.
        
        Returns:
            Dict containing Docker system info, containers, images, and compose files.
        """
        docker_info = {
            "system_info": self._get_docker_system_info(),
            "containers": self._get_docker_containers(),
            "images": self._get_docker_images(),
            "compose_files": self._find_compose_files(),
            "dockerfiles": self._find_dockerfiles(),
            "networks": self._get_docker_networks(),
            "volumes": self._get_docker_volumes(),
            "summary": {}
        }
        
        # Generate summary
        docker_info["summary"] = {
            "docker_available": docker_info["system_info"].get("available", False),
            "total_containers": len(docker_info["containers"]),
            "running_containers": len([c for c in docker_info["containers"] if c.get("status", "").startswith("Up")]),
            "total_images": len(docker_info["images"]),
            "compose_files_found": len(docker_info["compose_files"]),
            "dockerfiles_found": len(docker_info["dockerfiles"]),
            "networks": len(docker_info["networks"]),
            "volumes": len(docker_info["volumes"])
        }
        
        return docker_info
    
    def _get_docker_system_info(self) -> Dict[str, Any]:
        """Get Docker system information."""
        try:
            result = subprocess.run(
                ["docker", "version", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version_info = json.loads(result.stdout)
                return {
                    "available": True,
                    "client_version": version_info.get("Client", {}).get("Version"),
                    "server_version": version_info.get("Server", {}).get("Version"),
                    "api_version": version_info.get("Client", {}).get("ApiVersion")
                }
            else:
                return {"available": False, "error": "Docker command failed"}
        
        except subprocess.TimeoutExpired:
            return {"available": False, "error": "Docker command timeout"}
        except FileNotFoundError:
            return {"available": False, "error": "Docker not installed"}
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def _get_docker_containers(self) -> List[Dict[str, Any]]:
        """Get list of Docker containers."""
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            container = json.loads(line)
                            containers.append({
                                "id": container.get("ID"),
                                "name": container.get("Names"),
                                "image": container.get("Image"),
                                "status": container.get("Status"),
                                "ports": container.get("Ports"),
                                "created": container.get("CreatedAt")
                            })
                        except json.JSONDecodeError:
                            continue
                return containers
            else:
                return []
        
        except Exception:
            return []
    
    def _get_docker_images(self) -> List[Dict[str, Any]]:
        """Get list of Docker images."""
        try:
            result = subprocess.run(
                ["docker", "images", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                images = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            image = json.loads(line)
                            images.append({
                                "id": image.get("ID"),
                                "repository": image.get("Repository"),
                                "tag": image.get("Tag"),
                                "size": image.get("Size"),
                                "created": image.get("CreatedAt")
                            })
                        except json.JSONDecodeError:
                            continue
                return images
            else:
                return []
        
        except Exception:
            return []
    
    def _get_docker_networks(self) -> List[Dict[str, Any]]:
        """Get list of Docker networks."""
        try:
            result = subprocess.run(
                ["docker", "network", "ls", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                networks = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            network = json.loads(line)
                            networks.append({
                                "id": network.get("ID"),
                                "name": network.get("Name"),
                                "driver": network.get("Driver"),
                                "scope": network.get("Scope")
                            })
                        except json.JSONDecodeError:
                            continue
                return networks
            else:
                return []
        
        except Exception:
            return []
    
    def _get_docker_volumes(self) -> List[Dict[str, Any]]:
        """Get list of Docker volumes."""
        try:
            result = subprocess.run(
                ["docker", "volume", "ls", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                volumes = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            volume = json.loads(line)
                            volumes.append({
                                "name": volume.get("Name"),
                                "driver": volume.get("Driver"),
                                "mountpoint": volume.get("Mountpoint")
                            })
                        except json.JSONDecodeError:
                            continue
                return volumes
            else:
                return []
        
        except Exception:
            return []
    
    def _find_compose_files(self) -> List[Dict[str, Any]]:
        """Find and analyze Docker Compose files in the project."""
        compose_files = []
        
        # Common compose file patterns
        patterns = ["docker-compose*.yml", "docker-compose*.yaml", "compose*.yml", "compose*.yaml"]
        
        for pattern in patterns:
            for compose_file in self.project_root.rglob(pattern):
                if compose_file.is_file():
                    analysis = self._analyze_compose_file(compose_file)
                    if analysis:
                        compose_files.append(analysis)
        
        return compose_files
    
    def _find_dockerfiles(self) -> List[Dict[str, Any]]:
        """Find and analyze Dockerfiles in the project."""
        dockerfiles = []
        
        # Find Dockerfiles
        for dockerfile in self.project_root.rglob("Dockerfile*"):
            if dockerfile.is_file() and not dockerfile.suffix:
                analysis = self._analyze_dockerfile(dockerfile)
                if analysis:
                    dockerfiles.append(analysis)
        
        return dockerfiles
    
    def _analyze_compose_file(self, compose_file: Path) -> Optional[Dict[str, Any]]:
        """Analyze a Docker Compose file."""
        try:
            with open(compose_file, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if not content:
                return None
            
            services = content.get('services', {})
            networks = content.get('networks', {})
            volumes = content.get('volumes', {})
            
            # Extract service information
            service_info = {}
            for service_name, service_config in services.items():
                service_info[service_name] = {
                    "image": service_config.get("image"),
                    "build": service_config.get("build"),
                    "ports": service_config.get("ports", []),
                    "volumes": service_config.get("volumes", []),
                    "environment": self._extract_env_vars(service_config.get("environment", [])),
                    "depends_on": service_config.get("depends_on", []),
                    "networks": service_config.get("networks", [])
                }
            
            return {
                "file_path": str(compose_file.relative_to(self.project_root)),
                "version": content.get("version"),
                "services": service_info,
                "service_count": len(services),
                "networks": list(networks.keys()),
                "volumes": list(volumes.keys()),
                "external_networks": [n for n, config in networks.items() if config.get("external")],
                "exposed_ports": self._extract_all_ports(services)
            }
        
        except Exception as e:
            return {
                "file_path": str(compose_file.relative_to(self.project_root)),
                "error": f"Failed to parse: {str(e)}"
            }
    
    def _analyze_dockerfile(self, dockerfile: Path) -> Optional[Dict[str, Any]]:
        """Analyze a Dockerfile."""
        try:
            with open(dockerfile, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            analysis = {
                "file_path": str(dockerfile.relative_to(self.project_root)),
                "base_images": [],
                "exposed_ports": [],
                "environment_vars": [],
                "volumes": [],
                "entrypoint": None,
                "cmd": None,
                "workdir": None,
                "user": None,
                "instructions": []
            }
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(None, 1)
                if len(parts) < 1:
                    continue
                
                instruction = parts[0].upper()
                value = parts[1] if len(parts) > 1 else ""
                
                analysis["instructions"].append({
                    "line": line_num,
                    "instruction": instruction,
                    "value": value
                })
                
                # Extract specific information
                if instruction == "FROM":
                    analysis["base_images"].append(value)
                elif instruction == "EXPOSE":
                    analysis["exposed_ports"].extend(value.split())
                elif instruction == "ENV":
                    analysis["environment_vars"].append(value)
                elif instruction == "VOLUME":
                    analysis["volumes"].append(value)
                elif instruction == "ENTRYPOINT":
                    analysis["entrypoint"] = value
                elif instruction == "CMD":
                    analysis["cmd"] = value
                elif instruction == "WORKDIR":
                    analysis["workdir"] = value
                elif instruction == "USER":
                    analysis["user"] = value
            
            return analysis
        
        except Exception as e:
            return {
                "file_path": str(dockerfile.relative_to(self.project_root)),
                "error": f"Failed to parse: {str(e)}"
            }
    
    def _extract_env_vars(self, environment) -> List[str]:
        """Extract environment variables from Docker Compose service config."""
        env_vars = []
        
        if isinstance(environment, list):
            env_vars.extend(environment)
        elif isinstance(environment, dict):
            env_vars.extend([f"{k}={v}" for k, v in environment.items()])
        
        return env_vars
    
    def _extract_all_ports(self, services: Dict[str, Any]) -> List[str]:
        """Extract all exposed ports from services."""
        all_ports = []
        
        for service_name, service_config in services.items():
            ports = service_config.get("ports", [])
            for port in ports:
                all_ports.append(f"{service_name}: {port}")
        
        return all_ports
    
    def get_service_containers(self, service_name: str) -> List[Dict[str, Any]]:
        """Get containers for a specific service."""
        containers = self._get_docker_containers()
        service_containers = []
        
        for container in containers:
            # Check if container name or image matches the service
            container_name = container.get("name", "").lower()
            container_image = container.get("image", "").lower()
            
            if (service_name.lower() in container_name or 
                service_name.lower() in container_image):
                service_containers.append(container)
        
        return service_containers
    
    def get_docker_compose_services(self) -> Dict[str, List[str]]:
        """Get all services defined in Docker Compose files."""
        compose_services = {}
        
        compose_files = self._find_compose_files()
        for compose_file in compose_files:
            if "error" not in compose_file:
                file_path = compose_file["file_path"]
                services = list(compose_file["services"].keys())
                compose_services[file_path] = services
        
        return compose_services
