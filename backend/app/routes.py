from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

# import agent logic (to be implemented)
from . import agents

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    # placeholder: integrate with agents logic
    return {"reply": "This is a stub response to: " + req.message}

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
