from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import glob
import logging

logger = logging.getLogger("uvicorn")

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_name: str = "Chefe"

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    from .mem0 import AsyncMemoryClient
    memory = AsyncMemoryClient()
    user_id = req.user_name
    
    # Busca memórias para contexto
    memories = await memory.get_all(user_id=user_id)
    context_str = " ".join([m.get("memory", "") for m in memories]) if memories else "Sem memórias prévias."
    
    logger.info(f"Processando chat API para {user_id} com contexto: {context_str[:50]}...")
    
    # Resposta simulada que demonstra conhecimento do contexto
    reply = f"Entendido, {user_id}. Estou processando sua mensagem: '{req.message}'. "
    if memories:
        reply += "Com base no nosso histórico, estou pronto para prosseguir."
    
    return {"reply": reply}

@router.get("/memory")
def memory_endpoint():
    return {"memories": []}

@router.get("/livekit-token")
def livekit_token():
    # generate a short-lived LiveKit access token for the frontend to join

    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv("LIVEKIT_API_KEY")
    secret = os.getenv("LIVEKIT_API_SECRET")
    if not key or not secret:
        raise HTTPException(status_code=500, detail="LiveKit credentials not configured")
    # lazy import to avoid pulling SDK at module import time
    from livekit.api import AccessToken, VideoGrants

    access = AccessToken(key, secret)
    access.with_identity("jarvis")
    # build minimal video grants; room name can later come from request
    vg = VideoGrants(room="jarvis-room", room_join=True)
    access.with_grants(vg)
    return {"token": access.to_jwt()}
@router.get("/screenshots")
async def list_screenshots():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    if not os.path.exists(data_dir):
        return {"screenshots": []}
    
    files = glob.glob(os.path.join(data_dir, "*.png"))
    # Ordenar por data de modificação (mais recentes primeiro) e limitar a 20
    files.sort(key=os.path.getmtime, reverse=True)
    recent_files = files[:20]
    
    return {"screenshots": [os.path.basename(f) for f in recent_files]}

@router.api_route("/screenshots/{filename}", methods=["GET", "HEAD"])
async def get_screenshot(filename: str):
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    file_path = os.path.join(data_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Screenshot not found")
        
    return FileResponse(
        file_path, 
        headers={"Cache-Control": "public, max-age=5"},
        media_type="image/png"
    )

@router.get("/logs")
async def list_logs():
    from .utils.log_manager import log_manager
    return {"dates": log_manager.list_log_dates()}

@router.get("/logs/{date}")
async def get_logs(date: str):
    from .utils.log_manager import log_manager
    logs = log_manager.get_logs_by_date(date)
    return {"logs": logs}

@router.get("/vault-stats")
def vault_stats():
    """Retorna estatísticas do vault Obsidian (segundo cérebro do Jarvis)."""
    from .vault_memory import get_vault_stats
    return get_vault_stats()

class VaultMemoryRequest(BaseModel):
    title: str
    content: str
    project: str = ""
    keywords: list[str] = []
    importance: str = "MEDIA"

@router.post("/vault-memory")
def save_vault_memory(req: VaultMemoryRequest):
    """Salva uma memória episódica no vault Obsidian."""
    from .vault_memory import save_episodic, is_vault_available
    if not is_vault_available():
        raise HTTPException(status_code=503, detail="Vault Obsidian não disponível.")
    path = save_episodic(
        title=req.title,
        content=req.content,
        project=req.project,
        keywords=req.keywords,
        importance=req.importance,
    )
    return {"saved": True, "path": path}

