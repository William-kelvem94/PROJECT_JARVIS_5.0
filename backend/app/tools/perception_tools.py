import asyncio
from livekit import agents
from .base import BaseTool

class PerceptionTools(BaseTool):
    @agents.llm.function_tool(description="Retorna o estado atual da percepção (face, emoção, gestos).")
    async def get_perception_status(self):
        try:
            from ..perception import perception_manager
            snap = perception_manager.get_snapshot()
            return str(snap)
        except Exception as e:
            return f"Erro: {e}"

    @agents.llm.function_tool(description="Cadastra o rosto do usuário.")
    async def enroll_face(self, name: str):
        from ..perception import perception_manager
        from ..perception.face_engine import enroll_face as _enroll
        frame = perception_manager.capture_frame()
        if frame is None: return "Câmera off."
        return _enroll(name, frame)
