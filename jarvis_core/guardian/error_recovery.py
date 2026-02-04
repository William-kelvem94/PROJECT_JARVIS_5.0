"""
Guardian - Error Recovery
Sistema de recuperação automática de erros
"""

import logging
import traceback
from typing import Optional, Callable
import asyncio

logger = logging.getLogger(__name__)

class ErrorRecovery:
    """Sistema de recuperação de erros"""
    
    def __init__(self):
        self.error_count = 0
        self.recovery_strategies = {}
        self.last_error = None
        
        # Registrar estratégias padrão
        self._register_default_strategies()
        
        logger.info("✅ Error Recovery inicializado")
    
    def _register_default_strategies(self):
        """Registra estratégias de recuperação"""
        
        # Import Error → Instalar pacote
        self.recovery_strategies["ImportError"] = self._recover_import_error
        
        # Connection Error → Retry
        self.recovery_strategies["ConnectionError"] = self._recover_connection_error
        
        # File Not Found → Criar arquivo
        self.recovery_strategies["FileNotFoundError"] = self._recover_file_not_found
        
        # Permission Error → Pedir elevação
        self.recovery_strategies["PermissionError"] = self._recover_permission_error
    
    async def handle_error(self, error: Exception) -> bool:
        """Trata erro e tenta recuperar"""
        self.error_count += 1
        self.last_error = error
        
        error_type = type(error).__name__
        logger.error(f"❌ Erro #{self.error_count}: {error_type}")
        logger.error(f"   {str(error)}")
        
        # Tentar recuperação
        if error_type in self.recovery_strategies:
            logger.info(f"🔧 Tentando recuperação automática...")
            
            try:
                success = await self.recovery_strategies[error_type](error)
                
                if success:
                    logger.info(f"✅ Recuperação bem-sucedida!")
                    return True
                else:
                    logger.warning(f"⚠️ Recuperação falhou")
                    return False
            except Exception as recovery_error:
                logger.error(f"❌ Erro na recuperação: {recovery_error}")
                return False
        else:
            logger.warning(f"⚠️ Sem estratégia de recuperação para: {error_type}")
            return False
    
    async def _recover_import_error(self, error: ImportError) -> bool:
        """Recupera de ImportError instalando pacote"""
        import subprocess
        import sys
        
        # Extrair nome do pacote
        error_msg = str(error)
        if "No module named" in error_msg:
            module_name = error_msg.split("'")[1]
            
            logger.info(f"📦 Instalando {module_name}...")
            
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", module_name
                ])
                logger.info(f"✅ {module_name} instalado!")
                return True
            except:
                return False
        
        return False
    
    async def _recover_connection_error(self, error: Exception) -> bool:
        """Recupera de ConnectionError com retry"""
        logger.info("🔄 Aguardando 5s e tentando novamente...")
        await asyncio.sleep(5)
        return True  # Sinaliza para retry
    
    async def _recover_file_not_found(self, error: FileNotFoundError) -> bool:
        """Recupera de FileNotFoundError criando arquivo"""
        from pathlib import Path
        
        file_path = Path(error.filename) if error.filename else None
        
        if file_path:
            logger.info(f"📝 Criando arquivo: {file_path}")
            
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.touch()
                logger.info(f"✅ Arquivo criado!")
                return True
            except:
                return False
        
        return False
    
    async def _recover_permission_error(self, error: PermissionError) -> bool:
        """Recupera de PermissionError"""
        logger.warning("⚠️ Permissão negada. Execute como administrador.")
        return False
    
    def get_error_stats(self) -> dict:
        """Retorna estatísticas de erros"""
        return {
            "total_errors": self.error_count,
            "last_error": str(self.last_error) if self.last_error else None
        }


# Instância global
error_recovery = ErrorRecovery()


# Decorator para auto-recovery
def auto_recover(func):
    """Decorator para recuperação automática"""
    async def wrapper(*args, **kwargs):
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"⚠️ Tentativa {attempt + 1}/{max_retries} falhou")
                
                if attempt < max_retries - 1:
                    recovered = await error_recovery.handle_error(e)
                    if not recovered:
                        break
                else:
                    raise
        
        return None
    
    return wrapper
