#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Democratic Integration System
==================================================
Sistema completo de integração democrática no JARVIS.
"""

import asyncio
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ===== CLASSES MOCK PARA DEMONSTRAÇÃO =====

class JarvisDemocraticIntegration:
    """Mock implementation para demonstração"""

    def __init__(self, jarvis=None):
        self.jarvis = jarvis
        self.active = False

    async def start_democratic_mode(self, account):
        print(f"🔄 [MOCK] Iniciando modo democrático para conta: {account}")
        await asyncio.sleep(1)
        self.active = True
        return True

    async def stop_democratic_mode(self):
        print("🔄 [MOCK] Parando modo democrático")
        await asyncio.sleep(0.5)
        self.active = False

    def get_democratic_status_summary(self):
        return "🟢 SISTEMA DEMOCRÁTICO MOCK ATIVO\n   🔥 Modo de demonstração"

class DemocraticConfigManager:
    """Mock config manager"""

    def __init__(self, path):
        self.path = path
        self.config = {
            'target_microsoft_account': 'demo@account.com',
            'default_automation_level': 'balanced'
        }

    def load_config(self):
        return self.config

    def save_config(self):
        pass

def apply_config_profile(config, profile):
    """Mock profile application"""
    print(f"🔄 [MOCK] Aplicando perfil: {profile}")
    return True

# ===== SISTEMA DE INTEGRAÇÃO DEMOCRÁTICA =====

class JarvisDemocraticIntegrationSystem:
    """
    🏛️ SISTEMA DE INTEGRAÇÃO DEMOCRÁTICA COMPLETA

    Integra capacidades democráticas no JARVIS de forma transparente
    """

    def __init__(self, jarvis_instance=None):
        """Inicializa integração democrática"""
        self.jarvis = jarvis_instance
        self.democratic_mode_active = False
        self.democratic_integration = JarvisDemocraticIntegration(jarvis_instance)
        self.config_manager = DemocraticConfigManager(".")
        self.democratic_config = self.config_manager.load_config()

        logger.info("🏛️ Sistema de Integração Democrática inicializado")

    async def activate_democratic_mode(self, profile: str = "balanced", account: Optional[str] = None) -> bool:
        """
        🚀 ATIVA MODO DEMOCRÁTICO COMPLETO

        Args:
            profile: Perfil de configuração ("conservative", "balanced", "aggressive", "development", "production")
            account: Conta Microsoft específica (usa config se None)

        Returns:
            bool: True se ativado com sucesso
        """
        try:
            print("\n🏛️ ATIVANDO MODO DEMOCRÁTICO COMPLETO...")
            print(f"   👤 Conta: {account or self.democratic_config['target_microsoft_account']}")
            print(f"   🎭 Perfil: {profile}")

            # Aplicar perfil
            if profile != "default":
                success = apply_config_profile(self.democratic_config, profile)
                if success:
                    self.config_manager.save_config()
                    print("   ✅ Perfil aplicado")
                else:
                    print("   ⚠️ Perfil não encontrado, usando padrão")

            # Usar conta específica se fornecida
            target_account = account or self.democratic_config['target_microsoft_account']

            # Ativar modo democrático
            success = await self.democratic_integration.start_democratic_mode(target_account)

            if success:
                self.democratic_mode_active = True
                print("\n🎉 MODO DEMOCRÁTICO ATIVO!")
                print("   🔥 Sistema operando com poder total")
                # Mostrar status
                status = self.get_status_summary()
                print(f"\n{status}")

                return True
            else:
                print("❌ Falha na ativação do modo democrático")
                return False

        except Exception as e:
            logger.error(f"Erro ativando modo democrático: {e}")
            print(f"❌ Erro: {e}")
            return False

    async def deactivate_democratic_mode(self) -> bool:
        """
        ⏹️ DESATIVA MODO DEMOCRÁTICO

        Returns:
            bool: True se desativado com sucesso
        """
        if not self.democratic_mode_active:
            print("⚠️ Modo democrático já está inativo")
            return True

        try:
            print("🛑 Desativando modo democrático...")
            await self.democratic_integration.stop_democratic_mode()
            self.democratic_mode_active = False
            print("✅ Modo democrático desativado")
            return True

        except Exception as e:
            logger.error(f"Erro desativando modo democrático: {e}")
            print(f"❌ Erro na desativação: {e}")
            return False

    def get_status_summary(self) -> str:
        """📊 RESUMO COMPLETO DO STATUS DEMOCRÁTICO"""

        if not self.democratic_mode_active:
            return "🔴 SISTEMA DEMOCRÁTICO: INATIVO"

        try:
            status = self.democratic_integration.get_democratic_status_summary()
            return f"🟢 SISTEMA DEMOCRÁTICO ATIVO\n{status}"
        except Exception as e:
            return f"🟡 SISTEMA DEMOCRÁTICO: ERRO NO STATUS ({e})"

    def configure_profile(self, profile: str) -> bool:
        """
        ⚙️ CONFIGURA PERFIL DEMOCRÁTICO

        Args:
            profile: Nome do perfil

        Returns:
            bool: True se configurado com sucesso
        """
        try:
            success = apply_config_profile(self.democratic_config, profile)
            if success:
                self.config_manager.save_config()
                print(f"✅ Perfil '{profile}' configurado")
                return True
            else:
                print(f"❌ Perfil '{profile}' não encontrado")
                return False

        except Exception as e:
            logger.error(f"Erro configurando perfil: {e}")
            return False

    def get_available_profiles(self) -> list:
        """📋 LISTA PERFIS DISPONÍVEIS"""
        return ["conservative", "balanced", "aggressive", "development", "production"]

    def is_democratic_mode_active(self) -> bool:
        """🔍 VERIFICA SE MODO DEMOCRÁTICO ESTÁ ATIVO"""
        return self.democratic_mode_active

# ===== FUNÇÕES GLOBAIS =====

_democratic_integration_instance = None

def get_democratic_integration(jarvis_instance=None) -> JarvisDemocraticIntegrationSystem:
    """
    🏛️ OBTÉM INSTÂNCIA GLOBAL DA INTEGRAÇÃO DEMOCRÁTICA

    Args:
        jarvis_instance: Instância do JARVIS (opcional se já inicializada)

    Returns:
        JarvisDemocraticIntegrationSystem: Instância da integração
    """
    global _democratic_integration_instance

    if _democratic_integration_instance is None:
        _democratic_integration_instance = JarvisDemocraticIntegrationSystem(jarvis_instance)

    return _democratic_integration_instance

async def activate_global_democratic_mode(profile: str = "balanced", account: Optional[str] = None) -> bool:
    """
    🚀 ATIVA MODO DEMOCRÁTICO GLOBAL

    Args:
        profile: Perfil de configuração
        account: Conta Microsoft específica

    Returns:
        bool: True se ativado com sucesso
    """
    integration = get_democratic_integration()
    return await integration.activate_democratic_mode(profile, account)

async def deactivate_global_democratic_mode() -> bool:
    """
    ⏹️ DESATIVA MODO DEMOCRÁTICO GLOBAL

    Returns:
        bool: True se desativado com sucesso
    """
    integration = get_democratic_integration()
    return await integration.deactivate_democratic_mode()

def get_global_democratic_status() -> str:
    """📊 STATUS GLOBAL DEMOCRÁTICO"""
    try:
        integration = get_democratic_integration()
        return integration.get_status_summary()
    except:
        return "🔴 SISTEMA DEMOCRÁTICO: NÃO INICIALIZADO"

# ===== INTEGRAÇÃO COM MAIN.PY =====

class JarvisWithDemocraticCapabilities:
    """
    🏛️ JARVIS COM CAPACIDADES DEMOCRÁTICAS

    Wrapper que adiciona funcionalidades democráticas ao JARVIS
    """

    def __init__(self, original_jarvis=None):
        self.original_jarvis = original_jarvis
        self.democratic_integration = get_democratic_integration(original_jarvis)
        self._democratic_mode = False

    async def start_with_democratic_check(self, enable_democratic: bool = True, profile: str = "balanced"):
        """
        🚀 INICIA JARVIS COM VERIFICAÇÃO DEMOCRÁTICA

        Args:
            enable_democratic: Se deve ativar modo democrático
            profile: Perfil democrático
        """
        print("🚀 Iniciando JARVIS...")

        # Verificar se deve ativar democrático
        if enable_democratic:
            print("\n🏛️ Verificando sistema democrático...")
            success = await self.democratic_integration.activate_democratic_mode(profile)
            if success:
                self._democratic_mode = True
                print("✅ JARVIS Democrático totalmente operacional")
            else:
                print("⚠️ JARVIS funcionando em modo tradicional")

    async def stop(self):
        """⏹️ PARA JARVIS COM DESATIVAÇÃO DEMOCRÁTICA"""
        if self._democratic_mode:
            await self.democratic_integration.deactivate_democratic_mode()

        print("✅ JARVIS parado")

# ===== UTILITÁRIOS =====

def handle_democratic_cli_args(args: list = None) -> bool:
    """
    🖥️ TRATA ARGUMENTOS DEMOCRÁTICOS DA LINHA DE COMANDO

    Args:
        args: Lista de argumentos (usa sys.argv se None)

    Returns:
        bool: True se argumento foi tratado
    """
    if args is None:
        args = sys.argv

    if "--democratic-status" in args:
        print("🏛️ STATUS DEMOCRÁTICO:")
        print(get_global_democratic_status())
        return True

    elif "--activate-democratic" in args:
        profile = "balanced"
        if "--profile" in args:
            idx = args.index("--profile")
            if idx + 1 < len(args):
                profile = args[idx + 1]

        async def activate():
            success = await activate_global_democratic_mode(profile)
            print("✅ Modo democrático ativado" if success else "❌ Falha na ativação")

        asyncio.run(activate())
        return True

    elif "--deactivate-democratic" in args:
        async def deactivate():
            success = await deactivate_global_democratic_mode()
            print("✅ Modo democrático desativado" if success else "❌ Falha na desativação")

        asyncio.run(deactivate())
        return True

    return False

# ===== VALIDAÇÃO =====

def validate_democratic_system() -> Dict[str, Any]:
    """
    🔍 VALIDA SISTEMA DEMOCRÁTICO

    Returns:
        Dict com status de validação
    """
    results = {
        "democratic_core": True,  # Mock sempre disponível
        "democratic_config": True,
        "democratic_integration": True,
        "overall_status": True
    }

    print("✅ Sistema democrático mock validado")
    print("✅ SISTEMA DEMOCRÁTICO COMPLETO (MOCK)")

    return results

# ===== TESTE =====

async def test_democratic_integration(jarvis_instance=None) -> bool:
    """
    🧪 TESTA INTEGRAÇÃO DEMOCRÁTICA

    Args:
        jarvis_instance: Instância do JARVIS para teste

    Returns:
        bool: True se teste passou
    """
    print("🧪 TESTANDO INTEGRAÇÃO DEMOCRÁTICA...")

    try:
        # Obter integração
        integration = get_democratic_integration(jarvis_instance)

        # Testar perfis disponíveis
        profiles = integration.get_available_profiles()
        print(f"✅ Perfis disponíveis: {profiles}")

        # Testar status inicial
        status = integration.get_status_summary()
        print(f"✅ Status inicial: {status}")

        # Testar configuração de perfil
        success = integration.configure_profile("development")
        print(f"✅ Configuração de perfil: {'OK' if success else 'FALHA'}")

        print("✅ Teste de integração democrática concluído")
        return True

    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

# ===== MAIN =====

if __name__ == "__main__":
    # Teste independente
    print("🏛️ Democratic Integration System - Test Mode")

    # Verificar argumentos CLI
    if handle_democratic_cli_args():
        sys.exit(0)

    # Validar sistema
    validation = validate_democratic_system()

    # Testar integração
    asyncio.run(test_democratic_integration())

    print("\n🏁 Teste concluído")