import os
from .mem0 import AsyncMemoryClient
from .vault_memory import save_episodic, get_vault_stats, is_vault_available
from .local_memory import local_memory
from .config import settings

class MemoryManager:
    def __init__(self):
        self.hybrid = AsyncMemoryClient()

    async def add_user_message(self, user_id: str, user_message: str):
        """Adiciona uma mensagem do usuário à memória híbrida."""
        return await self.hybrid.add([{"role": "user", "content": user_message}], user_id=user_id)

    async def get_memory_context(self, user_id: str) -> str:
        results = await self.hybrid.get_all(user_id=user_id)
        if not results:
            return "Sem memórias registradas."
        return "\n".join([f"- {item.get('memory')}" for item in results if item.get('memory')])

    async def list_memories(self, user_id: str):
        return await self.hybrid.get_all(user_id=user_id)

    def vault_stats(self):
        return get_vault_stats()

    def save_vault_memory(self, title: str, content: str, project: str = "", keywords: list[str] | None = None, importance: str = "MEDIA") -> str:
        if not is_vault_available():
            raise RuntimeError("Vault Obsidian não disponível.")
        return save_episodic(
            title=title,
            content=content,
            project=project,
            keywords=keywords or [],
            importance=importance,
        )

    def current_settings(self):
        return {
            "openrouter_api_key": getattr(settings, "openrouter_api_key", ""),
            "google_api_key": getattr(settings, "google_api_key", ""),
            "openai_api_key": getattr(settings, "openai_api_key", ""),
            "jarvis_kb_path": getattr(settings, "jarvis_kb_path", ""),
            "jarvis_vault_root": getattr(settings, "jarvis_vault_root", ""),
        }

    def save_learning(self, fact: str, category: str = "tecnico") -> bool:
        from .vault_memory import save_learning
        return save_learning(fact=fact, category=category)
