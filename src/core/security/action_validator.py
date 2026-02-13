"""
A Jaula de Vidro (Security Middleware)
ValidaÃ§Ã£o rigorosa de aÃ§Ãµes, proteÃ§Ã£o de sistema e backups automÃ¡ticos.
"""

import os
import shutil
import logging
import re
from pathlib import Path
from typing import Tuple, List

# Logger setup
logger = logging.getLogger(__name__)

class ActionValidator:
    def __init__(self):
        # 1. Lista Negra Absoluta (Hardcoded)
        self.BLACKLIST_COMMANDS = [
            "del ", "rm ", "rmdir", "format ", "regedit", "diskpart", 
            "shutdown", "reboot", "mkfs", ":(){ :|:& };:", # Fork bomb
            "chmod 777", "chown", "takeown", "icacls /grant"
        ]
        
        self.BLACKLIST_PATHS = [
            r"C:\Windows\System32",
            r"C:\Windows",
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            r"\.git", # Proteger repositÃ³rio
        ]
        
        # 2. Zonas Seguras (Whitelist)
        # O Jarvis sÃ³ pode escrever aqui
        self.SAFE_ZONES = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")), # Project Root
            os.getenv("TEMP"),
        ]
        
        # Normalizar paths
        self.SAFE_ZONES = [p.lower() for p in self.SAFE_ZONES if p]

    def validate_action(self, action_type: str, target: str) -> Tuple[bool, str]:
        """
        Valida se uma aÃ§Ã£o Ã© segura.
        Retorna: (is_safe: bool, reason: str)
        """
        msg_prefix = f"[SECURITY SHIELD] Blocked {action_type}: "
        
        # ValidaÃ§Ã£o de Comandos Shell
        if action_type == "shell_command":
            for blocked in self.BLACKLIST_COMMANDS:
                if blocked in target.lower():
                    reason = f"Comando proibido detectado: '{blocked}'"
                    logger.critical(f"{msg_prefix} {reason}")
                    return False, f"Acesso negado: {reason}"
                    
        # ValidaÃ§Ã£o de ManipulaÃ§Ã£o de Arquivos
        if action_type in ["write_file", "delete_file", "move_file"]:
            target_path = os.path.abspath(target).lower()
            
            # Check Blacklist Paths
            for blocked_path in self.BLACKLIST_PATHS:
                if blocked_path.lower() in target_path:
                    reason = f"Tentativa de acesso a diretÃ³rio protegido: '{blocked_path}'"
                    logger.critical(f"{msg_prefix} {reason}")
                    return False, f"Acesso negado: {reason}"
            
            # Check Whitelist Zones (Apenas para escrita/modificaÃ§Ã£o)
            is_in_safe_zone = False
            for safe_zone in self.SAFE_ZONES:
                if target_path.startswith(safe_zone):
                    is_in_safe_zone = True
                    break
            
            if not is_in_safe_zone:
                reason = f"Caminho fora da zona segura: '{target}'"
                logger.warning(f"{msg_prefix} {reason}")
                return False, f"Acesso negado: Fora da zona de seguranÃ§a do Jarvis."

        return True, "Action Approved"

    def safe_file_edit(self, filepath: str, new_content: str, reason: str = "Unspecified autonomous update") -> bool:
        """
        EdiÃ§Ã£o segura com Backup AutomÃ¡tico (.bak).
        HITL Integration: Deve ser chamado apenas apÃ³s validaÃ§Ã£o.
        """
        try:
            path = Path(filepath)
            
            # Log evolution through EvolutionEngine
            try:
                from src.core.management.evolution_engine import evolution_engine
                evolution_engine.log_evolution(filepath, "File modification", reason)
            except Exception as e:
                logger.warning(f"Failed to log evolution event: {e}")

            if not path.exists():
                # Arquivo novo nÃ£o precisa de backup, mas precisa de validaÃ§Ã£o de path
                safe, reason = self.validate_action("write_file", filepath)
                if not safe: raise PermissionError(reason)
                
                # Criar diretÃ³rios se necessÃ¡rio
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logger.info(f"ðŸ’¾ Novo arquivo criado: {filepath}")
                return True

            # ValidaÃ§Ã£o
            safe, reason = self.validate_action("write_file", filepath)
            if not safe: raise PermissionError(reason)

            # Criar Backup Rotativo (.bak -> .bak.1)
            backup_path = path.with_suffix(path.suffix + ".bak")
            
            if backup_path.exists():
                # Rotacionar histÃ³rico simples (1 nÃ­vel)
                backup_history = path.with_suffix(path.suffix + ".bak.1")
                shutil.copy2(backup_path, backup_history)
                
            shutil.copy2(path, backup_path)
            logger.info(f"ðŸ›¡ï¸ Backup de seguranÃ§a criado: {backup_path}")

            # Escrever o novo conteÃºdo
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            return True

        except Exception as e:
            logger.error(f"âŒ Falha na ediÃ§Ã£o segura de '{filepath}': {e}")
            raise e

            raise e

    def check_intent_safety(self, command: str) -> bool:
        """
        ðŸ›¡ï¸ SeguranÃ§a Cognitiva (Sentinel)
        Usa LLM leve para detectar intenÃ§Ãµes maliciosas em comandos ofuscados (base64, aliases, etc).
        """
        try:
            import ollama
            
            # Prompt de SeguranÃ§a Estrita
            prompt = (
                f"Analise o seguinte comando de sistema quanto a riscos de seguranÃ§a, destruiÃ§Ã£o de dados ou invasÃ£o de privacidade.\n"
                f"Comando: '{command}'\n\n"
                f"Responda APENAS 'SAFE' se for seguro ou 'UNSAFE' se tiver risco (deletar arquivos, formatar, exfiltrar dados, reverse shell).\n"
                f"Se estiver em dÃºvida, responda UNSAFE."
            )
            
            # Usar modelo Sentinela (Tier Fast) - RÃ¡pido e focado
            response = ollama.chat(model='qwen2.5:3b', messages=[
                {'role': 'system', 'content': 'You are a security sentinel. Output only SAFE or UNSAFE.'},
                {'role': 'user', 'content': prompt}
            ])
            
            verdict = response['message']['content'].strip().upper()
            
            if "UNSAFE" in verdict:
                logger.critical(f"ðŸš« [SENTINEL] Comando bloqueado por IA: '{command}'")
                return False
                
            if "SAFE" in verdict:
                return True
                
            # Default deny se a resposta for confusa
            logger.warning(f"âš ï¸ [SENTINEL] Veredito confuso ('{verdict}'). Bloqueando por cautela.")
            return False
            
        except Exception as e:
            logger.error(f"âš ï¸ Erro no Security Sentinel: {e}. Bloqueando por falha aberta.")
            return False # Fail-safe closed

# InstÃ¢ncia Global
action_validator = ActionValidator()
