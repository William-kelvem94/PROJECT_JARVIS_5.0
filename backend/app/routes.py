from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import glob
import logging

from .chat_pipeline import chat_stream
from .unified_memory import memory
from .utils.db_manager import db_manager
from .utils.note_writer import note_writer

logger = logging.getLogger("uvicorn")

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_name: str = "Chefe"

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    full_reply = ""
    async for chunk in chat_stream(user_id=req.user_name, user_message=req.message):
        full_reply += chunk
    
    logger.info(f"Chat API processado para {req.user_name}.")
    return {"reply": full_reply}

@router.get("/memory")
async def memory_endpoint(user_name: str = "Chefe"):
    memories = await memory.get_all(user_id=user_name)
    return {"memories": memories}

@router.get("/screenshots")
async def list_screenshots():
    # Caminho absoluto para evitar erros de diretório relativo
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_dir = os.path.join(base_dir, "backend", "data")
    
    if not os.path.exists(data_dir):
        return {"screenshots": []}
    
    files = glob.glob(os.path.join(data_dir, "*.png"))
    files.sort(key=os.path.getmtime, reverse=True)
    recent_files = files[:20]
    
    return {"screenshots": [os.path.basename(f) for f in recent_files]}

@router.api_route("/screenshots/{filename}", methods=["GET", "HEAD"])
async def get_screenshot(filename: str):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_dir = os.path.join(base_dir, "backend", "data")
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
    return memory.get_stats()

class VaultMemoryRequest(BaseModel):
    title: str
    content: str
    project: str = ""
    keywords: list[str] = []
    importance: str = "MEDIA"

@router.post("/vault-memory")
async def save_vault_memory(req: VaultMemoryRequest):
    """Salva uma memória episódica no vault (Unified)."""
    if not memory.is_vault_available():
        # Avisa mas permite salvar se o cérebro interno estiver ok
        logger.warning("Vault Obsidian não disponível, salvando apenas no cérebro interno.")
        
    path = await memory.save_episodic(
        title=req.title,
        content=req.content,
        project=req.project,
        importance=req.importance,
        keywords=req.keywords
    )
    return {"saved": True, "path": path}

@router.get("/health")
async def health_check():
    """Telemetria oficial para o HUD de Engenharia, incluindo Percepção."""
    import psutil
    from .perception.perception_manager import perception_manager
    
    # Pega o snapshot em tempo real do que o Jarvis está vendo/ouvindo
    visao = perception_manager.get_snapshot()
    
    return {
        "status": "online",
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "is_ai_ready": True,
        # Dados de Percepção para o HUD
        "face_identity": visao.get("face_identity", "Unknown"),
        "face_emotion": visao.get("face_emotion", "Awaiting..."),
        "gesture": visao.get("hand_gesture", "None") or "None"
    }


@router.get("/telemetry/history")
async def telemetry_history(limit: int = 24):
    history = db_manager.get_telemetry_history(limit=limit)
    return {"history": history}


class NoteRequest(BaseModel):
    title: str
    body: str


@router.post("/notes")
async def create_note_endpoint(req: NoteRequest):
    note_path = note_writer.create_note(req.title, req.body)
    return {"saved": True, "path": note_path}
