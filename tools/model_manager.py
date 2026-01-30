"""
JARVIS Model Manager - Gerenciamento de Modelos de IA
Integração com HuggingFace e Ollama para baixar e gerenciar modelos
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
import subprocess
import time

from config import config

class ModelManager:
    """
    Gerenciador inteligente de modelos de IA.
    Busca, baixa e instala modelos do HuggingFace via Ollama.
    """

    def __init__(self):
        self.ollama_url = config.get("ollama_base_url", "http://localhost:11434")
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')  # Opcional para modelos privados

        # Cache de modelos disponíveis
        self.cache_file = Path("./data/model_cache.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_cache()

    def _load_cache(self):
        """Carrega cache de modelos."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.model_cache = json.load(f)
            except:
                self.model_cache = {}
        else:
            self.model_cache = {}

    def _save_cache(self):
        """Salva cache de modelos."""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.model_cache, f, indent=2, ensure_ascii=False)

    def is_ollama_running(self) -> bool:
        """Verifica se Ollama está rodando."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_installed_models(self) -> List[Dict[str, Any]]:
        """Lista modelos instalados no Ollama."""
        if not self.is_ollama_running():
            return []

        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
            return []
        except Exception as e:
            print(f"Erro ao listar modelos: {e}")
            return []

    def search_models(self, query: str, task: Optional[str] = None,
                     limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca modelos no HuggingFace compatíveis com Ollama.

        Args:
            query: Termo de busca
            task: Tipo de tarefa (text-generation, etc)
            limit: Número máximo de resultados

        Returns:
            Lista de modelos compatíveis
        """
        try:
            # Usar cache se disponível e recente
            cache_key = f"{query}_{task}_{limit}"
            if cache_key in self.model_cache:
                cached_time = self.model_cache[cache_key].get("timestamp", 0)
                if time.time() - cached_time < 3600:  # 1 hora
                    return self.model_cache[cache_key]["results"]

            # Buscar na API do HuggingFace
            url = "https://huggingface.co/api/models"
            params = {
                "search": query,
                "limit": limit * 2,  # Buscar mais para filtrar
                "sort": "downloads",
                "direction": -1
            }

            if task:
                params["pipeline_tag"] = task

            headers = {}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}"

            response = requests.get(url, params=params, headers=headers, timeout=15)

            if response.status_code != 200:
                print(f"Erro na busca HF: {response.status_code}")
                return []

            models = response.json()

            # Filtrar modelos compatíveis com Ollama
            compatible_models = []
            for model in models:
                if self._is_ollama_compatible(model):
                    compatible_models.append({
                        "id": model["id"],
                        "name": model["id"].split("/")[-1],
                        "full_name": model["id"],
                        "downloads": model.get("downloads", 0),
                        "likes": model.get("likes", 0),
                        "task": model.get("pipeline_tag", "unknown"),
                        "size": self._estimate_model_size(model),
                        "description": model.get("description", "")[:200]
                    })

                    if len(compatible_models) >= limit:
                        break

            # Salvar no cache
            self.model_cache[cache_key] = {
                "timestamp": time.time(),
                "results": compatible_models
            }
            self._save_cache()

            return compatible_models

        except Exception as e:
            print(f"Erro na busca de modelos: {e}")
            return []

    def _is_ollama_compatible(self, model: Dict[str, Any]) -> bool:
        """Verifica se modelo é compatível com Ollama."""
        model_id = model.get("id", "").lower()

        # Palavras-chave que indicam compatibilidade
        compatible_keywords = [
            "gguf", "ggml", "llama", "mistral", "codellama", "deepseek",
            "phi", "qwen", "gemma", "starcoder"
        ]

        # Tags de pipeline compatíveis
        compatible_tags = [
            "text-generation", "text2text-generation"
        ]

        # Verificar keywords no nome
        has_compatible_name = any(keyword in model_id for keyword in compatible_keywords)

        # Verificar tags
        has_compatible_tag = model.get("pipeline_tag") in compatible_tags

        # Verificar se tem arquivos GGUF
        has_gguf_files = any(
            file.get("filename", "").lower().endswith(".gguf")
            for file in model.get("siblings", [])
        )

        return has_compatible_name or has_compatible_tag or has_gguf_files

    def _estimate_model_size(self, model: Dict[str, Any]) -> str:
        """Estima tamanho do modelo baseado nos downloads e arquitetura."""
        model_id = model.get("id", "").lower()

        # Mapeamento aproximado de tamanhos
        size_map = {
            "7b": "4GB",
            "13b": "8GB",
            "30b": "16GB",
            "65b": "32GB",
            "70b": "40GB"
        }

        for key, size in size_map.items():
            if key in model_id:
                return size

        # Tamanho padrão
        return "4GB"

    def install_model(self, model_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Instala modelo no Ollama.

        Args:
            model_name: Nome do modelo
            force: Forçar reinstall se já existe

        Returns:
            Resultado da instalação
        """
        if not self.is_ollama_running():
            return {
                "success": False,
                "error": "Ollama não está rodando. Inicie o Ollama primeiro."
            }

        # Verificar se modelo já existe
        installed_models = self.get_installed_models()
        installed_names = [m["name"] for m in installed_models]

        if model_name in installed_names and not force:
            return {
                "success": False,
                "error": f"Modelo {model_name} já está instalado. Use force=True para reinstall."
            }

        try:
            print(f" Baixando modelo {model_name}...")

            # Executar ollama pull
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Monitorar progresso
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(f" {output.strip()}")
                    output_lines.append(output.strip())

            return_code = process.poll()

            if return_code == 0:
                # Verificar se foi instalado
                updated_models = self.get_installed_models()
                updated_names = [m["name"] for m in updated_models]

                if model_name in updated_names:
                    return {
                        "success": True,
                        "message": f" Modelo {model_name} instalado com sucesso!",
                        "output": output_lines
                    }
                else:
                    return {
                        "success": False,
                        "error": "Modelo foi baixado mas não apareceu na lista"
                    }
            else:
                error_output = process.stderr.read()
                return {
                    "success": False,
                    "error": f"Falha no download: {error_output}"
                }

        except FileNotFoundError:
            return {
                "success": False,
                "error": "Ollama não encontrado. Instale o Ollama primeiro."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao instalar modelo: {str(e)}"
            }

    def remove_model(self, model_name: str) -> Dict[str, Any]:
        """Remove modelo do Ollama."""
        if not self.is_ollama_running():
            return {
                "success": False,
                "error": "Ollama não está rodando"
            }

        try:
            process = subprocess.run(
                ["ollama", "rm", model_name],
                capture_output=True,
                text=True,
                timeout=60
            )

            if process.returncode == 0:
                return {
                    "success": True,
                    "message": f" Modelo {model_name} removido!"
                }
            else:
                return {
                    "success": False,
                    "error": process.stderr.strip()
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Obtém informações detalhadas de um modelo."""
        if not self.is_ollama_running():
            return None

        try:
            response = requests.post(
                f"{self.ollama_url}/api/show",
                json={"name": model_name},
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            return None

        except Exception as e:
            print(f"Erro ao obter info do modelo: {e}")
            return None

    def suggest_models_for_task(self, task_description: str) -> List[Dict[str, Any]]:
        """
        Sugere modelos baseado na descrição da tarefa.

        Args:
            task_description: Descrição do que o usuário quer fazer

        Returns:
            Lista de modelos sugeridos
        """
        task_lower = task_description.lower()

        # Mapeamento de tarefas para tipos de modelo
        task_mappings = {
            "programar": ["codellama", "deepseek-coder", "starcoder"],
            "conversar": ["llama2", "mistral", "neural-chat"],
            "analisar": ["llama2", "codellama"],
            "traduzir": ["mistral", "llama2"],
            "criar": ["codellama", "mistral"]
        }

        suggested_queries = []

        # Identificar tarefa principal
        for task_keyword, model_types in task_mappings.items():
            if task_keyword in task_lower:
                suggested_queries.extend(model_types)
                break

        # Adicionar modelos gerais se não encontrou específico
        if not suggested_queries:
            suggested_queries = ["codellama", "mistral", "llama2"]

        # Buscar modelos para cada sugestão
        all_suggestions = []
        for query in suggested_queries[:3]:  # Máximo 3 tipos
            models = self.search_models(query, limit=3)
            all_suggestions.extend(models[:2])  # Máximo 2 por tipo

        # Remover duplicatas e limitar
        seen_ids = set()
        unique_suggestions = []

        for model in all_suggestions:
            if model["id"] not in seen_ids:
                unique_suggestions.append(model)
                seen_ids.add(model["id"])

        return unique_suggestions[:6]  # Máximo 6 sugestões

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Retorna recomendações de modelos para começar."""
        recommendations = [
            {
                "name": "codellama:7b",
                "description": "Excelente para programação e desenvolvimento",
                "size": "4GB",
                "use_case": "Desenvolvimento de software"
            },
            {
                "name": "mistral:7b",
                "description": "Modelo conversacional rápido e inteligente",
                "size": "4GB",
                "use_case": "Conversas gerais e assistencia"
            },
            {
                "name": "deepseek-coder:6.7b",
                "description": "Especializado em geração de código",
                "size": "4GB",
                "use_case": "Programação avançada"
            }
        ]

        return recommendations

    def get_status(self) -> Dict[str, Any]:
        """Retorna status geral do gerenciador."""
        return {
            "ollama_running": self.is_ollama_running(),
            "installed_models_count": len(self.get_installed_models()),
            "cache_size": len(self.model_cache),
            "hf_token_configured": bool(self.hf_token)
        }