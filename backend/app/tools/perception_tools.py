import asyncio
from .base import BaseTool

class PerceptionTools(BaseTool):
    async def get_perception_status(self):
        try:
            from ..perception import perception_manager
            snap = perception_manager.get_snapshot()
            return str(snap)
        except Exception as e:
            return f"Erro: {e}"

    async def enroll_face(self, name: str):
        from ..perception import perception_manager
        from ..perception.face_engine import enroll_face as _enroll
        frame = perception_manager.capture_frame()
        if frame is None: return "Câmera off."
        return _enroll(name, frame)
