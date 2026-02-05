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
        
        # HUD Mock - Modern Premium Design
        from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer, QRect
        from PyQt6.QtGui import QFont
        
        class MockHUD(QWidget):
            """
            HUD Mock - Modern Premium Design
            Inspired by Iron Man's JARVIS interface
            Features: Glassmorphism, Animations, Gradients
            """
            def __init__(self):
                super().__init__()
                
                # Window setup
                self.setWindowTitle("J.A.R.V.I.S. Singularity")
                self.setGeometry(100, 100, 800, 500)
                
                # Modern glassmorphism style
                self.setStyleSheet("""
                    QWidget {
                        background: qlineargradient(
                            x1:0, y1:0, x2:1, y2:1,
                            stop:0 rgba(10, 15, 30, 240),
                            stop:0.5 rgba(15, 25, 45, 240),
                            stop:1 rgba(10, 15, 30, 240)
                        );
                        border-radius: 20px;
                        border: 2px solid rgba(100, 150, 255, 0.3);
                    }
                    QLabel {
                        background: transparent;
                        color: white;
                    }
                """)
                
                # Main layout
                main_layout = QVBoxLayout()
                main_layout.setContentsMargins(40, 40, 40, 40)
                main_layout.setSpacing(30)
                
                # ============================================================
                # HEADER - JARVIS Logo
                # ============================================================
                header = QLabel("J.A.R.V.I.S.")
                header.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
                header.setStyleSheet("""
                    color: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00d4ff,
                        stop:0.5 #0080ff,
                        stop:1 #00d4ff
                    );
                    padding: 10px;
                    letter-spacing: 8px;
                """)
                header.setAlignment(Qt.AlignmentFlag.AlignCenter)
                main_layout.addWidget(header)
                
                # ============================================================
                # REACTOR CORE - Animated Status Indicator
                # ============================================================
                reactor_container = QHBoxLayout()
                reactor_container.setSpacing(20)
                
                # Reactor circle (animated)
                self.reactor = QLabel("●")
                self.reactor.setFont(QFont("Segoe UI", 72))
                self.reactor.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.reactor.setStyleSheet("""
                    color: #808080;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 80px;
                    padding: 20px;
                    min-width: 160px;
                    min-height: 160px;
                """)
                
                # Opacity animation setup
                self.reactor_effect = QGraphicsOpacityEffect()
                self.reactor.setGraphicsEffect(self.reactor_effect)
                self.reactor_animation = QPropertyAnimation(self.reactor_effect, b"opacity")
                self.reactor_animation.setDuration(1500)
                self.reactor_animation.setStartValue(0.3)
                self.reactor_animation.setEndValue(1.0)
                self.reactor_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
                self.reactor_animation.setLoopCount(-1)  # Infinite loop
                
                reactor_container.addStretch()
                reactor_container.addWidget(self.reactor)
                reactor_container.addStretch()
                main_layout.addLayout(reactor_container)
                
                # ============================================================
                # STATUS TEXT
                # ============================================================
                self.status_label = QLabel("SISTEMA IDLE")
                self.status_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
                self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.status_label.setStyleSheet("""
                    color: #808080;
                    padding: 15px;
                    background: rgba(255, 255, 255, 0.03);
                    border-radius: 10px;
                    letter-spacing: 3px;
                """)
                main_layout.addWidget(self.status_label)
                
                # ============================================================
                # RESPONSE AREA
                # ============================================================
                self.response_label = QLabel("Aguardando comando...")
                self.response_label.setFont(QFont("Segoe UI", 14))
                self.response_label.setWordWrap(True)
                self.response_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.response_label.setStyleSheet("""
                    color: rgba(255, 255, 255, 0.7);
                    padding: 20px;
                    background: rgba(0, 0, 0, 0.3);
                    border-radius: 15px;
                    border: 1px solid rgba(100, 150, 255, 0.2);
                    min-height: 80px;
                """)
                main_layout.addWidget(self.response_label)
                
                main_layout.addStretch()
                self.setLayout(main_layout)
                
                # Start idle animation
                self._start_idle_pulse()
            
            def _start_idle_pulse(self):
                """Inicia animação de pulsação idle"""
                self.reactor_animation.start()
            
            def _stop_pulse(self):
                """Para animação de pulsação"""
                self.reactor_animation.stop()
                self.reactor_effect.setOpacity(1.0)
            
            def update_state(self, state: str):
                """Atualiza estado visual com animações"""
                state_map = {
                    "idle": {
                        "text": "SISTEMA IDLE",
                        "color": "#808080",
                        "reactor": "#808080",
                        "glow": "rgba(128, 128, 128, 0.3)",
                        "animate": True
                    },
                    "listening": {
                        "text": "OUVINDO COMANDO",
                        "color": "#00ff88",
                        "reactor": "#00ff88",
                        "glow": "rgba(0, 255, 136, 0.5)",
                        "animate": False
                    },
                    "thinking": {
                        "text": "PROCESSANDO...",
                        "color": "#00d4ff",
                        "reactor": "#00d4ff",
                        "glow": "rgba(0, 212, 255, 0.6)",
                        "animate": True
                    },
                    "speaking": {
                        "text": "RESPONDENDO",
                        "color": "#00ff88",
                        "reactor": "#00ff88",
                        "glow": "rgba(0, 255, 136, 0.5)",
                        "animate": False
                    },
                    "error": {
                        "text": "ERRO DETECTADO",
                        "color": "#ff3366",
                        "reactor": "#ff3366",
                        "glow": "rgba(255, 51, 102, 0.6)",
                        "animate": True
                    }
                }
                
                config = state_map.get(state, state_map["idle"])
                
                # Update status text
                self.status_label.setText(config["text"])
                self.status_label.setStyleSheet(f"""
                    color: {config['color']};
                    padding: 15px;
                    background: rgba(255, 255, 255, 0.03);
                    border-radius: 10px;
                    letter-spacing: 3px;
                    text-shadow: 0 0 20px {config['glow']};
                """)
                
                # Update reactor
                self.reactor.setStyleSheet(f"""
                    color: {config['reactor']};
                    background: {config['glow']};
                    border-radius: 80px;
                    padding: 20px;
                    min-width: 160px;
                    min-height: 160px;
                    box-shadow: 0 0 40px {config['glow']};
                """)
                
                # Animation control
                if config["animate"]:
                    self._start_idle_pulse()
                else:
                    self._stop_pulse()
            
            def show_response(self, response: str):
                """Mostra resposta do AI com fade-in"""
                # Truncate if too long
                display_text = response[:200] + "..." if len(response) > 200 else response
                self.response_label.setText(f"💬 {display_text}")
                
                # Fade-in animation
                effect = QGraphicsOpacityEffect()
                self.response_label.setGraphicsEffect(effect)
                anim = QPropertyAnimation(effect, b"opacity")
                anim.setDuration(500)
                anim.setStartValue(0.0)
                anim.setEndValue(1.0)
                anim.start()
            
            def show_error(self, error: str):
                """Mostra erro com destaque"""
                self.response_label.setText(f"❌ ERRO: {error}")
                self.response_label.setStyleSheet("""
                    color: #ff3366;
                    padding: 20px;
                    background: rgba(255, 51, 102, 0.1);
                    border-radius: 15px;
                    border: 2px solid rgba(255, 51, 102, 0.5);
                    min-height: 80px;
                    font-weight: bold;
                """)
        
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
        """
        Configura modo de voz completo com wake word detection.
        
        FLUXO:
        1. Aguarda wake word ("Jarvis")
        2. HUD → listening (verde)
        3. Captura comando de voz
        4. Envia para AIWorker
        5. HUD → thinking (azul)
        6. Resposta pronta → HUD → speaking (verde)
        7. Volta para aguardar wake word
        """
        print("   🎤 Configurando modo de voz...")
        
        # Verificar se voice_controller tem métodos necessários
        if not hasattr(voice_controller, 'listen_for_wake_word'):
            print("   ⚠️ voice_controller.listen_for_wake_word() não disponível")
            print("   Usando modo texto como fallback\n")
            self._setup_text_mode()
            return
        
        print("   ✅ Wake word detection ativo")
        print("   💡 Diga 'Jarvis' para ativar\n")
        
        def on_wake_word_detected():
            """Callback quando wake word é detectado"""
            print("\n🎤 Wake word detectado! Ouvindo comando...")
            self.hud.update_state("listening")
            
            # Aguardar 500ms para dar tempo do HUD atualizar
            QTimer.singleShot(500, self._listen_for_command)
        
        def _listen_for_command_impl():
            """Captura comando de voz"""
            try:
                # Usar método do voice_controller para capturar áudio
                if hasattr(voice_controller, 'listen_once'):
                    command = voice_controller.listen_once()
                elif hasattr(voice_controller, 'listen'):
                    command = voice_controller.listen()
                else:
                    # Fallback: usar SpeechRecognition diretamente
                    import speech_recognition as sr
                    recognizer = sr.Recognizer()
                    with sr.Microphone() as source:
                        print("   🎧 Ajustando ruído ambiente...")
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        print("   🎤 Pode falar...")
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    print("   🔄 Processando áudio...")
                    try:
                        command = recognizer.recognize_google(audio, language="pt-BR")
                    except sr.UnknownValueError:
                        command = None
                    except sr.RequestError:
                        # Fallback para inglês
                        command = recognizer.recognize_google(audio, language="en-US")
                
                if command:
                    print(f"   ✅ Comando capturado: '{command}'\n")
                    
                    # Processar comando
                    self.ai_worker.process_command(command)
                    
                    # Aguardar resposta e voltar para listening
                    QTimer.singleShot(2000, self._restart_wake_word_detection)
                else:
                    print("   ⚠️ Nenhum comando detectado")
                    self.hud.update_state("idle")
                    # Voltar para wake word detection
                    QTimer.singleShot(1000, self._restart_wake_word_detection)
                    
            except Exception as e:
                print(f"   ❌ Erro ao capturar comando: {e}")
                self.hud.update_state("error")
                # Voltar para wake word detection após erro
                QTimer.singleShot(2000, self._restart_wake_word_detection)
        
        # Armazenar referência para usar em callbacks
        self._listen_for_command = _listen_for_command_impl
        
        def _restart_wake_word_impl():
            """Reinicia detecção de wake word"""
            print("🔊 Aguardando wake word 'Jarvis'...")
            self.hud.update_state("idle")
            
            # Reiniciar loop de wake word
            QTimer.singleShot(100, lambda: voice_controller.listen_for_wake_word(
                callback=on_wake_word_detected,
                wake_word="jarvis"
            ))
        
        self._restart_wake_word_detection = _restart_wake_word_impl
        
        # Iniciar detecção de wake word
        try:
            voice_controller.listen_for_wake_word(
                callback=on_wake_word_detected,
                wake_word="jarvis"
            )
        except Exception as e:
            print(f"   ❌ Erro ao iniciar wake word detection: {e}")
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
        
        # Force exit após 3s se não encerrar
        def force_exit():
            print("\n⚠️ Forçando encerramento...")
            import os
            os._exit(0)
        
        QTimer.singleShot(3000, force_exit)
    
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
