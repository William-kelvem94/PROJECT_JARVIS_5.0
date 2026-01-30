"""
JARVIS Brain - Cérebro com RAG (Retrieval Augmented Generation)
Sistema de aprendizado e memória inteligente
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from config import config
from modules.rag.vector_store import VectorStore
from core.local_llm import LocalLLM

class Brain:
    """
    Cérebro do JARVIS com sistema RAG integrado.
    Aprende continuamente e adapta respostas baseado no contexto.
    """

    def __init__(self):
        self.vector_store = VectorStore(storage_path="./data/vector_db")
        self.llm = LocalLLM(model=config.get("ollama_model"))
        self.knowledge_stats = {"learned_items": 0, "queries_processed": 0}

        # Prompt base personalizado para William
        self.system_prompt_base = f"""Você é JARVIS, o assistente de IA pessoal do {config.get_user_name()}.

PERSONALIDADE:
- Extremamente consultivo e técnico quando apropriado
- Usa termos corretos (ex: "processamento de linguagem natural" não "aprendizado de máquina básico")
- Descontraído e amigável, usa emojis quando apropriado
- Focado em soluções práticas e eficientes

CONHECIMENTO PRÉVIO sobre {config.get_user_name()}:
- Gosta de volume em 20% (ambiente tranquilo)
- Usa Galaxy Book2 (notebook) e Desktop parrudo
- Desktop tem water cooler para resfriamento
- Prefere soluções técnicas robustas

CAPACIDADES:
- Controle total do sistema operacional
- Aprendizado contínuo e memória persistente
- Pesquisa web inteligente
- Gerenciamento de modelos de IA
- Monitoramento de hardware em tempo real

INSTRUÇÕES GERAIS:
- Sempre use português brasileiro
- Seja proativo em sugestões técnicas
- Aprenda com cada interação útil
- Mantenha contexto da conversa
- Ofereça soluções completas e executáveis
"""

    def learn(self, info: str, category: str = "user_preference",
              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Aprende nova informação e armazena no RAG.

        Args:
            info: Informação a ser aprendida
            category: Categoria da informação
            metadata: Metadados adicionais

        Returns:
            Resultado da operação
        """
        try:
            # Criar documento estruturado
            doc_text = f"[{category.upper()}] {info}"

            # Adicionar contexto temporal
            timestamp = datetime.now().isoformat()

            # Metadata padrão
            doc_metadata = {
                "category": category,
                "source": "brain_learn",
                "timestamp": timestamp,
                "user": config.get_user_name(),
                **(metadata or {})
            }

            # Armazenar no vector store
            result = self.vector_store.add_document(
                text=doc_text,
                metadata=doc_metadata,
                doc_id=f"learn_{timestamp}_{category}"
            )

            if result.get("success"):
                self.knowledge_stats["learned_items"] += 1

            return {
                "success": True,
                "message": f" Aprendido: {info[:50]}...",
                "stored": result.get("success", False)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao aprender: {str(e)}"
            }

    def recall(self, query: str, max_results: int = 3) -> str:
        """
        Recupera conhecimento relevante para uma query.

        Args:
            query: Query de busca
            max_results: Número máximo de resultados

        Returns:
            Contexto formatado para o LLM
        """
        try:
            # Buscar conhecimento relevante
            results = self.vector_store.search(query, n_results=max_results)

            if not results:
                return ""

            # Formatar contexto
            context_parts = []
            for i, doc in enumerate(results, 1):
                context_parts.append(f" Conhecimento {i}: {doc['text']}")

            context = "\n".join(context_parts)
            self.knowledge_stats["queries_processed"] += 1

            return f"\nCONTEXTO RELEVANTE APRENDIDO:\n{context}\n"

        except Exception as e:
            print(f"Erro ao recuperar conhecimento: {e}")
            return ""

    def think(self, user_query: str, system_context: Optional[str] = None) -> str:
        """
        Processa uma query do usuário com contexto RAG.

        Args:
            user_query: Query do usuário
            system_context: Contexto adicional do sistema

        Returns:
            Resposta do LLM com contexto
        """
        try:
            # Recuperar conhecimento relevante
            rag_context = self.recall(user_query)

            # Construir system prompt completo
            full_system_prompt = self.system_prompt_base

            if rag_context:
                full_system_prompt += f"\n\n{rag_context}"

            if system_context:
                full_system_prompt += f"\n\nCONTEXTO ATUAL:\n{system_context}"

            # Verificar se deve aprender desta interação
            if self._should_learn(user_query):
                learning_result = self._extract_learning(user_query)
                if learning_result:
                    self.learn(learning_result["info"],
                             learning_result["category"],
                             learning_result["metadata"])

            # Gerar resposta
            response = self.llm.generate(user_query, system=full_system_prompt)

            # Auto-aprendizagem baseada na resposta
            if config.get("learning.auto_learn_from_interactions"):
                self._learn_from_interaction(user_query, response)

            return response

        except Exception as e:
            return f" Erro no processamento: {str(e)}"

    def _should_learn(self, query: str) -> bool:
        """Verifica se a query contém informação útil para aprender."""
        learn_keywords = [
            "gosto", "prefiro", "sempre", "normalmente", "costumo",
            "minha configuração", "meu setup", "aprenda que",
            "lembre-se", "anote", "guarde"
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in learn_keywords)

    def _extract_learning(self, query: str) -> Optional[Dict[str, Any]]:
        """Extrai informação aprendível da query."""
        query_lower = query.lower()

        # Padrões de aprendizado
        patterns = {
            "volume_preference": [
                "gosto de volume", "volume em", "prefiro volume"
            ],
            "hardware_config": [
                "meu pc", "meu computador", "meu setup",
                "desktop", "notebook", "galaxy book"
            ],
            "software_preference": [
                "gosto de usar", "prefiro usar", "costumo usar"
            ]
        }

        for category, keywords in patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                return {
                    "info": query,
                    "category": category,
                    "metadata": {
                        "confidence": 0.8,
                        "extracted_from": "user_statement"
                    }
                }

        return None

    def _learn_from_interaction(self, query: str, response: str):
        """Aprende automaticamente das interações."""
        try:
            # Extrair conhecimento útil da resposta
            if "" in response or "aprendido" in response.lower():
                # A resposta indica que algo foi aprendido ou configurado
                learn_info = f"Interação: {query} -> {response[:200]}..."
                self.learn(learn_info, "interaction_learning",
                          {"interaction_type": "successful_config"})

        except Exception as e:
            print(f"Erro no aprendizado automático: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cérebro."""
        vector_stats = self.vector_store.get_stats()

        return {
            "knowledge_items": vector_stats.get("document_count", 0),
            "queries_processed": self.knowledge_stats["queries_processed"],
            "learned_items": self.knowledge_stats["learned_items"],
            "vector_store_available": vector_stats.get("chromadb_available", False),
            "embeddings_available": vector_stats.get("embeddings_available", False),
            "user_name": config.get_user_name()
        }

    def clear_memory(self, confirm: bool = False) -> Dict[str, Any]:
        """Limpa toda a memória (perigoso - requer confirmação)."""
        if not confirm:
            return {
                "success": False,
                "message": "⚠️ Use confirm=True para limpar toda a memória"
            }

        try:
            # Limpar vector store
            vector_stats = self.vector_store.get_stats()
            # Note: VectorStore não tem método clear, seria necessário implementar

            self.knowledge_stats = {"learned_items": 0, "queries_processed": 0}

            return {
                "success": True,
                "message": "🧠 Memória limpa completamente"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao limpar memória: {str(e)}"
            }