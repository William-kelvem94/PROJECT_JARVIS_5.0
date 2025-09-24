from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from core.local_llm import LocalLLM
from plugins.voice_plugin import VoicePlugin
import os

app = FastAPI()
llm = LocalLLM(model_path="./models/llama.bin", backend="llama.cpp")
voice = VoicePlugin()

# Servir arquivos estáticos (CSS, JS, imagens)
static_dir = os.path.join(os.path.dirname(__file__), '..', 'web')
app.mount("/static", StaticFiles(directory=os.path.join(static_dir, 'static')), name="static")

# Servir o index.html na raiz
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(static_dir, 'index.html')
    return FileResponse(index_path)

# WebSocket do chat
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        resposta = llm.generate(data)
        await websocket.send_text(resposta)
