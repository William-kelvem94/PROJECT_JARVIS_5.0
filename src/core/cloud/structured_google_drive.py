#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Structured Google Drive Integration
================================================================
Sistema de integração estruturada com Google Drive que evita 
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
    print("⚠️ Google API não disponível - funcionalidade limitada")

# Local imports
from src.core.identity.microsoft_device_identifier import MicrosoftDeviceIdentifier

logger = logging.getLogger(__name__)

class StructuredGoogleDriveManager:
    """
    ☁️ GERENCIADOR ESTRUTURADO DO GOOGLE DRIVE
    
    Funcionalidades:
    - Detecção automática do Google Drive local
    - Estrutura hierárquica organizada por usuário
    - Sincronização inteligente sem conflitos
    - Backup automático de modelos treinados
    - Consolidação de dados entre dispositivos
    - Cache local para performance
    - Monitoramento de mudanças
    """
    
    # Scopes necessários para Google Drive API
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self, jarvis_core, microsoft_identifier: MicrosoftDeviceIdentifier):
        self.jarvis_core = jarvis_core
        self.microsoft_identifier = microsoft_identifier
        
        # Paths locais
        self.base_path = Path(jarvis_core.config['system']['base_path'])
        self.data_path = self.base_path / "data"
        self.cache_path = self.data_path / "google_drive_cache"
        self.credentials_path = self.data_path / "google_credentials"
        
        # Criar diretórios necessários
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.credentials_path.mkdir(parents=True, exist_ok=True)
        
        # Estados
        self.local_drive_path: Optional[Path] = None
        self.google_service = None
        self.user_folder_id: Optional[str] = None
        self.sync_active = False
        self.last_sync: Optional[datetime] = None
        
        # Configurações
        self.user_folder_name = "JARVIS_default"
        self.sync_interval_minutes = 15
        self.auto_sync_enabled = True
        self.compression_enabled = True
        
        # Threading
        self.sync_thread: Optional[threading.Thread] = None
        self.stop_sync = threading.Event()
        
        print("☁️ Structured Google Drive Manager inicializado")
    
    def initialize(self) -> bool:
        """🚀 INICIALIZA O SISTEMA GOOGLE DRIVE"""
        
        print("🔍 Inicializando integração Google Drive...")
        
        try:
            # 1. Detectar Google Drive local
            if not self._detect_local_drive():
                print("📂 Google Drive local não detectado")
                return False
            
            # 2. Configurar nome da pasta do usuário
            self._setup_user_folder_name()
            
            # 3. Configurar API do Google Drive (se disponível)
            if GOOGLE_API_AVAILABLE:
                self._setup_google_api()
            
            # 4. Criar estrutura de pastas
            self._create_folder_structure()
            
            # 5. Iniciar sincronização automática
            if self.auto_sync_enabled:
                self._start_auto_sync()
            
            print("✅ Google Drive configurado com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro inicializando Google Drive: {e}")
            return False
    
    def _detect_local_drive(self) -> bool:
        """📂 DETECTA PASTA LOCAL DO GOOGLE DRIVE"""
        
        print("   🔍 Procurando pasta local do Google Drive...")
        
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
                    # Verificar se é realmente uma pasta do Google Drive
                    if self._is_google_drive_folder(path):
                        self.local_drive_path = path
                        print(f"   ✅ Google Drive encontrado: {path}")
                        return True
            
            print("   ❌ Pasta local do Google Drive não encontrada")
            return False
            
        except Exception as e:
            print(f"   ❌ Erro detectando Google Drive local: {e}")
            return False
    
    def _is_google_drive_folder(self, path: Path) -> bool:
        """🔍 VERIFICA SE É PASTA DO GOOGLE DRIVE"""
        
        try:
            # Verificar arquivos/pastas características do Google Drive
            indicators = [
                path / ".tmp.drivedownload",
                path / "desktop.ini"
            ]
            
            # Se tem pelo menos um indicador
            for indicator in indicators:
                if indicator.exists():
                    return True
            
            # Verificar se tem estrutura típica do Google Drive
            # (pastas com muitos arquivos, estrutura específica)
            subdirs = [d for d in path.iterdir() if d.is_dir()]
            
            # Se tem muitas pastas, provavelmente é Google Drive
            if len(subdirs) > 3:
                return True
            
            # Fallback: se a pasta existe e tem nome correto
            return "google" in path.name.lower() and "drive" in path.name.lower()
            
        except Exception:
            return False
    
    def _setup_user_folder_name(self):
        """👤 CONFIGURA NOME DA PASTA DO USUÁRIO"""
        
        try:
            if self.microsoft_identifier.microsoft_account:
                # Usar parte do email antes do @
                email = self.microsoft_identifier.microsoft_account.account_email
                username = email.split('@')[0]
                
                # Criar nome limpo e único
                self.user_folder_name = f"JARVIS_{username}"
                
            else:
                # Fallback usando nome do computador
                computer_name = os.getenv('COMPUTERNAME', 'unknown')
                self.user_folder_name = f"JARVIS_{computer_name}"
            
            print(f"   📁 Nome da pasta do usuário: {self.user_folder_name}")
            
        except Exception as e:
            print(f"❌ Erro configurando nome da pasta: {e}")
            self.user_folder_name = "JARVIS_default"
    
    def _setup_google_api(self):
        """🔑 CONFIGURA API DO GOOGLE DRIVE"""
        
        print("   🔑 Configurando API Google Drive...")
        
        try:
            creds = None
            token_file = self.credentials_path / "token.json"
            credentials_file = self.credentials_path / "credentials.json"
            
            # Carregar token existente
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(str(token_file), self.SCOPES)
            
            # Se não há credenciais válidas
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if credentials_file.exists():
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(credentials_file), self.SCOPES)
                        creds = flow.run_local_server(port=0)
                    else:
                        print("   ⚠️ Arquivo credentials.json não encontrado")
                        print("   📝 Para habilitar API: https://developers.google.com/drive/api/quickstart/python")
                        return False
                
                # Salvar credenciais
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            # Criar serviço
            self.google_service = build('drive', 'v3', credentials=creds)
            print("   ✅ API Google Drive configurada")
            return True
            
        except Exception as e:
            print(f"   ❌ Erro configurando API: {e}")
            return False
    
    def _create_folder_structure(self):
        """📁 CRIA ESTRUTURA DE PASTAS HIERÁRQUICA"""
        
        if not self.local_drive_path:
            return
        
        print("   📁 Criando estrutura de pastas...")
        
        try:
            # Pasta principal do usuário
            user_folder = self.local_drive_path / self.user_folder_name
            user_folder.mkdir(exist_ok=True)
            
            # Subpastas organizadas
            subfolders = {
                "models": "🧠 Modelos treinados",
                "datasets": "📊 Datasets de treinamento", 
                "configs": "⚙️ Configurações",
                "logs": "📝 Logs do sistema",
                "backups": "💾 Backups automáticos",
                "sync": "🔄 Sincronização entre dispositivos",
                "exports": "📤 Exportações e relatórios",
                "temp": "🗂️ Arquivos temporários"
            }
            
            for folder_name, description in subfolders.items():
                folder_path = user_folder / folder_name
                folder_path.mkdir(exist_ok=True)
                
                # Criar arquivo README em cada pasta
                readme_path = folder_path / "README.md"
                if not readme_path.exists():
                    readme_content = f"# {description}\n\n"
                    readme_content += f"Pasta criada automaticamente pelo JARVIS.\n"
                    readme_content += f"Usuário: {self.user_folder_name}\n"
                    readme_content += f"Criado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
            
            print(f"   ✅ Estrutura criada em: {user_folder}")
            
        except Exception as e:
            print(f"❌ Erro criando estrutura: {e}")
    
    def sync_models_to_drive(self, models_data: Dict[str, Any]) -> bool:
        """🧠 SINCRONIZA MODELOS PARA O DRIVE"""
        
        print("🧠 Sincronizando modelos para o Google Drive...")
        
        try:
            if not self.local_drive_path:
                print("❌ Google Drive local não disponível")
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
                
                print(f"   ✅ Modelo salvo: {model_name}")
            
            # Salvar metadata geral
            metadata_file = models_folder / "sync_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print("✅ Modelos sincronizados com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro sincronizando modelos: {e}")
            return False
    
    def sync_configs_to_drive(self) -> bool:
        """⚙️ SINCRONIZA CONFIGURAÇÕES PARA O DRIVE"""
        
        print("⚙️ Sincronizando configurações...")
        
        try:
            if not self.local_drive_path:
                return False
            
            configs_folder = self.local_drive_path / self.user_folder_name / "configs"
            
            # Arquivos de configuração para sincronizar
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
                    # Criar nome único para evitar conflitos
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
                    
                    print(f"   ✅ Config sincronizado: {config_file.name}")
            
            # Salvar informações de sincronização
            sync_file = configs_folder / f"sync_info_{int(time.time())}.json"
            with open(sync_file, 'w', encoding='utf-8') as f:
                json.dump(sync_info, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro sincronizando configurações: {e}")
            return False
    
    def backup_system_to_drive(self) -> bool:
        """💾 CRIA BACKUP COMPLETO NO DRIVE"""
        
        print("💾 Criando backup completo no Google Drive...")
        
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
                                        continue  # Pular arquivos problemáticos
            
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
            
            print(f"✅ Backup criado: {backup_file.name}")
            print(f"   📁 {added_files} arquivos, {total_size/1024/1024:.1f} MB")
            print(f"   📦 Compactado para {backup_file.stat().st_size/1024/1024:.1f} MB")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro criando backup: {e}")
            return False
    
    def consolidate_data_from_devices(self) -> Dict[str, Any]:
        """🔄 CONSOLIDA DADOS DE MÚLTIPLOS DISPOSITIVOS"""
        
        print("🔄 Consolidando dados de dispositivos...")
        
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
            
            # Buscar configurações
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
            
            print(f"✅ Dados consolidados de {len(consolidated_data['models'])} modelos")
            print(f"   📱 {len(consolidated_data['configs'])} dispositivos encontrados")
            
            return consolidated_data
            
        except Exception as e:
            print(f"❌ Erro consolidando dados: {e}")
            return {}
    
    def _start_auto_sync(self):
        """🔄 INICIA SINCRONIZAÇÃO AUTOMÁTICA"""
        
        if self.sync_active:
            return
        
        self.sync_active = True
        self.stop_sync.clear()
        
        self.sync_thread = threading.Thread(target=self._auto_sync_loop, daemon=True)
        self.sync_thread.start()
        
        print(f"🔄 Sincronização automática iniciada (intervalo: {self.sync_interval_minutes} minutos)")
    
    def _auto_sync_loop(self):
        """🔁 LOOP DE SINCRONIZAÇÃO AUTOMÁTICA"""
        
        while not self.stop_sync.wait(self.sync_interval_minutes * 60):
            try:
                print("🔄 Executando sincronização automática...")
                
                # Sincronizar configurações
                self.sync_configs_to_drive()
                
                # Criar backup periódico (a cada 4 horas)
                if (self.last_sync is None or 
                    datetime.now() - self.last_sync > timedelta(hours=4)):
                    self.backup_system_to_drive()
                
                self.last_sync = datetime.now()
                print("✅ Sincronização automática concluída")
                
            except Exception as e:
                print(f"❌ Erro na sincronização automática: {e}")
                time.sleep(60)  # Aguardar 1 minuto antes de tentar novamente
    
    def stop_auto_sync(self):
        """⏹️ PARA SINCRONIZAÇÃO AUTOMÁTICA"""
        
        if not self.sync_active:
            return
        
        self.sync_active = False
        self.stop_sync.set()
        
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=5)
        
        print("⏹️ Sincronização automática parada")
    
    def get_drive_status(self) -> Dict[str, Any]:
        """📊 STATUS DO GOOGLE DRIVE"""
        
        try:
            if not self.local_drive_path:
                return {"status": "not_detected"}
            
            user_folder = self.local_drive_path / self.user_folder_name
            
            # Calcular estatísticas
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
        """🔄 SINCRONIZAÇÃO MANUAL COMPLETA"""
        
        print("🔄 Executando sincronização manual completa...")
        
        try:
            success = True
            
            # 1. Sincronizar configurações
            if not self.sync_configs_to_drive():
                success = False
            
            # 2. Criar backup
            if not self.backup_system_to_drive():
                success = False
            
            # 3. Consolidar dados
            consolidated = self.consolidate_data_from_devices()
            if not consolidated:
                print("⚠️ Nenhum dado para consolidar")
            
            if success:
                print("✅ Sincronização manual concluída com sucesso")
            else:
                print("⚠️ Sincronização manual concluída com alguns erros")
            
            return success
            
        except Exception as e:
            print(f"❌ Erro na sincronização manual: {e}")
            return False

# Exemplo de uso:
# identifier = MicrosoftDeviceIdentifier("./data")
# drive_manager = StructuredGoogleDriveManager(jarvis_core, identifier)
# drive_manager.initialize()
# drive_manager.manual_sync()