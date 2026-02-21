import http.server
import socketserver
import json
import os
import threading
import webbrowser
import logging
import platform
import psutil
import re
import time
from typing import Any

logger = logging.getLogger(__name__)

# Global cache to prevent blocking the HTTP handler
_STATS_CACHE = {
    "model": "llama",
    "ollama_models": [],
    "rag_count": 0,
    "lang": "pt-BR",
    "settings": {},
    "system": {"os": "Windows", "node": "Local", "ram": "0%", "cpu": "0%", "version": "5.0 MVP"},
    "logs": [],
    "train_history": [],
    "training_stats": {"dataset_size": 0, "last_epoch": 0, "last_loss": 0},
    "evolution_stats": {"total_evolutions": 0, "active_simulations": 0},
    "active_tasks": [],
    "task_logs": [],
    "speaking": False
}
_LOCK = threading.Lock()

def log_task(message: str):
    """Adiciona uma mensagem aos logs de tarefas detalhados."""
    ts = time.strftime("%H:%M:%S")
    with _LOCK:
        _STATS_CACHE["task_logs"].append(f"[{ts}] {message}")
        if len(_STATS_CACHE["task_logs"]) > 50:
            _STATS_CACHE["task_logs"].pop(0)

def stats_updater(agent):
    """Background thread to update stats every 2 seconds."""
    from .config_manager import config
    from .rag import rag
    from .ollama_client import get_ollama_models
    
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    while True:
        try:
            with _LOCK:
                _STATS_CACHE["model"] = config.get("OLLAMA_MODEL") or "llama"
                _STATS_CACHE["rag_count"] = len(rag.entries)
                _STATS_CACHE["lang"] = config.get("DEVICE_LANGUAGE") or "pt-BR"
                _STATS_CACHE["settings"] = config.settings
                _STATS_CACHE["speaking"] = agent.is_speaking if agent else False
                _STATS_CACHE["system"] = {
                    "os": platform.system(),
                    "node": platform.node(),
                    "ram": f"{psutil.virtual_memory().percent}%",
                    "cpu": f"{psutil.cpu_percent()}%",
                    "version": "5.0 MVP CORE",
                    "last_sync": time.strftime("%H:%M:%S")
                }

                # Get logs from interactions.jsonl
                log_path = "data/interactions.jsonl"
                if os.path.exists(log_path):
                    with open(log_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        _STATS_CACHE["training_stats"]["dataset_size"] = len(lines)
                        temp_logs = []
                        for line in lines[-20:]:
                            try:
                                clean = ansi_escape.sub('', line).strip()
                                if not clean.startswith('{'): continue
                                j = json.loads(clean)
                                if "user" in j: j["user"] = ansi_escape.sub('', str(j["user"]))
                                if "assistant" in j: j["assistant"] = ansi_escape.sub('', str(j["assistant"]))
                                temp_logs.append(j)
                            except: continue
                        _STATS_CACHE["logs"] = temp_logs[-15:]

                # Training history
                hist_path = os.path.join(os.path.dirname(__file__), "models", "local_brain", "training_log.json")
                if os.path.exists(hist_path):
                    with open(hist_path, "r", encoding="utf-8") as f:
                        hist = json.load(f)
                        _STATS_CACHE["train_history"] = hist
                        if hist:
                            last = hist[-1]
                            _STATS_CACHE["training_stats"]["last_epoch"] = last.get("epoch", 0)
                            _STATS_CACHE["training_stats"]["last_loss"] = last.get("loss", 0)

                # Evolution Stats
                try:
                    from .evolution import EvolutionEngine
                    from .holodeck import HoloDeck
                    evo = EvolutionEngine(os.getcwd())
                    holo = HoloDeck(os.getcwd())
                    evo_data = evo.get_evolution_status()
                    _STATS_CACHE["evolution_stats"] = {
                        "total_evolutions": evo_data.get("total_evolutions", 0),
                        "active_simulations": len(holo.get_active_simulations())
                    }
                except Exception as e:
                    logger.debug(f"Evolution stats error: {e}")

            # Update models less frequently (every 10s)
            old_count = len(_STATS_CACHE["ollama_models"])
            _STATS_CACHE["ollama_models"] = get_ollama_models()
            new_count = len(_STATS_CACHE["ollama_models"])
            if new_count > 0 and old_count == 0:
                logger.info(f"[Ollama] {new_count} modelos detectados e sincronizados com o HUD.")
            
        except Exception as e:
            logger.debug(f"Stats update error: {e}")
            
        time.sleep(2)

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    agent_instance = None

    def log_message(self, format, *args):
        # Override to silence the terminal from constant polling logs
        return

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.path = "/jarvis/static/index.html"
        
        if self.path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            with _LOCK:
                self.wfile.write(json.dumps(_STATS_CACHE).encode("utf-8"))
        elif self.path == "/api/graph":
            from .database import db
            data = db.get_knowledge_graph_data()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            # Fallback to serving static files
            super().do_GET()

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            if self.path == "/api/config":
                self.update_config(data)
            elif self.path == "/api/action":
                self.handle_action(data)
            elif self.path == "/api/command":
                text = data.get("command")
                if text and self.agent_instance:
                    # Executa o comando no motor principal
                    threading.Thread(target=self.agent_instance.handle_command, args=(text,), daemon=True).start()
                    log_task(f"📡 Comando recebido via HUD: {text}")
                self.send_response(200)
                self.end_headers()
            else:
                self.send_error(404)
        except Exception as e:
            logger.error(f"POST error: {e}")
            self.send_error(500)

    def update_config(self, data):
        from .config_manager import config
        for k, v in data.items():
            if isinstance(v, str) and v.replace('.', '', 1).isdigit():
                v = float(v) if '.' in v else int(v)
            config.set(k, v)
        
        if self.agent_instance:
            if "TTS_RATE" in data: self.agent_instance.tts.rate = float(data["TTS_RATE"])
            if "TTS_EDGE_VOICE" in data: self.agent_instance.tts.edge_voice = data["TTS_EDGE_VOICE"]
            
        self.send_response(200)
        self.end_headers()

    def handle_action(self, data):
        action = data.get("action")
        if action == "test_voice" and self.agent_instance:
            self.agent_instance._speak("Teste do sistema. Jarvis v5.0 operacional.")
        
        elif action == "train_brain" and self.agent_instance:
            epochs = int(data.get("epochs", 1))
            lr = float(data.get("lr", 5e-5))
            bs = int(data.get("batch_size", 1))
            def _task():
                log_task(f"🚀 Iniciando Fine-Tuning Avançado...")
                log_task(f"⚙️ Config: Épocas={epochs}, LR={lr}, Batch={bs}")
                _STATS_CACHE["active_tasks"].append(f"Fine-Tuning ({epochs} ép) | LR={lr}")
                try: 
                    if not self.agent_instance or not hasattr(self.agent_instance, 'local_brain') or not self.agent_instance.local_brain:
                        log_task("❌ Erro: O Cérebro Local não está carregado ou foi desativado.")
                        return
                    self.agent_instance.local_brain.train_from_file(epochs=epochs, learning_rate=lr, batch_size=bs)
                    log_task("✅ Fine-Tuning concluído com sucesso.")
                except Exception as e:
                    log_task(f"❌ Erro no treinamento: {e}")
                finally: 
                    task_name = f"Fine-Tuning ({epochs} ép) | LR={lr}"
                    if task_name in _STATS_CACHE["active_tasks"]:
                        _STATS_CACHE["active_tasks"].remove(task_name)
            threading.Thread(target=_task, daemon=True).start()
        
        elif action == "study" and self.agent_instance:
            topic = data.get("topic", "")
            depth = data.get("depth", "standard") # quick, standard, deep
            def _task():
                log_task(f"🔍 Iniciando ciclo de pesquisa '{depth}': {topic}")
                _STATS_CACHE["active_tasks"].append(f"Pesquisa: {topic}")
                try:
                    from .agent import cmd_search
                    log_task("🌐 Mapeando fontes de dados...")
                    # Simular profundidade com múltiplas queries se for deep
                    search_queries = [topic]
                    if depth == "deep":
                        search_queries.append(f"detalhes técnicos sobre {topic}")
                        search_queries.append(f"história e futuro de {topic}")
                    
                    for i, q in enumerate(search_queries):
                        log_task(f"📝 Processando fatia {i+1}/{len(search_queries)}: {q}")
                        cmd_search(self.agent_instance, q)
                    
                    log_task(f"📚 Ciclo de pesquisa concluído. Dados integrados.")
                except Exception as e:
                    log_task(f"❌ Erro na pesquisa: {e}")
                finally:
                    if f"Pesquisa: {topic}" in _STATS_CACHE["active_tasks"]:
                        _STATS_CACHE["active_tasks"].remove(f"Pesquisa: {topic}")
            threading.Thread(target=_task, daemon=True).start()
            
        elif action == "clear_rag":
            from .rag import rag
            rag.entries = []
            rag.embeddings = []
            rag.save()
            log_task("🧹 Léxico Vetorial (RAG) zerado.")

        elif action == "clear_knowledge":
            from .database import db
            db.clear_knowledge()
            log_task("🧹 Banco de conhecimento (Grafo) reiniciado.")

        self.send_response(200)
        self.end_headers()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

def start_dashboard(agent=None, port=8000):
    DashboardHandler.agent_instance = agent
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(repo_root)

    # Start stats collector thread
    threading.Thread(target=stats_updater, args=(agent,), daemon=True).start()

    def _run():
        with ThreadedTCPServer(("", port), DashboardHandler) as httpd:
            logger.info(f"🚀 HUD operacional em http://localhost:{port}")
            httpd.serve_forever()
            
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    try:
        webbrowser.open(f"http://localhost:{port}")
    except: pass
