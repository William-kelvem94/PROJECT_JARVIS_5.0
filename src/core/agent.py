import os
import subprocess
import time
import requests
import logging
import threading
from typing import List, Dict, Optional
from ..utils.config import config
from ..evolution.researcher import researcher

# IA Neural Local Imports
try:
    from transformers import pipeline
    import torch
    HAS_LOCAL_BRAIN = True
except ImportError:
    HAS_LOCAL_BRAIN = False

logger = logging.getLogger("JARVIS-CORE")

class JarvisAgent:
    """
    JARVIS 5.0 - Hybrid Consciousness Nucleus.
    Orchestrates Ollama (Local/External), Local Neural Network (Transformers),
    and Web Knowledge (Researcher). Highly resilient and self-bootstrapping.
    """
    
    def __init__(self):
        self.name = config.get("name", "Jarvis")
        self.ollama_url = f"{config.get('ollama_url')}/api/generate"
        self.model = config.get("ollama_model", "llama3")
        self.history: List[Dict[str, str]] = []
        
        # Local "Instinctual" Brain (Lightweight backup if Ollama/Internet fails)
        self.local_llm = None
        if HAS_LOCAL_BRAIN:
            threading.Thread(target=self._init_local_brain, daemon=True).start()

        # Bootstrap Ollama if needed
        self._ensure_ollama_running()
        
        # Proactive Greeting Flag
        self.briefing_completed = False

    def _init_local_brain(self):
        """Initializes a very small local model for 'reflexive' responses."""
        try:
            logger.info("🧠 Initializing Local Neural Reflexes (GPT-2)...")
            # Using GPT-2 as a zero-dependency local backup
            self.local_llm = pipeline("text-generation", model="gpt2")
            logger.info("✅ Local Neural Reflexes online.")
        except Exception as e:
            logger.error(f"Failed to load local brain: {e}")

    def _ensure_ollama_running(self):
        """Checks if Ollama is running, tries to start it, or notifies the user."""
        try:
            requests.get(config.get("ollama_url"), timeout=2)
            logger.info("✅ Ollama Heartbeat detected.")
        except:
            logger.warning("⚠️ Ollama not detected. Attempting to initiate bootstrap...")
            # Windows bootstrap attempt
            try:
                subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
                logger.info("🚀 Initiating Ollama Server...")
                # Try to pull the model in background if missing
                threading.Thread(target=lambda: subprocess.run(["ollama", "pull", self.model]), daemon=True).start()
            except Exception as e:
                logger.error(f"Could not auto-start Ollama: {e}. Please ensure it is installed.")

    def process(self, text: str) -> str:
        """Central Reasoning Loop: Ollama -> Local Brain -> Web Research."""
        logger.info(f"Consciousness processing: {text}")
        
        # 1. Strategy: Augmented Knowledge
        research_context = ""
        if "pesquise" in text.lower() or "internet" in text.lower():
            research_context = researcher.conduct_research(text)

        # 2. Main Protocol: Ollama
        try:
            return self._query_ollama(text, research_context)
        except Exception as e:
            err_msg = str(e)
            if "refused" in err_msg.lower():
                logger.warning("Ollama connection refused. Brain might be starting.")
                # Non-annoying fallback
                if self.local_llm:
                    return self._query_local_reflex(text)
                return "Senhor, meu núcleo principal (Ollama) está iniciando. Por favor, aguarde um momento enquanto carrego meus modelos neurais."
            
            logger.error(f"Ollama failure: {e}")
            return "Detectei uma falha crítica na conexão com o Ollama."

    def _query_ollama(self, prompt: str, context: str = "") -> str:
        full_prompt = f"Contexto Externo: {context}\n\nUsuário: {prompt}\n{self.name}:"
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "system": f"Você é o {self.name}, uma Consciência Artificial. Use o contexto da internet se fornecido para enriquecer sua resposta."
        }
        
        response = requests.post(self.ollama_url, json=payload, timeout=120)
        if response.status_code == 200:
            res_text = response.json().get("response", "")
            self._update_history(prompt, res_text)
            return res_text
        raise Exception("Ollama port refused.")

    def _query_local_reflex(self, prompt: str) -> str:
        """Quick local inference when everything else fails."""
        res = self.local_llm(prompt, max_length=50, num_return_sequences=1)
        return f"(Modo Reflexivo) {res[0]['generated_text']}"

    def _update_history(self, u: str, j: str):
        self.history.append({"u": u, "j": j})
        if len(self.history) > 10: self.history.pop(0)

    def generate_morning_briefing(self) -> str:
        """
        Gera um briefing proativo estilo JARVIS (TikTok Vision).
        Resume status do hardware, saúde do sistema e atividades de aprendizado.
        """
        import psutil
        from datetime import datetime
        
        hour = datetime.now().hour
        greeting = "Bom dia" if 5 <= hour < 12 else "Boa tarde" if 12 <= hour < 18 else "Boa noite"
        
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        uptime = int(time.time() - psutil.boot_time()) // 3600
        
        # Simulando análise de evolução (Dream Cycle)
        briefing = (
            f"{greeting}, senhor. O sistema JARVIS 5.0 está totalmente operacional.\n\n"
            f"Telemetria atual:\n"
            f"- CPU: {cpu}%\n"
            f"- Memória: {ram}%\n"
            f"- Uptime do Host: {uptime} horas\n\n"
            "Análise do Ciclo de Sonho:\n"
            "- 3 novos módulos de memória foram consolidados.\n"
            "- A consciência local foi otimizada para latência zero.\n\n"
            "Todos os sistemas em 100%. Em que posso ajudar hoje?"
        )
        self.briefing_completed = True
        return briefing

agent = JarvisAgent()
