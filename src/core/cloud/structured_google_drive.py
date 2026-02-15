#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Structured Google Drive Integration
================================================================
Sistema de integraÃ§Ã£o estruturada com Google Drive que evita 
conflitos com contas compartilhadas e organiza dados hierarquicamente.
"""

import os
import json
import shutil
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time
import logging
import zipfile

# Google Drive API
try:
    from googleapiclient.discovery import build  # type: ignore
    from google.auth.transport.requests import Request  # type: ignore
    from google.oauth2.credentials import Credentials  # type: ignore
    from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
    GOOGLE_API_AVAILABLE = True
except ImportError:
    # Fallback when Google API not available
    class MockGoogleAPI:
        def __init__(self, *args, **kwargs): pass
        def build(self, *args, **kwargs): return None
        @classmethod
        def from_authorized_user_file(cls, *args, **kwargs): return cls()
        @classmethod
        def from_client_secrets_file(cls, *args, **kwargs): return cls()
        @classmethod
        def run_local_server(cls, *args, **kwargs): return cls()
        @property
        def valid(self): return False
        @property
        def expired(self): return False
        @property
        def refresh_token(self): return None
        def refresh(self, *args): pass
        def to_json(self): return "{}"
    
    build = MockGoogleAPI
    Request = MockGoogleAPI
    Credentials = MockGoogleAPI
    InstalledAppFlow = MockGoogleAPI
    GOOGLE_API_AVAILABLE = False
    print("âš ï¸ Google API nÃ£o disponÃ­vel - funcionalidade limitada")

# Local imports
from src.core.identity.microsoft_device_identifier import MicrosoftDeviceIdentifier

logger = logging.getLogger(__name__)

class StructuredGoogleDriveManager:
    """
    â˜ï¸ GERENCIADOR ESTRUTURADO DO GOOGLE DRIVE
    
    Funcionalidades:
    - DetecÃ§Ã£o automÃ¡tica do Google Drive local
    - Estrutura hierÃ¡rquica organizada por usuÃ¡rio
    - SincronizaÃ§Ã£o inteligente sem conflitos
    - Backup automÃ¡tico de modelos treinados
    - ConsolidaÃ§Ã£o de dados entre dispositivos
    - Cache local para performance
    - Monitoramento de mudanÃ§as
    """
    
    # Scopes necessÃ¡rios para Google Drive API
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self, jarvis_core, microsoft_identifier: MicrosoftDeviceIdentifier):
        self.jarvis_core = jarvis_core
        self.microsoft_identifier = microsoft_identifier
        
        # Paths locais
        self.base_path = Path(jarvis_core.config['system']['base_path'])
        self.data_path = self.base_path / "data"
        self.cache_path = self.data_path / "google_drive_cache"
        self.credentials_path = self.data_path / "google_credentials"
        
        # Criar diretÃ³rios necessÃ¡rios
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.credentials_path.mkdir(parents=True, exist_ok=True)
        
        # Estados
        self.local_drive_path: Optional[Path] = None
        self.google_service = None
        self.user_folder_id: Optional[str] = None
        self.sync_active = False
        self.last_sync: Optional[datetime] = None
        
        # ConfiguraÃ§Ãµes
        self.user_folder_name = "JARVIS_default"
        self.sync_interval_minutes = 15
        self.auto_sync_enabled = True
        self.compression_enabled = True
        
        # Threading
        self.sync_thread: Optional[threading.Thread] = None
        self.stop_sync = threading.Event()
        
        print("â˜ï¸ Structured Google Drive Manager inicializado")
    
    def initialize(self) -> bool:
        """ðŸš€ INICIALIZA O SISTEMA GOOGLE DRIVE"""
        
        print("ðŸ” Inicializando integraÃ§Ã£o Google Drive...")
        
        try:
            # 1. Detectar Google Drive local
            if not self._detect_local_drive():
                print("ðŸ“‚ Google Drive local nÃ£o detectado")
                return False
            
            # 2. Configurar nome da pasta do usuÃ¡rio
            self._setup_user_folder_name()
            
            # 3. Configurar API do Google Drive (se disponÃ­vel)
            if GOOGLE_API_AVAILABLE:
                self._setup_google_api()
            
            # 4. Criar estrutura de pastas
            self._create_folder_structure()
            
            # 5. Iniciar sincronizaÃ§Ã£o automÃ¡tica
            if self.auto_sync_enabled:
                self._start_auto_sync()
            
            print("âœ… Google Drive configurado com sucesso")
            return True
            
        except Exception as e:
            print(f"âŒ Erro inicializando Google Drive: {e}")
            return False
    
    def _detect_local_drive(self) -> bool:
        """ðŸ“‚ DETECTA PASTA LOCAL DO GOOGLE DRIVE"""
        
        print("   ðŸ” Procurando pasta local do Google Drive...")
        
        try:
            # Caminhos comuns do Google Drive
            common_paths = [
                Path.home() / "Google Drive",
                Path.home() / "GoogleDrive", 
                Path("C:") / "Users" / os.getenv("USERNAME", "") / "Google Drive",
                Path("C:") / "GoogleDrive",
                Path("D:") / "Google Drive",
                Path("E:") / "Google Drive"
            ]
            
            for path in common_paths:
                if path.exists() and path.is_dir():
                    # Verificar se Ã© realmente uma pasta do Google Drive
                    if self._is_google_drive_folder(path):
                        self.local_drive_path = path
                        print(f"   âœ… Google Drive encontrado: {path}")
                        return True
            
            print("   âŒ Pasta local do Google Drive nÃ£o encontrada")
            return False
            
        except Exception as e:
            print(f"   âŒ Erro detectando Google Drive local: {e}")
            return False
    
    def _is_google_drive_folder(self, path: Path) -> bool:
        """ðŸ” VERIFICA SE Ã‰ PASTA DO GOOGLE DRIVE"""
        
        try:
            # Verificar arquivos/pastas caracterÃ­sticas do Google Drive
            indicators = [
                path / ".tmp.drivedownload",
                path / "desktop.ini"
            ]
            
            # Se tem pelo menos um indicador
            for indicator in indicators:
                if indicator.exists():
                    return True
            
            # Verificar se tem estrutura tÃ­pica do Google Drive
            # (pastas com muitos arquivos, estrutura especÃ­fica)
            subdirs = [d for d in path.iterdir() if d.is_dir()]
            
            # Se tem muitas pastas, provavelmente Ã© Google Drive
            if len(subdirs) > 3:
                return True
            
            # Fallback: se a pasta existe e tem nome correto
            return "google" in path.name.lower() and "drive" in path.name.lower()
            
        except Exception:
            return False
    
    def _setup_user_folder_name(self):
        """ðŸ‘¤ CONFIGURA NOME DA PASTA DO USUÃRIO"""
        
        try:
            if self.microsoft_identifier.microsoft_account:
                # Usar parte do email antes do @
                email = self.microsoft_identifier.microsoft_account.account_email
                username = email.split('@')[0]
                
                # Criar nome limpo e Ãºnico
                self.user_folder_name = f"JARVIS_{username}"
                
            else:
                # Fallback usando nome do computador
                computer_name = os.getenv('COMPUTERNAME', 'unknown')
                self.user_folder_name = f"JARVIS_{computer_name}"
            
            print(f"   ðŸ“ Nome da pasta do usuÃ¡rio: {self.user_folder_name}")
            
        except Exception as e:
            print(f"âŒ Erro configurando nome da pasta: {e}")
            self.user_folder_name = "JARVIS_default"
    
    def _setup_google_api(self):
        """ðŸ”‘ CONFIGURA API DO GOOGLE DRIVE"""
        
        print("   ðŸ”‘ Configurando API Google Drive...")
        
        try:
            creds = None
            token_file = self.credentials_path / "token.json"
            credentials_file = self.credentials_path / "credentials.json"
            
            # Carregar token existente
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(str(token_file), self.SCOPES)
            
            # Se nÃ£o hÃ¡ credenciais vÃ¡lidas
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if credentials_file.exists():
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(credentials_file), self.SCOPES)
                        creds = flow.run_local_server(port=0)
                    else:
                        print("   âš ï¸ Arquivo credentials.json nÃ£o encontrado")
                        print("   ðŸ“ Para habilitar API: https://developers.google.com/drive/api/quickstart/python")
                        return False
                
                # Salvar credenciais
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            # Criar serviÃ§o
            self.google_service = build('drive', 'v3', credentials=creds)
            print("   âœ… API Google Drive configurada")
            return True
            
        except Exception as e:
            print(f"   âŒ Erro configurando API: {e}")
            return False
    
    def _create_folder_structure(self):
        """ðŸ“ CRIA ESTRUTURA DE PASTAS HIERÃRQUICA"""
        
        if not self.local_drive_path:
            return
        
        print("   ðŸ“ Criando estrutura de pastas...")
        
        try:
            # Pasta principal do usuÃ¡rio
            user_folder = self.local_drive_path / self.user_folder_name
            user_folder.mkdir(exist_ok=True)
            
            # Subpastas organizadas
            subfolders = {
                "models": "ðŸ§  Modelos treinados",
                "datasets": "ðŸ“Š Datasets de treinamento", 
                "configs": "âš™ï¸ ConfiguraÃ§Ãµes",
                "logs": "ðŸ“ Logs do sistema",
                "backups": "ðŸ’¾ Backups automÃ¡ticos",
                "sync": "ðŸ”„ SincronizaÃ§Ã£o entre dispositivos",
                "exports": "ðŸ“¤ ExportaÃ§Ãµes e relatÃ³rios",
                "temp": "ðŸ—‚ï¸ Arquivos temporÃ¡rios"
            }
            
            for folder_name, description in subfolders.items():
                folder_path = user_folder / folder_name
                folder_path.mkdir(exist_ok=True)
                
                # Criar arquivo README em cada pasta
                readme_path = folder_path / "README.md"
                if not readme_path.exists():
                    readme_content = f"# {description}\n\n"
                    readme_content += f"Pasta criada automaticamente pelo JARVIS.\n"
                    readme_content += f"UsuÃ¡rio: {self.user_folder_name}\n"
                    readme_content += f"Criado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
            
            print(f"   âœ… Estrutura criada em: {user_folder}")
            
        except Exception as e:
            print(f"âŒ Erro criando estrutura: {e}")
    
    def sync_models_to_drive(self, models_data: Dict[str, Any]) -> bool:
        """ðŸ§  SINCRONIZA MODELOS PARA O DRIVE"""
        
        print("ðŸ§  Sincronizando modelos para o Google Drive...")
        
        try:
            if not self.local_drive_path:
                print("âŒ Google Drive local nÃ£o disponÃ­vel")
                return False
            
            models_folder = self.local_drive_path / self.user_folder_name / "models"
            
            # Criar arquivo de metadados
            metadata = {
                "sync_timestamp": datetime.now().isoformat(),
                "device_id": self.microsoft_identifier.device_fingerprint.device_id if self.microsoft_identifier.device_fingerprint else "unknown",
                "user_account": self.microsoft_identifier.microsoft_account.account_email if self.microsoft_identifier.microsoft_account else "unknown",
                "models_count": len(models_data),
                "total_size": sum(len(str(model)) for model in models_data.values())
            }
            
            # Salvar modelos
            for model_name, model_data in models_data.items():
                model_file = models_folder / f"{model_name}_{int(time.time())}.json"
                
                with open(model_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "metadata": metadata,
                        "model_name": model_name,
                        "model_data": model_data
                    }, f, indent=2, ensure_ascii=False)
                
                print(f"   âœ… Modelo salvo: {model_name}")
            
            # Salvar metadata geral
            metadata_file = models_folder / "sync_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print("âœ… Modelos sincronizados com sucesso")
            return True
            
        except Exception as e:
            print(f"âŒ Erro sincronizando modelos: {e}")
            return False
    
    def sync_configs_to_drive(self) -> bool:
        """âš™ï¸ SINCRONIZA CONFIGURAÃ‡Ã•ES PARA O DRIVE"""
        
        print("âš™ï¸ Sincronizando configuraÃ§Ãµes...")
        
        try:
            if not self.local_drive_path:
                return False
            
            configs_folder = self.local_drive_path / self.user_folder_name / "configs"
            
            # Arquivos de configuraÃ§Ã£o para sincronizar
            config_files = [
                self.base_path / "config" / "ai_config.yaml",
                self.base_path / "config" / "auto_healing.yaml", 
                self.base_path / "config" / "settings.json"
            ]
            
            sync_info = {
                "sync_timestamp": datetime.now().isoformat(),
                "device_id": self.microsoft_identifier.device_fingerprint.device_id if self.microsoft_identifier.device_fingerprint else "unknown",
                "synced_files": []
            }
            
            for config_file in config_files:
                if config_file.exists():
                    # Criar nome Ãºnico para evitar conflitos
                    timestamp = int(time.time())
                    device_id = self.microsoft_identifier.device_fingerprint.device_id[:8] if self.microsoft_identifier.device_fingerprint else "unknown"
                    
                    target_name = f"{config_file.stem}_{device_id}_{timestamp}{config_file.suffix}"
                    target_path = configs_folder / target_name
                    
                    # Copiar arquivo
                    shutil.copy2(config_file, target_path)
                    sync_info["synced_files"].append({
                        "original": str(config_file),
                        "synced_as": target_name,
                        "size": target_path.stat().st_size
                    })
                    
                    print(f"   âœ… Config sincronizado: {config_file.name}")
            
            # Salvar informaÃ§Ãµes de sincronizaÃ§Ã£o
            sync_file = configs_folder / f"sync_info_{int(time.time())}.json"
            with open(sync_file, 'w', encoding='utf-8') as f:
                json.dump(sync_info, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"âŒ Erro sincronizando configuraÃ§Ãµes: {e}")
            return False
    
    def backup_system_to_drive(self) -> bool:
        """ðŸ’¾ CRIA BACKUP COMPLETO NO DRIVE"""
        
        print("ðŸ’¾ Criando backup completo no Google Drive...")
        
        try:
            if not self.local_drive_path:
                return False
            
            backups_folder = self.local_drive_path / str(self.user_folder_name) / "backups"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            device_id = self.microsoft_identifier.device_fingerprint.device_id[:8] if self.microsoft_identifier.device_fingerprint else "unknown"
            
            backup_name = f"JARVIS_backup_{device_id}_{timestamp}"
            backup_file = backups_folder / f"{backup_name}.zip"
            
            # Criar backup compactado
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Adicionar arquivos importantes
                important_paths = [
                    self.base_path / "config",
                    self.base_path / "data" / "system_health.json",
                    self.base_path / "data" / "memories",
                    self.base_path / "data" / "learning"
                ]
                
                added_files = 0
                total_size = 0
                
                for path in important_paths:
                    if path.exists():
                        if path.is_file():
                            zipf.write(path, path.relative_to(self.base_path))
                            added_files += 1
                            total_size += path.stat().st_size
                        elif path.is_dir():
                            for file_path in path.rglob("*"):
                                if file_path.is_file() and not file_path.name.startswith('.'):
                                    try:
                                        zipf.write(file_path, file_path.relative_to(self.base_path))
                                        added_files += 1
                                        total_size += file_path.stat().st_size
                                    except Exception:
                                        continue  # Pular arquivos problemÃ¡ticos
            
            # Criar arquivo de metadados do backup
            metadata = {
                "backup_name": backup_name,
                "created_at": datetime.now().isoformat(),
                "device_id": device_id,
                "user_account": self.microsoft_identifier.microsoft_account.account_email if self.microsoft_identifier.microsoft_account else "unknown",
                "files_count": added_files,
                "total_size_bytes": total_size,
                "backup_size_bytes": backup_file.stat().st_size,
                "compression_ratio": round((1 - backup_file.stat().st_size / max(1, total_size)) * 100, 2)
            }
            
            metadata_file = backups_folder / f"{backup_name}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"âœ… Backup criado: {backup_file.name}")
            print(f"   ðŸ“ {added_files} arquivos, {total_size/1024/1024:.1f} MB")
            print(f"   ðŸ“¦ Compactado para {backup_file.stat().st_size/1024/1024:.1f} MB")
            
            return True
            
        except Exception as e:
            print(f"âŒ Erro criando backup: {e}")
            return False
    
    def consolidate_data_from_devices(self) -> Dict[str, Any]:
        """ðŸ”„ CONSOLIDA DADOS DE MÃšLTIPLOS DISPOSITIVOS"""
        
        print("ðŸ”„ Consolidando dados de dispositivos...")
        
        try:
            if not self.local_drive_path:
                return {}
            
            sync_folder = self.local_drive_path / str(self.user_folder_name) / "sync"
            consolidated_data = {
                "models": {},
                "configs": {},
                "learning_data": {},
                "devices": [],
                "consolidation_timestamp": datetime.now().isoformat()
            }
            
            # Buscar dados de modelos de todos os dispositivos
            models_folder = self.local_drive_path / self.user_folder_name / "models"
            if models_folder.exists():
                for model_file in models_folder.glob("*.json"):
                    try:
                        with open(model_file, 'r', encoding='utf-8') as f:
                            model_data = json.load(f)
                        
                        if "model_name" in model_data:
                            model_name = model_data["model_name"]
                            device_id = model_data.get("metadata", {}).get("device_id", "unknown")
                            
                            if model_name not in consolidated_data["models"]:
                                consolidated_data["models"][model_name] = []
                            
                            consolidated_data["models"][model_name].append({
                                "device_id": device_id,
                                "data": model_data["model_data"],
                                "timestamp": model_data.get("metadata", {}).get("sync_timestamp")
                            })
                    except Exception:
                        continue
            
            # Buscar configuraÃ§Ãµes
            configs_folder = self.local_drive_path / self.user_folder_name / "configs"
            if configs_folder.exists():
                for config_file in configs_folder.glob("*.json"):
                    if "sync_info" in config_file.name:
                        try:
                            with open(config_file, 'r', encoding='utf-8') as f:
                                sync_data = json.load(f)
                            
                            device_id = sync_data.get("device_id", "unknown")
                            if device_id not in consolidated_data["configs"]:
                                consolidated_data["configs"][device_id] = []
                            
                            consolidated_data["configs"][device_id].extend(sync_data.get("synced_files", []))
                        except Exception:
                            continue
            
            # Salvar dados consolidados
            consolidated_file = sync_folder / f"consolidated_data_{int(time.time())}.json"
            with open(consolidated_file, 'w', encoding='utf-8') as f:
                json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
            
            print(f"âœ… Dados consolidados de {len(consolidated_data['models'])} modelos")
            print(f"   ðŸ“± {len(consolidated_data['configs'])} dispositivos encontrados")
            
            return consolidated_data
            
        except Exception as e:
            print(f"âŒ Erro consolidando dados: {e}")
            return {}
    
    def _start_auto_sync(self):
        """ðŸ”„ INICIA SINCRONIZAÃ‡ÃƒO AUTOMÃTICA"""
        
        if self.sync_active:
            return
        
        self.sync_active = True
        self.stop_sync.clear()
        
        self.sync_thread = threading.Thread(target=self._auto_sync_loop, daemon=True)
        self.sync_thread.start()
        
        print(f"ðŸ”„ SincronizaÃ§Ã£o automÃ¡tica iniciada (intervalo: {self.sync_interval_minutes} minutos)")
    
    def _auto_sync_loop(self):
        """ðŸ” LOOP DE SINCRONIZAÃ‡ÃƒO AUTOMÃTICA"""
        
        while not self.stop_sync.wait(self.sync_interval_minutes * 60):
            try:
                print("ðŸ”„ Executando sincronizaÃ§Ã£o automÃ¡tica...")
                
                # Sincronizar configuraÃ§Ãµes
                self.sync_configs_to_drive()
                
                # Criar backup periÃ³dico (a cada 4 horas)
                if (self.last_sync is None or 
                    datetime.now() - self.last_sync > timedelta(hours=4)):
                    self.backup_system_to_drive()
                
                self.last_sync = datetime.now()
                print("âœ… SincronizaÃ§Ã£o automÃ¡tica concluÃ­da")
                
            except Exception as e:
                print(f"âŒ Erro na sincronizaÃ§Ã£o automÃ¡tica: {e}")
                time.sleep(60)  # Aguardar 1 minuto antes de tentar novamente
    
    def stop_auto_sync(self):
        """â¹ï¸ PARA SINCRONIZAÃ‡ÃƒO AUTOMÃTICA"""
        
        if not self.sync_active:
            return
        
        self.sync_active = False
        self.stop_sync.set()
        
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=5)
        
        print("â¹ï¸ SincronizaÃ§Ã£o automÃ¡tica parada")
    
    def get_drive_status(self) -> Dict[str, Any]:
        """ðŸ“Š STATUS DO GOOGLE DRIVE"""
        
        try:
            if not self.local_drive_path:
                return {"status": "not_detected"}
            
            user_folder = self.local_drive_path / self.user_folder_name
            
            # Calcular estatÃ­sticas
            total_size = 0
            file_count = 0
            
            if user_folder.exists():
                for file_path in user_folder.rglob("*"):
                    if file_path.is_file():
                        try:
                            total_size += file_path.stat().st_size
                            file_count += 1
                        except Exception:
                            continue
            
            return {
                "status": "active",
                "local_path": str(self.local_drive_path),
                "user_folder": self.user_folder_name,
                "user_folder_path": str(user_folder),
                "total_files": file_count,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "api_enabled": self.google_service is not None,
                "auto_sync_active": self.sync_active,
                "last_sync": self.last_sync.isoformat() if self.last_sync else None,
                "sync_interval_minutes": self.sync_interval_minutes
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def manual_sync(self) -> bool:
        """ðŸ”„ SINCRONIZAÃ‡ÃƒO MANUAL COMPLETA"""
        
        print("ðŸ”„ Executando sincronizaÃ§Ã£o manual completa...")
        
        try:
            success = True
            
            # 1. Sincronizar configuraÃ§Ãµes
            if not self.sync_configs_to_drive():
                success = False
            
            # 2. Criar backup
            if not self.backup_system_to_drive():
                success = False
            
            # 3. Consolidar dados
            consolidated = self.consolidate_data_from_devices()
            if not consolidated:
                print("âš ï¸ Nenhum dado para consolidar")
            
            if success:
                print("âœ… SincronizaÃ§Ã£o manual concluÃ­da com sucesso")
            else:
                print("âš ï¸ SincronizaÃ§Ã£o manual concluÃ­da com alguns erros")
            
            return success
            
        except Exception as e:
            print(f"âŒ Erro na sincronizaÃ§Ã£o manual: {e}")
            return False

# Exemplo de uso:
# identifier = MicrosoftDeviceIdentifier("./data")
# drive_manager = StructuredGoogleDriveManager(jarvis_core, identifier)
# drive_manager.initialize()
# drive_manager.manual_sync()
