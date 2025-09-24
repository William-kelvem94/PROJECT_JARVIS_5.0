from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from core.local_llm import LocalLLM
from plugins.voice_plugin import VoicePlugin

app = FastAPI()
llm = LocalLLM(model_path="./models/llama.bin", backend="llama.cpp")  # Ajuste o caminho/modelo conforme necessário
voice = VoicePlugin()

@app.get("/")
def read_root():
    return {"message": "Jarvis IA Conversacional - Backend ativo!"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        resposta = llm.generate(data)
        await websocket.send_text(resposta)
