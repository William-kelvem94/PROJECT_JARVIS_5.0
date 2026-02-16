import os
import re

file_path = r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\src\core\intelligence\ai_agent.py'

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 1. Update imports
new_imports = "from src.core.intelligence.agent import AgentPromptManager, AgentEngagementManager\n\nclass AIAgent:"
content = content.replace("class AIAgent:", new_imports)

# 2. Refactor __init__
# We'll use a regex to find the __init__ and replace everything up to the first method
init_pattern = re.compile(r'def __init__\(self, provider: str = \'ollama\'\):.*?def ', re.DOTALL)

new_init = '''def __init__(self, provider: str = 'ollama'):
        """JARVIS 5.0 Intelligence Center"""
        # =====================================================================
        # 🧩 MODULAR MANAGERS (Refactored)
        # =====================================================================
        self.prompt_manager = AgentPromptManager()
        self.engagement_manager = AgentEngagementManager(self)
        
        # =====================================================================
        # 🛠️ AUTO-RECOVERY INTEGRATION (Unified)
        # =====================================================================
        self.auto_recovery = None
        self._initialize_auto_recovery()

        # =====================================================================
        # CORREÇÃO P0: VERIFICAÇÃO DE DEPENDÊNCIAS CRÍTICAS
        # =====================================================================
        self.safe_mode = False
        self._verify_critical_dependencies()
        
        self.provider = provider
        self.api_key = None # 100% Local Mode
        
        # Carregar URL do Ollama do env_manager
        try:
            from src.utils.env_manager import get_config
            config_obj = get_config()
            self.ollama_url = config_obj.ollama_url + "/api/generate" if config_obj else "http://localhost:11434/api/generate"
        except ImportError:
            self.ollama_url = "http://localhost:11434/api/generate"
        
        # Carregar configurações de IA
        try:
            from src.utils.config import config
            self.ai_config = config.get_ai_config()
            self.max_react_turns = config.get_ai_config('ai_agent.max_react_turns', 5)
            self.screenshot_timeout = config.get_ai_config('ai_agent.screenshot_timeout', 5.0)
            logger.info("✅ Configurações de IA carregadas")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar ai_config, usando defaults: {e}")
            self.ai_config = {}
            self.max_react_turns = 5
            self.screenshot_timeout = 5.0
        
        # Histórico de conversação
        self.chat_history = []
        
        # Brain Router - Sistema de Decisão Inteligente
        try:
            from src.core.intelligence.brain_router import brain_router
            self.brain_router = brain_router
            
            # 🎭 FASE 2: Conectar UX Masking
            if self.brain_router:
                self.brain_router.on_heavy_model_loading = self._on_heavy_model_loading
            logger.info("✅ Brain Router inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Brain Router não disponível: {e}")
            self.brain_router = None
        
        # Advanced Controllers
        self.advanced_actions = advanced_action_controller if ADVANCED_ACTIONS_AVAILABLE else None
        self.advanced_vision = advanced_vision_pipeline if ADVANCED_VISION_AVAILABLE else None
        self.advanced_speech = advanced_speech_processor if ADVANCED_SPEECH_AVAILABLE else None
        self.workflow_engine = workflow_engine if WORKFLOW_ENGINE_AVAILABLE else None
        self.security_advanced = security_manager_advanced if ADVANCED_SECURITY_AVAILABLE else None
        
        # Sync system prompt from manager
        self.use_structured_output = STRUCTURE_OUTPUT_AVAILABLE
        self.system_prompt = self.prompt_manager.get_system_prompt(self.use_structured_output)

    def get_security_manager(self):'''

content = init_pattern.sub(new_init, content, count=1)

# 3. Remove _get_dynamic_identity_prompt if it still exists
content = re.sub(r'def _get_dynamic_identity_prompt\(self\).*?return \(.*?\)\s*', '', content, flags=re.DOTALL)

# 4. Cleanup redundant observation methods if still there
content = re.sub(r'def _handle_contextual_observation\(self, current_intent: str\).*?memory_manager\.store_experience\("surveillance_event", results\)\s*', '', content, flags=re.DOTALL)
content = re.sub(r'def _generate_discreet_response\(self, core_message: str\).*?return discreet_versions\.get\(core_message, "Há uma nova atualização no sistema\."\)\s*', '', content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("AIAgent refactored successfully via script.")
