"""
JARVIS 5.0 - Script de Inicialização Otimizado
Inicializa todos os módulos com verificação de dependências
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

import logging
import time
from datetime import datetime

# Configurar logging
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"jarvis_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def print_banner():
    """Exibe banner do JARVIS"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗          ║
    ║        ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝          ║
    ║        ██║███████║██████╔╝██║   ██║██║███████╗          ║
    ║   ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║          ║
    ║   ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║          ║
    ║    ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝          ║
    ║                                                           ║
    ║              🚀 JARVIS 5.0 EVOLUTION 🚀                  ║
    ║         Just A Rather Very Intelligent System            ║
    ║                                                           ║
    ║              Status: 95% Completo                        ║
    ║              Versão: 5.0.0-evolution                     ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Verifica dependências críticas"""
    print("\n🔍 Verificando dependências...")
    
    dependencies = {
        "numpy": "NumPy",
        "cv2": "OpenCV",
        "PIL": "Pillow",
        "customtkinter": "CustomTkinter",
        "requests": "Requests"
    }
    
    missing = []
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - FALTANDO")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️ Dependências faltando: {', '.join(missing)}")
        print("Execute: pip install -r requirements_advanced.txt")
        return False
    
    return True

def initialize_core_modules():
    """Inicializa módulos principais"""
    print("\n🧠 Inicializando módulos principais...")
    
    modules = {}
    
    # Maintenance Manager (Auto-Reparo)
    try:
        from src.core.maintenance_manager import maintenance_manager
        modules['maintenance'] = maintenance_manager
        print("  ✅ Maintenance Manager")
    except Exception as e:
        print(f"  ❌ Maintenance Manager: {e}")
    
    # Brain Router
    try:
        from src.core.brain_router import brain_router
        modules['brain_router'] = brain_router
        print("  ✅ Brain Router")
    except Exception as e:
        print(f"  ⚠️ Brain Router: {e}")
    
    # Advanced Action Controller
    try:
        from src.core.advanced_action_controller import advanced_action_controller
        modules['advanced_actions'] = advanced_action_controller
        print("  ✅ Advanced Action Controller")
    except Exception as e:
        print(f"  ⚠️ Advanced Action Controller: {e}")
    
    # Workflow Engine
    try:
        from src.core.workflow_engine import workflow_engine
        modules['workflow'] = workflow_engine
        print("  ✅ Workflow Engine")
    except Exception as e:
        print(f"  ⚠️ Workflow Engine: {e}")
    
    # Advanced Vision Pipeline
    try:
        from src.core.advanced_vision_pipeline import advanced_vision_pipeline
        modules['vision'] = advanced_vision_pipeline
        print("  ✅ Advanced Vision Pipeline")
    except Exception as e:
        print(f"  ⚠️ Advanced Vision Pipeline: {e}")
    
    # Advanced Speech Processor
    try:
        from src.core.advanced_speech_processor import advanced_speech_processor
        modules['speech'] = advanced_speech_processor
        print("  ✅ Advanced Speech Processor")
    except Exception as e:
        print(f"  ⚠️ Advanced Speech Processor: {e}")
    
    # Security Manager
    try:
        from src.core.security_manager_advanced import security_manager
        modules['security'] = security_manager
        print("  ✅ Security Manager Advanced")
    except Exception as e:
        print(f"  ⚠️ Security Manager: {e}")
    
    # AI Agent
    try:
        from src.core.ai_agent import ai_agent
        modules['ai_agent'] = ai_agent
        print("  ✅ AI Agent")
    except Exception as e:
        print(f"  ❌ AI Agent: {e}")
    
    return modules

def run_auto_repair():
    """Executa auto-reparo se necessário"""
    print("\n🔧 Verificando integridade do sistema...")
    
    try:
        from src.core.maintenance_manager import maintenance_manager
        
        # Verificar se precisa de reparo
        needs_repair = False
        
        # Verificar CMake
        import subprocess
        try:
            subprocess.run(["cmake", "--version"], capture_output=True, timeout=2)
            print("  ✅ CMake instalado")
        except:
            print("  ⚠️ CMake não encontrado - será instalado")
            needs_repair = True
        
        # Verificar Vosk
        vosk_path = Path("models/vosk-model-small-pt-0.22")
        if vosk_path.exists():
            print("  ✅ Modelo Vosk PT-BR instalado")
        else:
            print("  ⚠️ Modelo Vosk não encontrado - será baixado")
            needs_repair = True
        
        if needs_repair:
            print("\n🔧 Executando auto-reparo...")
            maintenance_manager.check_and_repair_all()
        else:
            print("  ✅ Sistema íntegro")
        
    except Exception as e:
        print(f"  ⚠️ Erro no auto-reparo: {e}")

def start_gui():
    """Inicia interface gráfica"""
    print("\n🖥️ Iniciando interface gráfica...")
    
    try:
        from src.gui.main_window import MainWindow
        import customtkinter as ctk
        
        app = MainWindow()
        print("  ✅ Interface inicializada")
        print("\n🚀 JARVIS 5.0 está pronto!")
        print("  Pressione Ctrl+C para encerrar\n")
        
        app.mainloop()
        
    except KeyboardInterrupt:
        print("\n\n👋 Encerrando JARVIS...")
    except Exception as e:
        logger.error(f"Erro ao iniciar GUI: {e}")
        print(f"\n❌ Erro ao iniciar interface: {e}")
        print("\nTente executar em modo console:")
        print("  python -c \"from src.core.ai_agent import ai_agent; ai_agent.process_command('teste')\"")

def main():
    """Função principal"""
    print_banner()
    
    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Instalação incompleta. Execute:")
        print("  pip install -r requirements_advanced.txt")
        return 1
    
    # Inicializar módulos
    modules = initialize_core_modules()
    
    if not modules:
        print("\n❌ Nenhum módulo foi carregado. Verifique a instalação.")
        return 1
    
    print(f"\n✅ {len(modules)} módulos carregados com sucesso")
    
    # Auto-reparo
    run_auto_repair()
    
    # Iniciar GUI
    start_gui()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)
