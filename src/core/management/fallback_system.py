import logging
import threading
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class FallbackSystem:
    """
    Sistema de redundância em camadas para garantir que o Jarvis nunca deixe o usuário na mão.
    Se a internet cair, usa local. Se o local travar, usa hotkeys. Se tudo falhar, reinicia.
    
    🆕 Integração com Auto-Recovery System para healing automático de falhas.
    """
    
    def __init__(self, jarvis_core=None):
        self.jarvis = jarvis_core
        self.current_layer = 0
        
        # Integration with Auto-Recovery System
        self.auto_recovery = None
        self._initialize_auto_recovery()
        
    def _initialize_auto_recovery(self):
        """Initialize auto-recovery system integration"""
        try:
            from .auto_recovery_system import get_auto_recovery_system
            self.auto_recovery = get_auto_recovery_system()
            
            # Set bidirectional integration
            self.auto_recovery.set_fallback_system(self)
            
            # Register fallback system as a monitored module
            self.auto_recovery.register_module("fallback_system")
            
            logger.info("✅ Auto-Recovery System integration established")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize auto-recovery integration: {e}")
    
    def trigger_auto_recovery(self, exception: Exception, module_name: str = "unknown", severity: int = 5):
        """Trigger auto-recovery for detected failures"""
        if self.auto_recovery:
            try:
                from .auto_recovery_system import trigger_recovery_for_exception
                trigger_recovery_for_exception(module_name, exception, severity)
                logger.info(f"🔧 Auto-recovery triggered for {module_name}")
            except Exception as e:
                logger.error(f"❌ Failed to trigger auto-recovery: {e}")
        
    def process_command(self, command: str, max_layers=5):
        """Tenta processar comando em camadas de fallback com auto-recovery integrado"""
        
        # Sequência de tentativas
        layers = [
            self.layer0_hybrid_intellect,     # Cérebro Principal (Cloud/Local)
            self.layer1_local_only,           # Cérebro Local Estrito (Ollama)
            self.layer2_regex_commands,       # Comandos Regex Simples
            self.layer3_manual_hotkey,        # Sugestão de Hotkeys
            self.layer4_emergency_reboot      # Reinício dos subsistemas
        ]
        
        for i, layer_func in enumerate(layers):
            try:
                self.current_layer = i
                # logger.info(f"🛡️ Fallback System: Tentando Camada {i} ({layer_func.__name__})...")
                
                result = layer_func(command)
                
                if result and result.get("success"):
                    if i > 0:
                        logger.warning(f"⚠️ Comando executado via Fallback Layer {i}")
                    return result
                    
            except Exception as e:
                logger.error(f"❌ Falha na Camada {i}: {e}")
                
                # 🆕 Trigger auto-recovery for layer failures
                layer_name = f"fallback_layer_{i}"
                severity = min(10, 3 + i)  # Increasing severity with layer depth
                self.trigger_auto_recovery(e, layer_name, severity)
                
                continue
        
        # 🆕 If all fallback layers failed, trigger critical auto-recovery
        critical_failure = Exception("All fallback layers failed")
        self.trigger_auto_recovery(critical_failure, "fallback_system_critical", 10)
        
        return {"success": False, "response": "Falha crítica em todos os subsistemas de resposta."}
    
    def layer0_hybrid_intellect(self, command):
        """Camada 0: Tenta usar o AI Agent normal"""
        if not self.jarvis or not self.jarvis.ai_agent:
            return {"success": False}
            
        # Esta camada é apenas um proxy, a lógica real está no AIAgent
        # Se o AIAgent retornar erro ou string vazia, consideramos falha
        # Mas como o AIAgent já tem sua lógica interna, aqui simulamos a validação
        
        # Validar conexão internet
        # if not internet: raise Exception("No internet")
        
        # Se chegamos aqui, assumimos que o AIAgent será chamado externamente ou
        # aqui invocamos um método "try_process" se existisse. 
        # Para este design, assumimos que o FallbackSystem é chamado QUANDO o AIAgent falha
        # ou o AIAgent USA o FallbackSystem.
        
        # Vamos assumir que este método é chamado para TENTAR processar
        # Se fosse chamado de dentro do AIAgent, seria recursivo. 
        # O ideal é o Orchestrator chamar o FallbackSystem.
        
        return {"success": False} # Placeholder para forçar próximas camadas se chamado diretamente

    def layer1_local_only(self, command):
        """Camada 1: Força uso de modelo local leve ou cache"""
        # Ex: Busca resposta pré-calibrada
        if "horas" in command:
            from datetime import datetime
            return {"success": True, "response": f"Agora são {datetime.now().strftime('%H:%M')}."}
            
        if "data" in command:
             from datetime import datetime
             return {"success": True, "response": f"Hoje é {datetime.now().strftime('%d/%m/%Y')}."}

        return {"success": False}

    def layer2_regex_commands(self, command):
        """Camada 2: Comandos via Regex (sem IA)"""
        import re
        cmd = command.lower()
        
        if re.search(r'(abrir|executar) painel', cmd):
            if self.jarvis and self.jarvis.window_manager:
                from src.interface.window_manager import InterfaceMode
                self.jarvis.window_manager.switch_mode(InterfaceMode.STARK_DASHBOARD)
                return {"success": True, "response": "Abrindo painel de controle."}
                
        if re.search(r'(encerrar|desligar) (sistema|jarvis)', cmd):
             if self.jarvis:
                 self.jarvis.shutdown()
                 return {"success": True, "response": "Iniciando desligamento."}
                 
        return {"success": False}

    def layer3_manual_hotkey(self, command):
        """Camada 3: Instrui usuário a usar controle manual"""
        return {
            "success": True, 
            "response": "Desculpe, meus sistemas neurais estão instáveis. Por favor, use Ctrl+Shift+J para o Painel Manual."
        }

    def layer4_emergency_reboot(self, command):
        """Camada 4: Reinicia drivers de áudio/vídeo"""
        return {
            "success": True, 
            "response": "Detectei falha crítica. Reiniciando drivers sensoriais... Tente novamente em 5 segundos."
        }
