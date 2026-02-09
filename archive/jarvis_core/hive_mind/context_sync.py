"""
Hive Mind - Context Sync
Sincronização de contexto entre dispositivos
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ContextSync:
    """Gerenciador de sincronização de contexto"""
    
    def __init__(self):
        self.context_file = Path("data/context.json")
        self.context_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.current_context = {
            "last_command": "",
            "current_task": "",
            "active_apps": [],
            "timestamp": "",
            "device_id": ""
        }
    
    def save_context(self, device_id: str, context: Optional[Dict] = None) -> bool:
        """Salva contexto atual"""
        if context:
            self.current_context.update(context)
        
        self.current_context["timestamp"] = datetime.now().isoformat()
        self.current_context["device_id"] = device_id
        
        try:
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_context, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"✅ Contexto salvo: {device_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar contexto: {e}")
            return False
    
    def load_context(self) -> Optional[Dict]:
        """Carrega contexto de outro dispositivo"""
        if not self.context_file.exists():
            return None
        
        try:
            with open(self.context_file, 'r', encoding='utf-8') as f:
                context = json.load(f)
            
            logger.info(f"✅ Contexto carregado: {context.get('device_id', 'unknown')}")
            return context
        except Exception as e:
            logger.error(f"❌ Erro ao carregar contexto: {e}")
            return None
    
    def merge_contexts(self, local: Dict, remote: Dict) -> Dict:
        """Mescla contextos (local tem prioridade)"""
        merged = remote.copy()
        
        # Local sobrescreve remote
        for key, value in local.items():
            if value:  # Só sobrescreve se tiver valor
                merged[key] = value
        
        return merged


# Instância global
context_sync = ContextSync()
