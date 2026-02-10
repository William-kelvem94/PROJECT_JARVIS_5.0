import logging
import sys
from datetime import datetime
from typing import Optional

class ReflectionLogger:
    """
    Handles the 'Neural Reflection' logs for JARVIS 5.0.
    Provides a high-tech, cinematic logging style for the AI's thought process.
    """
    
    # ANSI Colors for Singularity 2.0 aesthetics
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    GLOW = "\033[1;96m" # Intense Cyan
    
    def __init__(self, name="JARVIS-REFLECT"):
        self.logger = logging.getLogger(name)
        self.enabled = False
        
    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    def reflect(self, thought: str, layer: str = "COGNITIVE"):
        """Logs a thought process step with Singularity styling"""
        if not self.enabled:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        print(f"\n{self.CYAN}--- NEURAL REFLECTION [{layer}] // {timestamp} ---{self.RESET}")
        
        # Split thought into lines for a cleaner terminal look
        lines = thought.split('\n')
        for line in lines:
            if not line.strip(): continue
            print(f"  {self.GLOW}⚡ {line.strip()}{self.RESET}")
            
        print(f"{self.CYAN}{'-' * 60}{self.RESET}\n")

    def log_action_plan(self, actions: list):
        """Logs the intended action sequence"""
        if not self.enabled:
            return
            
        print(f"  {self.MAGENTA}{self.BOLD}🎯 INTENTED TRAJECTORY:{self.RESET}")
        for i, action in enumerate(actions):
            print(f"    {i+1}. {self.YELLOW}{action}{self.RESET}")
        print("")

    def log_speech(self, text: str):
        """Logs what JARVIS is saying to the user"""
        if not self.enabled: return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n{self.GREEN}🗣️  JARVIS [{timestamp}]: {self.RESET}\"{self.YELLOW}{text}{self.RESET}\"\n")

# Global Instance
reflect_logger = ReflectionLogger()

def get_reflect_logger():
    return reflect_logger
