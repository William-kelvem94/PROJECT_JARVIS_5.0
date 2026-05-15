import os
import time
import threading
from pathlib import Path
from loguru import logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ObsidianWatcher(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            self.callback(event.src_path)

class SecondBrainConnector:
    """
    Conecta o JARVIS ao Vault Obsidian (Segundo Cérebro).
    Monitora mudanças, extrai tarefas e provê contexto em tempo real.
    """
    
    def __init__(self, vault_path: str = None):
        # 1. Prioridade: vault inteiro. JARVIS_KB_PATH é só subárvore de ingestão.
        v_path = vault_path or os.getenv("JARVIS_VAULT_ROOT") or os.getenv("OBSIDIAN_VAULT_PATH")
        if v_path and os.path.exists(v_path):
            self.vault_path = v_path
        # 2. Prioridade: Caminho conhecido no Windows
        elif os.path.exists(r"D:\DOCUMENTOS\GitHub\Will-obsidian"):
            self.vault_path = r"D:\DOCUMENTOS\GitHub\Will-obsidian"
        elif os.path.exists("C:/Users/willi/Documents/GitHub/Will-obsidian"):
            self.vault_path = "C:/Users/willi/Documents/GitHub/Will-obsidian"
        # 3. Fallback: Relativo ao projeto
        else:
            self.vault_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "kb_local")
        self.todo_file = os.path.join(self.vault_path, "TODO.md")
        self.active_todos = []
        self._last_index_time = 0
        
        if os.path.exists(self.vault_path):
            self._start_watcher()
            self.index_vault()
            logger.success(f"🧠 Segundo Cérebro Conectado: {self.vault_path}")
        else:
            logger.warning(f"⚠️ Vault Obsidian não encontrado em: {self.vault_path}")

    def _start_watcher(self):
        """Inicia o monitoramento de arquivos em tempo real."""
        observer = Observer()
        handler = ObsidianWatcher(self._on_file_changed)
        observer.schedule(handler, self.vault_path, recursive=True)
        observer.daemon = True
        observer.start()

    def _on_file_changed(self, path):
        logger.info(f"📝 Mudança detectada no Obsidian: {os.path.basename(path)}")
        if "TODO.md" in path:
            self.refresh_todos()
        
        # Atualiza o Grafo Neural em tempo real
        try:
            from .obsidian_graph import obsidian_graph
            obsidian_graph.update_node(path)
        except: pass

    def refresh_todos(self):
        """Extrai tarefas pendentes do TODO.md."""
        if not os.path.exists(self.todo_file): return
        try:
            try:
                with open(self.todo_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                with open(self.todo_file, 'r', encoding='latin-1') as f:
                    lines = f.readlines()
            
            new_todos = []
            for line in lines:
                if "- [ ]" in line:
                    task = line.replace("- [ ]", "").strip()
                    new_todos.append(task)
            
            self.active_todos = new_todos
            logger.info(f"✅ {len(self.active_todos)} Tarefas sincronizadas do Obsidian.")
        except Exception as e:
            logger.error(f"Erro ao ler TODO.md: {e}")

    def index_vault(self):
        """Cria um índice rápido de áreas de interesse (Projetos, Skills, Pessoal)."""
        # Futuramente: Integração com vetores leves ou busca por palavras-chave
        self.refresh_todos()
        self._last_index_time = time.time()

    def get_context_for_prompt(self, query: str = ""):
        """Busca contexto relevante para injetar no cérebro do Jarvis."""
        context = "[CONTEXTO DO SEGUNDO CÉREBRO (OBSIDIAN)]\n"
        
        # 1. Tarefas
        if self.active_todos:
            context += f"Tarefas Pendentes: {', '.join(self.active_todos[:3])}\n"
        
        # 2. Relações Neurais (GraphRAG)
        try:
            from .obsidian_graph import obsidian_graph
            related = obsidian_graph.query_related(query)
            if related:
                context += f"Notas Relacionadas a '{query}': {', '.join(related[:5])}\n"
        except: pass
        
        return context

# Singleton
second_brain = SecondBrainConnector()
