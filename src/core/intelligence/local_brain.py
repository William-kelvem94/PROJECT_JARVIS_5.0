"""
CÃ©rebro Local do Jarvis 5.0 (Local Brain)
Implementa um modelo de linguagem reduzido (Micro-LLM) rodando nativamente.
Fase 5: ModernizaÃ§Ã£o Definitiva via Optimum-Intel.
"""

import logging
import os
import threading
from typing import List, Dict, Optional, Callable

# ðŸ›¡ï¸ MONKEY PATCH: CorreÃ§Ã£o CrÃ­tica para OpenVINO/Optimum-Intel
try:
    import sys
    import openvino
    # openvino.runtime is deprecated in favor of openvino
    # openvino.runtime is deprecated in favor of openvino
    node_obj = getattr(openvino, 'Node', None)
    if not node_obj and 'openvino.runtime' in sys.modules:
        node_obj = getattr(sys.modules['openvino.runtime'], 'Node', None)
        
    if node_obj:
        if not hasattr(openvino, 'Node'): openvino.Node = node_obj
    
    op_obj = getattr(openvino, 'op', None)
    if not op_obj and 'openvino.runtime' in sys.modules:
        op_obj = getattr(sys.modules['openvino.runtime'], 'op', None)
        
    if op_obj:
        sys.modules['openvino.op'] = op_obj
        if not hasattr(openvino, 'op'): openvino.op = op_obj
except Exception:
    pass

from src.utils.stability import model_load_lock

# ConfiguraÃ§Ã£o de Logs
logger = logging.getLogger(__name__)

# DependÃªncias CrÃ­ticas
try:
    import torch
    TORCH_AVAILABLE = True
except (ImportError, OSError):
    TORCH_AVAILABLE = False
    torch = None

# OpenVINO - Import adiado para evitar problemas de inicialização
OPENVINO_AVAILABLE = False
OVModelForCausalLM = None

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class LocalBrain:
    """CÃ©rebro local HÃ­brido especializado em aceleraÃ§Ã£o Intel (GPU/OpenVINO)"""
    
    def __init__(self, model_id: str = "Qwen/Qwen2.5-1.5B-Instruct"):
        from src.utils.config import config
        self.model_id = config.get_ai_config('local_brain.model_path', model_id)
        self.model = None
        self.tokenizer = None
        self.device = "CPU"
        self.provider_name = "unknown"
        self._is_loaded = False
        self._is_loading = False
        self._load_lock = threading.Lock()
        self._load_event = threading.Event()
        
        # KV Cache Persistence
        self.past_key_values = None
        
        # Autoload
        autoload = config.get_ai_config('local_brain.autoload', True)
        if autoload:
            self.load_async()

    def load_async(self):
        if self._is_loaded or self._is_loading:
            return
        self._is_loading = True
        threading.Thread(target=self._load_model_background, daemon=True, name="Stark-Neural-Loader").start()

    def _load_model_background(self):
        try:
            with self._load_lock:
                if self._is_loaded: return
                
                # Trava de SeguranÃ§a Stark
                model_load_lock.acquire(f"LocalBrain ({self.model_id})")
                logger.info(f"ðŸ§  [LOCAL BRAIN] Iniciando motor neural: {self.model_id}")
                
                # 1. Carregar Tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=True)
                
                # 2. Tentar AceleraÃ§Ã£o OpenVINO (Optimum Intel) com Cache Inteligente
                if OPENVINO_AVAILABLE and os.environ.get("JARVIS_DISABLE_OPENVINO") != "1":
                    cache_dir = "data/models/ov_cache"
                    os.makedirs(cache_dir, exist_ok=True)
                    
                    try:
                        logger.info("âš¡ Tentando AceleraÃ§Ã£o OpenVINO via GPU Intel...")
                        self.model = OVModelForCausalLM.from_pretrained(
                            self.model_id,
                            export=True,
                            device="GPU", 
                            compile=False,  # Evita recompilaÃ§Ã£o desnecessÃ¡ria
                            trust_remote_code=True,
                            ov_config={
                                "PERFORMANCE_HINT": "LATENCY",
                                "CACHE_DIR": cache_dir,
                                "INFERENCE_PRECISION_HINT": "f16"  # Melhor performance
                            }
                        )
                        self.device = "GPU"
                        self.provider_name = "OpenVINO (GPU)"
                        logger.info("âœ… AceleraÃ§Ã£o OpenVINO Ativa (GPU)")
                    except Exception as e:
                        logger.warning(f"âš ï¸ GPU indisponÃ­vel ou falhou ({e}). Tentando OpenVINO CPU...")
                        try:
                            self.model = OVModelForCausalLM.from_pretrained(
                                self.model_id,
                                export=True,
                                device="CPU",
                                compile=False,  # Evita recompilaÃ§Ã£o
                                trust_remote_code=True,
                                ov_config={
                                    "PERFORMANCE_HINT": "THROUGHPUT",
                                    "CACHE_DIR": cache_dir
                                }
                            )
                            self.device = "CPU"
                            self.provider_name = "OpenVINO (CPU)"
                            logger.info("âœ… AceleraÃ§Ã£o OpenVINO Ativa (CPU)")
                        except Exception as e2:
                            logger.error(f"âŒ Falha total no OpenVINO: {e2}. Ativando fallback PyTorch.")
                            self.model = None

                # 3. Fallback PyTorch Nativo (Se OpenVINO falhou ou indisponÃ­vel)
                if self.model is None:
                    logger.info("ðŸ  Usando motor PyTorch Nativo (CPU)...")
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_id,
                        dtype=torch.float32 if torch else None,
                        trust_remote_code=True
                    )
                    self.device = "CPU"
                    self.provider_name = "PyTorch (Native)"

                self._is_loaded = True
                self._is_loading = False
                self._load_event.set()
                logger.info(f"ðŸ’Ž CÃ©rebro Local PRONTO: {self.provider_name}")
                
        except Exception as e:
            self._is_loading = False
            logger.error(f"âš ï¸ Falha catastrÃ³fica no LocalBrain: {e}")
        finally:
            model_load_lock.release()

    def generate_response(self, prompt: str, system_prompt: str = "", max_new_tokens: int = 128) -> str:
        if not self._is_loaded:
            if not self._is_loading: self.load_async()
            if not self._load_event.wait(timeout=60):
                return "CÃ©rebro local ainda estÃ¡ inicializando, Senhor."

        try:
            # Prepara conversa
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            response = self.tokenizer.decode(output[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            return response.strip()

        except Exception as e:
            logger.error(f"Erro na geraÃ§Ã£o neural: {e}")
            return f"Erro no processamento neural: {e}"

    def wait_for_load(self, timeout: float = 30.0):
        return self._load_event.wait(timeout)

# InstÃ¢ncia global
local_brain = LocalBrain()
