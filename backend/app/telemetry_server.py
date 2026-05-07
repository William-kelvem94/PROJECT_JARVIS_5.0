from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import psutil
import threading
import uvicorn
import socket
from loguru import logger
from .perception.perception_manager import perception_manager
from .utils.learning_manager import learning_manager
from .utils.second_brain_connector import second_brain

app = FastAPI(title="JARVIS Telemetry Dashboard")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
async def get_status():
    """Retorna o estado interno completo do JARVIS."""
    percep = perception_manager.get_snapshot()
    return {
        "hardware": {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "threads": threading.active_count()
        },
        "perception": {
            "face_identity": percep.get("face_identity"),
            "face_emotion": percep.get("face_emotion"),
            "detected_objects": percep.get("detected_objects", [])
        },
        "persona": learning_manager.profile.get("personality_traits", {}),
        "obsidian": {
            "active_todos": len(second_brain.active_todos),
            "vault_path": second_brain.vault_path
        }
    }

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Interface HTML simples para telemetria."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>JARVIS Cockpit Telemetry</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0a0a; color: #00ffcc; padding: 20px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .card { background: #1a1a1a; border: 1px solid #333; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
            h2 { color: #00aaff; margin-top: 0; border-bottom: 1px solid #333; padding-bottom: 10px; }
            .value { font-size: 1.2em; font-weight: bold; }
            .tag { display: inline-block; background: #004466; padding: 2px 8px; border-radius: 4px; margin: 2px; font-size: 0.8em; }
        </style>
    </head>
    <body>
        <h1>JARVIS 5.3 Engineering - Realtime Telemetry</h1>
        <div class="grid">
            <div class="card">
                <h2>Hardware Status</h2>
                <div id="hardware">Carregando...</div>
            </div>
            <div class="card">
                <h2>Perception HUD</h2>
                <div id="perception">Carregando...</div>
            </div>
            <div class="card">
                <h2>Persona & Learning</h2>
                <div id="persona">Carregando...</div>
            </div>
            <div class="card">
                <h2>Obsidian Second Brain</h2>
                <div id="obsidian">Carregando...</div>
            </div>
        </div>

        <script>
            async function update() {
                try {
                    const res = await fetch('/api/status');
                    const data = await res.json();
                    
                    document.getElementById('hardware').innerHTML = `
                        <p>CPU: <span class="value">${data.hardware.cpu}%</span></p>
                        <p>RAM: <span class="value">${data.hardware.ram}%</span></p>
                    `;
                    
                    document.getElementById('perception').innerHTML = `
                        <p>User: <span class="value">${data.perception.face_identity || 'Ninguém'}</span></p>
                        <p>Emotion: <span class="value">${data.perception.face_emotion}</span></p>
                        <p>Objects: ${data.perception.detected_objects.map(o => `<span class="tag">${o.label}</span>`).join('')}</p>
                    `;

                    document.getElementById('persona').innerHTML = `
                        <p>Technical: ${data.persona.technical_level}</p>
                        <p>Conciseness: ${data.persona.conciseness}</p>
                    `;

                    document.getElementById('obsidian').innerHTML = `
                        <p>Todos Pendentes: <span class="value">${data.obsidian.active_todos}</span></p>
                        <p>Vault: ${data.obsidian.vault_path}</p>
                    `;
                } catch (e) { console.error(e); }
            }
            setInterval(update, 2000);
            update();
        </script>
    </body>
    </html>
    """

def start_telemetry_server():
    """Inicia o dashboard em uma thread separada."""
    # Evita quebrar o startup principal se a porta já estiver em uso.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(0.3)
        if sock.connect_ex(("127.0.0.1", 8001)) == 0:
            logger.warning("⚠️ Telemetry dashboard já está ativo na porta 8001. Ignorando novo bind.")
            return
    finally:
        sock.close()

    thread = threading.Thread(
        target=lambda: uvicorn.run(app, host="0.0.0.0", port=8001, log_level="warning"),
        daemon=True
    )
    thread.start()
    logger.info("🚀 Dashboard de Telemetria disponível em: http://localhost:8001")
