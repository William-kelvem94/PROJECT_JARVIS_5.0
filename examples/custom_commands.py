#!/usr/bin/env python3
"""
Exemplos de comandos personalizados para JARVIS 5.0
"""

import os
import sys
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from jarvis import JarvisAssistant


class CustomCommands:
    """Classe com comandos personalizados de exemplo"""
    
    def __init__(self, speech_engine):
        self.speech_engine = speech_engine
    
    def weather_command(self, command_text: str) -> bool:
        """Comando de exemplo para clima"""
        self.speech_engine.speak(
            "Infelizmente ainda não tenho acesso a dados meteorológicos em tempo real. "
            "Mas posso abrir um site de previsão do tempo para você!",
            emotion='pensativo'
        )
        
        # Abrir site de clima
        try:
            webbrowser.open("https://weather.com")
            self.speech_engine.speak(
                "Pronto! Abri o site do clima para você.",
                emotion='entusiasta'
            )
        except:
            self.speech_engine.speak(
                "Ops! Não consegui abrir o navegador.",
                emotion='preocupado'
            )
        
        return True
    
    def reminder_command(self, command_text: str) -> bool:
        """Comando de exemplo para lembretes simples"""
        import re
        
        # Tentar extrair o lembrete
        match = re.search(r'lembrar (?:de )?(.+)', command_text)
        
        if match:
            reminder_text = match.group(1)
            
            # Salvar lembrete em arquivo simples
            try:
                with open('lembretes.txt', 'a', encoding='utf-8') as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    f.write(f"[{timestamp}] {reminder_text}\n")
                
                self.speech_engine.speak(
                    f"Pronto! Anotei o lembrete: {reminder_text}",
                    emotion='entusiasta'
                )
            except Exception as e:
                self.speech_engine.speak(
                    "Ops! Não consegui salvar o lembrete.",
                    emotion='preocupado'
                )
        else:
            self.speech_engine.speak(
                "O que você gostaria que eu lembrasse? "
                "Diga 'lembrar de' seguido do que quer lembrar.",
                emotion='pensativo'
            )
        
        return True
    
    def list_reminders_command(self, command_text: str) -> bool:
        """Lista lembretes salvos"""
        try:
            if os.path.exists('lembretes.txt'):
                with open('lembretes.txt', 'r', encoding='utf-8') as f:
                    reminders = f.readlines()
                
                if reminders:
                    count = len(reminders)
                    self.speech_engine.speak(
                        f"Você tem {count} lembrete{'s' if count > 1 else ''}. "
                        "Vou listar os mais recentes:",
                        emotion='entusiasta'
                    )
                    
                    # Mostrar últimos 3 lembretes
                    for reminder in reminders[-3:]:
                        print(f"📝 {reminder.strip()}")
                    
                    self.speech_engine.speak(
                        "Os lembretes estão sendo exibidos na tela.",
                        emotion='entusiasta'
                    )
                else:
                    self.speech_engine.speak(
                        "Você não tem lembretes salvos ainda.",
                        emotion='pensativo'
                    )
            else:
                self.speech_engine.speak(
                    "Você não tem lembretes salvos ainda.",
                    emotion='pensativo'
                )
        
        except Exception as e:
            self.speech_engine.speak(
                "Ops! Não consegui acessar os lembretes.",
                emotion='preocupado'
            )
        
        return True
    
    def joke_command(self, command_text: str) -> bool:
        """Comando para contar piadas"""
        import random
        
        jokes = [
            "Por que os pássaros voam para o sul no inverno? Porque é longe demais para ir andando!",
            "O que o pato disse para a pata? Vem quá!",
            "Por que o livro de matemática estava triste? Porque tinha muitos problemas!",
            "O que acontece quando você cruza um peixe com um elefante? Você consegue nadar no fundo do mar!",
            "Por que os programadores preferem o modo escuro? Porque a luz atrai bugs!"
        ]
        
        joke = random.choice(jokes)
        
        self.speech_engine.speak(
            f"Aqui vai uma piada para você: {joke}",
            emotion='entusiasta'
        )
        
        return True
    
    def system_info_command(self, command_text: str) -> bool:
        """Mostra informações do sistema"""
        import platform
        import psutil
        
        try:
            # Coletar informações
            system = platform.system()
            version = platform.version()
            processor = platform.processor()
            
            # Informações de memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Informações de disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            info_text = (
                f"Seu sistema é {system}, versão {version}. "
                f"O processador é {processor}. "
                f"Uso de memória: {memory_percent:.1f}%. "
                f"Uso de disco: {disk_percent:.1f}%."
            )
            
            self.speech_engine.speak(info_text, emotion='entusiasta')
            
        except ImportError:
            self.speech_engine.speak(
                "Para usar este comando, instale a biblioteca psutil com: pip install psutil",
                emotion='pensativo'
            )
        except Exception as e:
            self.speech_engine.speak(
                "Não consegui obter informações do sistema.",
                emotion='preocupado'
            )
        
        return True
    
    def music_command(self, command_text: str) -> bool:
        """Comando para abrir player de música"""
        import re
        
        # Tentar extrair nome da música/artista
        match = re.search(r'tocar (.+)', command_text)
        
        if match:
            music_query = match.group(1)
            
            # Abrir YouTube Music ou Spotify
            try:
                youtube_url = f"https://music.youtube.com/search?q={music_query.replace(' ', '+')}"
                webbrowser.open(youtube_url)
                
                self.speech_engine.speak(
                    f"Pronto! Abrindo YouTube Music para tocar {music_query}.",
                    emotion='entusiasta'
                )
            except:
                self.speech_engine.speak(
                    "Ops! Não consegui abrir o player de música.",
                    emotion='preocupado'
                )
        else:
            self.speech_engine.speak(
                "O que você gostaria de ouvir? "
                "Diga 'tocar' seguido do nome da música ou artista.",
                emotion='pensativo'
            )
        
        return True


def setup_custom_commands(assistant: JarvisAssistant):
    """Configura comandos personalizados no assistente"""
    
    # Obter speech engine do assistente
    speech_engine = assistant.speech_engine
    
    # Criar instância dos comandos personalizados
    custom_commands = CustomCommands(speech_engine)
    
    # Registrar comandos
    assistant.add_custom_command("clima", custom_commands.weather_command)
    assistant.add_custom_command("tempo", custom_commands.weather_command)
    
    assistant.add_custom_command("lembrar", custom_commands.reminder_command)
    assistant.add_custom_command("lembretes", custom_commands.list_reminders_command)
    
    assistant.add_custom_command("piada", custom_commands.joke_command)
    assistant.add_custom_command("conte uma piada", custom_commands.joke_command)
    
    assistant.add_custom_command("sistema", custom_commands.system_info_command)
    assistant.add_custom_command("informações", custom_commands.system_info_command)
    
    assistant.add_custom_command("tocar", custom_commands.music_command)
    assistant.add_custom_command("música", custom_commands.music_command)
    
    print("Comandos personalizados configurados:")
    print("- 'clima' ou 'tempo' - Abre site de previsão do tempo")
    print("- 'lembrar de [algo]' - Salva lembrete")
    print("- 'lembretes' - Lista lembretes salvos")
    print("- 'piada' - Conta uma piada")
    print("- 'sistema' - Mostra informações do sistema")
    print("- 'tocar [música]' - Abre player de música")


def main():
    """Exemplo de uso dos comandos personalizados"""
    print("JARVIS 5.0 - Exemplo com Comandos Personalizados")
    print("=" * 50)
    
    # Inicializar assistente
    assistant = JarvisAssistant()
    
    # Configurar comandos personalizados
    setup_custom_commands(assistant)
    
    print("\nComandos personalizados adicionados!")
    print("Agora você pode usar os novos comandos.")
    print("-" * 50)
    
    # Iniciar assistente
    assistant.start()


if __name__ == "__main__":
    main()
