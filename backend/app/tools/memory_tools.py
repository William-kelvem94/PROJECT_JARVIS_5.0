import asyncio
import os
from .base import BaseTool

class MemoryTools(BaseTool):
    async def save_memory(self, fact: str, user_id: str = "jarvis_user"):
        from ..unified_memory import memory
        await memory.add_memory(user_id, fact, source="explicit_tool")
        asyncio.create_task(self._log_activity("Memória", f"Fato salvo: {fact[:50]}", "info"))
        return "Fato memorizado."

    async def recall_memory(self, query: str, user_id: str = "jarvis_user"):
        from ..unified_memory import memory
        context = await memory.get_context(user_id, query=query)
        return context

    async def save_vault_memory(self, title: str, content: str, project: str = ""):
        from ..unified_memory import memory
        path = await memory.save_episodic(title=title, content=content, project=project)
        asyncio.create_task(self._log_activity("Vault", f"Nota: {title}", "info"))
        return f"Salvo no vault: {os.path.basename(path)}"
        
    async def update_vault_state(self, project: str, done: str, next_action: str):
        from ..unified_memory import memory
        await memory.update_current_state(project=project, done=done, next_action=next_action)
        return "Estado atualizado no Vault."
