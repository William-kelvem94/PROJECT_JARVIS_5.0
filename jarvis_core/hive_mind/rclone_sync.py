"""
Hive Mind - Rclone Sync Module
Sincronização bidirecional com Google Drive via Rclone
"""

import subprocess
import hashlib
import json
import logging
from pathlib import Path
from typing import Optional, Dict
import asyncio

logger = logging.getLogger(__name__)

class RcloneSync:
    """Gerenciador de sincronização via Rclone"""
    
    def __init__(self, remote_name: str = "gdrive", remote_path: str = "JARVIS_Hive"):
        self.remote_name = remote_name
        self.remote_path = remote_path
        self.remote = f"{remote_name}:{remote_path}"
        
        # Diretórios locais
        self.local_data = Path("data")
        self.local_memory = Path("data/memory")
        self.local_context = Path("data/context.json")
        
        # Garantir que existem
        self.local_data.mkdir(exist_ok=True)
        self.local_memory.mkdir(exist_ok=True)
    
    def check_rclone_installed(self) -> bool:
        """Verifica se rclone está instalado"""
        try:
            result = subprocess.run(
                ["rclone", "version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def check_remote_configured(self) -> bool:
        """Verifica se remote está configurado"""
        try:
            result = subprocess.run(
                ["rclone", "listremotes"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                remotes = result.stdout.strip().split('\n')
                return f"{self.remote_name}:" in remotes
            
            return False
        except:
            return False
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calcula MD5 de um arquivo"""
        if not file_path.exists():
            return ""
        
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        
        return md5.hexdigest()
    
    async def startup_sync(self) -> bool:
        """Sincroniza do remoto para local no startup"""
        logger.info("🌐 Iniciando sync de startup...")
        
        if not self.check_rclone_installed():
            logger.warning("⚠️ Rclone não instalado. Sync desabilitado.")
            return False
        
        if not self.check_remote_configured():
            logger.warning(f"⚠️ Remote '{self.remote_name}' não configurado.")
            logger.info("Configure com: rclone config")
            return False
        
        try:
            # Baixar memória da nuvem
            logger.info(f"📥 Baixando de {self.remote}...")
            
            result = await asyncio.create_subprocess_exec(
                "rclone", "sync",
                self.remote,
                str(self.local_data),
                "--verbose",
                "--checksum",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info("✅ Sync de startup completo!")
                return True
            else:
                logger.error(f"❌ Erro no sync: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no startup sync: {e}")
            return False
    
    async def heartbeat_sync(self) -> bool:
        """Sync periódico (upload context.json)"""
        logger.debug("💓 Heartbeat sync...")
        
        if not self.check_rclone_installed():
            return False
        
        try:
            # Upload apenas context.json (leve)
            if self.local_context.exists():
                result = await asyncio.create_subprocess_exec(
                    "rclone", "copy",
                    str(self.local_context),
                    f"{self.remote}/",
                    "--checksum",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                await result.communicate()
                
                if result.returncode == 0:
                    logger.debug("✅ Context sincronizado")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro no heartbeat: {e}")
            return False
    
    async def shutdown_sync(self) -> bool:
        """Sync completo no shutdown"""
        logger.info("🌐 Sync de shutdown...")
        
        if not self.check_rclone_installed():
            return False
        
        try:
            # Upload completo da memória
            logger.info(f"📤 Enviando para {self.remote}...")
            
            result = await asyncio.create_subprocess_exec(
                "rclone", "sync",
                str(self.local_data),
                self.remote,
                "--verbose",
                "--checksum",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info("✅ Memória sincronizada com a nuvem!")
                return True
            else:
                logger.error(f"❌ Erro no sync: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no shutdown sync: {e}")
            return False
    
    def get_remote_size(self) -> int:
        """Retorna tamanho do remote em bytes"""
        try:
            result = subprocess.run(
                ["rclone", "size", self.remote, "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("bytes", 0)
            
            return 0
        except:
            return 0
    
    def get_sync_status(self) -> Dict:
        """Retorna status do sync"""
        return {
            "rclone_installed": self.check_rclone_installed(),
            "remote_configured": self.check_remote_configured(),
            "remote_name": self.remote_name,
            "remote_path": self.remote_path,
            "remote_size_bytes": self.get_remote_size(),
            "local_data_exists": self.local_data.exists()
        }


# Instância global
rclone_sync = RcloneSync()


# Teste
if __name__ == "__main__":
    import asyncio
    
    async def test():
        sync = RcloneSync()
        
        print("🔍 Status do Rclone:")
        status = sync.get_sync_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        if status["rclone_installed"] and status["remote_configured"]:
            print("\n📥 Testando startup sync...")
            await sync.startup_sync()
    
    asyncio.run(test())
