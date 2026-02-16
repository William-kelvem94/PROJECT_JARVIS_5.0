#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Microsoft Account + Device Identification System
=====================================================================
Sistema completo de identificação da conta Microsoft real + hardware fingerprinting
para autorizar dispositivos na rede democrática.
"""

import hashlib
import json
import subprocess
import uuid
import platform
import psutil
import socket
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import requests
import os

# Platform compatibility
from src.utils.platform_compat import (
    IS_WINDOWS, winreg, WINREG_AVAILABLE, wmi, WMI_AVAILABLE,
    require_windows, windows_or_fallback
)

@dataclass
class MicrosoftAccountInfo:
    """ðŸ“‹ InformaÃ§Ãµes da conta Microsoft"""
    account_email: str
    account_type: str  # "local", "microsoft", "azure_ad", "work_school"
    display_name: str
    is_administrator: bool
    azure_tenant_id: Optional[str] = None
    domain_name: Optional[str] = None
    last_login: Optional[datetime] = None
    
@dataclass 
class DeviceFingerprint:
    """ðŸ”’ Fingerprint Ãºnico do dispositivo"""
    device_id: str
    computer_name: str
    hardware_hash: str
    cpu_info: str
    motherboard_serial: str
    bios_serial: str
    network_adapters: List[str]
    installed_date: Optional[str] = None
    windows_product_id: Optional[str] = None

@dataclass
class GoogleDriveAuth:
    """â˜ï¸ AutenticaÃ§Ã£o do Google Drive"""
    is_authenticated: bool
    account_email: str
    drive_path: Optional[str] = None
    sync_enabled: bool = False
    last_sync: Optional[datetime] = None

class MicrosoftDeviceIdentifier:
    """
    ðŸ” MICROSOFT ACCOUNT + DEVICE IDENTIFICATION SYSTEM
    
    Identifica:
    - Conta Microsoft real (nÃ£o sÃ³ usuÃ¡rio local)
    - Hardware fingerprinting Ãºnico
    - Google Drive da mesma conta (se disponÃ­vel)
    - AutorizaÃ§Ã£o para rede democrÃ¡tica
    """
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.cache_path = self.config_path / "identity_cache.json"
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Estado
        self.microsoft_account: Optional[MicrosoftAccountInfo] = None
        self.device_fingerprint: Optional[DeviceFingerprint] = None
        self.google_drive_auth: Optional[GoogleDriveAuth] = None
        
        # Cache para evitar detecÃ§Ãµes repetidas
        self._cache = {}
        
        print("ðŸ” Microsoft Device Identifier inicializado")
    
    def identify_complete_profile(self) -> Dict[str, Any]:
        """ðŸŽ¯ IDENTIFICAÃ‡ÃƒO COMPLETA DO USUÃRIO + DISPOSITIVO"""
        
        print("ðŸ” Iniciando identificaÃ§Ã£o completa...")
        
        try:
            # 1. IDENTIFICAR CONTA MICROSOFT REAL
            print("   ðŸ‘¤ Detectando conta Microsoft...")
            self.microsoft_account = self._detect_microsoft_account()
            
            # 2. CRIAR FINGERPRINT DO DISPOSITIVO
            print("   ðŸ”’ Criando fingerprint do dispositivo...")
            self.device_fingerprint = self._create_device_fingerprint()
            
            # 3. VERIFICAR GOOGLE DRIVE
            print("   â˜ï¸ Verificando Google Drive...")
            self.google_drive_auth = self._detect_google_drive()
            
            # 4. SALVAR CACHE
            self._save_identity_cache()
            
            profile = {
                'microsoft_account': asdict(self.microsoft_account) if self.microsoft_account else None,
                'device_fingerprint': asdict(self.device_fingerprint) if self.device_fingerprint else None,
                'google_drive_auth': asdict(self.google_drive_auth) if self.google_drive_auth else None,
                'identification_timestamp': datetime.now().isoformat(),
                'is_authorized_for_democratic_network': self._is_authorized_for_democratic_network()
            }
            
            print("âœ… IdentificaÃ§Ã£o completa finalizada!")
            return profile
            
        except Exception as e:
            print(f"âŒ Erro na identificaÃ§Ã£o: {e}")
            return {'error': str(e)}
    
    def _detect_microsoft_account(self) -> MicrosoftAccountInfo:
        """ðŸ‘¤ DETECÃ‡ÃƒO AVANÃ‡ADA DA CONTA MICROSOFT"""
        
        account_info = MicrosoftAccountInfo(
            account_email="unknown",
            account_type="local",
            display_name="unknown",
            is_administrator=False
        )
        
        try:
            # 1. VERIFICAR SE Ã‰ ADMINISTRADOR
            try:
                import ctypes
                account_info.is_administrator = ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                pass
            
            # 2. TENTAR REGISTRY - LOGON UI (Ãšltima conta que fez login)
            try:
                key_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Authentication\\LogonUI"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    try:
                        last_user, _ = winreg.QueryValueEx(key, "LastLoggedOnUser")
                        if '@' in last_user:  # Ã‰ uma conta Microsoft
                            account_info.account_email = last_user
                            account_info.account_type = "microsoft"
                            print(f"   âœ… Conta Microsoft detectada: {last_user}")
                    except FileNotFoundError:
                        pass
                    
                    try:
                        display_name, _ = winreg.QueryValueEx(key, "LastLoggedOnDisplayName")
                        account_info.display_name = display_name
                    except FileNotFoundError:
                        pass
            except Exception as e:
                print(f"   âš ï¸ Erro acessando Logon UI: {e}")
            
            # 3. VERIFICAR AZURE AD JOIN
            try:
                azure_key_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\AAD"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, azure_key_path) as key:
                    try:
                        tenant_id, _ = winreg.QueryValueEx(key, "TenantId")
                        if tenant_id:
                            account_info.azure_tenant_id = tenant_id
                            account_info.account_type = "azure_ad"
                            print(f"   ðŸ¢ Azure AD Tenant: {tenant_id}")
                    except FileNotFoundError:
                        pass
            except FileNotFoundError:
                pass  # NÃ£o Ã© Azure AD joined
            
            # 4. VERIFICAR VIA WMI (Contas de usuÃ¡rio)
            try:
                wmi_conn = wmi.WMI()
                current_user = os.getenv('USERNAME')
                
                for user in wmi_conn.Win32_UserAccount():
                    if user.Name == current_user:
                        if not user.LocalAccount:  # Conta de domÃ­nio/Microsoft
                            if account_info.account_email == "unknown":
                                account_info.account_email = f"{user.Name}@{user.Domain}"
                                account_info.account_type = "domain"
                        
                        if user.FullName:
                            account_info.display_name = user.FullName
                        
                        break
            except Exception as e:
                print(f"   âš ï¸ Erro acessando WMI: {e}")
            
            # 5. VERIFICAR WHOAMI (Fallback)
            try:
                result = subprocess.run(['whoami', '/fqdn'], capture_output=True, text=True)
                if result.returncode == 0:
                    fqdn = result.stdout.strip()
                    if '@' in fqdn or '\\\\' in fqdn:
                        account_info.account_email = fqdn
                        if account_info.account_type == "local":
                            account_info.account_type = "domain"
            except:
                pass
            
            # 6. SE AINDA Ã‰ LOCAL, TENTAR DETECTAR VIA REGISTRY USERS
            if account_info.account_type == "local":
                try:
                    # Verificar se hÃ¡ contas Microsoft conectadas
                    users_key = r"SOFTWARE\\Microsoft\\IdentityCRL\\UserExtendedProperties"
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, users_key) as key:
                        # Enumerar subkeys para encontrar contas Microsoft
                        i = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                if '@' in subkey_name:  # Parece email
                                    account_info.account_email = subkey_name
                                    account_info.account_type = "microsoft"
                                    print(f"   âœ… Conta Microsoft via Identity: {subkey_name}")
                                    break
                                i += 1
                            except OSError:
                                break
                except Exception as e:
                    print(f"   âš ï¸ Erro acessando Identity Registry: {e}")
            
            # 7. FALLBACK: USAR INFORMAÃ‡Ã•ES BÃSICAS
            if account_info.account_email == "unknown":
                account_info.account_email = f"{os.getenv('USERNAME', 'unknown')}@local"
                account_info.display_name = os.getenv('USERNAME', 'unknown')
            
            print(f"   ðŸ“‹ Resultado: {account_info.account_type} - {account_info.account_email}")
            
            return account_info
            
        except Exception as e:
            print(f"âŒ Erro detectando conta Microsoft: {e}")
            return account_info
    
    def _create_device_fingerprint(self) -> DeviceFingerprint:
        """ðŸ”’ CRIA FINGERPRINT ÃšNICO DO DISPOSITIVO"""
        
        try:
            # InformaÃ§Ãµes bÃ¡sicas
            computer_name = socket.gethostname()
            
            # Coletar informaÃ§Ãµes de hardware via WMI
            fingerprint_data = {
                'computer_name': computer_name,
                'cpu_info': '',
                'motherboard_serial': '',
                'bios_serial': '',
                'network_adapters': [],
                'windows_product_id': ''
            }
            
            try:
                wmi_conn = wmi.WMI()
                
                # CPU Info
                for cpu in wmi_conn.Win32_Processor():
                    fingerprint_data['cpu_info'] = f"{cpu.Name}_{cpu.ProcessorId}"
                    break
                
                # Motherboard Serial
                for board in wmi_conn.Win32_BaseBoard():
                    if board.SerialNumber and board.SerialNumber.strip():
                        fingerprint_data['motherboard_serial'] = board.SerialNumber.strip()
                    break
                
                # BIOS Serial
                for bios in wmi_conn.Win32_BIOS():
                    if bios.SerialNumber and bios.SerialNumber.strip():
                        fingerprint_data['bios_serial'] = bios.SerialNumber.strip()
                    break
                
                # Network Adapters (MACs)
                for adapter in wmi_conn.Win32_NetworkAdapterConfiguration():
                    if adapter.MACAddress and adapter.MACAddress != '00:00:00:00:00:00':
                        fingerprint_data['network_adapters'].append(adapter.MACAddress)
                
                # Windows Product ID
                for system in wmi_conn.Win32_OperatingSystem():
                    if system.SerialNumber:
                        fingerprint_data['windows_product_id'] = system.SerialNumber
                    break
                    
            except Exception as e:
                print(f"   âš ï¸ Erro coletando WMI: {e}")
                # Fallback para mÃ©todos alternativos
                fingerprint_data['cpu_info'] = platform.processor()
                fingerprint_data['motherboard_serial'] = str(uuid.getnode())  # MAC como fallback
            
            # Criar hash Ãºnico baseado no hardware
            hardware_string = (
                f"{fingerprint_data['cpu_info']}_"
                f"{fingerprint_data['motherboard_serial']}_"
                f"{fingerprint_data['bios_serial']}_"
                f"{'_'.join(sorted(fingerprint_data['network_adapters']))}_"
                f"{fingerprint_data['windows_product_id']}"
            )
            
            hardware_hash = hashlib.sha256(hardware_string.encode()).hexdigest()[:16]
            
            # Gerar device_id Ãºnico
            device_id = f"{computer_name}_{hardware_hash}"
            
            print(f"   ðŸ”’ Device ID: {device_id}")
            print(f"   ðŸ’¾ Hardware Hash: {hardware_hash}")
            
            return DeviceFingerprint(
                device_id=device_id,
                computer_name=computer_name,
                hardware_hash=hardware_hash,
                cpu_info=fingerprint_data['cpu_info'],
                motherboard_serial=fingerprint_data['motherboard_serial'],
                bios_serial=fingerprint_data['bios_serial'],
                network_adapters=fingerprint_data['network_adapters'],
                windows_product_id=fingerprint_data['windows_product_id']
            )
            
        except Exception as e:
            print(f"âŒ Erro criando fingerprint: {e}")
            # Fallback mÃ­nimo
            return DeviceFingerprint(
                device_id=f"{socket.gethostname()}_{hashlib.md5(str(uuid.getnode()).encode()).hexdigest()[:8]}",
                computer_name=socket.gethostname(),
                hardware_hash="fallback",
                cpu_info=platform.processor(),
                motherboard_serial="unknown",
                bios_serial="unknown",
                network_adapters=[]
            )
    
    def _detect_google_drive(self) -> GoogleDriveAuth:
        """â˜ï¸ DETECTA GOOGLE DRIVE E AUTENTICAÃ‡ÃƒO"""
        
        drive_auth = GoogleDriveAuth(
            is_authenticated=False,
            account_email="unknown",
            sync_enabled=False
        )
        
        try:
            # 1. VERIFICAR SE GOOGLE DRIVE ESTÃ INSTALADO
            possible_paths = [
                os.path.expanduser("~\\Google Drive"),
                os.path.expanduser("~\\GoogleDrive"),
                "C:\\Program Files\\Google\\Drive File Stream",
                "C:\\Program Files (x86)\\Google\\Drive File Stream",
                "C:\\Users\\Default\\Google Drive"
            ]
            
            google_drive_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    google_drive_path = path
                    drive_auth.drive_path = path
                    drive_auth.sync_enabled = True
                    break
            
            # 2. VERIFICAR PROCESSO DO GOOGLE DRIVE
            google_drive_running = False
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    proc_name = proc.info['name'].lower()
                    if 'googledrivesync' in proc_name or 'google drive' in proc_name:
                        google_drive_running = True
                        break
            except:
                pass
            
            # 3. TENTAR DETECTAR CONTA VIA REGISTRY
            try:
                # Google Drive File Stream guarda info no Registry
                drive_key = r"SOFTWARE\\Google\\DriveFS"
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, drive_key) as key:
                        drive_auth.is_authenticated = True
                        
                        # Tentar encontrar email da conta
                        i = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                if '@' in subkey_name:
                                    drive_auth.account_email = subkey_name
                                    break
                                i += 1
                            except OSError:
                                break
                        
                except FileNotFoundError:
                    pass
            except Exception as e:
                print(f"   âš ï¸ Erro verificando Registry Google Drive: {e}")
            
            # 4. VERIFICAR VIA CREDSTORE (Windows Credential Manager)
            try:
                result = subprocess.run([
                    'cmdkey', '/list'
                ], capture_output=True, text=True, shell=True)
                
                if result.returncode == 0:
                    output = result.stdout
                    if 'google' in output.lower():
                        drive_auth.is_authenticated = True
                        # Tentar extrair email do output
                        lines = output.split('\\n')
                        for line in lines:
                            if '@' in line and 'google' in line.lower():
                                # Extrair email da linha
                                import re
                                email_match = re.search(r'[\\w\\.-]+@[\\w\\.-]+\\.\\w+', line)
                                if email_match:
                                    drive_auth.account_email = email_match.group()
                                    break
                                    
            except Exception as e:
                print(f"   âš ï¸ Erro verificando Credential Manager: {e}")
            
            if drive_auth.is_authenticated:
                print(f"   âœ… Google Drive detectado: {drive_auth.account_email}")
                if drive_auth.drive_path:
                    print(f"   ðŸ“ Path: {drive_auth.drive_path}")
            else:
                print(f"   âŒ Google Drive nÃ£o autenticado")
            
            return drive_auth
            
        except Exception as e:
            print(f"âŒ Erro detectando Google Drive: {e}")
            return drive_auth
    
    def _is_authorized_for_democratic_network(self) -> bool:
        """ðŸ›ï¸ VERIFICA SE DISPOSITIVO ESTÃ AUTORIZADO PARA REDE DEMOCRÃTICA"""
        
        if not self.microsoft_account:
            return False
        
        # Verificar se Ã© uma das contas autorizadas
        authorized_accounts = [
            "" + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "" + self.config.get("target_user_email", os.getenv("JARVIS_USER_EMAIL", "williamkelvem64@gmail.com")) + "")) + "",
            "williamkelvem64@outlook.com", 
            "williamkelvem64@hotmail.com",
            "williamkelvem64@live.com"
        ]
        
        # Verificar email exato ou se contÃ©m o usuÃ¡rio autorizado
        account_email = self.microsoft_account.account_email.lower()
        
        for authorized in authorized_accounts:
            if authorized in account_email or account_email in authorized:
                return True
        
        # Verificar se o usuÃ¡rio local Ã© 'willi' (fallback)
        if 'willi' in account_email.lower():
            return True
        
        return False
    
    def create_device_authorization_token(self) -> Optional[str]:
        """ðŸŽŸï¸ CRIA TOKEN DE AUTORIZAÃ‡ÃƒO PARA O DISPOSITIVO"""
        
        if not self._is_authorized_for_democratic_network():
            print("âŒ Dispositivo nÃ£o autorizado para rede democrÃ¡tica")
            return None
        
        try:
            # Dados para o token
            device_id = "unknown"
            account_email = "unknown"
            hardware_hash = "unknown"
            computer_name = "unknown"
            
            if self.device_fingerprint:
                device_id = self.device_fingerprint.device_id
                hardware_hash = self.device_fingerprint.hardware_hash
                computer_name = self.device_fingerprint.computer_name
            
            if self.microsoft_account:
                account_email = self.microsoft_account.account_email
            
            token_data = {
                'device_id': device_id,
                'account_email': account_email,
                'hardware_hash': hardware_hash,
                'computer_name': computer_name,
                'timestamp': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Criar assinatura baseada nos dados
            token_string = json.dumps(token_data, sort_keys=True)
            token_hash = hashlib.sha256(token_string.encode()).hexdigest()
            
            token = f"JARVIS_DEMOCRATIC_{token_hash[:32]}"
            
            print(f"ðŸŽŸï¸ Token de autorizaÃ§Ã£o criado: {token[:20]}...")
            return token
            
        except Exception as e:
            print(f"âŒ Erro criando token: {e}")
            return None
    
    def get_google_drive_jarvis_folder(self) -> Optional[str]:
        """ðŸ“ RETORNA PASTA JARVIS NO GOOGLE DRIVE (SE DISPONÃVEL)"""
        
        if not (self.google_drive_auth and self.google_drive_auth.sync_enabled):
            return None
        
        try:
            # Determinar usuÃ¡rio para pasta
            if self.microsoft_account:
                username = self.microsoft_account.account_email.split('@')[0]
            else:
                username = os.getenv('USERNAME', 'unknown')
            
            # Criar estrutura de pasta
            if self.google_drive_auth and self.google_drive_auth.drive_path:
                jarvis_folder = Path(self.google_drive_auth.drive_path) / f"JARVIS_{username}"
                
                # Criar pasta se nÃ£o existir
                jarvis_folder.mkdir(exist_ok=True)
                
                # Criar subpastas
                subfolders = ['devices', 'memories', 'learning', 'models', 'sync_data', 'emergencies']
                for subfolder in subfolders:
                    (jarvis_folder / subfolder).mkdir(exist_ok=True)
                
                print(f"ðŸ“ Pasta JARVIS: {jarvis_folder}")
                return str(jarvis_folder)
            return None
            
        except Exception as e:
            print(f"âŒ Erro criando pasta JARVIS no Google Drive: {e}")
            return None
    
    def _save_identity_cache(self):
        """ðŸ’¾ SALVA CACHE DE IDENTIDADE"""
        
        try:
            cache_data = {
                'microsoft_account': asdict(self.microsoft_account) if self.microsoft_account else None,
                'device_fingerprint': asdict(self.device_fingerprint) if self.device_fingerprint else None,
                'google_drive_auth': asdict(self.google_drive_auth) if self.google_drive_auth else None,
                'last_update': datetime.now().isoformat()
            }
            
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"âŒ Erro salvando cache: {e}")
    
    def load_cached_identity(self) -> bool:
        """ðŸ“ CARREGA IDENTIDADE DO CACHE"""
        
        if not self.cache_path.exists():
            return False
        
        try:
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Verificar se cache nÃ£o Ã© muito antigo (1 hora)
            last_update = datetime.fromisoformat(cache_data.get('last_update', '2000-01-01'))
            if (datetime.now() - last_update).total_seconds() > 3600:
                return False
            
            # Carregar dados
            if cache_data.get('microsoft_account'):
                self.microsoft_account = MicrosoftAccountInfo(**cache_data['microsoft_account'])
            
            if cache_data.get('device_fingerprint'):
                self.device_fingerprint = DeviceFingerprint(**cache_data['device_fingerprint'])
            
            if cache_data.get('google_drive_auth'):
                self.google_drive_auth = GoogleDriveAuth(**cache_data['google_drive_auth'])
            
            print("ðŸ“ Identidade carregada do cache")
            return True
            
        except Exception as e:
            print(f"âŒ Erro carregando cache: {e}")
            return False
    
    # ===== MÃ‰TODOS PÃšBLICOS =====
    
    def initialize(self) -> bool:
        """ðŸš€ INICIALIZA IDENTIFICAÃ‡ÃƒO"""
        if self.load_cached_identity():
            return True
        
        result = self.identify_complete_profile()
        return "error" not in result

    def is_authorized_device(self) -> bool:
        """âœ… VERIFICA SE DISPOSITIVO ESTÃ AUTORIZADO"""
        if not self.microsoft_account:
            return False
        return self._is_authorized_for_democratic_network()
    
    def get_identity_summary(self) -> str:
        """ðŸ“‹ RESUMO DA IDENTIDADE DO DISPOSITIVO"""
        
        if not (self.microsoft_account and self.device_fingerprint):
            return "âŒ Identidade nÃ£o detectada"
        
        auth_status = "âœ… AUTORIZADO" if self.is_authorized_device() else "âŒ NÃƒO AUTORIZADO"
        google_status = "âœ… CONECTADO" if (self.google_drive_auth and self.google_drive_auth.is_authenticated) else "âŒ DESCONECTADO"
        
        summary = f"""
ðŸ” IDENTIDADE DO DISPOSITIVO
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
ðŸ‘¤ Conta Microsoft: {self.microsoft_account.account_email}
ðŸ·ï¸ Tipo: {self.microsoft_account.account_type}
ðŸ“± Dispositivo: {self.device_fingerprint.computer_name}
ðŸ”’ Device ID: {self.device_fingerprint.device_id}
ðŸ›ï¸ Rede DemocrÃ¡tica: {auth_status}
â˜ï¸ Google Drive: {google_status}
"""
        return summary

# Exemplo de uso:
# identifier = MicrosoftDeviceIdentifier("./data/identity")
# profile = identifier.identify_complete_profile()
# token = identifier.create_device_authorization_token()
# jarvis_folder = identifier.get_google_drive_jarvis_folder()
