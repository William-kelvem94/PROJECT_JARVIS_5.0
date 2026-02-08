"""
Cérebro Local do Jarvis 5.0 (Local Brain)
Implementa um modelo de linguagem reduzido (Micro-LLM) rodando nativamente via Transformers.
Isso remove a dependência 100% externa do Ollama/Gemini para comandos básicos.
"""

import logging
from typing import List, Dict, Optional

try:
    import torch
    TORCH_AVAILABLE = True
except (ImportError, OSError) as e:
    TORCH_AVAILABLE = False
    torch = None
    logging.warning(f"⚠️ torch not available in local_brain: {e}")

from src.core.management.hardware_manager import hardware_manager

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

import threading
import asyncio
from typing import Optional, Callable

class LocalBrain:
    """Cérebro local com carregamento assíncrono para evitar travar a GUI"""
    
    def __init__(self, model_id: str = "Qwen/Qwen2.5-1.5B-Instruct"):
        self.model_id = model_id
        self.model = None
        self.tokenizer = None
        self.pipe = None
        
        self._is_loaded = False
        self._is_loading = False
        self._load_lock = threading.Lock()
        self._load_event = threading.Event()
        
        logger.info(f"Cérebro Local configurado: {model_id} (lazy loading)")
    
    def load_async(self):
        """Carrega modelo em background thread"""
        if self._is_loaded or self._is_loading:
            return
        
        self._is_loading = True
        thread = threading.Thread(
            target=self._load_model_background,
            daemon=True,
            name="ModelLoader-LocalBrain"
        )
        thread.start()
    
    def _load_model_background(self):
        """Carrega modelo em thread separada"""
        try:
            with self._load_lock:
                if self._is_loaded:
                    return
                
                device = hardware_manager.get_device()
                compute_type = torch.float16 if device == "cuda" else torch.float32
                
                logger.info(f"Carregando {self.model_id} em {device}...")
                
                # Tokenizer (rápido)
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
                
                # Modelo (lento)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    torch_dtype=compute_type,
                    device_map="auto" if device == "cuda" else None,
                    low_cpu_mem_usage=True
                )
                
                if device == "cpu":
                    self.model.to("cpu")
                
                # Pipeline
                self.pipe = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device_map="auto" if device == "cuda" else None
                )
                
                self._is_loaded = True
                self._is_loading = False
                self._load_event.set()
                logger.info("✅ Cérebro Local pronto para uso")
                
        except Exception as e:
            self._is_loading = False
            logger.error(f"❌ Erro ao carregar Cérebro Local: {e}")
    
    def wait_for_load(self, timeout: float = 30.0) -> bool:
        """Espera o carregamento completar"""
        return self._load_event.wait(timeout)
    
    def generate_response(self, prompt: str, system_prompt: str = "", 
                          max_new_tokens: int = 128) -> str:
        """Gera resposta (carrega modelo se necessário)"""
        
        # Carregamento automático se necessário
        if not self._is_loaded:
            if not self._is_loading:
                logger.info("Modelo não carregado. Iniciando carregamento em background...")
                self.load_async()
            
            # Espera carregar (com timeout)
            if not self.wait_for_load(timeout=10):
                return "William, estou carregando meu cérebro local. Por favor, aguarde alguns segundos e tente novamente."
        
        try:
            # Construir mensagens formatadas
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            text = self.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            
            with torch.no_grad():
                generated_ids = self.model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated_ids = [
                output_ids[len(input_ids):] 
                for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Erro na geração local: {e}")
            return f"Desculpe William, tive uma falha no meu processamento local: {e}"

# Instância global
local_brain = LocalBrain()
