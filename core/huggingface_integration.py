"""
HuggingFace Integration - Sistema para buscar e usar modelos externos gratuitos
Integra com HuggingFace Hub para buscar modelos e datasets
"""

import os
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.logger import logger

try:
    from huggingface_hub import HfApi, list_models, list_datasets
    HUGGINGFACE_HUB_AVAILABLE = True
except ImportError:
    HUGGINGFACE_HUB_AVAILABLE = False
    logger.warning("huggingface_hub não disponível. Instale com: pip install huggingface_hub")

class HuggingFaceIntegration:
    """
    Integração com HuggingFace para:
    - Buscar modelos gratuitos
    - Baixar modelos
    - Integrar com Ollama
    - Usar modelos de embedding
    """
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Inicializa integração com HuggingFace.
        
        Args:
            api_token: Token da API do HuggingFace (opcional, para modelos privados)
        """
        self.api_token = api_token or os.getenv('HUGGINGFACE_API_TOKEN')
        
        if HUGGINGFACE_HUB_AVAILABLE:
            try:
                self.api = HfApi(token=self.api_token)
                logger.info("HuggingFace API inicializada")
            except Exception as e:
                logger.warning(f"Erro ao inicializar HuggingFace API: {e}")
                self.api = None
        else:
            self.api = None
            logger.warning("HuggingFace Hub não disponível")
    
    def search_models(
        self,
        query: str,
        task: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Busca modelos no HuggingFace.
        
        Args:
            query: Termo de busca
            task: Tipo de tarefa (text-generation, text2text-generation, etc)
            limit: Número máximo de resultados
        
        Returns:
            Lista de modelos encontrados
        """
        try:
            if not HUGGINGFACE_HUB_AVAILABLE or not self.api:
                # Fallback: usar API REST
                return self._search_models_rest(query, task, limit)
            
            # Buscar usando huggingface_hub
            filters = {}
            if task:
                filters["task"] = task
            
            models = list_models(
                search=query,
                limit=limit,
                **filters
            )
            
            results = []
            for model in models:
                results.append({
                    "id": model.id,
                    "author": model.author,
                    "downloads": getattr(model, 'downloads', 0),
                    "likes": getattr(model, 'likes', 0),
                    "task": getattr(model, 'task', None),
                    "library": getattr(model, 'library', None),
                    "pipeline_tag": getattr(model, 'pipeline_tag', None)
                })
            
            logger.info(f"✅ {len(results)} modelos encontrados para '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao buscar modelos: {e}")
            return []
    
    def _search_models_rest(
        self,
        query: str,
        task: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Busca modelos via API REST do HuggingFace."""
        try:
            url = "https://huggingface.co/api/models"
            params = {
                "search": query,
                "limit": limit,
                "full": "false"
            }
            
            if task:
                params["task"] = task
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                models = response.json()
                results = []
                for model in models[:limit]:
                    results.append({
                        "id": model.get("id"),
                        "author": model.get("author"),
                        "downloads": model.get("downloads", 0),
                        "likes": model.get("likes", 0),
                        "task": model.get("pipeline_tag"),
                        "library": model.get("library_name")
                    })
                return results
            else:
                logger.error(f"Erro na API REST: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Erro na busca REST: {e}")
            return []
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Obtém informações detalhadas de um modelo.
        
        Args:
            model_id: ID do modelo (ex: "microsoft/DialoGPT-medium")
        
        Returns:
            Informações do modelo
        """
        try:
            if HUGGINGFACE_HUB_AVAILABLE and self.api:
                model_info = self.api.model_info(model_id)
                return {
                    "id": model_info.id,
                    "author": model_info.author,
                    "downloads": model_info.downloads,
                    "likes": model_info.likes,
                    "task": model_info.task,
                    "library": model_info.library_name,
                    "siblings": [s.rfilename for s in model_info.siblings],
                    "tags": model_info.tags if hasattr(model_info, 'tags') else []
                }
            else:
                # Fallback REST
                url = f"https://huggingface.co/api/models/{model_id}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response.json()
                return {}
                
        except Exception as e:
            logger.error(f"Erro ao obter informações do modelo {model_id}: {e}")
            return {}
    
    def get_ollama_compatible_models(
        self,
        query: str = "llm",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Busca modelos compatíveis com Ollama.
        Ollama suporta modelos GGUF e alguns formatos específicos.
        
        Args:
            query: Termo de busca
            limit: Número de resultados
        
        Returns:
            Lista de modelos compatíveis
        """
        try:
            # Buscar modelos de texto
            models = self.search_models(
                query=query,
                task="text-generation",
                limit=limit * 2
            )
            
            # Filtrar modelos compatíveis (GGUF ou suportados pelo Ollama)
            compatible_models = [
                "llama", "mistral", "codellama", "phi", "gemma",
                "qwen", "neural-chat", "deepseek", "dolphin"
            ]
            
            compatible = []
            for model in models:
                model_id_lower = model.get("id", "").lower()
                
                # Verificar se é compatível
                is_compatible = any(
                    name in model_id_lower for name in compatible_models
                )
                
                if is_compatible:
                    compatible.append({
                        **model,
                        "ollama_format": self._detect_ollama_format(model.get("id", ""))
                    })
            
            logger.info(f"✅ {len(compatible)} modelos compatíveis com Ollama encontrados")
            return compatible[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao buscar modelos compatíveis: {e}")
            return []
    
    def _detect_ollama_format(self, model_id: str) -> str:
        """Detecta formato do modelo para Ollama."""
        model_lower = model_id.lower()
        
        # Mapear nomes conhecidos
        format_map = {
            "llama": "llama",
            "mistral": "mistral",
            "codellama": "codellama",
            "phi": "phi",
            "gemma": "gemma",
            "qwen": "qwen",
            "neural-chat": "neural-chat",
            "deepseek": "deepseek-coder",
            "dolphin": "dolphin-mistral"
        }
        
        for key, value in format_map.items():
            if key in model_lower:
                return value
        
        return "unknown"
    
    def suggest_model_for_task(self, task_description: str) -> List[Dict[str, Any]]:
        """
        Sugere modelos baseado em descrição de tarefa.
        
        Args:
            task_description: Descrição da tarefa
        
        Returns:
            Lista de modelos sugeridos
        """
        try:
            # Mapear descrições para tipos de tarefa
            task_map = {
                "código": "text-generation",
                "code": "text-generation",
                "programação": "text-generation",
                "chat": "text-generation",
                "conversação": "text-generation",
                "texto": "text-generation"
            }
            
            task_type = None
            for key, value in task_map.items():
                if key in task_description.lower():
                    task_type = value
                    break
            
            # Buscar modelos
            models = self.search_models(
                query=task_description,
                task=task_type,
                limit=10
            )
            
            # Ordenar por popularidade (downloads + likes)
            models.sort(key=lambda x: x.get("downloads", 0) + x.get("likes", 0) * 10, reverse=True)
            
            return models[:5]  # Top 5
            
        except Exception as e:
            logger.error(f"Erro ao sugerir modelos: {e}")
            return []
    
    def download_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Obtém informações para download de modelo.
        Retorna informações necessárias para baixar via Ollama ou diretamente.
        
        Args:
            model_id: ID do modelo
        
        Returns:
            Informações de download
        """
        try:
            model_info = self.get_model_info(model_id)
            
            # Verificar se está disponível no Ollama
            ollama_format = self._detect_ollama_format(model_id)
            
            return {
                "model_id": model_id,
                "ollama_format": ollama_format,
                "ollama_name": f"{ollama_format}:7b" if ollama_format != "unknown" else None,
                "huggingface_url": f"https://huggingface.co/{model_id}",
                "download_instructions": self._get_download_instructions(model_id, ollama_format),
                "info": model_info
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter info de download: {e}")
            return {}
    
    def _get_download_instructions(
        self,
        model_id: str,
        ollama_format: str
    ) -> str:
        """Gera instruções de download."""
        if ollama_format != "unknown":
            return f"Use Ollama: ollama pull {ollama_format}:7b"
        else:
            return f"Baixe de: https://huggingface.co/{model_id}"
    
    def search_datasets(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca datasets no HuggingFace.
        
        Args:
            query: Termo de busca
            limit: Número de resultados
        
        Returns:
            Lista de datasets encontrados
        """
        try:
            if not HUGGINGFACE_HUB_AVAILABLE or not self.api:
                # Fallback REST
                url = "https://huggingface.co/api/datasets"
                params = {"search": query, "limit": limit}
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    datasets = response.json()
                    return [
                        {
                            "id": d.get("id"),
                            "downloads": d.get("downloads", 0),
                            "likes": d.get("likes", 0),
                            "tags": d.get("tags", [])
                        }
                        for d in datasets[:limit]
                    ]
                return []
            
            # Usar huggingface_hub
            datasets = list_datasets(search=query, limit=limit)
            
            return [
                {
                    "id": ds.id,
                    "downloads": getattr(ds, 'downloads', 0),
                    "likes": getattr(ds, 'likes', 0)
                }
                for ds in datasets
            ]
            
        except Exception as e:
            logger.error(f"Erro ao buscar datasets: {e}")
            return []

