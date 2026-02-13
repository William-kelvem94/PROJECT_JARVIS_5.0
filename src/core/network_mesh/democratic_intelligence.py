#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Democratic Network Intelligence
===================================================
Sistema de rede neural democrática entre dispositivos pessoais.
Características:
- SEM dispositivo principal fixo
- Eleição dinâmica baseada em capacidade e necessidade  
- Treinamento distribuído inteligente
- Consolidação automática via Google Drive
- Identificação por conta Windows (" + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "" + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "williamkelvem64@gmail.com")) + "")) + ")
"""

import asyncio
import json
import os
import platform
import socket
import hashlib
import time
import winreg
import psutil
import threading
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Imports para eleição e treinamento
import shutil
import tempfile
import zipfile

class DeviceCapability(Enum):
    """Capacidades específicas dos dispositivos"""
    CUDA_TRAINING = "cuda_training"      # GPU NVIDIA para treinar
    AUDIO_PROCESSING = "audio_processing"  # Boa placa de som
    VISION_PROCESSING = "vision_processing"  # Webcam + processamento
    STORAGE_BACKUP = "storage_backup"    # Muito armazenamento
    NETWORK_BRIDGE = "network_bridge"   # Boa conectividade
    MEMORY_INTENSIVE = "memory_intensive"  # Muita RAM
    COMPUTE_INTENSIVE = "compute_intensive"  # CPU potente

class TaskType(Enum):
    """Tipos de tarefas que podem ser distribuídas"""
    VOICE_TRAINING = "voice_training"
    FACE_TRAINING = "face_training" 
    LLM_FINETUNING = "llm_finetuning"
    MEMORY_CONSOLIDATION = "memory_consolidation"
    SYSTEM_BACKUP = "system_backup"
    HEAVY_INFERENCE = "heavy_inference"
    DATA_PROCESSING = "data_processing"

class ElectionStatus(Enum):
    """Status da eleição para liderança de tarefa"""
    IDLE = "idle"
    VOTING = "voting"
    ELECTED = "elected"
    WORKING = "working"
    CONSOLIDATING = "consolidating"

@dataclass
class DeviceSpecs:
    """Especificações técnicas do dispositivo"""
    cpu_cores: int
    cpu_freq_mhz: float
    total_ram_gb: float
    available_ram_gb: float
    gpu_name: Optional[str]
    gpu_memory_gb: float
    storage_free_gb: float
    network_speed_mbps: float
    current_load: float  # 0.0 - 1.0
    power_state: str  # "ac_power", "battery_low", "battery_good"

@dataclass
class DistributedTask:
    """Tarefa que pode ser distribuída entre dispositivos"""
    task_id: str
    task_type: TaskType
    estimated_duration_min: int
    required_capabilities: List[DeviceCapability]
    priority: int  # 1-10
    data_size_mb: float
    can_be_distributed: bool
    min_devices_required: int
    created_by_device: str
    created_at: datetime

@dataclass
class ElectionBid:
    """Proposta de um dispositivo para executar tarefa"""
    device_id: str
    device_name: str
    capability_score: float  # 0.0 - 1.0
    current_availability: float  # 0.0 - 1.0  
    estimated_completion_time: int  # minutos
    power_efficiency: float  # custo energético
    proposed_role: str  # "leader", "worker", "backup"

class DemocraticNetworkIntelligence:
    """
    🏛️ SISTEMA DE INTELIGÊNCIA EM REDE DEMOCRÁTICA
    
    Funcionalidades:
    - Identificação por conta Windows específica
    - Eleição dinâmica para liderança de tarefas
    - Treinamento distribuído inteligente
    - Consolidação automática de resultados  
    - Backup e sincronização via Google Drive
    - Monitoramento de capacidade em tempo real
    """
    
    def __init__(self, jarvis_core_path: str, target_account: str = "" + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "" + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "williamkelvem64@gmail.com")) + "")) + ""):
        self.jarvis_core_path = Path(jarvis_core_path)
        self.target_account = target_account.lower()
        self.config_path = self.jarvis_core_path / "data" / "democratic_network"
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Estado do dispositivo local
        self.local_specs = self._analyze_local_specs()
        self.device_account = self._get_windows_account()
        self.is_authorized = self._verify_account_authorization()
        
        if not self.is_authorized:
            print(f"⚠️ Dispositivo não autorizado. Conta detectada: {self.device_account}")
            print(f"   Conta esperada: {self.target_account}")
            return
        
        self.device_id = self._generate_device_id()
        self.discovered_devices: Dict[str, Dict] = {}
        
        # Sistema de eleição e tarefas
        self.current_tasks: Dict[str, DistributedTask] = {}
        self.election_status = ElectionStatus.IDLE
        self.current_role: Optional[str] = None
        
        # Configurações de rede
        self.discovery_port = 7778  
        self.election_timeout = 30  # segundos
        self.heartbeat_interval = 15  # segundos
        
        # Google Drive para consolidação
        self.gdrive_base_path = self._detect_google_drive_path()
        self.consolidation_folder = self._setup_consolidation_folder()
        
        # Threading
        self.is_running = False
        self.discovery_task = None
        self.heartbeat_task = None
        self.election_task = None
        
        print(f"🏛️ Democratic Network Intelligence inicializado")
        print(f"   📱 Dispositivo: {platform.node()}")
        print(f"   👤 Conta autorizada: {self.device_account}")
        print(f"   💪 Specs: {self.local_specs.cpu_cores}C/{self.local_specs.total_ram_gb:.0f}GB")
        print(f"   🎮 GPU: {self.local_specs.gpu_name or 'Integrada'}")
        print(f"   ☁️ Google Drive: {'✅' if self.gdrive_base_path else '❌'}")
    
    def _get_windows_account(self) -> str:
        """🔍 DETECTA CONTA WINDOWS LOGADA"""
        try:
            # Método 1: Registry LastLoggedOnUser  
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\LogonUI") as key:
                    username, _ = winreg.QueryValueEx(key, "LastLoggedOnUser")
                    if '\\' in username:
                        return username.split('\\')[-1].lower()
                    return username.lower()
            except Exception:
                pass
            
            # Método 2: WMI UserName
            try:
                result = subprocess.run(['wmic', 'computersystem', 'get', 'username'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        username = lines[1].strip()
                        if '\\' in username:
                            return username.split('\\')[-1].lower()
                        return username.lower()
            except Exception:
                pass
            
            # Método 3: Environment variables
            domain = os.getenv('USERDOMAIN', '')
            user = os.getenv('USERNAME', '')
            if '@' in user:
                return user.lower()  # Já é email
            
            # Se não achou email, tentar construir baseado no domínio
            return f"{user.lower()}@unknown.local"
            
        except Exception as e:
            print(f"❌ Erro detectando conta Windows: {e}")
            return "unknown@unknown.local"
    
    def _verify_account_authorization(self) -> bool:
        """✅ VERIFICA SE DISPOSITIVO ESTÁ AUTORIZADO"""
        return self.device_account == self.target_account or \
               self.device_account.split('@')[0] == self.target_account.split('@')[0]
    
    def _generate_device_id(self) -> str:
        """🆔 GERA ID ÚNICO PARA DISPOSITIVO"""
        # Combinar conta + hardware fingerprint
        system_info = {
            'account': self.device_account,
            'node': platform.node(),
            'processor': platform.processor()[:50],  # Truncar pra evitar variações
            'system': platform.system()
        }
        
        # Tentar obter UUID da máquina
        try:
            result = subprocess.run(['wmic', 'csproduct', 'get', 'uuid'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    system_info['uuid'] = lines[1].strip()
        except Exception:
            pass
        
        info_str = json.dumps(system_info, sort_keys=True)
        return hashlib.sha256(info_str.encode()).hexdigest()[:16]
    
    def _analyze_local_specs(self) -> DeviceSpecs:
        """💪 ANALISA CAPACIDADES DO DISPOSITIVO LOCAL"""
        
        # CPU
        cpu_count = psutil.cpu_count(logical=False)  # Cores físicos
        cpu_freq = psutil.cpu_freq()
        cpu_freq_mhz = cpu_freq.current if cpu_freq else 2000
        
        # RAM
        memory = psutil.virtual_memory()
        total_ram_gb = memory.total / (1024**3)
        available_ram_gb = memory.available / (1024**3)
        
        # Storage - Detectar disco principal automaticamente
        try:
            # Tentar detectar o disco do sistema
            system_disk = 'C:\\' if os.name == 'nt' else '/'  # Windows vs Unix-like
            disk = psutil.disk_usage(system_disk)
            storage_free_gb = disk.free / (1024**3)
        except Exception:
            # Fallback: usar o primeiro disco disponível
            try:
                partitions = psutil.disk_partitions()
                if partitions:
                    disk = psutil.disk_usage(partitions[0].mountpoint)
                    storage_free_gb = disk.free / (1024**3)
                else:
                    storage_free_gb = 0.0
            except Exception:
                storage_free_gb = 0.0
        
        # GPU Detection
        gpu_name = None
        gpu_memory_gb = 0.0
        
        try:
            # NVIDIA-SMI para GPU NVIDIA
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines and lines[0]:
                    gpu_info = lines[0].split(', ')
                    gpu_name = gpu_info[0]
                    gpu_memory_gb = float(gpu_info[1]) / 1024  # MB para GB
        except Exception:
            pass
        
        if not gpu_name:
            # Fallback: WMIC para qualquer GPU
            try:
                result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[1:]:  # Pular header
                        if line.strip() and 'Microsoft' not in line:
                            gpu_name = line.strip()
                            break
            except Exception:
                pass
        
        # Network speed (estimative)
        network_speed_mbps = 100.0  # Default assumption
        
        # Current load
        current_load = psutil.cpu_percent(interval=1) / 100.0
        
        # Power state
        battery = psutil.sensors_battery()
        if battery is None:
            power_state = "ac_power"
        elif battery.power_plugged:
            power_state = "ac_power"
        elif battery.percent > 50:
            power_state = "battery_good"
        else:
            power_state = "battery_low"
        
        return DeviceSpecs(
            cpu_cores=cpu_count or 1,  # Garantir que não seja None
            cpu_freq_mhz=cpu_freq_mhz,
            total_ram_gb=total_ram_gb,
            available_ram_gb=available_ram_gb,
            gpu_name=gpu_name,
            gpu_memory_gb=gpu_memory_gb,
            storage_free_gb=storage_free_gb,
            network_speed_mbps=network_speed_mbps,
            current_load=current_load,
            power_state=power_state
        )
    
    def _detect_google_drive_path(self) -> Optional[str]:
        """🔍 DETECTA CAMINHO DO GOOGLE DRIVE"""
        possible_paths = [
            os.path.expanduser(r"~\Google Drive"),
            os.path.expanduser(r"~\GoogleDrive"),
            r"C:\Users\{}\Google Drive".format(os.getenv('USERNAME', '')),
            r"G:\My Drive",
            r"G:\Meu Drive",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _setup_consolidation_folder(self) -> Optional[Path]:
        """📁 CONFIGURA PASTA DE CONSOLIDAÇÃO"""
        if not self.gdrive_base_path:
            return None
        
        # Pasta específica da conta
        account_name = self.device_account.split('@')[0]  # williamkelvem64
        consolidation_folder = Path(self.gdrive_base_path) / f"JARVIS_Democratic_{account_name}"
        consolidation_folder.mkdir(exist_ok=True)
        
        # Subpastas organizadas  
        (consolidation_folder / "elections").mkdir(exist_ok=True)
        (consolidation_folder / "tasks").mkdir(exist_ok=True)
        (consolidation_folder / "models").mkdir(exist_ok=True)
        (consolidation_folder / "backups").mkdir(exist_ok=True)
        (consolidation_folder / "consolidation").mkdir(exist_ok=True)
        
        return consolidation_folder
    
    async def start_democratic_network(self):
        """🚀 INICIA REDE DEMOCRÁTICA"""
        if not self.is_authorized:
            print("❌ Dispositivo não autorizado para rede democrática")
            return
        
        if self.is_running:
            return
        
        self.is_running = True
        print("\n🏛️ Iniciando Rede Democrática...")
        
        # Registrar dispositivo na rede
        await self._register_device()
        
        # Iniciar tarefas de background
        self.discovery_task = asyncio.create_task(self._discovery_loop())
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop()) 
        self.election_task = asyncio.create_task(self._election_management_loop())
        
        print("✅ Rede Democrática ativa")
    
    async def stop_democratic_network(self):
        """⏹️ PARA REDE DEMOCRÁTICA"""
        if not self.is_running:
            return
        
        print("🛑 Parando Rede Democrática...")
        self.is_running = False
        
        # Cancelar tarefas
        for task in [self.discovery_task, self.heartbeat_task, self.election_task]:
            if task and not task.done():
                task.cancel()
        
        # Remover registro
        await self._unregister_device()
        print("✅ Rede Democrática parada")
    
    async def _discovery_loop(self):
        """🔍 LOOP DE DESCOBERTA DE DISPOSITIVOS"""
        while self.is_running:
            try:
                await self._discover_peer_devices()
                await asyncio.sleep(30)  # Descoberta a cada 30s
            except Exception as e:
                print(f"❌ Erro na descoberta: {e}")
                await asyncio.sleep(60)
    
    async def _heartbeat_loop(self):
        """💓 LOOP DE HEARTBEAT"""
        while self.is_running:
            try:
                await self._send_heartbeat()
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                print(f"❌ Erro no heartbeat: {e}")
                await asyncio.sleep(30)
    
    async def _election_management_loop(self):
        """🗳️ LOOP DE GERENCIAMENTO DE ELEIÇÕES"""
        while self.is_running:
            try:
                await self._check_for_pending_elections()
                await self._cleanup_completed_tasks()
                await asyncio.sleep(10)  # Check a cada 10s
            except Exception as e:
                print(f"❌ Erro no gerenciamento de eleições: {e}")
                await asyncio.sleep(30)
    
    async def request_distributed_task(self, task_type: TaskType, **kwargs) -> str:
        """🎯 SOLICITA EXECUÇÃO DE TAREFA DISTRIBUÍDA"""
        
        # Criar tarefa
        task = DistributedTask(
            task_id=hashlib.sha256(f"{time.time()}:{task_type.value}".encode()).hexdigest()[:16],
            task_type=task_type,
            estimated_duration_min=kwargs.get('duration_min', 30),
            required_capabilities=self._get_required_capabilities(task_type),
            priority=kwargs.get('priority', 5),
            data_size_mb=kwargs.get('data_size_mb', 100.0),
            can_be_distributed=kwargs.get('can_be_distributed', True),
            min_devices_required=kwargs.get('min_devices', 1),
            created_by_device=self.device_id,
            created_at=datetime.now()
        )
        
        self.current_tasks[task.task_id] = task
        
        print(f"🎯 Solicitando tarefa distribuída: {task_type.value}")
        print(f"   📊 Duração estimada: {task.estimated_duration_min} min")
        print(f"   💾 Tamanho dos dados: {task.data_size_mb} MB")
        
        # Iniciar eleição
        await self._start_election_for_task(task)
        
        return task.task_id
    
    def _get_required_capabilities(self, task_type: TaskType) -> List[DeviceCapability]:
        """📋 OBTÉM CAPACIDADES NECESSÁRIAS PARA TAREFA"""
        
        capability_map = {
            TaskType.VOICE_TRAINING: [DeviceCapability.CUDA_TRAINING, DeviceCapability.AUDIO_PROCESSING],
            TaskType.FACE_TRAINING: [DeviceCapability.CUDA_TRAINING, DeviceCapability.VISION_PROCESSING],
            TaskType.LLM_FINETUNING: [DeviceCapability.CUDA_TRAINING, DeviceCapability.MEMORY_INTENSIVE],
            TaskType.MEMORY_CONSOLIDATION: [DeviceCapability.MEMORY_INTENSIVE, DeviceCapability.STORAGE_BACKUP],
            TaskType.SYSTEM_BACKUP: [DeviceCapability.STORAGE_BACKUP, DeviceCapability.NETWORK_BRIDGE],
            TaskType.HEAVY_INFERENCE: [DeviceCapability.CUDA_TRAINING, DeviceCapability.COMPUTE_INTENSIVE],
            TaskType.DATA_PROCESSING: [DeviceCapability.COMPUTE_INTENSIVE, DeviceCapability.MEMORY_INTENSIVE]
        }
        
        return capability_map.get(task_type, [DeviceCapability.COMPUTE_INTENSIVE])
    
    async def _start_election_for_task(self, task: DistributedTask):
        """🗳️ INICIA ELEIÇÃO PARA TAREFA"""
        
        print(f"🗳️ Iniciando eleição para tarefa: {task.task_type.value}")
        
        # Avaliar capacidade local
        local_bid = self._generate_local_bid(task)
        
        # Broadcast da eleição para dispositivos descobertos
        election_data = {
            'task': asdict(task),
            'local_bid': asdict(local_bid),
            'election_timeout': self.election_timeout
        }
        
        await self._broadcast_election(election_data)
        
        # Aguardar propostas de outros dispositivos
        await asyncio.sleep(self.election_timeout)
        
        # Processar resultados da eleição
        await self._process_election_results(task.task_id)
    
    def _generate_local_bid(self, task: DistributedTask) -> ElectionBid:
        """💡 GERA PROPOSTA LOCAL PARA TAREFA"""
        
        # Atualizar specs atual
        current_specs = self._analyze_local_specs()
        
        # Calcular capability score baseado nos requisitos
        capability_score = self._calculate_capability_score(task.required_capabilities, current_specs)
        
        # Calcular availability (quanto está livre)
        availability = max(0.0, 1.0 - current_specs.current_load)
        
        # Estimar tempo de conclusão
        base_time = task.estimated_duration_min
        # Ajustar por capacidade e carga
        estimated_time = int(base_time / max(0.1, capability_score * availability))
        
        # Power efficiency (melhor se conectado na tomada)
        power_efficiency = 1.0 if current_specs.power_state == "ac_power" else 0.5
        
        # Determinar papel proposto
        if capability_score > 0.8 and availability > 0.7:
            proposed_role = "leader"
        elif capability_score > 0.5 and availability > 0.4:
            proposed_role = "worker"
        else:
            proposed_role = "backup"
        
        return ElectionBid(
            device_id=self.device_id,
            device_name=platform.node(),
            capability_score=capability_score,
            current_availability=availability,
            estimated_completion_time=estimated_time,
            power_efficiency=power_efficiency,
            proposed_role=proposed_role
        )
    
    def _calculate_capability_score(self, required_caps: List[DeviceCapability], specs: DeviceSpecs) -> float:
        """📊 CALCULA SCORE DE CAPACIDADE"""
        
        if not required_caps:
            return 0.5  # Score neutro
        
        score = 0.0
        cap_weight = 1.0 / len(required_caps)
        
        for capability in required_caps:
            if capability == DeviceCapability.CUDA_TRAINING:
                if specs.gpu_name and 'rtx' in specs.gpu_name.lower():
                    score += cap_weight * 1.0
                elif specs.gpu_name and 'gtx' in specs.gpu_name.lower():
                    score += cap_weight * 0.7
                else:
                    score += cap_weight * 0.1
                    
            elif capability == DeviceCapability.MEMORY_INTENSIVE:
                if specs.total_ram_gb >= 32:
                    score += cap_weight * 1.0
                elif specs.total_ram_gb >= 16:
                    score += cap_weight * 0.7
                else:
                    score += cap_weight * 0.4
                    
            elif capability == DeviceCapability.COMPUTE_INTENSIVE:
                if specs.cpu_cores >= 8:
                    score += cap_weight * 1.0
                elif specs.cpu_cores >= 4:
                    score += cap_weight * 0.7
                else:
                    score += cap_weight * 0.4
                    
            elif capability == DeviceCapability.STORAGE_BACKUP:
                if specs.storage_free_gb >= 500:
                    score += cap_weight * 1.0
                elif specs.storage_free_gb >= 100:
                    score += cap_weight * 0.7
                else:
                    score += cap_weight * 0.3
            else:
                score += cap_weight * 0.5  # Default
        
        return min(1.0, score)
    
    # ===== MÉTODOS DE CONSOLIDAÇÃO E TREINAMENTO =====
    
    async def consolidate_distributed_training(self, task_id: str, model_parts: List[str]):
        """🧠 CONSOLIDA RESULTADO DE TREINAMENTO DISTRIBUÍDO"""
        
        print(f"🧠 Consolidando treinamento distribuído: {task_id}")
        
        if not self.consolidation_folder:
            print("❌ Google Drive não disponível para consolidação")
            return None
        
        consolidation_dir = self.consolidation_folder / "consolidation" / task_id
        consolidation_dir.mkdir(parents=True, exist_ok=True)
        
        # Baixar partes dos modelos de outros dispositivos  
        model_files = []
        for part_name in model_parts:
            part_file = consolidation_dir / f"{part_name}.pkl"
            # Aqui você carregaria da cloud ou rede local
            model_files.append(part_file)
        
        # Consolidar modelos (exemplo simplificado)
        consolidated_model_path = consolidation_dir / "consolidated_model.pkl"
        
        # Salvar modelo consolidado de volta na cloud
        cloud_model_file = self.consolidation_folder / "models" / f"{task_id}_final.pkl"  
        shutil.copy2(consolidated_model_path, cloud_model_file)
        
        print(f"✅ Modelo consolidado salvo: {cloud_model_file}")
        
        # Notificar outros dispositivos
        await self._broadcast_consolidation_complete(task_id, str(cloud_model_file))
        
        return str(cloud_model_file)
    
    # ===== PLACEHOLDER METHODS (implementação completa seria muito extensa) =====
    
    async def _register_device(self):
        """Implementação simplificada"""
        print(f"📝 Registrando dispositivo {platform.node()}")
    
    async def _discover_peer_devices(self):
        """Implementação simplificada"""
        pass
    
    async def _send_heartbeat(self):
        """Implementação simplificada"""
        pass
    
    async def _check_for_pending_elections(self):
        """Implementação simplificada"""
        pass
    
    async def _cleanup_completed_tasks(self):
        """Implementação simplificada"""
        pass
    
    async def _broadcast_election(self, data: Dict):
        """Implementação simplificada"""
        pass
    
    async def _process_election_results(self, task_id: str):
        """Implementação simplificada"""
        pass
    
    async def _unregister_device(self):
        """Implementação simplificada"""
        pass
    
    async def _broadcast_consolidation_complete(self, task_id: str, model_path: str):
        """Implementação simplificada"""
        print(f"📡 Notificando rede: consolidação {task_id} completa")
    
    # ===== MÉTODOS PÚBLICOS PARA USO =====
    
    def get_network_status(self) -> Dict[str, Any]:
        """📊 STATUS DA REDE DEMOCRÁTICA"""
        return {
            'device_id': self.device_id,
            'account': self.device_account,
            'authorized': self.is_authorized,
            'specs': asdict(self.local_specs),
            'discovered_devices': len(self.discovered_devices),
            'current_tasks': len(self.current_tasks),
            'election_status': self.election_status.value if self.election_status else None,
            'current_role': self.current_role,
            'google_drive_available': self.consolidation_folder is not None,
            'network_active': self.is_running
        }

# ============================================================================
# EXEMPLO DE USO PRÁTICO
# ============================================================================

async def democratic_training_demo():
    """🎭 DEMONSTRAÇÃO DE TREINAMENTO DEMOCRÁTICO"""
    
    print("\n🏛️ " + "="*60)
    print("    DEMOCRATIC NETWORK TRAINING DEMO")
    print("="*60 + "\n")
    
    # Inicializar rede democrática
    jarvis_path = r"C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0"
    network = DemocraticNetworkIntelligence(jarvis_path, "" + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "" + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "williamkelvem64@gmail.com")) + "")) + "")
    
    if not network.is_authorized:
        print("❌ Dispositivo não autorizado para demo")
        return
    
    # Iniciar rede
    await network.start_democratic_network()
    
    # Mostrar status
    status = network.get_network_status()
    print("📊 STATUS DA REDE DEMOCRÁTICA:")
    print(f"   👤 Conta: {status['account']}")
    print(f"   💪 CPU: {status['specs']['cpu_cores']} cores @ {status['specs']['cpu_freq_mhz']:.0f}MHz")
    print(f"   🧠 RAM: {status['specs']['total_ram_gb']:.1f}GB (disponível: {status['specs']['available_ram_gb']:.1f}GB)")
    print(f"   🎮 GPU: {status['specs']['gpu_name'] or 'Integrada'}")
    print(f"   📱 Dispositivos conectados: {status['discovered_devices']}")
    
    print("\n🎯 SIMULANDO SOLICITAÇÕES DE TREINAMENTO:")
    
    # Solicitação 1: Treinamento de voz (pesado)
    print("\n🎤 Solicitando treinamento de modelo de voz...")
    task_id_voice = await network.request_distributed_task(
        TaskType.VOICE_TRAINING,
        duration_min=45,
        data_size_mb=500.0,
        priority=8
    )
    
    await asyncio.sleep(3)
    
    # Solicitação 2: Fine-tuning de LLM (muito pesado)
    print("\n🧠 Solicitando fine-tuning distribuído de LLM...")
    task_id_llm = await network.request_distributed_task(
        TaskType.LLM_FINETUNING,
        duration_min=120,
        data_size_mb=2000.0, 
        priority=6,
        can_be_distributed=True,
        min_devices=2
    )
    
    await asyncio.sleep(5)
    
    # Mostrar status final
    final_status = network.get_network_status()
    print(f"\n📈 RESULTADO DA ELEIÇÃO:")
    print(f"   🎯 Tarefas ativas: {final_status['current_tasks']}")
    print(f"   👑 Papel atual: {final_status['current_role'] or 'Aguardando eleição'}")
    print(f"   🗳️ Status: {final_status['election_status']}")
    
    # Parar rede
    await network.stop_democratic_network()
    print("\n🏁 Demo concluída!")

if __name__ == "__main__":
    asyncio.run(democratic_training_demo())