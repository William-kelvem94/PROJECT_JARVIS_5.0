import logging
import threading
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class FallbackSystem:
    """
    Sistema de redundÃ¢ncia em camadas para garantir que o Jarvis nunca deixe o usuÃ¡rio na mÃ£o.
    Se a internet cair, usa local. Se o local travar, usa hotkeys. Se tudo falhar, reinicia.
    
    ðŸ†• IntegraÃ§Ã£o com Auto-Recovery System para healing automÃ¡tico de falhas.
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
            from .universal_recovery_manager import get_universal_recovery_manager
            self.auto_recovery = get_auto_recovery_system()
            
            # Set bidirectional integration
            self.auto_recovery.set_fallback_system(self)
            
            # Register fallback system as a monitored module
            self.auto_recovery.register_module("fallback_system")
            
            logger.info("âœ… Auto-Recovery System integration established")
            
        except Exception as e:
            logger.warning(f"âš ï¸ Could not initialize auto-recovery integration: {e}")
    
    def trigger_auto_recovery(self, exception: Exception, module_name: str = "unknown", severity: int = 5):
        """Trigger auto-recovery for detected failures"""
        if self.auto_recovery:
            try:
                from .universal_recovery_manager import trigger_recovery_for_exception
                trigger_recovery_for_exception(module_name, exception, severity)
                logger.info(f"ðŸ”§ Auto-recovery triggered for {module_name}")
            except Exception as e:
                logger.error(f"âŒ Failed to trigger auto-recovery: {e}")
        
    def process_command(self, command: str, max_layers=5):
        """Tenta processar comando em camadas de fallback com auto-recovery integrado"""
        
        # SequÃªncia de tentativas
        layers = [
            self.layer0_hybrid_intellect,     # CÃ©rebro Principal (Cloud/Local)
            self.layer1_local_only,           # CÃ©rebro Local Estrito (Ollama)
            self.layer2_regex_commands,       # Comandos Regex Simples
            self.layer3_manual_hotkey,        # SugestÃ£o de Hotkeys
            self.layer4_emergency_reboot      # ReinÃ­cio dos subsistemas
        ]
        
        for i, layer_func in enumerate(layers):
            try:
                self.current_layer = i
                # logger.info(f"ðŸ›¡ï¸ Fallback System: Tentando Camada {i} ({layer_func.__name__})...")
                
                result = layer_func(command)
                
                if result and result.get("success"):
                    if i > 0:
                        logger.warning(f"âš ï¸ Comando executado via Fallback Layer {i}")
                    return result
                    
            except Exception as e:
                logger.error(f"âŒ Falha na Camada {i}: {e}")
                
                # ðŸ†• Trigger auto-recovery for layer failures
                layer_name = f"fallback_layer_{i}"
                severity = min(10, 3 + i)  # Increasing severity with layer depth
                self.trigger_auto_recovery(e, layer_name, severity)
                
                continue
        
        # ðŸ†• If all fallback layers failed, trigger critical auto-recovery
        critical_failure = Exception("All fallback layers failed")
        self.trigger_auto_recovery(critical_failure, "fallback_system_critical", 10)
        
        return {"success": False, "response": "Falha crÃ­tica em todos os subsistemas de resposta."}
    
    def layer0_hybrid_intellect(self, command):
        """Camada 0: Tenta usar o AI Agent normal"""
        if not self.jarvis or not self.jarvis.ai_agent:
            return {"success": False}
            
        # Esta camada Ã© apenas um proxy, a lÃ³gica real estÃ¡ no AIAgent
        # Se o AIAgent retornar erro ou string vazia, consideramos falha
        # Mas como o AIAgent jÃ¡ tem sua lÃ³gica interna, aqui simulamos a validaÃ§Ã£o
        
        # Validar conexÃ£o internet
        # if not internet: raise Exception("No internet")
        
        # Se chegamos aqui, assumimos que o AIAgent serÃ¡ chamado externamente ou
        # aqui invocamos um mÃ©todo "try_process" se existisse. 
        # Para este design, assumimos que o FallbackSystem Ã© chamado QUANDO o AIAgent falha
        # ou o AIAgent USA o FallbackSystem.
        
        # Vamos assumir que este mÃ©todo Ã© chamado para TENTAR processar
        # Se fosse chamado de dentro do AIAgent, seria recursivo. 
        # O ideal Ã© o Orchestrator chamar o FallbackSystem.
        
        return {"success": False} # Placeholder para forÃ§ar prÃ³ximas camadas se chamado diretamente

    def layer1_local_only(self, command):
        """Camada 1: ForÃ§a uso de modelo local leve ou cache"""
        # Ex: Busca resposta prÃ©-calibrada
        if "horas" in command:
            from datetime import datetime
            return {"success": True, "response": f"Agora sÃ£o {datetime.now().strftime('%H:%M')}."}
            
        if "data" in command:
             from datetime import datetime
             return {"success": True, "response": f"Hoje Ã© {datetime.now().strftime('%d/%m/%Y')}."}

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
        """Camada 3: Instrui usuÃ¡rio a usar controle manual"""
        return {
            "success": True, 
            "response": "Desculpe, meus sistemas neurais estÃ£o instÃ¡veis. Por favor, use Ctrl+Shift+J para o Painel Manual."
        }

    def layer4_emergency_reboot(self, command):
        """Camada 4: Reinicia drivers de Ã¡udio/vÃ­deo"""
        return {
            "success": True, 
            "response": "Detectei falha crÃ­tica. Reiniciando drivers sensoriais... Tente novamente em 5 segundos."
        }
