#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
# JARVIS SINGULARITY - AI Worker Thread
# ============================================================================
# Wrapper QThread para o ai_agent.py (bloqueante)
# Solução cirúrgica para evitar congelamento da UI PyQt6
# ============================================================================

import sys
import threading
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# PATH SETUP
# -------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

# -------------------------------------------------------------------------
# AI WORKER - QThread Wrapper
# -------------------------------------------------------------------------
class AIWorker(QThread):
    """
    Thread worker que encapsula o ai_agent.process_command() bloqueante.
    
    **SINAIS EMITIDOS:**
    - status_changed(str): Mudança de estado ("listening", "thinking", "speaking", "idle", "error")
    - response_ready(str): Resposta final do AI pronta
    - error_occurred(str): Erro durante processamento
    - progress_update(str): Atualizações intermediárias
    """
    
    # PyQt6 Signals
    status_changed = pyqtSignal(str)      # "listening" | "thinking" | "speaking" | "idle" | "error"
    response_ready = pyqtSignal(str)      # Resposta final do AI
    error_occurred = pyqtSignal(str)      # Mensagem de erro
    progress_update = pyqtSignal(str)     # Atualizações intermediárias
    
    # Singleton internal reference for ai_agent
    _ai_agent = None
    _ai_agent_lock = threading.Lock()

    def __init__(self, parent=None):
        """
        Inicializa o worker.
        """
        super().__init__(parent)
        self._command: Optional[str] = None
        self._is_running = False
        
        # Lazy load check
        self._ensure_agent()

    def _ensure_agent(self):
        """Garante que o ai_agent seja carregado de forma segura"""
        if AIWorker._ai_agent is None:
            with AIWorker._ai_agent_lock:
                if AIWorker._ai_agent is None:
                    try:
                        from src.core.intelligence.ai_agent import ai_agent
                        AIWorker._ai_agent = ai_agent
                        logger.info("✅ AIWorker: ai_agent carregado com sucesso.")
                    except Exception as e:
                        logger.error(f"❌ AIWorker: Erro ao carregar ai_agent: {e}")

    @pyqtSlot(str)
    def process_command(self, command: str):
        """
        Processa um comando do usuário (chamado da thread principal).
        """
        if self.isRunning():
            self.error_occurred.emit("AI ainda está processando um comando anterior.")
            return
        
        self._command = command
        self.start()

    def stop(self):
        """
        Solicita parada da thread (graceful shutdown).
        """
        self._is_running = False
        if self.isRunning():
            if not self.wait(2000):
                self.terminate()
                self.wait(500)

    def run(self):
        """
        Método executado na thread separada (NÃO bloqueia UI).
        """
        if not self._command:
            return
        
        self._is_running = True
        
        try:
            # 1. Pensando
            self.status_changed.emit("thinking")
            
            # 2. Processamento Bloqueante com Lock
            with self._ai_agent_lock:
                self._ensure_agent()
                if self._ai_agent:
                    # O ai_agent tem seu próprio controle interno de TTS e estado
                    response = self._ai_agent.process_command(self._command)
                else:
                    response = "Erro: Núcleo Neural (ai_agent) não disponível."
            
            # 3. Falando (Opcional, dependendo se o ai_agent emite sinais ou é síncrono)
            self.status_changed.emit("speaking")
            
            # 4. Enviar Resposta
            if response:
                self.response_ready.emit(response)
            else:
                self.error_occurred.emit("AI retornou resposta vazia.")
            
        except Exception as e:
            logger.error(f"❌ AIWorker Exception: {e}", exc_info=True)
            self.error_occurred.emit(f"Erro: {type(e).__name__}")
            self.status_changed.emit("error")
        
        finally:
            self._is_running = False
            self._command = None
            self.status_changed.emit("idle")

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    worker = AIWorker()
    worker.status_changed.connect(lambda s: print(f"📡 Status: {s}"))
    worker.response_ready.connect(lambda r: print(f"💬 Resposta: {r}"))
    worker.process_command("Teste de pulso")
    worker.finished.connect(app.quit)
    sys.exit(app.exec())
