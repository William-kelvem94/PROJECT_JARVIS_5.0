# ============================================================================
# JARVIS SINGULARITY - AI Worker Thread
# ============================================================================
# Wrapper QThread para o ai_agent.py legado (bloqueante)
# Solução cirúrgica para evitar congelamento da UI PyQt6
# ============================================================================

import sys
import threading
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot

# -------------------------------------------------------------------------
# PATH SETUP - Replicando lógica do legacy/main.py linha 17
# -------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# -------------------------------------------------------------------------
# IMPORTS DO CÓDIGO LEGADO
# -------------------------------------------------------------------------
try:
    from core.ai_agent import ai_agent  # Singleton global (linha 513)
except ImportError as e:
    print(f"⚠️ ERRO: Não foi possível importar ai_agent: {e}")
    print(f"   Certifique-se de que src/core/ai_agent.py existe em: {PROJECT_ROOT}")
    ai_agent = None


# ============================================================================
# AI WORKER - QThread Wrapper
# ============================================================================
class AIWorker(QThread):
    """
    Thread worker que encapsula o ai_agent.process_command() bloqueante.
    
    **PROBLEMA RESOLVIDO:**
    - ai_agent.process_command() tem loops síncronos de 30-150s (ReAct loop)
    - Chamadas HTTP bloqueantes (Gemini/Ollama)
    - TTS bloqueante (voice_controller.speak)
    
    **SOLUÇÃO:**
    - Executa process_command() em thread separada
    - Emite sinais PyQt6 para atualizar UI sem bloqueio
    - Gerencia acesso thread-safe ao singleton global
    
    **SINAIS EMITIDOS:**
    - status_changed(str): Mudança de estado ("listening", "thinking", "speaking", "idle", "error")
    - response_ready(str): Resposta final do AI pronta
    - error_occurred(str): Erro durante processamento
    - progress_update(str): Atualizações intermediárias (opcional)
    """
    
    # -------------------------------------------------------------------------
    # SINAIS PyQt6
    # -------------------------------------------------------------------------
    status_changed = pyqtSignal(str)      # "listening" | "thinking" | "speaking" | "idle" | "error"
    response_ready = pyqtSignal(str)      # Resposta final do AI
    error_occurred = pyqtSignal(str)      # Mensagem de erro
    progress_update = pyqtSignal(str)     # Atualizações intermediárias (ex: "Turno 2/5")
    
    # -------------------------------------------------------------------------
    # LOCK GLOBAL - Proteção do Singleton (Auditoria Seção 7.1 - Crítico 2)
    # -------------------------------------------------------------------------
    _ai_agent_lock = threading.Lock()
    
    def __init__(self, parent=None):
        """
        Inicializa o worker.
        
        Args:
            parent: Widget pai (opcional)
        """
        super().__init__(parent)
        self._command: Optional[str] = None
        self._is_running = False
        
        # Verificar se ai_agent foi importado com sucesso
        if ai_agent is None:
            raise RuntimeError(
                "AIWorker não pode ser inicializado: ai_agent não foi importado. "
                "Verifique se src/core/ai_agent.py existe."
            )
    
    # -------------------------------------------------------------------------
    # MÉTODOS PÚBLICOS
    # -------------------------------------------------------------------------
    @pyqtSlot(str)
    def process_command(self, command: str):
        """
        Processa um comando do usuário (chamado da thread principal).
        
        Args:
            command: Comando de voz transcrito ou texto digitado
        """
        if self.isRunning():
            self.error_occurred.emit("AI ainda está processando comando anterior. Aguarde...")
            return
        
        self._command = command
        self.start()  # Inicia a thread (chama run())
    
    def stop(self):
        """
        Solicita parada da thread (graceful shutdown).
        
        NOTA: ai_agent.process_command() não tem mecanismo de cancelamento.
        Esta flag apenas previne novos comandos.
        """
        self._is_running = False
        self.wait(5000)  # Aguarda até 5s para thread terminar
    
    # -------------------------------------------------------------------------
    # THREAD EXECUTION
    # -------------------------------------------------------------------------
    def run(self):
        """
        Método executado na thread separada (NÃO bloqueia UI).
        
        FLUXO:
        1. Emite status "thinking"
        2. Chama ai_agent.process_command() com LOCK
        3. Emite resposta ou erro
        4. Emite status "idle"
        """
        if not self._command:
            return
        
        self._is_running = True
        
        try:
            # ----------------------------------------------------------------
            # FASE 1: Pensando (Azul no HUD)
            # ----------------------------------------------------------------
            self.status_changed.emit("thinking")
            
            # ----------------------------------------------------------------
            # FASE 2: Processamento Bloqueante (PROTEGIDO POR LOCK)
            # ----------------------------------------------------------------
            # Auditoria Seção 7.1 - Crítico 2: Singleton global thread-unsafe
            # Solução: Lock para garantir acesso exclusivo
            # ----------------------------------------------------------------
            with self._ai_agent_lock:
                # Chamada bloqueante (30-150s potencial)
                # Localização: ai_agent.py linhas 154-285
                response = ai_agent.process_command(self._command)
            
            # ----------------------------------------------------------------
            # FASE 3: Falando (Verde no HUD - presumindo que TTS já ocorreu)
            # ----------------------------------------------------------------
            # NOTA: voice_controller.speak() já foi chamado dentro de process_command
            # (linha 296 do ai_agent.py). Aqui apenas sinalizamos conclusão.
            self.status_changed.emit("speaking")
            
            # ----------------------------------------------------------------
            # FASE 4: Resposta Pronta
            # ----------------------------------------------------------------
            if response:
                self.response_ready.emit(response)
            else:
                self.error_occurred.emit("AI retornou resposta vazia")
            
        except Exception as e:
            # ----------------------------------------------------------------
            # TRATAMENTO DE ERRO
            # ----------------------------------------------------------------
            error_msg = f"Erro ao processar comando: {type(e).__name__}: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.status_changed.emit("error")
            
            # Log para debug (opcional)
            import traceback
            print(f"❌ AIWorker Exception:\n{traceback.format_exc()}")
        
        finally:
            # ----------------------------------------------------------------
            # FASE 5: Retornar ao estado Idle
            # ----------------------------------------------------------------
            self._is_running = False
            self._command = None
            self.status_changed.emit("idle")


# ============================================================================
# EXEMPLO DE USO (para testes standalone)
# ============================================================================
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Criar worker
    worker = AIWorker()
    
    # Conectar sinais (para debug)
    worker.status_changed.connect(lambda s: print(f"📡 Status: {s}"))
    worker.response_ready.connect(lambda r: print(f"💬 Resposta: {r}"))
    worker.error_occurred.connect(lambda e: print(f"❌ Erro: {e}"))
    
    # Processar comando de teste
    print("🧪 Testando AIWorker com comando simples...")
    worker.process_command("Olá, Jarvis!")
    
    # Manter app rodando até thread terminar
    worker.finished.connect(app.quit)
    
    sys.exit(app.exec())
