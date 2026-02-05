"""
JARVIS SINGULARITY - Orquestrador Completo
Integra HUD Transparente + AI Agent + Voice Controller
"""

import sys
import asyncio
import threading
import logging
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from src.interface.hud import JarvisHUD

# Importar componentes existentes
try:
    from src.core.ai_agent import AIAgent
    AI_AGENT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"AI Agent não disponível: {e}")
    AI_AGENT_AVAILABLE = False

try:
    from src.core.voice_controller import voice_controller
    VOICE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Voice Controller não disponível: {e}")
    VOICE_AVAILABLE = False

try:
    from src.core.camera_controller import camera_controller
    CAMERA_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Camera Controller não disponível: {e}")
    CAMERA_AVAILABLE = False

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis_singularity.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("JARVIS_SINGULARITY")


class SingularityCore:
    """
    Núcleo do JARVIS Singularity
    Gerencia HUD + AI Agent + Voice em threads separadas
    """
    
    def __init__(self):
        logger.info("🚀 Inicializando JARVIS Singularity...")
        
        # GUI (Thread Principal - obrigatório no Windows)
        self.app = QApplication(sys.argv)
        self.hud = JarvisHUD()
        
        # Cérebro (AI Agent existente)
        if AI_AGENT_AVAILABLE:
            try:
                self.brain = AIAgent(provider='gemini')
                logger.info("✅ AI Agent carregado")
            except Exception as e:
                logger.error(f"❌ Erro ao carregar AI Agent: {e}")
                self.brain = None
        else:
            self.brain = None
            logger.warning("⚠️ Rodando sem AI Agent")
        
        # Voice Controller
        self.voice = voice_controller if VOICE_AVAILABLE else None
        
        # Camera Controller
        self.camera = camera_controller if CAMERA_AVAILABLE else None
        
        self.running = True
        self.wake_word_active = False

    def on_wake_detected(self):
        """Callback quando wake word é detectado"""
        logger.info("🎤 Wake Word detectado!")
        self.hud.update_state("listening")
        
        # Obter usuário da câmera (se disponível)
        if self.camera:
            user_name = self.camera.last_seen_user
            if user_name:
                logger.info(f"👤 Usuário identificado: {user_name}")
        
        # Escutar comando
        if self.voice:
            self.voice.listen_once(on_command=self.on_command_received)

    def on_command_received(self, command_text: str):
        """Callback quando comando de voz é recebido"""
        logger.info(f"💬 Comando recebido: {command_text}")
        self.hud.update_state("thinking")
        
        # Processar com AI Agent
        if self.brain:
            try:
                # Executar em thread separada para não bloquear
                threading.Thread(
                    target=self._process_command,
                    args=(command_text,),
                    daemon=True
                ).start()
            except Exception as e:
                logger.error(f"❌ Erro ao processar comando: {e}")
                self.hud.update_state("error")
        else:
            logger.warning("⚠️ AI Agent não disponível")
            self.hud.update_state("error")

    def _process_command(self, command_text: str):
        """Processa comando em thread separada"""
        try:
            # Processar com AI Agent
            self.brain.process_command(command_text)
            
            # Voltar para idle
            self.hud.update_state("idle")
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento: {e}")
            self.hud.update_state("error")

    async def brain_loop(self):
        """
        Loop de processamento assíncrono do Cérebro
        """
        logger.info("🧠 Cérebro Iniciado (Loop Assíncrono)")
        
        # Inicialização
        self.hud.update_state("thinking")
        await asyncio.sleep(2)
        
        # Iniciar câmera (se disponível)
        if self.camera:
            try:
                logger.info("📷 Iniciando Camera Controller...")
                self.camera.start_monitoring()
                logger.info("✅ Camera Controller ativo")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao iniciar câmera: {e}")
        
        # Iniciar voice controller (se disponível)
        if self.voice:
            try:
                logger.info("🎤 Iniciando Voice Controller...")
                self.hud.update_state("listening")
                
                # Iniciar escuta de wake word em thread separada
                voice_thread = threading.Thread(
                    target=self._start_voice_listening,
                    daemon=True,
                    name="VoiceThread"
                )
                voice_thread.start()
                logger.info("✅ Voice Controller ativo")
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao iniciar voz: {e}")
        
        self.hud.update_state("idle")
        logger.info("✅ Sistema ONLINE")
        
        # Loop principal
        while self.running:
            try:
                # Manter loop vivo
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Erro no loop neural: {e}")
                self.hud.update_state("error")
                await asyncio.sleep(1)

    def _start_voice_listening(self):
        """Inicia escuta de wake word em thread separada"""
        try:
            if self.voice:
                logger.info("👂 Escutando wake word...")
                self.voice.listen_for_wake_word(on_wake=self.on_wake_detected)
        except Exception as e:
            logger.error(f"❌ Erro na escuta de voz: {e}")

    def start(self):
        """
        Inicia o sistema completo
        - GUI na Thread Principal
        - Cérebro em Thread Secundária (asyncio)
        """
        logger.info("🎯 Iniciando Protocolo Singularity...")
        
        # Criar loop de eventos para o cérebro numa thread separada
        brain_thread = threading.Thread(
            target=self._run_async_loop,
            daemon=True,
            name="BrainThread"
        )
        brain_thread.start()
        logger.info("🧵 Brain Thread iniciada")
        
        # GUI assume o controle da Thread Principal (Obrigatório no Windows)
        logger.info("🖥️ Iniciando HUD...")
        sys.exit(self.app.exec())

    def _run_async_loop(self):
        """Executa loop assíncrono em thread separada"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.brain_loop())
        except Exception as e:
            logger.error(f"❌ Erro fatal no brain loop: {e}")
        finally:
            loop.close()

    def shutdown(self):
        """Desliga o sistema gracefully"""
        logger.info("🛑 Desligando JARVIS...")
        self.running = False
        self.app.quit()


def main():
    """Entry point principal"""
    try:
        core = SingularityCore()
        core.start()
    except KeyboardInterrupt:
        logger.info("⚠️ Interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
