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
        from src.utils.config import config
        # 🆕 Preferir model_path do config se existir
        self.model_id = config.get_ai_config('local_brain.model_path', model_id)
        self.model = None
        self.tokenizer = None
        self.pipe = None
        
        self._is_loaded = False
        self._is_loading = False
        self._load_lock = threading.Lock()
        self._load_event = threading.Event()
        
        # 🆕 KV Cache Persistence (Fase 5)
        self.past_key_values = None
        self.last_context_tokens = None
        
        # 🆕 Verificar se deve dar autoload
        autoload = config.get_ai_config('local_brain.autoload', True)
        logger.info(f"🧠 Cérebro Local configurado: {self.model_id} (Autoload: {autoload})")
        
        if autoload:
            self.load_async()
    
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
                tier = hardware_manager.get_tier()
                compute_type = hardware_manager.get_compute_type()
                
                logger.info(f"Carregando {self.model_id} - Tier: {tier} | Device: {device}...")
                
                # Tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
                
                # Modelo (Quantizado para Máxima Velocidade)
                quantization_config = None
                try:
                    # Somente ULTRA (CUDA) se beneficia massivamente de 4-bit no carregamento
                    if tier == "ULTRA":
                        from transformers import BitsAndBytesConfig
                        quantization_config = BitsAndBytesConfig(
                            load_in_4bit=True,
                            bnb_4bit_compute_dtype=torch.float16,
                            bnb_4bit_quant_type="nf4",
                            bnb_4bit_use_double_quant=True
                        )
                        logger.info("📦 Aceleração Nuclear: 4-bit Ativo via CUDA")
                except ImportError:
                    logger.warning("⚠️ bitsandbytes não disponível.")

                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    torch_dtype=getattr(torch, compute_type),
                    device_map="auto" if tier == "ULTRA" else None,
                    quantization_config=quantization_config,
                    low_cpu_mem_usage=True,
                    trust_remote_code=True,
                    use_safetensors=True  # Usar safetensors se disponível
                )
                
                # Somente mover para CPU se não estiver usando device_map="auto"
                if tier != "ULTRA":
                    self.model.to(device)
                
                # Pipeline  
                self.pipe = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=device if tier != "ULTRA" else None
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
                          max_new_tokens: int = 128, use_cache: bool = True) -> str:
        """Gera resposta com suporte opcional a KV Cache"""
        
        if not self._is_loaded:
            if not self._is_loading:
                self.load_async()
            if not self.wait_for_load(timeout=60):
                return "William, estou carregando meu cérebro local..."

        try:
            # 1. Preparar mensagens
            if self.past_key_values is None or not use_cache:
                # Primeiro turno ou cache desabilitado: incluir system prompt
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
                text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
                self.past_key_values = None # Reset
            else:
                # Turno subsequente: Concatenar apenas o novo prompt
                messages = [{"role": "user", "content": prompt}]
                text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                # O tokenizer chat template costuma adicionar o início do chat, 
                # precisamos apenas da parte nova se o modelo for stateful.
                # Para simplificar na Fase 5, vamos usar o re-feed otimizado:
                inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    past_key_values=self.past_key_values,
                    use_cache=True,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                    return_dict_in_generate=True
                )
            
            # Atualizar Cache para o próximo turno
            if use_cache:
                self.past_key_values = output.past_key_values
            
            # Decodificar apenas a parte nova
            input_len = inputs.input_ids.shape[1]
            response_ids = output.sequences[0][input_len:]
            response = self.tokenizer.decode(response_ids, skip_special_tokens=True)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Erro na geração local com cache: {e}")
            self.past_key_values = None # Reset cache em erro
            return f"Falha no processamento: {e}"

    def generate_stream(self, prompt: str, system_prompt: str = "", max_new_tokens: int = 128):
        """Gera resposta em streaming (yield chunks)"""
        if not self._is_loaded:
            # 🔥 Iniciar carregamento se não estiver rodando
            if not self._is_loading:
                logger.warning("⚠️ LocalBrain não carregado! Iniciando carregamento...")
                self.load_async()
            
            # 🔥 TIMEOUT AUMENTADO: 10s → 60s (modelo demora para carregar)
            yield "William, estou carregando meu cérebro local..."
            if not self.wait_for_load(timeout=60):
                logger.error("❌ LocalBrain: Timeout no carregamento (60s)")
                yield "Desculpe, meu cérebro local não respondeu a tempo. Tente novamente em alguns segundos."
                return

        try:
            from transformers import TextIteratorStreamer
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            
            streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
            
            generation_kwargs = dict(
                model_inputs,
                streamer=streamer,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Start generation in thread
            thread = threading.Thread(target=self.model.generate, kwargs=generation_kwargs)
            thread.start()
            
            # Yield chunks
            for new_text in streamer:
                if new_text:
                    yield new_text
                    
        except Exception as e:
            logger.error(f"Erro no streaming local: {e}")
            yield f"Erro no processamento: {e}"

# Instância global
local_brain = LocalBrain()
