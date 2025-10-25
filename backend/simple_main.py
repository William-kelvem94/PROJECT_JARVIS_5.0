"""JARVIS Backend - Versão Simplificada"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json

app = FastAPI(title="JARVIS AI Assistant")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ChatRequest(BaseModel):
    message: str
    conversation_id: str = None

class LoginRequest(BaseModel):
    username: str
    password: str

# In-memory storage
users = {}
conversations = {}

@app.get("/")
async def root():
    return {"message": "JARVIS AI Assistant", "version": "3.0.0", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "mode": "demo"}

@app.post("/api/v1/auth/register")
async def register(user: LoginRequest):
    if user.username in users:
        return {"detail": "Username already exists"}, 400
    users[user.username] = {"username": user.username, "password": user.password}
    return {
        "id": user.username,
        "username": user.username,
        "email": f"{user.username}@demo.com",
        "is_active": True
    }

@app.post("/api/v1/auth/login")
async def login(user: LoginRequest):
    if user.username not in users:
        # Auto-criar usuário
        users[user.username] = {"username": user.username, "password": user.password}
    
    return {
        "access_token": f"demo_token_{user.username}",
        "refresh_token": f"refresh_{user.username}",
        "token_type": "bearer"
    }

@app.get("/api/v1/users/me")
async def get_me():
    return {
        "id": "demo_user",
        "username": "demo",
        "email": "demo@jarvis.ai",
        "is_active": True
    }

@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    await asyncio.sleep(0.3)
    return {
        "message": f"🤖 [MODO DEMO] Recebi: '{request.message[:50]}...' Instale Ollama para IA real!",
        "conversation_id": request.conversation_id or "demo_conv",
        "message_id": "demo_msg",
        "model": "demo",
        "tokens_used": 0
    }

@app.websocket("/api/v1/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    
    # Enviar mensagem de boas-vindas
    await websocket.send_text(json.dumps({
        "type": "connection",
        "status": "connected",
        "message": "Bem-vindo ao JARVIS! (Modo Demo)"
    }))
    
    try:
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            
            if data.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                continue
            
            # Simular streaming
            await websocket.send_text(json.dumps({
                "type": "message_start",
                "conversation_id": "demo_conv"
            }))
            
            mensagem_usuario = data.get("message", "")
            resposta = f"🤖 Olá! Recebi sua mensagem: '{mensagem_usuario[:60]}...' Este é o MODO DEMO. Para IA real, instale o Ollama!"
            
            # Enviar palavra por palavra
            for palavra in resposta.split():
                await websocket.send_text(json.dumps({
                    "type": "message_chunk",
                    "content": palavra + " "
                }))
                await asyncio.sleep(0.05)
            
            await websocket.send_text(json.dumps({
                "type": "message_end",
                "conversation_id": "demo_conv",
                "message_id": "demo_msg"
            }))
    
    except WebSocketDisconnect:
        print("WebSocket desconectado")

@app.get("/api/v1/conversations")
async def list_conversations():
    return []

@app.get("/api/v1/plugins")
async def list_plugins():
    return [
        {"name": "voice", "enabled": False, "initialized": False},
        {"name": "deepseek", "enabled": False, "initialized": False},
        {"name": "alexa", "enabled": False, "initialized": False}
    ]

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🤖 JARVIS AI Assistant - Backend Simplificado")
    print("="*60)
    print("\n✅ Backend rodando em: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n⚠️  MODO DEMO - Respostas simuladas")
    print("📥 Instale Ollama para IA real: https://ollama.ai\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)

