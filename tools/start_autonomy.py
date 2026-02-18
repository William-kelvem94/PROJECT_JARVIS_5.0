# --- Imports organizados ---
import sys
import os
import asyncio
import logging
import subprocess
import time
from contextlib import AsyncExitStack
from typing import Optional, Dict, Any

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Delayed imports to allow sys.path adjustment
try:
    from src.core.intelligence.ai_agent import AIAgent
    from src.core.audio.voice_controller import VoiceController
    from src.core.intelligence.brain_router import BrainRouter
except ImportError:
    # Mocks or fallbacks for analysis tools
    pass

# --- Configuração ---


def safe_execute(default=None, log_error=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logging.error(f"Error in {func.__name__}: {e}")
                return default
        return wrapper
    return decorator


class AutonomyConfig:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.health_check_interval = 60.0  # segundos
        self.max_retry_attempts = 3
        self.retry_delay = 5.0
        self.log_level = os.getenv("AUTONOMY_LOG_LEVEL", "INFO")
        self.enable_self_healing = (
            os.getenv("ENABLE_SELF_HEALING", "true").lower() == "true"
        )


# --- Logging estruturado ---


def setup_logging(config: AutonomyConfig):
    level = getattr(logging, config.log_level.upper(), logging.INFO)

    log_dir = os.path.join(config.project_root, "data", "logs")
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(log_dir, "autonomy.log"), encoding='utf-8'),
        ],
    )
    return logging.getLogger("Autonomy")


# --- Gestão de serviços ---


class ServiceManager:
    def __init__(self, config: AutonomyConfig):
        self.config = config
        self.services: Dict[str, Any] = {}
        self.health_status: Dict[str, bool] = {}
        self.logger = logging.getLogger("ServiceManager")

    async def start_service(
            self,
            name: str,
            service_instance,
            health_check_func=None):
        try:
            self.services[name] = service_instance
            if health_check_func:
                if asyncio.iscoroutinefunction(health_check_func):
                    is_healthy = await health_check_func()
                else:
                    is_healthy = health_check_func()
                self.health_status[name] = is_healthy
                return is_healthy
            self.health_status[name] = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to start {name}: {e}")
            self.health_status[name] = False
            return False

    async def periodic_health_check(self):
        while True:
            for name, service in self.services.items():
                # Implementar health checks específicos se necessário
                pass
            await asyncio.sleep(self.config.health_check_interval)


# --- Procedimentos de inicialização ---


async def run_init_procedures(config: AutonomyConfig, agent, logger):
    if config.enable_self_healing:
        await run_self_healing(config, logger)
    if hasattr(agent, "analyze_codebase"):
        logger.info("🔎 Starting codebase analysis...")
        asyncio.create_task(agent.analyze_codebase())
    else:
        logger.debug("Agent doesn't support codebase analysis")


async def run_self_healing(config: AutonomyConfig, logger):
    try:
        script_path = os.path.join(
            config.project_root, "tools", "self_healing.py")
        if os.path.exists(script_path):
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                logger.info("✅ Self-healing completed successfully")
            else:
                logger.warning(
                    f"Self-healing completed with warnings: {stderr.decode()}"
                )
        else:
            logger.warning("Self-healing script not found")
    except Exception as e:
        logger.error(f"Self-healing failed: {e}")


async def periodic_self_healing(config: AutonomyConfig):
    while True:
        await asyncio.sleep(config.health_check_interval * 10)
        await run_self_healing(config, logging.getLogger("PeriodicHealing"))


async def start_background_tasks(
        config: AutonomyConfig,
        agent,
        service_manager):
    tasks = []
    tasks.append(asyncio.create_task(service_manager.periodic_health_check()))
    if config.enable_self_healing:
        tasks.append(asyncio.create_task(periodic_self_healing(config)))
    return tasks


async def main_loop(config: AutonomyConfig, agent, service_manager, logger):
    while True:
        try:
            # Lógica principal do agente
            if not all(service_manager.health_status.values()):
                logger.warning("Some services are unhealthy")
            await asyncio.sleep(config.health_check_interval)
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            await asyncio.sleep(5)


# --- Loop principal ---


async def conscious_loop():
    config = AutonomyConfig()
    logger = setup_logging(config)

    try:
        from src.core.intelligence.ai_agent import AIAgent
        from src.core.audio.voice_controller import VoiceController
        from src.core.intelligence.brain_router import BrainRouter
    except ImportError as e:
        logger.error(f"Failed to import core modules: {e}")
        return

    async with AsyncExitStack() as stack:
        try:
            logger.info("🧠 Initializing Consciousness System...")
            service_manager = ServiceManager(config)

            brain = BrainRouter()
            # Assuming check_connectivity is async or sync, handled by ServiceManager
            brain_healthy = await service_manager.start_service(
                "brain", brain, getattr(brain, "check_connectivity", lambda: True)
            )
            if not brain_healthy:
                logger.warning(
                    "⚠️ Brain connectivity issues - fallback to local mode")

            voice = VoiceController()
            await service_manager.start_service("voice", voice)
            # await voice.speak("Consciousness initialized and systems operational.")

            agent = AIAgent()
            agent_status = await service_manager.start_service("agent", agent)

            if getattr(agent, "safe_mode", False):
                logger.error(
                    "❌ Agent started in SAFE MODE - functionality limited")
            elif not agent_status:
                logger.error("❌ Agent initialization failed")
                return

            await run_init_procedures(config, agent, logger)
            background_tasks = await start_background_tasks(
                config, agent, service_manager
            )

            logger.info("🚀 Autonomy System Fully Operational")
            await main_loop(config, agent, service_manager, logger)

        except KeyboardInterrupt:
            logger.info("Shutdown signal received...")
        except Exception as e:
            logger.error(f"Fatal error in autonomy loop: {e}")
            raise
        finally:
            logger.info("Cleaning up resources...")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    try:
        asyncio.run(conscious_loop())
    except KeyboardInterrupt:
        print("\nShutdown completed. Goodbye! 👋")
    except Exception as e:
        # logging might not be setup yet
        print(f"Application crashed: {e}")
        sys.exit(1)
