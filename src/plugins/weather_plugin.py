from jarvis_minimal.commands import command

def setup(agent):
    """Setup function called by PluginManager."""
    print("[Plugin] Weather plugin carregado!")

@command(["clima", "tempo"], is_prefix=True)
def cmd_weather(agent, city):
    city = city.replace("clima em", "").replace("tempo em", "").strip()
    if not city:
        city = "sua localização atual"
    
    # Mock weather response
    resp = f"O clima em {city} está ensolarado com 25 graus Celsius. É um ótimo dia para ser Jarvis!"
    agent._speak(resp)
    agent._log_interaction(f"Consultou o clima para {city}", resp, system=True)
