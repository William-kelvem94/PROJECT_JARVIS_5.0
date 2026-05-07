from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import os
import glob
import threading
from pathlib import Path

from .security.sentinel_parser import SentinelParser
from .security.sentinel_core import SentinelSecurity
from .security.blackbox import BlackBox
from .chat_pipeline import chat_stream
from .unified_memory import memory
from .utils.db_manager import db_manager
from .utils.note_writer import note_writer
from loguru import logger

# Global Security Instances
sentinel_parser = SentinelParser()
# Derive key from HWID -> Argon2id -> SHA256
security_core = SentinelSecurity()
system_key = security_core.derive_system_key()
# BlackBox initialization with derived key
blackbox = BlackBox(
    db_path=os.path.join(os.path.dirname(__file__), "..", "data", "blackbox.db"),
    encryption_key=system_key
)
security_core.blackbox = blackbox

router = APIRouter()
SCREENSHOT_DIR = Path(__file__).resolve().parents[2] / "data"


def _safe_screenshot_path(filename: str) -> Path:
    candidate = (SCREENSHOT_DIR / Path(filename).name).resolve(strict=False)
    if candidate.parent != SCREENSHOT_DIR.resolve():
        raise HTTPException(status_code=400, detail="Invalid filename")
    return candidate

class ChatRequest(BaseModel):
    message: str
    user_name: str = "Chefe"

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    # --- SENTINEL REAL-TIME INTERCEPTION ---
    # Validates the user message before it reaches the LLM pipeline to prevent prompt injection/destructive commands
    if not await security_core.validate_llm_command(req.message, sentinel_parser):
        raise HTTPException(status_code=403, detail="Sentinel Blocked: Destructive or unauthorized command detected.")
    # --------------------------------------

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
    if not SCREENSHOT_DIR.exists():
        return {"screenshots": []}
    
    files = glob.glob(str(SCREENSHOT_DIR / "*.png"))
    files.sort(key=os.path.getmtime, reverse=True)
    recent_files = files[:20]
    
    return {"screenshots": [os.path.basename(f) for f in recent_files]}

@router.api_route("/screenshots/{filename}", methods=["GET", "HEAD"])
async def get_screenshot(filename: str):
    file_path = _safe_screenshot_path(filename)
    
    if not file_path.exists():
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


@router.get("/telemetry/status")
async def telemetry_status():
    """Endpoint de telemetria com tratamento robusto de erros."""
    import psutil
    
    result = {
        "hardware": {
            "cpu": 0.0,
            "ram": 0.0,
            "threads": 0,
        },
        "perception": {
            "face_identity": None,
            "face_emotion": None,
            "detected_objects": [],
        },
        "persona": {},
        "obsidian": {
            "active_todos": 0,
            "vault_path": "",
        },
        "status": "ok",
    }
    
    # Hardware - sempre disponível
    try:
        result["hardware"]["cpu"] = psutil.cpu_percent(interval=0.1)
        result["hardware"]["ram"] = psutil.virtual_memory().percent
        result["hardware"]["threads"] = threading.active_count()
    except Exception as e:
        logger.warning(f"Hardware telemetry error: {e}")
    
    # Perception - pode não estar disponível
    try:
        from .perception.perception_manager import perception_manager
        percep = perception_manager.get_snapshot()
        result["perception"] = {
            "face_identity": percep.get("face_identity"),
            "face_emotion": percep.get("face_emotion"),
            "detected_objects": percep.get("detected_objects", []),
        }
    except Exception as e:
        logger.warning(f"Perception telemetry error: {e}")
    
    # Learning Manager - pode não estar disponível
    try:
        from .utils.learning_manager import learning_manager
        result["persona"] = learning_manager.profile.get("personality_traits", {})
    except Exception as e:
        logger.warning(f"Learning manager telemetry error: {e}")
    
    # Second Brain - pode não estar disponível
    try:
        from .utils.second_brain_connector import second_brain
        result["obsidian"] = {
            "active_todos": len(getattr(second_brain, "active_todos", [])),
            "vault_path": getattr(second_brain, "vault_path", ""),
        }
    except Exception as e:
        logger.warning(f"Second brain telemetry error: {e}")
    
    return result


@router.get("/telemetry/api/status")
async def telemetry_api_status():
    """Alias endpoint para compatibilidade."""
    return await telemetry_status()


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


# ============================================================================
# MULTI-AGENT ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/agents/summary")
async def get_agents_summary():
    """Retorna um sumário do estado de todos os agentes de análise."""
    from .multi_agent_analysis import get_orchestrator
    orchestrator = get_orchestrator()
    summary = orchestrator.get_summary()
    return summary


@router.get("/agents/findings")
async def get_agents_findings(severity: str = None):
    """Retorna todos os findings dos agentes, opcionalmente filtrados por severidade."""
    from .multi_agent_analysis import get_orchestrator, Severity
    
    orchestrator = get_orchestrator()
    severity_filter = None
    
    if severity:
        try:
            severity_filter = Severity(severity.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
    
    findings = orchestrator.get_all_findings(severity=severity_filter)
    
    # Convert findings to dict for JSON serialization
    findings_dict = [
        {
            "agent_type": f.agent_type.value,
            "severity": f.severity.value,
            "title": f.title,
            "description": f.description,
            "recommendation": f.recommendation,
            "timestamp": f.timestamp.isoformat(),
            "auto_fixable": f.auto_fixable,
            "metrics": f.metrics
        }
        for f in findings
    ]
    
    return {"findings": findings_dict, "total": len(findings_dict)}


@router.get("/agents/critical")
async def get_critical_findings():
    """Retorna apenas findings críticos."""
    from .multi_agent_analysis import get_orchestrator, Severity
    
    orchestrator = get_orchestrator()
    critical = orchestrator.get_all_findings(severity=Severity.CRITICAL)
    high = orchestrator.get_all_findings(severity=Severity.HIGH)
    
    findings_dict = [
        {
            "agent_type": f.agent_type.value,
            "severity": f.severity.value,
            "title": f.title,
            "description": f.description,
            "recommendation": f.recommendation,
            "timestamp": f.timestamp.isoformat()
        }
        for f in critical + high
    ]
    
    return {"critical_findings": findings_dict, "count": len(findings_dict)}


# ============================================================================
# SYSTEM CAPABILITIES HEALTH ENDPOINTS
# ============================================================================

@router.get("/system/capabilities")
async def get_system_capabilities():
    """Retorna status em tempo real de todas as capabilities do sistema."""
    try:
        from .health_checker import get_health_checker
        
        checker = get_health_checker()
        # Force fresh check
        checks = checker.check_all()
        summary = checker.get_summary()
        
        # Organize by groups
        capabilities = {
            "nucleo_cognitivo": {
                "title": "Nucleo cognitivo",
                "components": [
                    _format_health(checks.get("smart_router")),
                    _format_health(checks.get("unified_memory")),
                    _format_health(checks.get("engineer_brain")),
                    _format_health(checks.get("adaptive_persona"))
                ]
            },
            "percepcao": {
                "title": "Percepcao",
                "components": [
                    _format_health(checks.get("face_engine")),
                    _format_health(checks.get("gestures")),
                    _format_health(checks.get("objects")),
                    _format_health(checks.get("realtime_audio"))
                ]
            },
            "sistema": {
                "title": "Sistema",
                "components": [
                    _format_health(checks.get("os_tools")),
                    _format_health(checks.get("browser_engine")),
                    _format_health(checks.get("screen_capture")),
                    _format_health(checks.get("assisted_execution"))
                ]
            },
            "seguranca": {
                "title": "Seguranca",
                "components": [
                    _format_health(checks.get("sentinel_parser")),
                    _format_health(checks.get("blackbox")),
                    _format_health(checks.get("holodeck")),
                    _format_health(checks.get("biometric_vault"))
                ]
            },
            "hardware": {
                "title": "Hardware",
                "components": [
                    _format_health(checks.get("camera")),
                    _format_health(checks.get("microphone")),
                    _format_health(checks.get("screen_mirror"))
                ]
            }
        }
        
        return {
            "capabilities": capabilities,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[API] Health checker error: {e}")
        # Retornar resposta mínima se falhar
        return {
            "capabilities": {},
            "summary": {
                "total_components": 0,
                "online_count": 0,
                "offline_count": 0,
                "health_percentage": 0.0,
                "error": str(e)
            },
            "timestamp": datetime.now().isoformat()
        }


def _format_health(health):
    """Formata um ComponentHealth para JSON."""
    if not health:
        return {
            "name": "Unknown",
            "status": "error",
            "available": False,
            "message": "Component not found"
        }
    
    return {
        "name": health.name,
        "status": health.status.value,
        "available": health.available,
        "message": health.message,
        "details": health.details,
        "error": health.error
    }


@router.get("/system/hardware")
async def get_hardware_status():
    """Retorna status específico do hardware (camera, mic, screen)."""
    try:
        from .health_checker import get_health_checker
        
        checker = get_health_checker()
        checks = checker.check_all()
        
        return {
            "camera": _format_health(checks.get("camera")),
            "microphone": _format_health(checks.get("microphone")),
            "screen_mirror": _format_health(checks.get("screen_mirror")),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[API] Hardware check error: {e}")
        return {
            "camera": {"name": "Camera", "status": "error", "available": False, "message": str(e), "error": str(e)},
            "microphone": {"name": "Microphone", "status": "error", "available": False, "message": str(e), "error": str(e)},
            "screen_mirror": {"name": "Screen Mirror", "status": "error", "available": False, "message": str(e), "error": str(e)},
            "timestamp": datetime.now().isoformat()
        }
