"""
Cérebro Local do Jarvis 5.0 (Local Brain)
Implementa um modelo de linguagem reduzido (Micro-LLM) rodando nativamente via Transformers.
Isso remove a dependência 100% externa do Ollama/Gemini para comandos básicos.
"""

import logging
import torch
from typing import List, Dict, Optional
from src.core.hardware_manager import hardware_manager

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class LocalBrain:
    """Classe que roda uma LLM local leve diretamente no processo do Jarvis"""

    def __init__(self, model_id: str = "Qwen/Qwen2.5-0.5B-Instruct"):
        self.model_id = model_id
        self.model = None
        self.tokenizer = None
        self.pipe = None
        self.is_loaded = False
        
        if TRANSFORMERS_AVAILABLE:
            logger.info(f"Inicializando Cérebro Local ({model_id})...")
            # Carregamento preguiçoso para não travar o startup da GUI
        else:
            logger.warning("Transformers não instalado. Cérebro Local desativado.")

    def load(self):
        """Carrega o modelo na memória/GPU"""
        if not TRANSFORMERS_AVAILABLE or self.is_loaded: return
        
        try:
            device = hardware_manager.get_device()
            compute_type = torch.float16 if device == "cuda" else torch.float32
            
            logger.info(f"Carregando {self.model_id} em {device}...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=compute_type,
                device_map="auto" if device == "cuda" else None
            )
            
            if device == "cpu":
                self.model.to("cpu")

            self.pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map="auto" if device == "cuda" else None
            )
            
            self.is_loaded = True
            logger.info("Cérebro Local pronto para uso.")
        except Exception as e:
            logger.error(f"Erro ao carregar Cérebro Local: {e}")

    def generate_response(self, prompt: str, system_prompt: str = "", max_new_tokens: int = 128) -> str:
        """Gera resposta localmente"""
        if not self.is_loaded:
            self.load()
            if not self.is_loaded: return "Erro ao carregar cérebro local."

        try:
            # Construir mensagens formatadas
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # Preparar inputs
            text = self.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

            # Gerar sem autocast explícito (deixar o PyTorch/Transformers gerenciar)
            # ou usar torch.no_grad()
            with torch.no_grad():
                generated_ids = self.model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decodificar
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Erro na geração local: {e}")
            return f"Desculpe William, tive uma falha no meu processamento local: {e}"

# Instância global
local_brain = LocalBrain()
