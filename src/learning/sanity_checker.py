"""
JARVIS 5.0 - Autonomous Sanity Checker
=====================================
Executa testes de integridade em tempo real nos subsistemas crÃ­ticos.
Fornece mÃ©tricas quantitativas de 'Confiabilidade do Sistema'.
"""

import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

try:
    from src.utils.env_manager import get_config
except ImportError:
    get_config = lambda: None

logger = logging.getLogger("JARVIS-SANITY-CHECK")

class SanityChecker:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.last_report = {}
        self.health_score = 0.0 # 0.0 to 1.0

    def run_full_check(self) -> Dict[str, Any]:
        """Executa uma bateria completa de testes internos."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "total_score": 0.0
        }
        
        checks = [
            ("Disk_IO", self._check_disk_io),
            ("Intelligence_LLM", self._check_ollama),
            ("Vision_Pipeline", self._check_vision),
            ("Memory_DB", self._check_memory),
            ("Security_Sentinel", self._check_security)
        ]
        
        passed = 0
        for name, func in checks:
            try:
                success, details = func()
                results["components"][name] = {"status": "PASS" if success else "FAIL", "details": details}
                if success: passed += 1
            except Exception as e:
                results["components"][name] = {"status": "ERROR", "details": str(e)}
        
        results["total_score"] = passed / len(checks)
        self.health_score = results["total_score"]
        self.last_report = results
        
        return results

    def _check_disk_io(self):
        """Verifica se consegue escrever e ler no diretÃ³rio de data"""
        test_file = self.project_root / "data" / ".sanity_test"
        try:
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text("SANITY_CHECK", encoding="utf-8")
            content = test_file.read_text(encoding="utf-8")
            test_file.unlink()
            return content == "SANITY_CHECK", "Disk Read/Write OK"
        except Exception as e:
            return False, str(e)

    def _check_ollama(self):
        """Verifica se o serviÃ§o Ollama estÃ¡ respondendo"""
        try:
            import requests
            
            # Usar URL configurada ou fallback
            config = get_config()
            ollama_url = config.ollama_url if config else "http://localhost:11434"
            
            response = requests.get(f"{ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return len(models) > 0, f"Ollama Online ({len(models)} models available)"
            return False, f"Ollama status code: {response.status_code}"
        except Exception as e:
            return False, f"Ollama connection failed: {e}"

    def _check_vision(self):
        """Verifica se os modelos de visÃ£o estÃ£o carregados"""
        try:
            from src.core.vision.advanced_vision_pipeline import advanced_vision_pipeline
            if advanced_vision_pipeline:
                return True, "Vision Pipeline Instance Global: ONLINE"
            return False, "Vision Pipeline instance is None"
        except Exception as e:
            return False, str(e)

    def _check_memory(self):
        """Verifica conexÃ£o com o banco de dados vetorial"""
        try:
            # Check if neural_memory is available
            try:
                from src.core.intelligence.neural_memory import neural_memory
                if neural_memory and neural_memory.client:
                    return True, "Neural Memory (ChromaDB) Connected"
            except ImportError:
                 return True, "Neural Memory (Fallback Mode): OK"
            return False, "Neural Memory client not initialized"
        except Exception as e:
            return False, str(e)

    def _check_security(self):
        """Verifica se o validador de aÃ§Ãµes estÃ¡ ativo"""
        try:
            from src.core.security.action_validator import action_validator
            if action_validator:
                return True, "Security Validator Active"
            return False, "Security Validator is None"
        except Exception as e:
            return False, str(e)

# Global Instance
sanity_checker = None

def get_sanity_checker(project_root: Path):
    global sanity_checker
    if sanity_checker is None:
        sanity_checker = SanityChecker(project_root)
    return sanity_checker
