import psutil
import platform
import os
import asyncio
from typing import Dict, Any, Optional
from loguru import logger

class DeviceAwareness:
    """
    Omega-Brain Hardware Consciousness.
    Implements Hardware Profiles, Resource Governing, and Lazy Loading support.
    """

    def __init__(self, cpu_threshold_balanced=50, cpu_threshold_overload=85, ram_threshold_overload=90):
        self.cpu_threshold_balanced = cpu_threshold_balanced
        self.cpu_threshold_overload = cpu_threshold_overload
        self.ram_threshold_overload = ram_threshold_overload

        # Hardware Profile state
        self.profile = self._detect_hardware_profile()
        self.current_state = "Ocioso"
        self.last_governor_action = None

    def _detect_hardware_profile(self) -> Dict[str, Any]:
        """
        Detects if the system is a Laptop or Desktop and sets the priority engine.
        """
        # Basic heuristic: check for battery presence or common laptop indicators
        is_laptop = False
        try:
            # On Windows, we can check for battery via psutil or shell
            if platform.system() == "Windows":
                # Simple check: if psutil.sensors_battery() returns something, it's likely a laptop/UPS
                if psutil.sensors_battery():
                    is_laptop = True
            elif platform.system() == "Linux":
                if os.path.exists("/sys/class/power_supply/BAT0") or os.path.exists("/sys/class/power_supply/BAT1"):
                    is_laptop = True
        except Exception as e:
            logger.warning(f"Hardware detection error: {e}. Defaulting to Desktop profile.")

        if is_laptop:
            profile = {
            "type": "Laptop",
            "priority_engine": "OpenVINO",
            "quantization": "int8",
            "max_local_model_size": "7B",
            "aggressive_offloading": True
        }
        else:
            profile = {
                "type": "Desktop",
                "priority_engine": "CUDA",
                "quantization": "fp16",
                "max_local_model_size": "30B",
                "aggressive_offloading": False
            }

        logger.info(f"Hardware Profile Materialized: {profile['type']} (Priority: {profile['priority_engine']})")
        return profile

    def get_system_state(self) -> str:
        """
        Analyzes hardware metrics to define the current psyche mode.
        Returns: 'Ocioso', 'Equilibrado', or 'Sobrecarga'.
        """
        cpu_usage = psutil.cpu_percent(interval=0.1)
        ram_usage = psutil.virtual_memory().percent

        if cpu_usage >= self.cpu_threshold_overload or ram_usage >= self.ram_threshold_overload:
            state = "Sobrecarga"
        elif cpu_usage >= self.cpu_threshold_balanced:
            state = "Equilibrado"
        else:
            state = "Ocioso"

        self.current_state = state
        return state

    async def resource_governor_loop(self, callback_fn=None):
        """
        Real-time monitor that triggers operational mode changes based on resource pressure.
        """
        logger.info("Resource Governor activated.")
        while True:
            try:
                state = self.get_system_state()

                # Logic for dynamic mode alteration
                if state == "Sobrecarga":
                    action = "MIGRATE_TO_LIGHTWEIGHT_API"
                elif state == "Equilibrado":
                    action = "BALANCED_LOCAL_CLOUD"
                else:
                    action = "MAX_LOCAL_PERFORMANCE"

                if action != self.last_governor_action:
                    logger.warning(f"Governor Trigger: System state {state} -> Action: {action}")
                    self.last_governor_action = action
                    if callback_fn:
                        await callback_fn(action, state)

                await asyncio.sleep(5) # Monitor every 5 seconds
            except Exception as e:
                logger.error(f"Governor error: {e}")
                await asyncio.sleep(10)

    def should_load_module(self, module_requirements: Dict[str, Any]) -> bool:
        """
        Lazy Loading Guard: Checks if the hardware profile supports a specific module.
        Example module_requirements: {"min_ram_gb": 16, "required_engine": "CUDA"}
        """
        # RAM check
        available_ram = psutil.virtual_memory().total / (1024**3)
        if "min_ram_gb" in module_requirements and available_ram < module_requirements["min_ram_gb"]:
            logger.info(f"Lazy Loading: Module rejected due to RAM ({available_ram:.2f}GB < {module_requirements['min_ram_gb']}GB)")
            return False

        # Engine check
        if "required_engine" in module_requirements:
            if self.profile["priority_engine"] != module_requirements["required_engine"]:
                # Allow if it's not strictly required or if we have fallback
                if not module_requirements.get("allow_fallback", True):
                    logger.info(f"Lazy Loading: Module rejected. Hardware uses {self.profile['priority_engine']}, module requires {module_requirements['required_engine']}")
                    return False

        return True

if __name__ == "__main__":
    awareness = DeviceAwareness()
    print(f"Profile: {awareness.profile}")
    print(f"Initial State: {awareness.get_system_state()}")
