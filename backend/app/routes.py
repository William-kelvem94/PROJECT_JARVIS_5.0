from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# import agent logic (to be implemented)
from . import agents

router = APIRouter()

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
    # TODO: generate token using LIVEKIT_API_KEY/SECRET
    raise HTTPException(status_code=501, detail="Not implemented")
