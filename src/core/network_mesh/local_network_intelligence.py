#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Local Network Intelligence System
====================================================
Sistema de inteligÃªncia distribuÃ­da entre dispositivos pessoais do usuÃ¡rio.

CaracterÃ­sticas:
- Identifica automaticamente atravÃ©s da conta Windows logada
- Sincroniza inteligÃªncia via Google Drive (gratuito)
- Detecta outros dispositivos JARVIS na rede local  
- Compartilha aprendizados e memÃ³rias entre dispositivos
- Recovery automÃ¡tico entre mÃ¡quinas pessoais
"""

import asyncio
import json
import os
import platform
import socket
import hashlib
import time
from src.utils.platform_compat import winreg, WINREG_AVAILABLE
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Imports para detecÃ§Ã£o de rede
import subprocess
import threading

class DeviceRole(Enum):
    PRIMARY = "primary"        # Dispositivo principal
    SECONDARY = "secondary"    # Dispositivo secundÃ¡rio
    MOBILE = "mobile"         # Dispositivo mÃ³vel
    EMERGENCY = "emergency"   # Dispositivo de emergÃªncia

class SyncStatus(Enum):
    CONNECTED = "connected"
    SYNCING = "syncing"  
    OFFLINE = "offline"
    ERROR = "error"

@dataclass
class LocalJarvisDevice:
    """Representa um dispositivo JARVIS na rede local"""
    device_id: str              # Hash Ãºnico baseado na conta + hardware
    device_name: str            # Nome do computador
    user_account: str           # Conta Windows logada
    ip_address: str             # IP na rede local
    role: DeviceRole            # Papel na rede mesh
    sync_status: SyncStatus     # Status de sincronizaÃ§Ã£o
    last_seen: datetime         # Ãšltima vez visto online
    capabilities: List[str]     # Capacidades (GPU, TTS, etc.)
    load_average: float         # Carga mÃ©dia do sistema (0.0-1.0)
    gdrive_sync_path: Optional[str]  # Caminho do Google Drive
    jarvis_version: str         # VersÃ£o do JARVIS
    trust_level: float          # NÃ­vel de confianÃ§a (0.0-1.0)

@dataclass
class IntelligencePacket:
    """Pacote de inteligÃªncia para sincronizaÃ§Ã£o"""
    packet_id: str
    source_device: str
    packet_type: str  # "memory", "learning", "config", "emergency"
    content: Dict[str, Any]
    timestamp: datetime
    importance_level: int  # 1-10
    sync_encrypted: bool

class LocalNetworkIntelligence:
    """
    ðŸ  SISTEMA DE INTELIGÃŠNCIA EM REDE LOCAL
    
    Funcionalidades:
    - Auto-descoberta de dispositivos JARVIS na rede
    - IdentificaÃ§Ã£o automÃ¡tica via conta Windows
    - SincronizaÃ§Ã£o inteligente via Google Drive
    - Recovery distribuÃ­do entre dispositivos pessoais
    - Mente coletiva mantendo privacidade
    """
    
    def __init__(self, jarvis_core_path: str):
        self.jarvis_core_path = Path(jarvis_core_path)
        self.config_path = self.jarvis_core_path / "data" / "network_mesh"
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Estado do dispositivo local
        self.local_device = self._detect_local_device()
        self.discovered_devices: Dict[str, LocalJarvisDevice] = {}
        self.sync_queue: List[IntelligencePacket] = []
        
        # ConfiguraÃ§Ãµes de rede
        self.mesh_port = 7777  # Porta para comunicaÃ§Ã£o mesh
        self.discovery_interval = 30  # Descoberta a cada 30s
        self.sync_interval = 60       # Sync a cada 60s
        
        # Google Drive sync
        self.gdrive_base_path = self._detect_google_drive_path()
        self.jarvis_cloud_folder = self._setup_cloud_sync_folder()
        
        # Estado de execuÃ§Ã£o
        self.is_running = False
        self.discovery_task = None
        self.sync_task = None
        
        print(f"ðŸ  Local Network Intelligence inicializado")
        print(f"   ðŸ“± Dispositivo: {self.local_device.device_name} ({self.local_device.role.value})")
        print(f"   ðŸ‘¤ UsuÃ¡rio: {self.local_device.user_account}")
        print(f"   â˜ï¸ Google Drive: {'âœ…' if self.gdrive_base_path else 'âŒ'}")
    
    def _detect_local_device(self) -> LocalJarvisDevice:
        """ðŸ” DETECÃ‡ÃƒO AUTOMÃTICA DO DISPOSITIVO LOCAL"""
        
        # 1. Obter informaÃ§Ãµes da conta Windows
        try:
            user_account = self._get_windows_logged_user()
        except Exception:
            user_account = os.getenv('USERNAME', 'unknown_user')
        
        # 2. InformaÃ§Ãµes do sistema
        device_name = platform.node()
        
        # 3. Gerar ID Ãºnico baseado em conta + hardware
        hardware_info = self._get_hardware_fingerprint()
        device_id = hashlib.sha256(f"{user_account}:{hardware_info}".encode()).hexdigest()[:16]
        
        # 4. Detectar IP local
        local_ip = self._get_local_ip()
        
        # 5. Detectar capacidades
        capabilities = self._detect_system_capabilities()
        
        # 6. Determinar papel na rede (PRIMARY para primeiro dispositivo)
        role = self._determine_device_role(capabilities)
        
        # 7. Verificar Google Drive
        gdrive_path = self._detect_google_drive_path()
        
        return LocalJarvisDevice(
            device_id=device_id,
            device_name=device_name,
            user_account=user_account,
            ip_address=local_ip,
            role=role,
            sync_status=SyncStatus.OFFLINE,
            last_seen=datetime.now(),
            capabilities=capabilities,
            load_average=0.5,
            gdrive_sync_path=gdrive_path,
            jarvis_version="5.0",
            trust_level=1.0  # Dispositivos prÃ³prios tÃªm confianÃ§a total
        )
    
    def _get_windows_logged_user(self) -> str:
        """ObtÃ©m conta Windows logada usando Registry"""
        try:
            # MÃ©todo 1: Registry do Windows
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\LogonUI")
            username, _ = winreg.QueryValueEx(key, "LastLoggedOnUser")
            winreg.CloseKey(key)
            
            # Formatar para pegar sÃ³ o nome do usuÃ¡rio
            if '\\' in username:
                return username.split('\\')[-1]
            return username
            
        except Exception:
            # MÃ©todo 2: VariÃ¡veis de ambiente
            domain_user = os.getenv('USERDOMAIN', '') + '\\' + os.getenv('USERNAME', '')
            return domain_user
    
    def _get_hardware_fingerprint(self) -> str:
        """Gera fingerprint Ãºnico do hardware"""
        try:
            # Usar informaÃ§Ãµes do sistema que nÃ£o mudam
            system_info = {
                'processor': platform.processor(),
                'machine': platform.machine(), 
                'system': platform.system(),
                'node': platform.node()
            }
            
            # Tentar obter UUID da mÃ¡quina (Windows)
            try:
                result = subprocess.run(['wmic', 'csproduct', 'get', 'uuid'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        system_info['uuid'] = lines[1].strip()
            except Exception:
                pass
            
            # Gerar hash
            info_str = json.dumps(system_info, sort_keys=True)
            return hashlib.sha256(info_str.encode()).hexdigest()[:16]
            
        except Exception:
            return hashlib.sha256(f"{platform.node()}:{time.time()}".encode()).hexdigest()[:16]
    
    def _get_local_ip(self) -> str:
        """ObtÃ©m IP local na rede"""
        try:
            # Conectar a um endereÃ§o externo para descobrir IP local
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
    
    def _detect_system_capabilities(self) -> List[str]:
        """Detecta capacidades do sistema"""
        capabilities = []
        
        # GPU Detection
        try:
            import torch
            if torch.cuda.is_available():
                capabilities.append("CUDA_GPU")
                capabilities.append("AI_ACCELERATION")
        except ImportError:
            pass
        
        # Ãudio
        try:
            import sounddevice
            capabilities.append("AUDIO_IO")
        except ImportError:
            pass
        
        # Webcam/Camera
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                capabilities.append("CAMERA")
            cap.release()
        except ImportError:
            pass
        
        # Sistema base
        capabilities.extend(["LOCAL_STORAGE", "NETWORK_CLIENT", "TEXT_PROCESSING"])
        
        return capabilities
    
    def _determine_device_role(self, capabilities: List[str]) -> DeviceRole:
        """Determina papel do dispositivo na rede"""
        
        # Se tem GPU = PRIMARY candidate
        if "CUDA_GPU" in capabilities:
            return DeviceRole.PRIMARY
        
        # Se tem capacidades completas = SECONDARY
        if len(capabilities) >= 4:
            return DeviceRole.SECONDARY
        
        # Caso contrÃ¡rio = MOBILE/EMERGENCY
        return DeviceRole.MOBILE
    
    def _detect_google_drive_path(self) -> Optional[str]:
        """ðŸ” DETECTA CAMINHO DO GOOGLE DRIVE AUTOMATICAMENTE"""
        
        # Caminhos tÃ­picos do Google Drive no Windows
        possible_paths = [
            os.path.expanduser(r"~\Google Drive"),
            os.path.expanduser(r"~\GoogleDrive"),  
            r"C:\Users\{}\Google Drive".format(os.getenv('USERNAME', '')),
            r"G:\My Drive",  # Drives mapeados
            r"G:\Meu Drive", 
            # Google Drive File Stream
            os.path.expanduser(r"~\Google Drive File Stream\My Drive"),
            # Novos caminhos do Google Drive para desktop
            os.path.expanduser(r"~\Google Drive\My Drive"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"âœ… Google Drive detectado: {path}")
                return path
        
        # Se nÃ£o encontrou, perguntar para o usuÃ¡rio na primeira vez
        print("âš ï¸ Google Drive nÃ£o detectado automaticamente")
        return None
    
    def _setup_cloud_sync_folder(self) -> Optional[Path]:
        """ðŸ—‚ï¸ CONFIGURA PASTA DE SINCRONIZAÃ‡ÃƒO NA NUVEM"""
        
        if not self.gdrive_base_path:
            return None
        
        # Criar pasta especÃ­fica do JARVIS no Google Drive
        jarvis_folder = Path(self.gdrive_base_path) / "JARVIS_Network_Intelligence"
        jarvis_folder.mkdir(exist_ok=True)
        
        # Subpastas organizadas
        (jarvis_folder / "devices").mkdir(exist_ok=True)
        (jarvis_folder / "memories").mkdir(exist_ok=True)
        (jarvis_folder / "learning").mkdir(exist_ok=True)
        (jarvis_folder / "emergencies").mkdir(exist_ok=True)
        
        print(f"ðŸ“ Pasta de sincronizaÃ§Ã£o criada: {jarvis_folder}")
        return jarvis_folder
    
    async def start_network_mesh(self):
        """ðŸš€ INICIA SISTEMA DE REDE MESH"""
        if self.is_running:
            return
        
        self.is_running = True
        print("\nðŸŒ Iniciando Local Network Intelligence...")
        
        # Registrar dispositivo local no Google Drive
        await self._register_device_in_cloud()
        
        # Iniciar tarefas assÃ­ncronas
        self.discovery_task = asyncio.create_task(self._discovery_loop())
        self.sync_task = asyncio.create_task(self._cloud_sync_loop())
        
        print("âœ… Network Mesh ativo")
    
    async def stop_network_mesh(self):
        """â¹ï¸ PARA SISTEMA DE REDE MESH"""
        if not self.is_running:
            return
            
        print("ðŸ›‘ Parando Network Mesh...")
        self.is_running = False
        
        if self.discovery_task:
            self.discovery_task.cancel()
        if self.sync_task:
            self.sync_task.cancel()
        
        # Atualizar status no cloud
        await self._update_device_status_in_cloud(SyncStatus.OFFLINE)
        print("âœ… Network Mesh parado")
    
    async def _discovery_loop(self):
        """ðŸ” LOOP DE DESCOBERTA DE DISPOSITIVOS"""
        while self.is_running:
            try:
                await self._discover_devices_in_cloud()
                await asyncio.sleep(self.discovery_interval)
            except Exception as e:
                print(f"âŒ Erro na descoberta: {e}")
                await asyncio.sleep(self.discovery_interval)
    
    async def _cloud_sync_loop(self):
        """â˜ï¸ LOOP DE SINCRONIZAÃ‡ÃƒO COM CLOUD"""
        while self.is_running:
            try:
                await self._sync_with_cloud()
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                print(f"âŒ Erro na sincronizaÃ§Ã£o: {e}")
                await asyncio.sleep(self.sync_interval)
    
    async def _register_device_in_cloud(self):
        """ðŸ“ REGISTRA DISPOSITIVO NO GOOGLE DRIVE"""
        if not self.jarvis_cloud_folder:
            return
        
        device_info = {
            'device_info': asdict(self.local_device),
            'last_update': datetime.now().isoformat(),
            'status': 'online'
        }
        
        # Salvar info do dispositivo
        device_file = self.jarvis_cloud_folder / "devices" / f"{self.local_device.device_id}.json"
        with open(device_file, 'w', encoding='utf-8') as f:
            json.dump(device_info, f, indent=2, ensure_ascii=False)
        
        print(f"ðŸ“ Dispositivo registrado no cloud: {self.local_device.device_name}")
    
    async def _discover_devices_in_cloud(self):
        """ðŸ” DESCOBRE OUTROS DISPOSITIVOS VIA GOOGLE DRIVE"""
        if not self.jarvis_cloud_folder:
            return
        
        devices_folder = self.jarvis_cloud_folder / "devices"
        if not devices_folder.exists():
            return
        
        discovered = 0
        for device_file in devices_folder.glob("*.json"):
            if device_file.stem == self.local_device.device_id:
                continue  # Pular prÃ³prio dispositivo
            
            try:
                with open(device_file, 'r', encoding='utf-8') as f:
                    device_data = json.load(f)
                
                device_info = device_data.get('device_info', {})
                
                # Verificar se Ã© confiÃ¡vel (mesmo usuÃ¡rio)
                if device_info.get('user_account') == self.local_device.user_account:
                    
                    # Criar objeto do dispositivo
                    device = LocalJarvisDevice(
                        device_id=device_info['device_id'],
                        device_name=device_info['device_name'],
                        user_account=device_info['user_account'],
                        ip_address=device_info['ip_address'],
                        role=DeviceRole(device_info['role']),
                        sync_status=SyncStatus.CONNECTED,
                        last_seen=datetime.fromisoformat(device_data['last_update']),
                        capabilities=device_info['capabilities'],
                        load_average=device_info.get('load_average', 0.5),
                        gdrive_sync_path=device_info.get('gdrive_sync_path'),
                        jarvis_version=device_info.get('jarvis_version', '5.0'),
                        trust_level=1.0
                    )
                    
                    self.discovered_devices[device.device_id] = device
                    discovered += 1
                    
            except Exception as e:
                print(f"âš ï¸ Erro ao ler dispositivo {device_file.name}: {e}")
        
        if discovered > 0:
            print(f"ðŸ” Descobertos {discovered} dispositivos JARVIS na rede")
    
    async def _sync_with_cloud(self):
        """â˜ï¸ SINCRONIZA INTELIGÃŠNCIA COM GOOGLE DRIVE"""
        if not self.jarvis_cloud_folder:
            return
        
        # 1. Atualizar status prÃ³prio
        await self._update_device_status_in_cloud(SyncStatus.SYNCING)
        
        # 2. Sincronizar pacotes pendentes
        await self._upload_pending_intelligence()
        
        # 3. Baixar inteligÃªncia de outros dispositivos  
        await self._download_intelligence_from_cloud()
        
        # 4. Status final
        await self._update_device_status_in_cloud(SyncStatus.CONNECTED)
    
    async def _update_device_status_in_cloud(self, status: SyncStatus):
        """ðŸ“Š ATUALIZA STATUS DO DISPOSITIVO NO CLOUD"""
        if not self.jarvis_cloud_folder:
            return
        
        # Atualizar status local
        self.local_device.sync_status = status
        self.local_device.last_seen = datetime.now()
        
        # Salvar no cloud
        await self._register_device_in_cloud()
    
    async def _upload_pending_intelligence(self):
        """ðŸ“¤ UPLOAD DE INTELIGÃŠNCIA PENDENTE"""
        if not self.sync_queue or not self.jarvis_cloud_folder:
            return
        
        for packet in self.sync_queue.copy():
            try:
                # Determinar pasta pelo tipo
                folder_map = {
                    'memory': 'memories',
                    'learning': 'learning', 
                    'emergency': 'emergencies'
                }
                
                folder = self.jarvis_cloud_folder / folder_map.get(packet.packet_type, 'learning')
                timestamp = packet.timestamp.strftime("%Y%m%d_%H%M%S")
                filename = f"{packet.source_device}_{timestamp}_{packet.packet_type}.json"
                
                # Salvar pacote
                with open(folder / filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'packet': asdict(packet),
                        'upload_time': datetime.now().isoformat()
                    }, f, indent=2, ensure_ascii=False, default=str)
                
                # Remover da queue
                self.sync_queue.remove(packet)
                
            except Exception as e:
                print(f"âŒ Erro ao enviar pacote {packet.packet_id}: {e}")
    
    async def _download_intelligence_from_cloud(self):
        """ðŸ“¥ DOWNLOAD DE INTELIGÃŠNCIA DO CLOUD"""
        if not self.jarvis_cloud_folder:
            return
        
        # Verificar pastas de inteligÃªncia
        for folder_name in ['memories', 'learning', 'emergencies']:
            folder = self.jarvis_cloud_folder / folder_name
            if not folder.exists():
                continue
            
            # Processar arquivos de outros dispositivos
            for intel_file in folder.glob("*.json"):
                if self.local_device.device_id in intel_file.name:
                    continue  # Pular prÃ³prios arquivos
                
                try:
                    with open(intel_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    packet_data = data.get('packet', {})
                    
                    # Verificar se jÃ¡ foi processado
                    if self._is_packet_already_processed(packet_data.get('packet_id')):
                        continue
                    
                    # Processar inteligÃªncia
                    await self._process_intelligence_packet(packet_data)
                    
                    # Marcar como processado
                    self._mark_packet_as_processed(packet_data.get('packet_id'))
                    
                except Exception as e:
                    print(f"âŒ Erro ao processar {intel_file.name}: {e}")
    
    def _is_packet_already_processed(self, packet_id: str) -> bool:
        """Verifica se pacote jÃ¡ foi processado"""
        processed_file = self.config_path / "processed_packets.json"
        
        if not processed_file.exists():
            return False
        
        try:
            with open(processed_file, 'r') as f:
                processed = json.load(f)
            return packet_id in processed
        except Exception:
            return False
    
    def _mark_packet_as_processed(self, packet_id: str):
        """Marca pacote como processado"""
        processed_file = self.config_path / "processed_packets.json"
        
        try:
            if processed_file.exists():
                with open(processed_file, 'r') as f:
                    processed = json.load(f)
            else:
                processed = []
            
            processed.append(packet_id)
            
            # Manter apenas Ãºltimos 1000
            if len(processed) > 1000:
                processed = processed[-1000:]
            
            with open(processed_file, 'w') as f:
                json.dump(processed, f)
                
        except Exception as e:
            print(f"âŒ Erro ao marcar pacote: {e}")
    
    async def _process_intelligence_packet(self, packet_data: Dict):
        """ðŸ§  PROCESSA PACOTE DE INTELIGÃŠNCIA RECEBIDO"""
        packet_type = packet_data.get('packet_type')
        content = packet_data.get('content', {})
        source = packet_data.get('source_device', 'unknown')
        
        print(f"ðŸ§  Processando inteligÃªncia de {source}: {packet_type}")
        
        try:
            if packet_type == 'memory':
                await self._integrate_memory(content)
            elif packet_type == 'learning':
                await self._integrate_learning(content)
            elif packet_type == 'emergency':
                await self._handle_emergency_intel(content)
        
        except Exception as e:
            print(f"âŒ Erro ao processar pacote {packet_type}: {e}")
    
    async def _integrate_memory(self, memory_data: Dict):
        """Integra memÃ³rias de outro dispositivo"""
        # Aqui vocÃª integraria com o sistema de memÃ³ria do JARVIS
        print(f"ðŸ’­ Integrando memÃ³rias: {len(memory_data)} itens")
    
    async def _integrate_learning(self, learning_data: Dict):
        """Integra aprendizados de outro dispositivo"""
        # Aqui vocÃª integraria com o sistema de aprendizado
        print(f"ðŸŽ“ Integrando aprendizados: {learning_data.keys()}")
    
    async def _handle_emergency_intel(self, emergency_data: Dict):
        """Processa inteligÃªncia de emergÃªncia"""
        print(f"ðŸš¨ Processando emergÃªncia: {emergency_data.get('type', 'unknown')}")
    
    # ===== MÃ‰TODOS PÃšBLICOS PARA USO PELO JARVIS =====
    
    async def share_memory(self, memory_type: str, memory_data: Dict, importance: int = 5):
        """ðŸ“¤ COMPARTILHA MEMÃ“RIA COM REDE"""
        packet = IntelligencePacket(
            packet_id=hashlib.sha256(f"{time.time()}:{memory_type}".encode()).hexdigest()[:16],
            source_device=self.local_device.device_id,
            packet_type="memory",
            content={
                'memory_type': memory_type,
                'data': memory_data
            },
            timestamp=datetime.now(),
            importance_level=importance,
            sync_encrypted=False
        )
        
        self.sync_queue.append(packet)
        print(f"ðŸ“¤ MemÃ³ria adicionada para sync: {memory_type}")
    
    async def share_learning(self, learning_type: str, learning_data: Dict, importance: int = 7):
        """ðŸŽ“ COMPARTILHA APRENDIZADO COM REDE"""
        packet = IntelligencePacket(
            packet_id=hashlib.sha256(f"{time.time()}:{learning_type}".encode()).hexdigest()[:16],
            source_device=self.local_device.device_id,
            packet_type="learning",
            content={
                'learning_type': learning_type,
                'data': learning_data
            },
            timestamp=datetime.now(),
            importance_level=importance,
            sync_encrypted=False
        )
        
        self.sync_queue.append(packet)
        print(f"ðŸŽ“ Aprendizado adicionado para sync: {learning_type}")
    
    async def emergency_broadcast(self, emergency_type: str, emergency_data: Dict):
        """ðŸš¨ BROADCAST DE EMERGÃŠNCIA PARA TODA REDE"""
        packet = IntelligencePacket(
            packet_id=hashlib.sha256(f"{time.time()}:EMERGENCY".encode()).hexdigest()[:16],
            source_device=self.local_device.device_id,
            packet_type="emergency",
            content={
                'emergency_type': emergency_type,
                'data': emergency_data,
                'requires_immediate_sync': True
            },
            timestamp=datetime.now(),
            importance_level=10,  # MÃ¡xima prioridade
            sync_encrypted=False
        )
        
        self.sync_queue.append(packet)
        
        # ForÃ§ar sync imediato para emergÃªncias
        if self.is_running:
            await self._upload_pending_intelligence()
        
        print(f"ðŸš¨ EMERGÃŠNCIA transmitida para rede: {emergency_type}")
    
    def get_network_status(self) -> Dict:
        """ðŸ“Š RETORNA STATUS DA REDE"""
        return {
            'local_device': asdict(self.local_device),
            'discovered_devices': len(self.discovered_devices),
            'sync_queue_size': len(self.sync_queue),
            'google_drive_connected': self.gdrive_base_path is not None,
            'mesh_active': self.is_running,
            'devices_list': [
                {
                    'name': device.device_name,
                    'role': device.role.value,
                    'status': device.sync_status.value,
                    'capabilities': len(device.capabilities)
                }
                for device in self.discovered_devices.values()
            ]
        }

# ============================================================================
# EXEMPLO DE USO E DEMONSTRAÃ‡ÃƒO
# ============================================================================

async def test_local_network_intelligence():
    """ðŸ§ª TESTE DO SISTEMA DE REDE LOCAL"""
    
    print("\nðŸ  " + "="*60)
    print("    LOCAL NETWORK INTELLIGENCE TEST")
    print("="*60 + "\n")
    
    # Inicializar sistema
    jarvis_path = r"C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0"
    network = LocalNetworkIntelligence(jarvis_path)
    
    # Iniciar mesh
    await network.start_network_mesh()
    
    # Aguardar descoberta
    await asyncio.sleep(5)
    
    # Mostrar status
    status = network.get_network_status()
    print("ðŸ“Š STATUS DA REDE:")
    print(f"   ðŸ“± Dispositivo local: {status['local_device']['device_name']}")
    print(f"   ðŸ‘¤ UsuÃ¡rio: {status['local_device']['user_account']}")
    print(f"   ðŸ” Dispositivos descobertos: {status['discovered_devices']}")
    print(f"   â˜ï¸ Google Drive: {'âœ…' if status['google_drive_connected'] else 'âŒ'}")
    print(f"   ðŸ“¦ Fila de sync: {status['sync_queue_size']} pacotes")
    
    # Simular compartilhamento de inteligÃªncia
    print("\nðŸ§  SIMULANDO COMPARTILHAMENTO DE INTELIGÃŠNCIA:")
    
    # Compartilhar uma memÃ³ria
    await network.share_memory("user_preference", {
        "language": "pt-BR",
        "voice_speed": "normal",
        "preferred_ai_model": "local"
    }, importance=6)
    
    # Compartilhar um aprendizado
    await network.share_learning("voice_recognition", {
        "user_voice_signature": "exemplo_hash_voice",
        "accuracy_improvement": 15.5,
        "training_hours": 2.5
    }, importance=8)
    
    # Aguardar sync
    print("â³ Aguardando sincronizaÃ§Ã£o...")
    await asyncio.sleep(10)
    
    # Status final
    final_status = network.get_network_status()
    print(f"\nâœ… SincronizaÃ§Ã£o concluÃ­da!")
    print(f"   ðŸ“¦ Pacotes restantes: {final_status['sync_queue_size']}")
    
    # Parar sistema
    await network.stop_network_mesh()
    print("ðŸ Teste concluÃ­do!")

if __name__ == "__main__":
    asyncio.run(test_local_network_intelligence())
