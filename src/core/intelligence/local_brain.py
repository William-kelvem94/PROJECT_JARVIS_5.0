"""
Cérebro Local do Jarvis 5.0 (Local Brain)
Implementa um modelo de linguagem reduzido (Micro-LLM) rodando nativamente via Transformers.
Isso remove a dependência 100% externa do Ollama/Gemini para comandos básicos.
"""

import logging
import os
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

from src.core.management.compute_orchestrator import compute_orchestrator

logger = logging.getLogger(__name__)

import threading
import asyncio
from typing import Optional, Callable
from src.utils.stability import model_load_lock

class LocalBrain:
    """Cérebro local Híbrido (CPU + iGPU + GPU)"""
    
    def __init__(self, model_id: str = "Qwen/Qwen2.5-1.5B-Instruct"):
        from src.utils.config import config
        # Preferir model_path do config se existir
        self.model_id = config.get_ai_config('local_brain.model_path', model_id)
        self.model = None
        self.tokenizer = None
        self.ov_config = None
        
        self._is_loaded = False
        self._is_loading = False
        self._load_lock = threading.Lock()
        self._load_event = threading.Event()
        
        # KV Cache Persistence
        self.past_key_values = None
        
        # Verificar se deve dar autoload
        autoload = config.get_ai_config('local_brain.autoload', True)
        logger.info(f"🧠 Cérebro Local Híbrido configurado: {self.model_id} (Autoload: {autoload})")
        
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
        try:
            with self._load_lock:
                if self._is_loaded:
                    return
                
                # Adquirir trava de segurança global
                model_load_lock.acquire(f"LocalBrain ({self.model_id})")
                
                provider = compute_orchestrator.get_best_provider()
                logger.info(f"🧠 LocalBrain: Iniciando motor híbrido via {provider['name']}...")
                
                # Tokenizer
                from transformers import AutoTokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)

                if provider['backend'] == 'openvino' and os.environ.get("JARVIS_DISABLE_OPENVINO") != "1":
                    try:
                        from optimum.intel.openvino import OVModelForCausalLM
                        
                        # Configuração Real de Distribuição de Carga
                        self.ov_config = {
                            "PERFORMANCE_HINT": "LATENCY",
                            "CACHE_DIR": "data/models/ov_cache"
                        }
                        
                        logger.info(f"📦 Carregando modelo na iGPU + Fallback CPU (OpenVINO)...")
                        self.model = OVModelForCausalLM.from_pretrained(
                            self.model_id,
                            export=True, # Exporta para OpenVINO no primeiro boot
                            device=compute_orchestrator.get_execution_strategy(), # 'HETERO:GPU,CPU'
                            ov_config=self.ov_config,
                            compile=True
                        )
                    except Exception as ov_error:
                        logger.info(f"ℹ️ OpenVINO não disponível ({ov_error}). Usando PyTorch Standard (CPU).")
                        # Fallback seguro para PyTorch
                        from transformers import AutoModelForCausalLM
                        self.model = AutoModelForCausalLM.from_pretrained(
                            self.model_id,
                            torch_dtype=torch.float32,
                            device_map=None,
                            low_cpu_mem_usage=True,
                            trust_remote_code=True,
                            use_safetensors=True
                        )
                        # Forçar provider para CPU para evitar erros futuros
                        provider['device'] = 'cpu'
                else:
                    # Fallback Torch (CPU ou NVIDIA)
                    from transformers import AutoModelForCausalLM
                    compute_type = "float16" if provider['device'] == 'cuda' else "float32"
                    
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_id,
                        torch_dtype=getattr(torch, compute_type),
                        device_map="auto" if provider['device'] == 'cuda' else None,
                        low_cpu_mem_usage=True,
                        trust_remote_code=True,
                        use_safetensors=True
                    )
                    if provider['device'] != 'cuda':
                        self.model.to(provider['device'])
                
                self._is_loaded = True
                self._is_loading = False
                self._load_event.set()
                logger.info(f"✅ Cérebro Local Híbrido PRONTO ({provider['name']})")
                
        except Exception as e:
            self._is_loading = False
            logger.error(f"❌ Erro crítico no motor híbrido: {e}")
        finally:
            # Liberar trava de segurança global
            model_load_lock.release()
    
    def wait_for_load(self, timeout: float = 30.0) -> bool:
        """Espera o carregamento completar"""
        return self._load_event.wait(timeout)
    
    def unload(self):
        """Descarrega o modelo da memória para liberar recursos"""
        if not self._is_loaded:
            return
            
        logger.info(f"🧠 LocalBrain: Descarregando modelo {self.model_id}...")
        try:
            with self._load_lock:
                self.model = None
                self.tokenizer = None
                self.past_key_values = None
                self._is_loaded = False
                if torch and torch.cuda.is_available():
                    torch.cuda.empty_cache()
            logger.info("✅ Memória liberada com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao descarregar modelo: {e}")

    def generate_response(self, prompt: str, system_prompt: str = "", 
                          max_new_tokens: int = 128, use_cache: bool = True) -> str:
        """Gera resposta com suporte opcional a KV Cache"""
        
        if not self._is_loaded:
            if not self._is_loading:
                self.load_async()
            if not self.wait_for_load(timeout=60):
                return f"⚠️ Erro: Cérebro Local não carregou a tempo ({self.model_id}). Verifique logs."

        # TENTATIVA 1: Geração Normal com Cache
        try:
            return self._generate_internal(prompt, system_prompt, max_new_tokens, use_cache=True)
        except Exception as e:
            logger.warning(f"⚠️ Falha na geração com cache (Tentativa 1): {e}")
            
            # TENTATIVA 2: Limpeza de Memória + Sem Cache
            try:
                self._clear_memory()
                return self._generate_internal(prompt, system_prompt, max_new_tokens, use_cache=False)
            except Exception as e2:
                logger.error(f"❌ Falha crítica no Cérebro Local (Tentativa 2): {e2}")
                return f"❌ Falha crítica no processamento neural local: {e2}. Tentando transição para subsistemas..."

    def _clear_memory(self):
        """Força limpeza de VRAM/RAM"""
        self.past_key_values = None
        if torch:
            import gc
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def _generate_internal(self, prompt: str, system_prompt: str, max_new_tokens: int, use_cache: bool) -> str:
        """Lógica interna de geração"""
        # Preparar inputs
        inputs = self._prepare_inputs(prompt, system_prompt, use_cache)
        
        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                use_cache=use_cache,
                past_key_values=self.past_key_values if use_cache else None,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
                return_dict_in_generate=True
            )
        
        if use_cache:
            self.past_key_values = output.past_key_values
        
        input_len = inputs.input_ids.shape[1]
        response_ids = output.sequences[0][input_len:]
        response = self.tokenizer.decode(response_ids, skip_special_tokens=True)
        return response.strip()

    def _prepare_inputs(self, prompt: str, system_prompt: str, use_cache: bool):
        """Prepara tokens com ou sem histórico"""
        if self.past_key_values is None or not use_cache:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        else:
            messages = [{"role": "user", "content": prompt}]
            
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        return self.tokenizer(text, return_tensors="pt").to(self.model.device)

    def generate_stream(self, prompt: str, system_prompt: str = "", max_new_tokens: int = 128):
        """Gera resposta em streaming (yield chunks)"""
        # Lógica de streaming simplificada sem retry complexo por enquanto
        if not self._is_loaded:
             self.load_async()
             if not self.wait_for_load(timeout=60):
                 yield "Estou carregando meus módulos neurais..."
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
