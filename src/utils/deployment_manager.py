"""
DeploymentManager - Gerenciador de deployment automatizado para JARVIS 5.0
Gerencia builds, releases, containers e orquestração.
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import docker
import yaml

logger = logging.getLogger(__name__)

@dataclass
class DeploymentConfig:
    """Configuração de deployment."""
    environment: str  # 'development', 'staging', 'production'
    version: str
    docker_image: str
    ports: Dict[str, int]
    volumes: List[str]
    environment_variables: Dict[str, str]
    health_checks: Dict[str, Any]
    scaling: Dict[str, Any]

@dataclass
class DeploymentResult:
    """Resultado de um deployment."""
    success: bool
    deployment_id: str
    environment: str
    version: str
    timestamp: datetime
    logs: List[str]
    errors: List[str]
    rollback_available: bool = False

class DeploymentManager:
    """
    Gerenciador de deployment automatizado com suporte a múltiplas estratégias.
    """

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.deployments_dir = self.project_root / "deployments"
        self.deployments_dir.mkdir(exist_ok=True)

        # Configurações de deployment
        self.environments = self._load_environments()

        # Cliente Docker
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker not available: {e}")
            self.docker_client = None

    def _load_environments(self) -> Dict[str, DeploymentConfig]:
        """Carrega configurações de ambientes."""
        environments = {}

        # Configurações padrão
        default_configs = {
            "development": DeploymentConfig(
                environment="development",
                version="latest",
                docker_image="jarvis-dev:latest",
                ports={"web": 8080, "api": 8081},
                volumes=["./data:/app/data", "./config:/app/config"],
                environment_variables={
                    "ENV": "development",
                    "LOG_LEVEL": "DEBUG",
                    "DEBUG": "true"
                },
                health_checks={
                    "interval": 30,
                    "timeout": 10,
                    "retries": 3
                },
                scaling={"replicas": 1}
            ),
            "staging": DeploymentConfig(
                environment="staging",
                version="stable",
                docker_image="jarvis-staging:latest",
                ports={"web": 8082, "api": 8083},
                volumes=["./data/staging:/app/data", "./config/staging:/app/config"],
                environment_variables={
                    "ENV": "staging",
                    "LOG_LEVEL": "INFO"
                },
                health_checks={
                    "interval": 60,
                    "timeout": 15,
                    "retries": 5
                },
                scaling={"replicas": 2}
            ),
            "production": DeploymentConfig(
                environment="production",
                version="latest-stable",
                docker_image="jarvis-prod:latest",
                ports={"web": 80, "api": 443},
                volumes=["/data/jarvis:/app/data", "/config/jarvis:/app/config"],
                environment_variables={
                    "ENV": "production",
                    "LOG_LEVEL": "WARNING"
                },
                health_checks={
                    "interval": 30,
                    "timeout": 10,
                    "retries": 3
                },
                scaling={"replicas": 3}
            )
        }

        # Carrega configurações customizadas se existirem
        config_file = self.project_root / "config" / "deployment.yaml"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_configs = yaml.safe_load(f)

                for env_name, config_data in custom_configs.items():
                    if env_name in default_configs:
                        # Merge com configurações padrão
                        default = default_configs[env_name]
                        merged = DeploymentConfig(
                            environment=env_name,
                            version=config_data.get('version', default.version),
                            docker_image=config_data.get('docker_image', default.docker_image),
                            ports=config_data.get('ports', default.ports),
                            volumes=config_data.get('volumes', default.volumes),
                            environment_variables=config_data.get('environment_variables', default.environment_variables),
                            health_checks=config_data.get('health_checks', default.health_checks),
                            scaling=config_data.get('scaling', default.scaling)
                        )
                        environments[env_name] = merged
                    else:
                        # Nova configuração
                        environments[env_name] = DeploymentConfig(**config_data)
            except Exception as e:
                logger.error(f"Failed to load deployment config: {e}")

        # Usa configurações padrão se não houver customizadas
        if not environments:
            environments = default_configs

        return environments

    async def deploy_to_docker(self, environment: str, version: str = None) -> DeploymentResult:
        """
        Faz deployment usando Docker.

        Args:
            environment: Ambiente de destino
            version: Versão para deploy (opcional)

        Returns:
            Resultado do deployment
        """
        if not self.docker_client:
            return DeploymentResult(
                success=False,
                deployment_id=f"docker_{int(datetime.now().timestamp())}",
                environment=environment,
                version=version or "unknown",
                timestamp=datetime.now(),
                logs=[],
                errors=["Docker client not available"]
            )

        config = self.environments.get(environment)
        if not config:
            return DeploymentResult(
                success=False,
                deployment_id=f"docker_{int(datetime.now().timestamp())}",
                environment=environment,
                version=version or "unknown",
                timestamp=datetime.now(),
                logs=[],
                errors=[f"Environment '{environment}' not configured"]
            )

        deployment_id = f"docker_{environment}_{int(datetime.now().timestamp())}"
        logs = []
        errors = []

        try:
            # Build da imagem
            logs.append("Building Docker image...")
            image_tag = f"jarvis-{environment}:{version or config.version}"

            build_result = await self._build_docker_image(image_tag)
            logs.extend(build_result["logs"])
            if build_result["errors"]:
                errors.extend(build_result["errors"])

            if not build_result["success"]:
                return DeploymentResult(
                    success=False,
                    deployment_id=deployment_id,
                    environment=environment,
                    version=version or config.version,
                    timestamp=datetime.now(),
                    logs=logs,
                    errors=errors
                )

            # Para containers existentes
            logs.append("Stopping existing containers...")
            await self._stop_containers(f"jarvis-{environment}")

            # Inicia novo container
            logs.append("Starting new container...")
            container_result = await self._start_container(config, image_tag)
            logs.extend(container_result["logs"])
            if container_result["errors"]:
                errors.extend(container_result["errors"])

            success = len(errors) == 0

            return DeploymentResult(
                success=success,
                deployment_id=deployment_id,
                environment=environment,
                version=version or config.version,
                timestamp=datetime.now(),
                logs=logs,
                errors=errors,
                rollback_available=True
            )

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            errors.append(str(e))
            return DeploymentResult(
                success=False,
                deployment_id=deployment_id,
                environment=environment,
                version=version or config.version,
                timestamp=datetime.now(),
                logs=logs,
                errors=errors
            )

    async def deploy_to_systemd(self, environment: str) -> DeploymentResult:
        """
        Faz deployment como serviço systemd.

        Args:
            environment: Ambiente de destino

        Returns:
            Resultado do deployment
        """
        config = self.environments.get(environment)
        if not config:
            return DeploymentResult(
                success=False,
                deployment_id=f"systemd_{int(datetime.now().timestamp())}",
                environment=environment,
                version="unknown",
                timestamp=datetime.now(),
                logs=[],
                errors=[f"Environment '{environment}' not configured"]
            )

        deployment_id = f"systemd_{environment}_{int(datetime.now().timestamp())}"
        logs = []
        errors = []

        try:
            # Cria arquivo de serviço
            service_content = self._generate_systemd_service(config)
            service_path = f"/etc/systemd/system/jarvis-{environment}.service"

            logs.append(f"Creating systemd service at {service_path}...")

            # Escreve arquivo de serviço (requer sudo)
            write_result = await self._write_systemd_service(service_content, service_path)
            logs.extend(write_result["logs"])
            if write_result["errors"]:
                errors.extend(write_result["errors"])

            # Recarrega systemd
            logs.append("Reloading systemd...")
            reload_result = await self._run_command(["sudo", "systemctl", "daemon-reload"])
            logs.extend(reload_result["logs"])
            if reload_result["errors"]:
                errors.extend(reload_result["errors"])

            # Para serviço existente
            logs.append("Stopping existing service...")
            stop_result = await self._run_command(["sudo", "systemctl", "stop", f"jarvis-{environment}"])
            logs.extend(stop_result["logs"])  # Não trata como erro se já estava parado

            # Inicia novo serviço
            logs.append("Starting service...")
            start_result = await self._run_command(["sudo", "systemctl", "start", f"jarvis-{environment}"])
            logs.extend(start_result["logs"])
            if start_result["errors"]:
                errors.extend(start_result["errors"])

            # Habilita serviço
            logs.append("Enabling service...")
            enable_result = await self._run_command(["sudo", "systemctl", "enable", f"jarvis-{environment}"])
            logs.extend(enable_result["logs"])
            if enable_result["errors"]:
                errors.extend(enable_result["errors"])

            success = len(errors) == 0

            return DeploymentResult(
                success=success,
                deployment_id=deployment_id,
                environment=environment,
                version=config.version,
                timestamp=datetime.now(),
                logs=logs,
                errors=errors,
                rollback_available=True
            )

        except Exception as e:
            logger.error(f"Systemd deployment failed: {e}")
            errors.append(str(e))
            return DeploymentResult(
                success=False,
                deployment_id=deployment_id,
                environment=environment,
                version=config.version,
                timestamp=datetime.now(),
                logs=logs,
                errors=errors
            )

    async def create_release(self, version: str, changelog: str = None) -> Dict[str, Any]:
        """
        Cria uma release do projeto.

        Args:
            version: Versão da release
            changelog: Changelog (opcional)

        Returns:
            Informações da release
        """
        release_dir = self.deployments_dir / f"release_{version}"
        release_dir.mkdir(exist_ok=True)

        # Cria changelog se não fornecido
        if not changelog:
            changelog = self._generate_changelog(version)

        # Arquivos para incluir na release
        include_patterns = [
            "src/**/*",
            "main.py",
            "jarvis.bat",
            "requirements.txt",
            "config/**/*.yaml",
            "docs/**/*",
            "README.md",
            "LICENSE"
        ]

        # Cria arquivo da release
        release_info = {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "changelog": changelog,
            "files": [],
            "checksums": {}
        }

        try:
            # Copia arquivos
            for pattern in include_patterns:
                for file_path in Path(self.project_root).glob(pattern):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(self.project_root)
                        dest_path = release_dir / relative_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, dest_path)

                        release_info["files"].append(str(relative_path))

            # Calcula checksums
            import hashlib
            for file_path in release_dir.rglob("*"):
                if file_path.is_file():
                    with open(file_path, 'rb') as f:
                        checksum = hashlib.sha256(f.read()).hexdigest()
                    relative_path = file_path.relative_to(release_dir)
                    release_info["checksums"][str(relative_path)] = checksum

            # Salva informações da release
            info_file = release_dir / "release.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(release_info, f, indent=2)

            # Cria arquivo tar.gz
            tar_path = self.deployments_dir / f"jarvis-{version}.tar.gz"
            shutil.make_archive(str(tar_path.with_suffix('')), 'gztar', release_dir)

            logger.info(f"Release {version} created successfully")

            return {
                "success": True,
                "version": version,
                "release_dir": str(release_dir),
                "archive_path": str(tar_path),
                "info": release_info
            }

        except Exception as e:
            logger.error(f"Failed to create release: {e}")
            return {
                "success": False,
                "version": version,
                "error": str(e)
            }

    async def rollback_deployment(self, deployment_id: str) -> bool:
        """
        Faz rollback de um deployment.

        Args:
            deployment_id: ID do deployment para rollback

        Returns:
            Sucesso do rollback
        """
        # Carrega informações do deployment
        deployment_file = self.deployments_dir / f"{deployment_id}.json"
        if not deployment_file.exists():
            logger.error(f"Deployment {deployment_id} not found")
            return False

        try:
            with open(deployment_file, 'r', encoding='utf-8') as f:
                deployment_info = json.load(f)

            # Estratégia de rollback baseada no tipo
            deployment_type = deployment_info.get("type")

            if deployment_type == "docker":
                return await self._rollback_docker(deployment_info)
            elif deployment_type == "systemd":
                return await self._rollback_systemd(deployment_info)
            else:
                logger.error(f"Unknown deployment type: {deployment_type}")
                return False

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    async def _build_docker_image(self, image_tag: str) -> Dict[str, Any]:
        """Constrói imagem Docker."""
        logs = []
        errors = []

        try:
            dockerfile_path = self.project_root / "Dockerfile"
            if not dockerfile_path.exists():
                # Cria Dockerfile básico
                await self._create_dockerfile()

            logs.append(f"Building Docker image: {image_tag}")

            # Build usando subprocess para melhor controle
            cmd = [
                "docker", "build",
                "-t", image_tag,
                "-f", str(dockerfile_path),
                str(self.project_root)
            ]

            result = await self._run_command(cmd)
            logs.extend(result["logs"])
            if result["errors"]:
                errors.extend(result["errors"])

            success = len(errors) == 0
            return {"success": success, "logs": logs, "errors": errors}

        except Exception as e:
            errors.append(str(e))
            return {"success": False, "logs": logs, "errors": errors}

    async def _start_container(self, config: DeploymentConfig, image_tag: str) -> Dict[str, Any]:
        """Inicia container Docker."""
        logs = []
        errors = []

        try:
            container_name = f"jarvis-{config.environment}"

            # Monta comando docker run
            cmd = [
                "docker", "run",
                "-d",
                "--name", container_name,
                "--restart", "unless-stopped"
            ]

            # Adiciona portas
            for service, port in config.ports.items():
                cmd.extend(["-p", f"{port}:{port}"])

            # Adiciona volumes
            for volume in config.volumes:
                cmd.extend(["-v", volume])

            # Adiciona variáveis de ambiente
            for key, value in config.environment_variables.items():
                cmd.extend(["-e", f"{key}={value}"])

            # Adiciona imagem
            cmd.append(image_tag)

            logs.append(f"Starting container: {container_name}")
            result = await self._run_command(cmd)
            logs.extend(result["logs"])
            if result["errors"]:
                errors.extend(result["errors"])

            success = len(errors) == 0
            return {"success": success, "logs": logs, "errors": errors}

        except Exception as e:
            errors.append(str(e))
            return {"success": False, "logs": logs, "errors": errors}

    async def _stop_containers(self, name_pattern: str):
        """Para containers com padrão de nome."""
        try:
            cmd = ["docker", "ps", "-q", "--filter", f"name={name_pattern}"]
            result = await self._run_command(cmd)

            if result["logs"]:
                container_ids = result["logs"]
                for container_id in container_ids:
                    await self._run_command(["docker", "stop", container_id.strip()])
                    await self._run_command(["docker", "rm", container_id.strip()])

        except Exception as e:
            logger.warning(f"Failed to stop containers: {e}")

    async def _create_dockerfile(self):
        """Cria Dockerfile básico."""
        dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create data directories
RUN mkdir -p data/logs data/cache data/backups

# Expose ports
EXPOSE 8080 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Start the application
CMD ["python", "main.py"]
"""

        dockerfile_path = self.project_root / "Dockerfile"
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)

        logger.info("Created basic Dockerfile")

    def _generate_systemd_service(self, config: DeploymentConfig) -> str:
        """Gera arquivo de serviço systemd."""
        service_content = f"""[Unit]
Description=JARVIS 5.0 AI Assistant ({config.environment})
After=network.target

[Service]
Type=simple
User=jarvis
WorkingDirectory={self.project_root}
Environment=PYTHONPATH={self.project_root}
"""

        # Adiciona variáveis de ambiente
        for key, value in config.environment_variables.items():
            service_content += f"Environment={key}={value}\n"

        service_content += f"""
ExecStart={sys.executable} main.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=jarvis-{config.environment}

[Install]
WantedBy=multi-user.target
"""

        return service_content

    async def _write_systemd_service(self, content: str, path: str) -> Dict[str, Any]:
        """Escreve arquivo de serviço systemd."""
        logs = []
        errors = []

        try:
            # Usa tee para escrever com sudo
            cmd = ["sudo", "tee", path]
            result = await self._run_command(cmd, input_data=content)
            logs.extend(result["logs"])
            if result["errors"]:
                errors.extend(result["errors"])

            success = len(errors) == 0
            return {"success": success, "logs": logs, "errors": errors}

        except Exception as e:
            errors.append(str(e))
            return {"success": False, "logs": logs, "errors": errors}

    def _generate_changelog(self, version: str) -> str:
        """Gera changelog básico."""
        return f"""# Changelog for version {version}

## Features
- Improved system stability
- Enhanced monitoring capabilities
- Better error handling

## Bug Fixes
- Fixed memory leaks
- Resolved configuration issues
- Improved logging

## Technical Improvements
- Code refactoring
- Performance optimizations
- Security enhancements

Generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    async def _run_command(self, cmd: List[str], input_data: str = None) -> Dict[str, Any]:
        """Executa comando do sistema."""
        logs = []
        errors = []

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE if input_data else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root
            )

            stdout, stderr = await process.communicate(
                input_data.encode() if input_data else None
            )

            if stdout:
                logs.extend(stdout.decode().strip().split('\n'))
            if stderr:
                errors.extend(stderr.decode().strip().split('\n'))

            if process.returncode != 0:
                errors.append(f"Command failed with return code {process.returncode}")

        except Exception as e:
            errors.append(str(e))

        return {"logs": logs, "errors": errors}

    async def _rollback_docker(self, deployment_info: Dict[str, Any]) -> bool:
        """Rollback de deployment Docker."""
        try:
            # Lógica de rollback específica para Docker
            # Implementação simplificada
            logger.info("Docker rollback not fully implemented yet")
            return False
        except Exception as e:
            logger.error(f"Docker rollback failed: {e}")
            return False

    async def _rollback_systemd(self, deployment_info: Dict[str, Any]) -> bool:
        """Rollback de deployment systemd."""
        try:
            # Lógica de rollback específica para systemd
            # Implementação simplificada
            logger.info("Systemd rollback not fully implemented yet")
            return False
        except Exception as e:
            logger.error(f"Systemd rollback failed: {e}")
            return False

# Funções de conveniência
async def deploy_to_environment(environment: str, strategy: str = "docker") -> DeploymentResult:
    """
    Faz deployment para um ambiente específico.

    Args:
        environment: Ambiente de destino
        strategy: Estratégia ('docker' ou 'systemd')

    Returns:
        Resultado do deployment
    """
    manager = DeploymentManager()

    if strategy == "docker":
        return await manager.deploy_to_docker(environment)
    elif strategy == "systemd":
        return await manager.deploy_to_systemd(environment)
    else:
        return DeploymentResult(
            success=False,
            deployment_id=f"unknown_{int(datetime.now().timestamp())}",
            environment=environment,
            version="unknown",
            timestamp=datetime.now(),
            logs=[],
            errors=[f"Unknown deployment strategy: {strategy}"]
        )

def create_release(version: str, changelog: str = None) -> Dict[str, Any]:
    """
    Cria uma release síncrona.

    Args:
        version: Versão da release
        changelog: Changelog

    Returns:
        Informações da release
    """
    manager = DeploymentManager()
    return asyncio.run(manager.create_release(version, changelog))

if __name__ == "__main__":
    # Exemplo de uso
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Deployment Manager")
    parser.add_argument("action", choices=["deploy", "release", "rollback"])
    parser.add_argument("--environment", "-e", default="development")
    parser.add_argument("--strategy", "-s", choices=["docker", "systemd"], default="docker")
    parser.add_argument("--version", "-v")

    args = parser.parse_args()

    if args.action == "deploy":
        result = asyncio.run(deploy_to_environment(args.environment, args.strategy))
        print(f"Deployment {'successful' if result.success else 'failed'}")
        if result.errors:
            print("Errors:", result.errors)

    elif args.action == "release":
        if not args.version:
            print("Version required for release")
            sys.exit(1)

        result = create_release(args.version)
        print(f"Release {'created' if result['success'] else 'failed'}")

    elif args.action == "rollback":
        if not args.version:
            print("Deployment ID required for rollback")
            sys.exit(1)

        manager = DeploymentManager()
        success = asyncio.run(manager.rollback_deployment(args.version))
        print(f"Rollback {'successful' if success else 'failed'}")