#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Safe Executor (Immune System)
==========================================
Executa as correções propostas pelo Auto Healer em ambiente controlado.
Realiza backups, validações e rollbacks.

Responsibilities:
- Execução segura de modificações de arquivo
- Backup automático antes de alterações
- Validação pós-correção (linting, tests)
- Rollback automático em caso de falha
- Notificação de resultados

Author: JARVIS 5.0 Evolution Layer
"""

import shutil
import json
import logging
import py_compile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

from src.core.config.system_manifest import system_manifest
from src.core.infrastructure.async_event_bus import event_bus, EventType, EventPriority
from src.core.infrastructure.async_event_bus import Event
from src.evolution.knowledge_db import knowledge_db

logger = logging.getLogger(__name__)

BACKUP_DIR = Path(__file__).parent.parent.parent / "data" / "backups" / "auto"


class SafeExecutor:
    """
    O braço executor do sistema de auto-correção.
    """

    def __init__(self):
        self.running = False

    async def start(self):
        """Inicia o Safe Executor"""
        if self.running:
            return None

        self.running = True

        # Create backup directory if it doesn't exist
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        # Subscribe to diagnostic plans (not async)
        event_bus.subscribe(
            EventType.SYSTEM_DIAGNOSTIC_PLAN,
            self._handle_diagnostic_plan,
            priority_filter=[EventPriority.HIGH],
        )

        logger.info("🛡️ Safe Executor operational")
        return None

    async def stop(self):
        self.running = False
        logger.info("🛡️ Safe Executor stopped")

    async def _handle_diagnostic_plan(self, event: Event):
        """Executa o plano de correção"""
        if not self.running:
            return

        plan = event.data.get("plan", [])

        for action in plan:
            success = await self._execute_action(action)

            if success:
                event_bus.publish(
                    EventType.SYSTEM_CORRECTION_SUCCEEDED,
                    data={"action": action},
                    source="safe_executor",
                )
            else:
                event_bus.publish(
                    EventType.SYSTEM_CORRECTION_FAILED,
                    data={"action": action},
                    source="safe_executor",
                )

    async def _execute_action(self, action: Dict) -> bool:
        """Executes a single action safely"""
        # Support both Portuguese and English keys for backward compatibility
        description = action.get("descricao") or action.get(
            "description", "No description"
        )
        logger.info(f"🔧 Executing fix: {description}")

        start_time = time.time()
        action_type = action.get("tipo")
        target_file = action.get("arquivo")
        problem_hash = action.get("problem_hash")  # If provided by the healer

        if not target_file:
            logger.error("Action missing target file")
            return False

        full_path = system_manifest.project_root / target_file

        # 1. Verification
        if not full_path.exists():
            logger.error(f"Target file not found: {full_path}")
            return False

        # 2. Backup
        backup_path = self._create_backup(full_path)
        if not backup_path:
            return False

        # 3. Apply Change
        success = False
        error_message = None
        try:
            if action_type == "codigo":
                self._apply_code_change(full_path, action)
            elif action_type == "configuracao":
                self._apply_config_change(full_path, action)

            # 4. Validation
            if self._validate_change(full_path):
                logger.info("✅ Fix validated successfully")
                success = True
            else:
                logger.warning("❌ Validation failed, rolling back...")
                error_message = "Validation failed"
                self._restore_backup(backup_path, full_path)

        except Exception as e:
            logger.error(f"💥 Exception during execution: {e}")
            error_message = str(e)
            self._restore_backup(backup_path, full_path)

        # 5. Record result in knowledge base
        execution_time_ms = int((time.time() - start_time) * 1000)
        if problem_hash:
            try:
                knowledge_db.record_solution(
                    problem_hash=problem_hash,
                    action_type=action_type or "unknown",
                    description=action.get("descricao")
                    or action.get("description", "No description"),
                    success=success,
                    files_modified=[target_file],
                    code_diff=action.get("codigo_corrigido"),
                    impact_score=1.0 if success else 0.0,
                    execution_time_ms=execution_time_ms,
                    error_message=error_message,
                )
            except Exception as e:
                logger.warning(f"Failed to record solution in knowledge base: {e}")

        return success

    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """Cria um backup timestamped do arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.{timestamp}.bak"
        backup_path = BACKUP_DIR / backup_name

        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None

    def _restore_backup(self, backup_path: Path, target_path: Path):
        """Restaura o arquivo original"""
        try:
            shutil.copy2(backup_path, target_path)
            logger.info(f"🔄 Restored from {backup_path.name}")
        except Exception as e:
            logger.critical(f"FATAL: Restore failed! {e}")

    def _apply_code_change(self, file_path: Path, action: Dict):
        """Aplica mudança de código"""
        # Se 'codigo_corrigido' is full content
        if "codigo_corrigido" in action:
            new_content = action["codigo_corrigido"]
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        # TODO: Implement partial replacement if needed

    def _apply_config_change(self, file_path: Path, action: Dict):
        """Aplica mudança de configuração usando patching inteligente"""
        patch_data = action.get("codigo_corrigido") or action.get("config_patch")
        if not patch_data:
            logger.warning("No config data found in action")
            return

        suffix = file_path.suffix.lower()
        if suffix == ".json":
            self._patch_json(file_path, patch_data)
        elif suffix in [".yaml", ".yml"]:
            self._patch_yaml(file_path, patch_data)
        elif suffix == ".env" or file_path.name == ".env":
            self._patch_env(file_path, patch_data)
        else:
            # Fallback for unknown extensions: direct write
            with open(file_path, "w", encoding="utf-8") as f:
                if isinstance(patch_data, str):
                    f.write(patch_data)
                else:
                    json.dump(patch_data, f, indent=4)

    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Recursively merges source into target"""
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def _patch_json(self, file_path: Path, patch_data: Dict):
        """Patches a JSON file by merging new data"""
        try:
            content = {}
            if file_path.exists() and file_path.stat().st_size > 0:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = json.load(f)

            if isinstance(patch_data, dict):
                self._deep_merge(content, patch_data)
            else:
                content = patch_data

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=4)
        except Exception as e:
            logger.error(f"JSON patching failed: {e}")
            raise

    def _patch_yaml(self, file_path: Path, patch_data: Dict):
        """Patches a YAML file by merging new data"""
        try:
            import yaml

            content = {}
            if file_path.exists() and file_path.stat().st_size > 0:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = yaml.safe_load(f) or {}

            if isinstance(patch_data, dict):
                self._deep_merge(content, patch_data)
            else:
                content = patch_data

            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(content, f, default_flow_style=False)
        except ImportError:
            logger.warning("PyYAML not found, falling back to full overwrite")
            if isinstance(patch_data, str):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(patch_data)
            else:
                raise Exception("PyYAML is required for dictionary merging")
        except Exception as e:
            logger.error(f"YAML patching failed: {e}")
            raise

    def _patch_env(self, file_path: Path, patch_data: Dict):
        """Patches a .env file by updating or adding keys"""
        try:
            lines = []
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

            if isinstance(patch_data, dict):
                for key, value in patch_data.items():
                    found = False
                    for i, line in enumerate(lines):
                        if line.strip().startswith(f"{key}="):
                            lines[i] = f"{key}={value}\n"
                            found = True
                            break
                    if not found:
                        lines.append(f"{key}={value}\n")
            elif isinstance(patch_data, str):
                if "=" in patch_data:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(patch_data)
                    return
                else:
                    lines.append(patch_data if patch_data.endswith("\n") else patch_data + "\n")

            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception as e:
            logger.error(f"ENV patching failed: {e}")
            raise

    def _validate_change(self, file_path: Path) -> bool:
        """Valida se o arquivo modificado é válido"""
        # 1. Syntax Check
        suffix = file_path.suffix.lower()

        if suffix == ".py":
            try:
                py_compile.compile(str(file_path), doraise=True)
            except py_compile.PyCompileError:
                logger.error(f"Syntax error in modified Python file: {file_path}")
                return False
        elif suffix == ".json":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json.load(f)
            except Exception as e:
                logger.error(f"Invalid JSON in modified file: {e}")
                return False
        elif suffix in [".yaml", ".yml"]:
            try:
                import yaml
                with open(file_path, "r", encoding="utf-8") as f:
                    yaml.safe_load(f)
            except ImportError:
                pass  # Cannot validate if PyYAML is missing
            except Exception as e:
                logger.error(f"Invalid YAML in modified file: {e}")
                return False

        # 2. Basic Import Check (Runtime)
        # TODO: Run specific unit tests if available

        return True


# Singleton
safe_executor = SafeExecutor()
