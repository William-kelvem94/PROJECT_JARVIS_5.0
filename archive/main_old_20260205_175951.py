# ============================================================================
# JARVIS SINGULARITY V2 - Main Entry Point (QThread Architecture)
# ============================================================================
# Versão melhorada usando AIWorker (QThread) ao invés de threading.Thread
# Solução cirúrgica conforme auditoria forense
# ============================================================================

import sys
import signal
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QObject

# -------------------------------------------------------------------------
# PATH SETUP
# -------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# -------------------------------------------------------------------------
# IMPORTS
# -------------------------------------------------------------------------
print("🔧 Carregando módulos...")

# AIWorker (QThread wrapper)
try:
    from interface.ai_worker import AIWorker
    print("✅ AIWorker (QThread) carregado")
except ImportError as e:
    print(f"❌ ERRO CRÍTICO: AIWorker não encontrado: {e}")
    print("   Certifique-se de que src/interface/ai_worker.py existe")
    sys.exit(1)

# HUD
try:
    from interface.hud import JarvisHUD
    print("✅ HUD carregado de interface.hud")
    HUD_CLASS = JarvisHUD
except ImportError:
    try:
        from interface.transparent_hud import TransparentHUD
        print("✅ HUD carregado de interface.transparent_hud")
        HUD_CLASS = TransparentHUD
    except ImportError as e:
        print(f"⚠️ HUD não encontrado: {e}")
        print("   Usando HUD Mock para testes")
        
        # HUD Mock
        from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
        
        class MockHUD(QWidget):
            """HUD Mock - Substitua pelo HUD real"""
            def __init__(self):
                super().__init__()
                self.setWindowTitle("JARVIS HUD (Mock)")
                self.setGeometry(100, 100, 600, 400)
                self.setStyleSheet("background-color: #1a1a1a; color: white;")
                
                layout = QVBoxLayout()
                
                # Status
                self.status_label = QLabel("⚪ Status: IDLE")
                self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
                layout.addWidget(self.status_label)
                
                # Response
                self.response_label = QLabel("Aguardando comando...")
                self.response_label.setWordWrap(True)
                self.response_label.setStyleSheet("font-size: 16px; padding: 20px;")
                layout.addWidget(self.response_label)
                
                self.setLayout(layout)
            
            def update_state(self, state: str):
                """Atualiza estado visual (compatível com HUD real)"""
                state_map = {
                    "idle": ("⚪", "IDLE", "#808080"),
                    "listening": ("🟢", "OUVINDO", "#00ff00"),
                    "thinking": ("🔵", "PENSANDO", "#0080ff"),
                    "speaking": ("🟢", "FALANDO", "#00ff00"),
                    "error": ("🔴", "ERRO", "#ff0000")
                }
                
                emoji, text, color = state_map.get(state, ("⚪", state.upper(), "#ffffff"))
                self.status_label.setText(f"{emoji} Status: {text}")
                self.status_label.setStyleSheet(f"font-size: 24px; font-weight: bold; padding: 20px; color: {color};")
            
            def show_response(self, response: str):
                """Mostra resposta do AI"""
                self.response_label.setText(f"💬 {response}")
            
            def show_error(self, error: str):
                """Mostra erro"""
                self.response_label.setText(f"❌ ERRO: {error}")
                self.response_label.setStyleSheet("font-size: 16px; padding: 20px; color: #ff0000;")
        
        HUD_CLASS = MockHUD

# Voice Controller (opcional)
try:
    from core.voice_controller import voice_controller
    VOICE_AVAILABLE = True
    print("✅ Voice Controller disponível")
except ImportError:
    VOICE_AVAILABLE = False
    print("⚠️ Voice Controller não disponível (modo texto)")


# ============================================================================
# JARVIS SINGULARITY V2 APPLICATION
# ============================================================================
class JarvisSingularityV2(QObject):
    """
    Aplicação JARVIS Singularity usando arquitetura QThread.
    
    **DIFERENÇAS DA V1:**
    - Usa AIWorker (QThread) ao invés de threading.Thread
    - Sinais PyQt6 nativos para comunicação thread-safe
    - Melhor integração com event loop do Qt
    - Shutdown gracioso garantido
    
    **MAPEAMENTO DE ESTADOS (conforme solicitado):**
    - idle: Cinza (⚪)
    - listening: Verde (🟢) - Ouvindo comando
    - thinking: Azul (🔵) - Processando com AI
    - speaking: Verde (🟢) - Falando resposta
    - error: Vermelho (🔴)
    """
    
    def __init__(self):
        """Inicializa a aplicação"""
        super().__init__()  # CRITICAL: Initialize QObject
        
        print("\n" + "="*70)
        print("🚀 JARVIS SINGULARITY V2 - Arquitetura QThread")
        print("="*70 + "\n")
        
        # QApplication
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("JARVIS Singularity V2")
        self.app.setStyle("Fusion")
        
        # Componentes
        self.hud = None
        self.ai_worker = None
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def initialize(self):
        """Inicializa todos os componentes"""
        print("📋 Sequência de Inicialização:\n")
        
        # 1. HUD
        print("1️⃣ Criando HUD...")
        self.hud = HUD_CLASS()
        self.hud.show()
        print("   ✅ HUD ativo\n")
        
        # 2. AI Worker
        print("2️⃣ Criando AI Worker (QThread)...")
        try:
            self.ai_worker = AIWorker()
            print("   ✅ AI Worker criado\n")
        except RuntimeError as e:
            print(f"   ❌ ERRO: {e}")
            print("   Verifique se src/core/ai_agent.py existe")
            sys.exit(1)
        
        # 3. Conectar Sinais
        print("3️⃣ Conectando sinais PyQt6...")
        self._connect_signals()
        print("   ✅ Sinais conectados\n")
        
        # 4. Modo de Entrada
        if VOICE_AVAILABLE:
            print("4️⃣ Modo: VOZ (wake word)")
            self._setup_voice_mode()
        else:
            print("4️⃣ Modo: TEXTO (console)")
            self._setup_text_mode()
        
        print("\n" + "="*70)
        print("✅ SISTEMA ONLINE - Aguardando comandos...")
        print("="*70 + "\n")
        
        # Estado inicial
        self.hud.update_state("idle")
    
    def _connect_signals(self):
        """
        Conecta sinais do AIWorker ao HUD.
        
        SINAIS:
        - status_changed → update_state (muda cor do reator)
        - response_ready → show_response (exibe resposta)
        - error_occurred → show_error (exibe erro)
        """
        # Status changes
        self.ai_worker.status_changed.connect(self._on_status_changed)
        
        # Response ready
        self.ai_worker.response_ready.connect(self._on_response_ready)
        
        # Errors
        self.ai_worker.error_occurred.connect(self._on_error)
        
        # Progress (debug)
        self.ai_worker.progress_update.connect(
            lambda msg: print(f"📊 {msg}")
        )
    
    @pyqtSlot(str)
    def _on_status_changed(self, status: str):
        """Handler para mudanças de status"""
        print(f"📡 Status: {status.upper()}")
        self.hud.update_state(status)
    
    @pyqtSlot(str)
    def _on_response_ready(self, response: str):
        """Handler para resposta pronta"""
        print(f"💬 Resposta: {response[:100]}...")
        
        # Mostrar no HUD (se tiver método show_response)
        if hasattr(self.hud, 'show_response'):
            self.hud.show_response(response)
    
    @pyqtSlot(str)
    def _on_error(self, error: str):
        """Handler para erros"""
        print(f"❌ ERRO: {error}")
        
        # Mostrar no HUD (se tiver método show_error)
        if hasattr(self.hud, 'show_error'):
            self.hud.show_error(error)
    
    def _setup_voice_mode(self):
        """Configura modo de voz (wake word)"""
        # TODO: Implementar integração com voice_controller
        # Exemplo:
        # def on_wake():
        #     self.hud.update_state("listening")
        #     voice_controller.listen_once(on_command=self._process_voice_command)
        # 
        # def _process_voice_command(self, command: str):
        #     self.ai_worker.process_command(command)
        # 
        # voice_controller.listen_for_wake_word(on_wake=on_wake)
        
        print("   ⚠️ Voice mode não implementado ainda")
        print("   Usando modo texto como fallback\n")
        self._setup_text_mode()
    
    def _setup_text_mode(self):
        """Configura modo texto (console input)"""
        def prompt_command():
            """Solicita comando via console"""
            print("\n" + "-"*70)
            try:
                command = input("💬 Digite um comando (ou 'sair'): ").strip()
            except EOFError:
                # Ctrl+D ou EOF
                self.app.quit()
                return
            
            if command.lower() in ['sair', 'exit', 'quit', 'q']:
                print("👋 Encerrando...")
                self.app.quit()
                return
            
            if command:
                print(f"🚀 Processando: '{command}'")
                self.ai_worker.process_command(command)
            
            # Próximo prompt após 1s
            QTimer.singleShot(1000, prompt_command)
        
        # Primeiro prompt após 2s (dar tempo para inicialização)
        QTimer.singleShot(2000, prompt_command)
    
    def _signal_handler(self, signum, frame):
        """Handler para SIGINT/SIGTERM (Ctrl+C)"""
        print("\n\n⚠️ Sinal de interrupção recebido")
        print("🛑 Encerrando graciosamente...\n")
        
        # Parar AI Worker
        if self.ai_worker:
            print("   Parando AI Worker...")
            self.ai_worker.stop()
        
        # Fechar app
        self.app.quit()
    
    def run(self):
        """Executa o loop principal"""
        return self.app.exec()


# ============================================================================
# ENTRY POINT
# ============================================================================
def main():
    """Função principal"""
    try:
        app = JarvisSingularityV2()
        app.initialize()
        sys.exit(app.run())
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


# ============================================================================
# GUIA DE USO
# ============================================================================
"""
INSTALAÇÃO:
-----------
pip install -r requirements_singularity.txt

CONFIGURAÇÃO:
-------------
# Windows
set GOOGLE_API_KEY=sua_chave_aqui

# Linux/Mac
export GOOGLE_API_KEY=sua_chave_aqui

EXECUÇÃO:
---------
python main_singularity_v2.py

TESTES:
-------
1. Teste básico (sem AI):
   - Execute e digite "olá"
   - Verifique se HUD muda de cor (idle → thinking → speaking → idle)

2. Teste com AI:
   - Configure GOOGLE_API_KEY
   - Digite "qual é a capital do Brasil?"
   - Aguarde resposta (pode demorar 5-30s)

3. Teste de bloqueio:
   - Digite comando longo
   - Tente mover janela do HUD
   - UI deve permanecer responsiva (não congelar)

INTEGRAÇÃO COM HUD REAL:
-------------------------
Substitua MockHUD pelo seu HUD real. Certifique-se de que tem:

class SeuHUD:
    def update_state(self, state: str):
        # state: "idle" | "listening" | "thinking" | "speaking" | "error"
        # Mude cor do reator:
        # - thinking: Azul
        # - listening/speaking: Verde
        pass
    
    def show_response(self, response: str):  # Opcional
        pass
    
    def show_error(self, error: str):  # Opcional
        pass

TROUBLESHOOTING:
----------------
❌ "AIWorker não encontrado"
   → Verifique se src/interface/ai_worker.py existe

❌ "ai_agent não foi importado"
   → Verifique se src/core/ai_agent.py existe
   → Verifique se requirements estão instalados

❌ UI congela
   → Verifique se está usando main_singularity_v2.py (QThread)
   → NÃO use main_singularity.py (threading.Thread)

❌ Sem resposta do AI
   → Verifique GOOGLE_API_KEY
   → Verifique logs em jarvis_singularity.log
   → Teste Ollama: http://localhost:11434

PRÓXIMOS PASSOS:
----------------
1. Implementar _setup_voice_mode() com voice_controller
2. Integrar camera_controller para detecção de usuário
3. Adicionar feedback visual no HUD (animações)
4. Implementar cancelamento de comandos
"""
