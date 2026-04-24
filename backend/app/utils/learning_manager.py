import os
import json
from loguru import logger
from datetime import datetime

class LearningManager:
    """
    O Motor de Evolução do JARVIS.
    Aprende padrões de uso, preferências do usuário e evolui a persona do assistente.
    """
    
    def __init__(self, data_path: str = None):
        from ..config import settings
        self.data_path = data_path or os.path.join(settings.BASE_DIR, "backend", "data", "persona_evolution.json")
        self.profile = {
            "user_name": "William",
            "personality_traits": {
                "technical_level": 0.8, # 0.0 a 1.0
                "conciseness": 0.5,
                "formality": 0.3,
                "sarcasm_level": 0.2
            },
            "known_facts": [],
            "interaction_count": 0,
            "biography_synced": False,
            "last_updated": datetime.now().isoformat()
        }
        self._load_profile()
        self.sync_with_obsidian_personal()

    def _load_profile(self):
        """Carrega o perfil persistido se existir."""
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    self.profile.update(json.load(f))
                logger.info("🧬 Perfil de Persona carregado e pronto para evoluir.")
            except Exception as e:
                logger.error(f"Erro ao carregar persona: {e}")

    def save_profile(self):
        """Salva a evolução atual no disco."""
        try:
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(self.profile, f, indent=4, ensure_ascii=False)
            logger.debug("💾 Evolução de persona salva com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao salvar persona: {e}")

    def learn_from_interaction(self, user_text: str, assistant_text: str):
        """
        Analisa a interação para ajustar traços de personalidade.
        Ex: Se o usuário pede 'seja breve', aumenta o nível de concisão.
        """
        self.profile["interaction_count"] += 1
        
        # Lógica de Aprendizado Simples (Expansível com LLM)
        text_lower = user_text.lower()
        
        if "seja mais técnico" in text_lower:
            self.profile["personality_traits"]["technical_level"] = min(1.0, self.profile["personality_traits"]["technical_level"] + 0.1)
        if "resuma" in text_lower or "seja breve" in text_lower:
            self.profile["personality_traits"]["conciseness"] = min(1.0, self.profile["personality_traits"]["conciseness"] + 0.1)
        
        # Fatos conhecidos (Extração básica)
        if "meu aniversário é" in text_lower:
            self.profile["known_facts"].append(f"Aniversário: {user_text}")

        self.profile["last_updated"] = datetime.now().isoformat()
        self.save_profile()

    def sync_with_obsidian_personal(self):
        """Lê notas da pasta Will-Pessoal para alinhar a persona."""
        from .second_brain_connector import second_brain
        path = os.path.join(second_brain.vault_path, "Will-Pessoal")
        if not os.path.exists(path): return
        
        try:
            logger.info("🧬 Sincronizando biografia pessoal do Obsidian...")
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".md"):
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                            if "preferência" in content or "gosto de" in content:
                                self.profile["known_facts"].append(f"Fato de {file}: Contexto biográfico assimilado.")
            
            self.profile["biography_synced"] = True
            self.save_profile()
        except Exception as e:
            logger.error(f"Erro na sincronização biográfica: {e}")

    def get_persona_instructions(self):
        """Gera as diretrizes de sistema baseadas na evolução da persona."""
        p = self.profile["personality_traits"]
        instr = f"\n[DIRETRIZES DE PERSONA EVOLUÍDA]:\n"
        instr += f"- Nível Técnico: {p['technical_level']:.1f} (Aja como um engenheiro experiente)\n"
        instr += f"- Concisão: {p['conciseness']:.1f}\n"
        if p['technical_level'] > 0.7:
            instr += "- Use jargões técnicos de software e hardware quando apropriado.\n"
        
        return instr

# Singleton
learning_manager = LearningManager()
