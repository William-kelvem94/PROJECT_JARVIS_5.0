# -*- coding: utf-8 -*-
"""
TRUTH VALIDATOR - Validação de Fatos com Dados Externos
JARVIS 5.0 - Ground Truth para Auto-Correção Evolutiva
"""

import sys
import os
import json
import logging
import asyncio
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib
from bs4 import BeautifulSoup

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TRUTH-VALIDATOR")

# Adicionar diretório raiz
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class SearchOrchestrator:
    """Orquestrador de buscas multi-engine para validação de verdade."""
    
    def __init__(self):
        self.user_agent = "JARVIS-TruthValidator/5.0 (Educational AI Research)"
        
    def google_search(self, query: str) -> List[Dict[str, str]]:
        """Busca via Google (googlesearch-python ou scraping)."""
        logger.info(f"🔎 Google Engine: Buscando '{query}'")
        results = []
        try:
            from googlesearch import search
            for url in search(query, num_results=3):
                results.append({
                    "title": "Google Result",
                    "snippet": f"Content from {url}",
                    "url": url,
                    "source": "Google"
                })
        except Exception as e:
            logger.warning(f"⚠️ Google Search failed: {e}")
        return results

    def hf_hub_search(self, query: str) -> List[Dict[str, str]]:
        """Valida versões de modelos e datasets via HF Hub."""
        logger.info(f"🤗 HF Hub Engine: Validando '{query}'")
        results = []
        try:
            from huggingface_hub import HfApi
            api = HfApi()
            models = api.list_models(search=query, limit=3)
            for model in models:
                results.append({
                    "title": model.modelId,
                    "snippet": f"Model on HF Hub. Task: {model.pipeline_tag}, Likes: {model.downloads}",
                    "url": f"https://huggingface.co/{model.modelId}",
                    "source": "HuggingFace"
                })
        except Exception as e:
            logger.warning(f"⚠️ HF Hub Search failed: {e}")
        return results

    def arxiv_wiki_search(self, query: str) -> List[Dict[str, str]]:
        """Busca definições técnicas no ArXiv ou Wikipedia."""
        logger.info(f"📚 ArXiv/Wiki Engine: Buscando '{query}'")
        results = []
        try:
            # Wikipedia Search
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
            resp = requests.get(wiki_url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                results.append({
                    "title": data.get("title", query),
                    "snippet": data.get("extract", ""),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "source": "Wikipedia"
                })
        except Exception:
            pass
        return results

class TruthValidator:
    """Validador de Verdade - Ground Truth para Auto-Correção."""

    def __init__(self):
        self.verified_knowledge_path = Path("data/learning/verified_knowledge.json")
        self.verified_knowledge_path.parent.mkdir(parents=True, exist_ok=True)
        self.search_orchestrator = SearchOrchestrator()
        self.validation_cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()

    def _load_cache(self):
        if self.verified_knowledge_path.exists():
            try:
                with open(self.verified_knowledge_path, 'r', encoding='utf-8') as f:
                    self.validation_cache = json.load(f)
            except Exception:
                self.validation_cache = {}

    def _save_cache(self):
        try:
            with open(self.verified_knowledge_path, 'w', encoding='utf-8') as f:
                json.dump(self.validation_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Erro salvando cache: {e}")

    def _get_similarity(self, text1: str, text2: str) -> float:
        """Calcula a similaridade de cosseno entre dois textos usando o modelo local."""
        try:
            from src.core.intelligence.neural_memory import neural_memory
            if not hasattr(neural_memory, "model") or neural_memory.model is None:
                neural_memory._ensure_model_loaded()
            
            if neural_memory.model:
                emb1 = neural_memory.model.encode(text1)
                emb2 = neural_memory.model.encode(text2)
                from numpy import dot
                from numpy.linalg import norm
                return dot(emb1, emb2) / (norm(emb1) * norm(emb2))
        except Exception as e:
            logger.warning(f"⚠️ Semantic similarity failed: {e}")
        
        # Fallback: Jaccard similarity simples
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        return intersection / union if union > 0 else 0.0

    def cross_reference_fatos(self, query: str) -> Dict[str, Any]:
        """Realiza a votação de veracidade entre múltiplas fontes com validação semântica."""
        logger.info(f"⚖️ Elite Search: Cross-Referencing '{query}'")
        
        all_results = []
        try:
            all_results.extend(self.search_orchestrator.google_search(query))
            all_results.extend(self.search_orchestrator.hf_hub_search(query))
            all_results.extend(self.search_orchestrator.arxiv_wiki_search(query))
        except Exception as e:
            logger.error(f"❌ Critical Search Failure: {e}")
            # Log para o MaintenanceManager
            with open("data/logs/truth_validator_errors.log", "a") as f:
                f.write(f"{datetime.now().isoformat()} - {query} - {str(e)}\n")

        if not all_results:
            return {"query": query, "status": "NO_DATA", "confidence": 0.0}

        # Comparação Semântica entre os 2 melhores resultados
        confidence_boost = 0.0
        if len(all_results) >= 2:
            sim = self._get_similarity(all_results[0]["snippet"], all_results[1]["snippet"])
            logger.info(f"🔍 Semantic Similarity between Top 2: {sim:.4f}")
            if sim > 0.7:
                confidence_boost = 0.3

        sources_count = len(set(r["source"] for r in all_results))
        
        status = "DISPUTED"
        if sources_count >= 2 and confidence_boost > 0:
            status = "HIGH_CONFIDENCE"
        elif sources_count >= 1:
            status = "PARTIAL_VALIDATION"
            
        validation_data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "results": all_results,
            "sources_count": sources_count,
            "semantic_agreement": confidence_boost > 0
        }
        
        cache_key = hashlib.md5(query.encode()).hexdigest()
        self.validation_cache[cache_key] = validation_data
        self._save_cache()
        
        return validation_data

    def validate_fact(self, query: str) -> Dict[str, Any]:
        return self.cross_reference_fatos(query)

_truth_validator = None

def get_truth_validator() -> TruthValidator:
    global _truth_validator
    if _truth_validator is None:
        _truth_validator = TruthValidator()
    return _truth_validator

def validate_fact_external(query: str) -> Dict[str, Any]:
    validator = get_truth_validator()
    return validator.validate_fact(query)
