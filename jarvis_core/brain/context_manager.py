"""
Brain - Context Manager
Gerenciamento inteligente de contexto
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ContextManager:
    """Gerenciador de contexto conversacional"""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.context_window = []
        self.summarized_history = []
        
        logger.info(f"✅ Context Manager inicializado (max: {max_tokens} tokens)")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Adiciona mensagem ao contexto"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.context_window.append(message)
        
        # Auto-trim se necessário
        if self._estimate_tokens() > self.max_tokens:
            self._trim_context()
    
    def get_context(self, max_messages: Optional[int] = None) -> List[Dict]:
        """Retorna contexto atual"""
        if max_messages:
            return self.context_window[-max_messages:]
        return self.context_window
    
    def get_formatted_context(self) -> str:
        """Retorna contexto formatado para LLM"""
        formatted = ""
        
        # Incluir resumo histórico
        if self.summarized_history:
            formatted += "[HISTÓRICO RESUMIDO]\n"
            for summary in self.summarized_history:
                formatted += f"- {summary}\n"
            formatted += "\n[CONVERSA ATUAL]\n"
        
        # Incluir mensagens recentes
        for msg in self.context_window:
            formatted += f"{msg['role']}: {msg['content']}\n"
        
        return formatted
    
    def _estimate_tokens(self) -> int:
        """Estima número de tokens (aproximado)"""
        total_chars = sum(len(msg["content"]) for msg in self.context_window)
        # Aproximação: 1 token ≈ 4 caracteres
        return total_chars // 4
    
    def _trim_context(self):
        """Remove mensagens antigas e resume"""
        logger.info("✂️ Trimming contexto...")
        
        # Pegar primeiras 10 mensagens para resumir
        to_summarize = self.context_window[:10]
        
        # Criar resumo
        summary = self._create_summary(to_summarize)
        self.summarized_history.append(summary)
        
        # Remover mensagens resumidas
        self.context_window = self.context_window[10:]
        
        logger.info(f"✅ Contexto reduzido. Tokens: ~{self._estimate_tokens()}")
    
    def _create_summary(self, messages: List[Dict]) -> str:
        """Cria resumo de mensagens"""
        # Simplificado - em produção, usar LLM
        topics = []
        for msg in messages:
            if len(msg["content"]) > 50:
                topics.append(msg["content"][:50] + "...")
        
        timestamp = messages[0]["timestamp"]
        return f"[{timestamp}] Discussão sobre: {', '.join(topics[:3])}"
    
    def clear_context(self):
        """Limpa contexto"""
        self.context_window = []
        self.summarized_history = []
        logger.info("🗑️ Contexto limpo")
    
    def get_recent_topics(self, n: int = 5) -> List[str]:
        """Extrai tópicos recentes"""
        topics = []
        
        for msg in self.context_window[-n:]:
            # Extrair palavras-chave (simplificado)
            words = msg["content"].split()
            if len(words) > 3:
                topics.append(" ".join(words[:3]))
        
        return topics


# Instância global
context_manager = ContextManager()
