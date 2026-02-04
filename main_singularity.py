"""
JARVIS SINGULARITY - Main Orchestrator
Entry point único do sistema
"""

import asyncio
import logging
import sys
import signal
from pathlib import Path
import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis_singularity.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class JarvisSingularity:
    """Orquestrador principal"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.running = False
        self.modules = {}
        
        logger.info("="*60)
        logger.info("  JARVIS SINGULARITY - INICIANDO")
        logger.info("="*60)
    
    def _load_config(self, config_path: str) -> dict:
        """Carrega configuração"""
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
            logger.info(f"✅ Config carregado: {config_path}")
            return config
        except Exception as e:
            logger.error(f"❌ Erro ao carregar config: {e}")
            return {}
    
    async def initialize(self):
        """Inicializa todos os módulos"""
        logger.info("\n🚀 INICIALIZANDO MÓDULOS...")
        
        # 1. Hive Mind
        if self.config.get('hive_mind', {}).get('enabled', True):
            await self._init_hive_mind()
        
        # 2. Brain
        await self._init_brain()
        
        # 3. Senses
        await self._init_senses()
        
        # 4. Mouth
        await self._init_mouth()
        
        # 5. World
        if self.config.get('world', {}).get('fauxmo_enabled', False):
            await self._init_world()
        
        # 6. Interface
        if self.config.get('interface', {}).get('hud_enabled', True):
            await self._init_interface()
        
        # 7. Guardian
        if self.config.get('guardian', {}).get('watchdog_enabled', True):
            await self._init_guardian()
        
        logger.info("\n✅ TODOS OS MÓDULOS INICIALIZADOS!\n")
    
    async def _init_hive_mind(self):
        """Inicializa Hive Mind"""
        logger.info("🌐 Inicializando Hive Mind...")
        
        try:
            from jarvis_core.hive_mind import rclone_sync, hybrid_memory, LockfileManager
            
            # Sync inicial
            await rclone_sync.startup_sync()
            
            # Lockfile
            device_id = self.config.get('device_id', 'unknown')
            lockfile = LockfileManager(device_id)
            await lockfile.acquire_lock()
            
            self.modules['hive_mind'] = {
                'rclone': rclone_sync,
                'memory': hybrid_memory,
                'lockfile': lockfile
            }
            
            logger.info("  ✅ Hive Mind pronto")
        except Exception as e:
            logger.error(f"  ❌ Erro Hive Mind: {e}")
    
    async def _init_brain(self):
        """Inicializa Brain"""
        logger.info("🧠 Inicializando Brain...")
        
        try:
            from jarvis_core.brain import get_router, context_manager, dev_buddy
            
            # Neural Router
            groq_key = self.config.get('brain', {}).get('groq_api_key')
            gemini_key = self.config.get('brain', {}).get('gemini_api_key')
            
            router = get_router(groq_key, gemini_key)
            
            self.modules['brain'] = {
                'router': router,
                'context': context_manager,
                'dev_buddy': dev_buddy
            }
            
            logger.info("  ✅ Brain pronto")
        except Exception as e:
            logger.error(f"  ❌ Erro Brain: {e}")
    
    async def _init_senses(self):
        """Inicializa Senses"""
        logger.info("👁️ Inicializando Senses...")
        
        try:
            from jarvis_core.senses import neural_touch, action_dispatcher
            from jarvis_core.senses.vision_hybrid import vision_system
            from jarvis_core.senses.hearing import hearing
            from jarvis_core.senses.screen_monitor import screen_monitor
            
            self.modules['senses'] = {
                'touch': neural_touch,
                'dispatcher': action_dispatcher,
                'vision': vision_system,
                'hearing': hearing,
                'monitor': screen_monitor
            }
            
            logger.info("  ✅ Senses pronto")
        except Exception as e:
            logger.error(f"  ❌ Erro Senses: {e}")
    
    async def _init_mouth(self):
        """Inicializa Mouth"""
        logger.info("🗣️ Inicializando Mouth...")
        
        try:
            from jarvis_core.mouth import get_tts, BargeIn
            from jarvis_core.mouth.voice_modulation import voice_modulation
            
            # TTS
            engine = self.config.get('mouth', {}).get('tts_engine', 'edge')
            voice = self.config.get('mouth', {}).get('voice', 'pt-BR-FranciscaNeural')
            
            tts = get_tts(engine, voice)
            
            # Barge-in
            barge_in = BargeIn(tts)
            
            self.modules['mouth'] = {
                'tts': tts,
                'barge_in': barge_in,
                'modulation': voice_modulation
            }
            
            logger.info("  ✅ Mouth pronto")
        except Exception as e:
            logger.error(f"  ❌ Erro Mouth: {e}")
    
    async def _init_world(self):
        """Inicializa World"""
        logger.info("🏠 Inicializando World...")
        
        try:
            from jarvis_core.world import alexa_bridge
            from jarvis_core.world.tuya_control import smart_home
            from jarvis_core.world.automation_scenes import automation_scenes
            
            # Fauxmo
            alexa_bridge.start_server()
            
            self.modules['world'] = {
                'alexa': alexa_bridge,
                'smart_home': smart_home,
                'scenes': automation_scenes
            }
            
            logger.info("  ✅ World pronto")
        except Exception as e:
            logger.error(f"  ❌ Erro World: {e}")
    
    async def _init_interface(self):
        """Inicializa Interface"""
        logger.info("🖥️ Inicializando Interface...")
        
        try:
            from jarvis_core.interface import get_hud
            from jarvis_core.interface.orb_animation import orb_animation
            from jarvis_core.interface.targeting_system import targeting_system
            from jarvis_core.interface.notification_system import notification_system
            from jarvis_core.interface.theme_manager import theme_manager
            
            # HUD
            transparency = self.config.get('interface', {}).get('transparency', 0.9)
            hud = get_hud(transparency)
            
            self.modules['interface'] = {
                'hud': hud,
                'orb': orb_animation,
                'targeting': targeting_system,
                'notifications': notification_system,
                'themes': theme_manager
            }
            
            logger.info("  ✅ Interface pronto")
        except Exception as e:
            logger.error(f"  ❌ Erro Interface: {e}")
    
    async def _init_guardian(self):
        """Inicializa Guardian"""
        logger.info("🛡️ Inicializando Guardian...")
        
        try:
            from jarvis_core.guardian import system_watchdog, privacy_filter
            from jarvis_core.guardian.safe_mode import safe_mode
            from jarvis_core.guardian.health_monitor import health_monitor
            from jarvis_core.guardian.error_recovery import error_recovery
            
            self.modules['guardian'] = {
                'watchdog': system_watchdog,
                'privacy': privacy_filter,
                'safe_mode': safe_mode,
                'health': health_monitor,
                'recovery': error_recovery
            }
            
            logger.info("  ✅ Guardian pronto")
        except Exception as e:
            logger.error(f"  ❌ Erro Guardian: {e}")
    
    async def run(self):
        """Loop principal"""
        self.running = True
        
        logger.info("\n" + "="*60)
        logger.info("  JARVIS SINGULARITY ONLINE")
        logger.info("="*60 + "\n")
        
        # Notificação de startup
        if 'interface' in self.modules:
            self.modules['interface']['notifications'].success("JARVIS Singularity Online!")
        
        # Loop principal
        try:
            while self.running:
                # Heartbeat sync
                if 'hive_mind' in self.modules:
                    await self.modules['hive_mind']['rclone'].heartbeat_sync()
                
                # Health check
                if 'guardian' in self.modules:
                    health = self.modules['guardian']['health'].get_full_status()
                    if health['health_score'] < 50:
                        logger.warning(f"⚠️ Saúde baixa: {health['health_score']}/100")
                
                await asyncio.sleep(300)  # 5 minutos
                
        except KeyboardInterrupt:
            logger.info("\n⚠️ Interrupção detectada...")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Desligamento gracioso"""
        logger.info("\n🛑 DESLIGANDO JARVIS SINGULARITY...")
        
        self.running = False
        
        # Sync final
        if 'hive_mind' in self.modules:
            await self.modules['hive_mind']['rclone'].shutdown_sync()
            await self.modules['hive_mind']['lockfile'].release_lock()
        
        logger.info("✅ Shutdown completo\n")


async def main():
    """Entry point"""
    # Verificar argumentos
    safe_mode_arg = "--safe-mode" in sys.argv
    
    if safe_mode_arg:
        logger.warning("🛡️ INICIANDO EM SAFE MODE")
        from jarvis_core.guardian.safe_mode import safe_mode
        safe_mode.enter_safe_mode()
    
    # Criar e executar
    jarvis = JarvisSingularity()
    
    # Signal handlers
    def signal_handler(sig, frame):
        logger.info("\n⚠️ Signal recebido, desligando...")
        asyncio.create_task(jarvis.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Inicializar e executar
    await jarvis.initialize()
    await jarvis.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"💥 ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
