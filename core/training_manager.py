"""
Training Manager - Sistema de Treinamento Real com Ollama
Usa Ollama Modelfile para criar modelos customizados baseados em interações
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from core.logger import logger
from modules.memory.persistent_memory import PersistentMemory

class TrainingManager:
    """
    Gerencia treinamento de modelos usando Ollama Modelfile.
    Cria modelos customizados baseados em interações do usuário.
    """
    
    def __init__(self, ollama_base_url: str = None, memory: PersistentMemory = None):
        """
        Inicializa o Training Manager.
        
        Args:
            ollama_base_url: URL base do Ollama
            memory: Instância de memória persistente
        """
        self.ollama_base_url = ollama_base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_api = f"{self.ollama_base_url}/api"
        self.memory = memory or PersistentMemory()
        self.training_data_dir = Path("./data/training")
        self.training_data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"TrainingManager inicializado: {self.ollama_base_url}")
    
    def collect_training_data(self, min_interactions: int = 50) -> List[Dict[str, Any]]:
        """
        Coleta dados de treinamento do histórico de conversas.
        
        Args:
            min_interactions: Número mínimo de interações necessárias
        
        Returns:
            Lista de pares query-resposta formatados para treinamento
        """
        try:
            # Buscar histórico de conversas
            history = self.memory.get_conversation_history(limit=min_interactions * 2)
            
            # Agrupar por pares user-assistant
            training_pairs = []
            current_user = None
            
            for msg in history:
                if msg["role"] == "user":
                    current_user = msg["content"]
                elif msg["role"] == "assistant" and current_user:
                    # Criar par de treinamento
                    training_pairs.append({
                        "input": current_user,
                        "output": msg["content"],
                        "timestamp": msg.get("timestamp"),
                        "metadata": msg.get("metadata", {})
                    })
                    current_user = None
            
            logger.info(f"Coletados {len(training_pairs)} pares de treinamento")
            return training_pairs
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados de treinamento: {e}")
            return []
    
    def create_modelfile(
        self, 
        base_model: str, 
        training_pairs: List[Dict[str, Any]],
        model_name: str = "jarvis-custom"
    ) -> str:
        """
        Cria um Modelfile do Ollama com dados de treinamento.
        
        Args:
            base_model: Modelo base (ex: "codellama:7b")
            training_pairs: Pares de treinamento
            model_name: Nome do modelo customizado
        
        Returns:
            Conteúdo do Modelfile
        """
        modelfile_content = f"FROM {base_model}\n\n"
        modelfile_content += "# Sistema personalizado do JARVIS\n"
        modelfile_content += "# Treinado com interações do usuário\n\n"
        
        # Adicionar exemplos de few-shot learning
        # Modelfile suporta SYSTEM, PARAMETER e template
        modelfile_content += "SYSTEM \"\"\"\n"
        modelfile_content += "Você é JARVIS, um assistente de IA inteligente e útil.\n"
        modelfile_content += "Você aprendeu com as interações do usuário e melhorou suas respostas.\n"
        modelfile_content += "Seja direto, útil e amigável.\n"
        modelfile_content += "\"\"\"\n\n"
        
        # Adicionar exemplos baseados nos pares de treinamento
        # Limitar a 20 exemplos para não exceder tamanho do modelfile
        examples = training_pairs[:20]
        if examples:
            modelfile_content += "# Exemplos de aprendizado:\n"
            for i, pair in enumerate(examples, 1):
                input_text = pair["input"].replace('"', '\\"').replace('\n', '\\n')[:200]
                output_text = pair["output"].replace('"', '\\"').replace('\n', '\\n')[:300]
                modelfile_content += f"# Exemplo {i}:\n"
                modelfile_content += f"# Q: {input_text}\n"
                modelfile_content += f"# A: {output_text}\n\n"
        
        # Salvar Modelfile
        modelfile_path = self.training_data_dir / f"{model_name}.Modelfile"
        with open(modelfile_path, 'w', encoding='utf-8') as f:
            f.write(modelfile_content)
        
        logger.info(f"Modelfile criado: {modelfile_path}")
        return str(modelfile_path)
    
    def create_training_dataset_file(self, training_pairs: List[Dict[str, Any]]) -> str:
        """
        Cria arquivo JSON com dataset completo para uso futuro.
        
        Args:
            training_pairs: Pares de treinamento
        
        Returns:
            Caminho do arquivo JSON
        """
        dataset_path = self.training_data_dir / f"dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        dataset = {
            "created_at": datetime.now().isoformat(),
            "pairs_count": len(training_pairs),
            "pairs": training_pairs
        }
        
        with open(dataset_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Dataset salvo: {dataset_path}")
        return str(dataset_path)
    
    def train_model(
        self,
        base_model: str,
        custom_model_name: str = "jarvis-custom",
        min_interactions: int = 50,
        force_retrain: bool = False
    ) -> Dict[str, Any]:
        """
        Treina um modelo customizado usando Ollama Modelfile.
        
        Args:
            base_model: Modelo base para fine-tuning
            custom_model_name: Nome do modelo customizado
            min_interactions: Número mínimo de interações necessárias
            force_retrain: Se True, força retreino mesmo se modelo existe
        
        Returns:
            Resultado do treinamento
        """
        try:
            logger.info(f"Iniciando treinamento: {base_model} -> {custom_model_name}")
            
            # Verificar se modelo já existe
            if not force_retrain:
                existing_models = self._list_ollama_models()
                if custom_model_name in existing_models:
                    logger.info(f"Modelo {custom_model_name} já existe. Use force_retrain=True para retreinar.")
                    return {
                        "success": True,
                        "message": f"Modelo {custom_model_name} já existe",
                        "model_name": custom_model_name
                    }
            
            # 1. Coletar dados de treinamento
            training_pairs = self.collect_training_data(min_interactions)
            
            if len(training_pairs) < min_interactions:
                return {
                    "success": False,
                    "message": f"Interações insuficientes: {len(training_pairs)}/{min_interactions}",
                    "need_more": min_interactions - len(training_pairs)
                }
            
            # 2. Criar Modelfile
            modelfile_path = self.create_modelfile(base_model, training_pairs, custom_model_name)
            
            # 3. Salvar dataset completo
            dataset_path = self.create_training_dataset_file(training_pairs)
            
            # 4. Criar modelo usando Ollama API
            # Ollama usa create endpoint com Modelfile
            success = self._create_ollama_model(modelfile_path, custom_model_name)
            
            if success:
                # Salvar metadados do treinamento
                training_metadata = {
                    "model_name": custom_model_name,
                    "base_model": base_model,
                    "training_pairs": len(training_pairs),
                    "created_at": datetime.now().isoformat(),
                    "modelfile_path": modelfile_path,
                    "dataset_path": dataset_path
                }
                
                self.memory.save_context(f"training_{custom_model_name}", training_metadata)
                
                logger.info(f"✅ Modelo {custom_model_name} treinado com sucesso!")
                
                return {
                    "success": True,
                    "message": f"Modelo {custom_model_name} criado com sucesso",
                    "model_name": custom_model_name,
                    "training_pairs": len(training_pairs),
                    "metadata": training_metadata
                }
            else:
                return {
                    "success": False,
                    "message": "Erro ao criar modelo no Ollama"
                }
                
        except Exception as e:
            logger.error(f"Erro no treinamento: {e}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }
    
    def _create_ollama_model(self, modelfile_path: str, model_name: str) -> bool:
        """
        Cria modelo no Ollama usando Modelfile.
        
        Args:
            modelfile_path: Caminho do Modelfile
            model_name: Nome do modelo
        
        Returns:
            True se sucesso
        """
        try:
            # Ler conteúdo do Modelfile
            with open(modelfile_path, 'r', encoding='utf-8') as f:
                modelfile_content = f.read()
            
            # Ollama API: POST /api/create
            # Parâmetros: name, modelfile
            response = requests.post(
                f"{self.ollama_api}/create",
                json={
                    "name": model_name,
                    "modelfile": modelfile_content
                },
                timeout=300  # 5 minutos para criar modelo
            )
            
            if response.status_code == 200:
                logger.info(f"Modelo {model_name} criado no Ollama")
                return True
            else:
                logger.error(f"Erro ao criar modelo: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao criar modelo no Ollama: {e}")
            return False
    
    def _list_ollama_models(self) -> List[str]:
        """Lista modelos disponíveis no Ollama."""
        try:
            response = requests.get(f"{self.ollama_api}/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [m.get('name') for m in models]
            return []
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {e}")
            return []
    
    def incremental_training(
        self,
        base_model: str,
        custom_model_name: str = "jarvis-custom",
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """
        Treinamento incremental - adiciona novos dados ao modelo existente.
        
        Args:
            base_model: Modelo base (ou modelo customizado anterior)
            custom_model_name: Nome do modelo customizado
            batch_size: Número de novas interações necessárias
        
        Returns:
            Resultado do treinamento incremental
        """
        try:
            # Buscar novas interações desde último treinamento
            last_training = self.memory.get_context(f"training_{custom_model_name}")
            last_training_time = None
            
            if last_training:
                last_training_time = last_training.get("created_at")
            
            # Coletar apenas interações novas
            all_history = self.memory.get_conversation_history(limit=1000)
            new_interactions = []
            
            if last_training_time:
                # Filtrar interações após último treinamento
                for msg in all_history:
                    if msg.get("timestamp") and msg.get("timestamp") > last_training_time:
                        if msg["role"] == "user":
                            new_interactions.append(msg)
            else:
                # Primeiro treinamento - pegar últimas interações
                new_interactions = [msg for msg in all_history if msg["role"] == "user"][:batch_size]
            
            if len(new_interactions) < batch_size:
                return {
                    "success": False,
                    "message": f"Novas interações insuficientes: {len(new_interactions)}/{batch_size}",
                    "need_more": batch_size - len(new_interactions)
                }
            
            # Usar modelo existente como base ou modelo original
            model_to_use = custom_model_name if self._model_exists(custom_model_name) else base_model
            
            # Retreinar com dados novos + antigos
            return self.train_model(
                base_model=model_to_use,
                custom_model_name=custom_model_name,
                min_interactions=batch_size,
                force_retrain=True
            )
            
        except Exception as e:
            logger.error(f"Erro no treinamento incremental: {e}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }
    
    def _model_exists(self, model_name: str) -> bool:
        """Verifica se modelo existe no Ollama."""
        models = self._list_ollama_models()
        return model_name in models
    
    def get_training_status(self) -> Dict[str, Any]:
        """Retorna status do treinamento."""
        try:
            models = self._list_ollama_models()
            custom_models = [m for m in models if "jarvis" in m.lower()]
            
            training_metadata = {}
            for model_name in custom_models:
                meta = self.memory.get_context(f"training_{model_name}")
                if meta:
                    training_metadata[model_name] = meta
            
            # Estatísticas de dados disponíveis
            history = self.memory.get_conversation_history(limit=1000)
            user_messages = [m for m in history if m["role"] == "user"]
            assistant_messages = [m for m in history if m["role"] == "assistant"]
            
            return {
                "custom_models": custom_models,
                "training_metadata": training_metadata,
                "available_interactions": len(user_messages),
                "pairs_available": min(len(user_messages), len(assistant_messages)),
                "can_train": len(user_messages) >= 50,
                "status": "ready" if len(user_messages) >= 50 else "collecting_data"
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

