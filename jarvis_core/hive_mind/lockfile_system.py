"""
Hive Mind - Lockfile System
Controle de concorrência entre dispositivos
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import socket

logger = logging.getLogger(__name__)

class LockfileManager:
    """Gerenciador de lockfile para evitar conflitos"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.lock_file = Path("data/jarvis.lock")
        self.hostname = socket.gethostname()
    
    async def acquire_lock(self) -> bool:
        """Tenta adquirir lock"""
        logger.info(f"🔒 Tentando adquirir lock para {self.device_id}...")
        
        # Verificar se já existe lock
        if self.lock_file.exists():
            lock_data = self._read_lock()
            
            if lock_data:
                logger.warning(f"⚠️ Lock já existe: {lock_data['device_id']} ({lock_data['hostname']})")
                logger.info("Entrando em modo read-only...")
                return False
        
        # Criar novo lock
        lock_data = {
            "device_id": self.device_id,
            "hostname": self.hostname,
            "timestamp": datetime.now().isoformat(),
            "pid": os.getpid()
        }
        
        self._write_lock(lock_data)
        logger.info(f"✅ Lock adquirido: {self.device_id}")
        return True
    
    async def release_lock(self) -> bool:
        """Libera lock"""
        logger.info(f"🔓 Liberando lock...")
        
        if not self.lock_file.exists():
            logger.warning("⚠️ Lock não existe")
            return False
        
        # Verificar se é nosso lock
        lock_data = self._read_lock()
        
        if lock_data and lock_data.get("device_id") == self.device_id:
            self.lock_file.unlink()
            logger.info("✅ Lock liberado")
            return True
        else:
            logger.error("❌ Lock pertence a outro dispositivo!")
            return False
    
    def check_active_device(self) -> Optional[str]:
        """Retorna ID do dispositivo ativo"""
        if not self.lock_file.exists():
            return None
        
        lock_data = self._read_lock()
        return lock_data.get("device_id") if lock_data else None
    
    def force_unlock(self) -> bool:
        """Força remoção do lock (emergência)"""
        logger.warning("⚠️ Forçando unlock...")
        
        if self.lock_file.exists():
            self.lock_file.unlink()
            logger.info("✅ Lock removido à força")
            return True
        
        return False
    
    def _read_lock(self) -> Optional[dict]:
        """Lê dados do lock"""
        try:
            with open(self.lock_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def _write_lock(self, data: dict):
        """Escreve lock"""
        self.lock_file.parent.mkdir(exist_ok=True)
        with open(self.lock_file, 'w') as f:
            json.dump(data, f, indent=2)


import os
