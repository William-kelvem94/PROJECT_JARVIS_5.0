import logging
import psutil
from datetime import datetime
import os

logger = logging.getLogger("JARVIS-BRIEFING")

class BriefingManager:
    """
    Handles proactive startup briefings and daily reports.
    (TikTok 'Completão' Vision 5.0)
    """
    
    def __init__(self):
        self.user_name = os.getenv("USER_NAME", "Senhor")
        
    def generate_startup_briefing(self) -> str:
        """Generates a complete holographic-style briefing."""
        hour = datetime.now().hour
        greeting = "Bom dia" if 5 <= hour < 12 else "Boa tarde" if 12 <= hour < 18 else "Boa noite"
        
        # 1. System Telemetry
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        # 2. Weather (Mocked for now, but ready for API)
        weather = "Céu limpo, 24°C"
        
        # 3. News / Agenda (Mocked)
        agenda = "Você tem 2 reuniões agendadas para hoje às 14h e 16h."
        news = "As ações da Stark Industries subiram 2% hoje."
        
        # 4. Neural Status (Dream Engine Analysis)
        dream_status = "O Ciclo de Sonho consolidou 15 novas relações semânticas."
        
        briefing = (
            f"{greeting}, {self.user_name}. Sistema JARVIS 5.0 totalmente funcional.\n\n"
            f"📅 HOJE: {datetime.now().strftime('%d/%m/%Y')} | {weather}\n"
            f"📊 STATUS: CPU {cpu}% | RAM {ram}%\n"
            f"🧠 NEURAL: {dream_status}\n\n"
            f"📝 AGENDA: {agenda}\n"
            f"🌐 NOTÍCIAS: {news}\n\n"
            "Todos os protocolos Stark estão ativos. Aguardando suas instruções."
        )
        return briefing

briefing_manager = BriefingManager()
