"""
Senses - Action Dispatcher
Large Action Model - Tenta múltiplas estratégias
"""

import logging
from typing import Optional, Dict
import asyncio

logger = logging.getLogger(__name__)

class ActionDispatcher:
    """Dispatcher de ações com fallback"""
    
    def __init__(self):
        # Importar módulos
        try:
            from jarvis_core.senses.ui_automation import neural_touch
            self.ui_automation = neural_touch
        except:
            self.ui_automation = None
            logger.warning("⚠️ UI Automation não disponível")
        
        # Estatísticas
        self.stats = {
            "ui_automation_success": 0,
            "ui_automation_fail": 0,
            "fallback_used": 0
        }
    
    async def execute(self, command: str, context: Optional[Dict] = None) -> bool:
        """Executa comando com múltiplas estratégias"""
        context = context or {}
        
        logger.info(f"🎯 Executando: {command}")
        
        # Estratégia 1: UI Automation
        if await self._try_ui_automation(command, context):
            self.stats["ui_automation_success"] += 1
            return True
        
        # Estratégia 2: Fallback para código legado
        if await self._try_legacy_action(command, context):
            self.stats["fallback_used"] += 1
            return True
        
        # Estratégia 3: Pedir ajuda ao usuário
        logger.warning(f"⚠️ Não consegui executar: {command}")
        self.stats["ui_automation_fail"] += 1
        return False
    
    async def _try_ui_automation(self, command: str, context: Dict) -> bool:
        """Tenta UI Automation"""
        if not self.ui_automation:
            return False
        
        try:
            # Parsear comando
            # Exemplo: "clica no botão Play do Spotify"
            if "clica" in command.lower():
                parts = command.lower().split()
                
                # Extrair app e elemento
                if "do" in parts:
                    do_index = parts.index("do")
                    app_name = parts[do_index + 1]
                    
                    # Encontrar nome do elemento
                    if "botão" in parts:
                        botao_index = parts.index("botão")
                        element_name = parts[botao_index + 1]
                        
                        # Executar
                        return self.ui_automation.click_element(
                            app_name.capitalize(),
                            element_name.capitalize(),
                            "button"
                        )
            
            return False
        except Exception as e:
            logger.error(f"❌ Erro UI Automation: {e}")
            return False
    
    async def _try_legacy_action(self, command: str, context: Dict) -> bool:
        """Fallback para sistema legado"""
        try:
            # Importar action controller legado
            import sys
            from pathlib import Path
            
            legacy_path = Path("jarvis_core/legacy_src/core")
            if legacy_path.exists():
                sys.path.insert(0, str(legacy_path.parent))
                
                from core.action_controller import action_controller
                
                # Tentar executar
                # (Isso depende da implementação do action_controller)
                logger.info("🔄 Usando sistema legado...")
                return False  # Por enquanto
        except Exception as e:
            logger.error(f"❌ Erro fallback: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas"""
        return self.stats


# Instância global
action_dispatcher = ActionDispatcher()
