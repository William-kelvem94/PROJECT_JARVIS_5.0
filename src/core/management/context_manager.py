"""
JARVIS 5.0 - Context Manager
===========================
Responsabilidade: Gerenciar estados globais como Modo Noturno, Politeness Logic
e Modos de Operação (Foco, Pesquisa, etc).
"""

import logging
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ContextManager:
    """Singleton para gerenciar contexto comportamental do JARVIS"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.night_mode = False
        self.focus_mode = False
        self.politeness_enabled = True
        self.current_protocol = "Singularity"
        self.last_interaction = datetime.datetime.now()
        
        # 🧠 DINÂMICA INTERPESSOAL (Aprendizado Adaptativo)
        self.user_preferences = {
            "proactivity": 0.5, # 0 (espera) a 1 (inicia conversas)
            "tone": "professional_warm", # humor preferido
            "interruption_tolerance": 0.8
        }
        self.bond_level = 50 # 0 a 100 (nível de sintonia com o usuário)
        self.interaction_history = [] 
        
        # 👤 IDENTIDADE E WORKSPACE
        self.current_user = "William" # Default Master
        self.current_role = "master"
        self.workspace_path = Path("data/users/william/workspace")
        self.authorized_people = ["William"]
        
        from src.core.management.user_manager import user_manager
        self._refresh_authorized_list(user_manager)
        
        logger.info(f"✅ ContextManager inicializado. Usuário Ativo: {self.current_user}")

    def _refresh_authorized_list(self, user_manager):
        self.authorized_people = user_manager.get_all_authorized_names()

    def switch_user(self, name: str):
        """Alterna o contexto de workspace e permissões para o novo usuário detectado"""
        from src.core.management.user_manager import user_manager
        user = user_manager.get_user(name)
        if user:
            self.current_user = user["name"]
            self.current_role = user["role"]
            self.workspace_path = Path(user["dirs"]["workspace"])
            self.workspace_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"🔄 Workspace alternado para: {self.current_user} ({self.current_role})")
            return True
        return False

    def record_interaction(self, sentiment: str, was_helpful: bool):
        """Estuda o usuário durante o uso para adaptar o comportamento"""
        if was_helpful:
            self.bond_level = min(100, self.bond_level + 1)
        else:
            self.bond_level = max(0, self.bond_level - 2)
            
        # Ajusta proatividade se o usuário for muito responsivo
        if sentiment == "positive":
            self.user_preferences["proactivity"] = min(1.0, self.user_preferences["proactivity"] + 0.05)
        
        logger.debug(f"📈 Bond Level: {self.bond_level} | Proactivity: {self.user_preferences['proactivity']:.2f}")

    def should_initiate_conversation(self) -> bool:
        """Decide se o JARVIS deve 'puxar assunto' baseado na afinidade e proatividade"""
        import random
        # Só inicia se o vínculo for alto e o humor do sistema permitir
        threshold = 1.0 - self.user_preferences["proactivity"]
        return random.random() > threshold and self.bond_level > 30

    def is_night_time(self) -> bool:
        """Verifica se é horário de silêncio (ex: 22h - 07h)"""
        now = datetime.datetime.now().hour
        return now >= 22 or now < 7

    def should_be_quiet(self) -> bool:
        """Decide se o JARVIS deve falar baixo ou apenas em texto"""
        return self.night_mode or self.is_night_time() or self.focus_mode

    def check_politeness(self) -> bool:
        """
        Verifica se o usuário está ocupado.
        Adaptativo: se o bond for alto, ele pode ser mais 'audacioso' em interromper.
        """
        if not self.politeness_enabled:
            return True
            
        # Se estivermos em alto vínculo, o JARVIS entende que tem 'liberdade'
        if self.bond_level > 80:
            return True
            
        return True 

    def update_protocol(self, protocol_name: str):
        """Muda o protocolo de operação e personalidade"""
        self.current_protocol = protocol_name
        logger.info(f"🔄 Protocolo alterado para: {protocol_name}")

context_manager = ContextManager()
