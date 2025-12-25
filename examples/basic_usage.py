#!/usr/bin/env python3
"""
Exemplo básico de uso do JARVIS 5.0
"""

import sys
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from jarvis import JarvisAssistant


def exemplo_basico():
    """Exemplo mais simples possível"""
    print("=== Exemplo Básico ===")
    
    # Criar e iniciar assistente
    assistant = JarvisAssistant()
    assistant.start()


def exemplo_com_configuracao_personalizada():
    """Exemplo com configuração personalizada"""
    print("=== Exemplo com Configuração Personalizada ===")
    
    from jarvis.core.config import ConfigManager
    
    # Criar configuração personalizada
    config = ConfigManager()
    
    # Personalizar voz
    config.set('voice.rate', 200)  # Mais rápido
    config.set('voice.volume', 1.0)  # Volume máximo
    config.set('voice.use_gtts', True)  # Usar Google TTS
    
    # Personalizar reconhecimento
    config.set('recognition.timeout', 10)  # Timeout maior
    config.set('recognition.phrase_limit', 15)  # Frases mais longas
    
    # Personalizar fala natural
    config.set('natural_speech.use_fillers', True)  # Usar fillers
    config.set('natural_speech.use_hesitations', True)  # Usar hesitações
    
    # Salvar configuração
    config.save()
    
    # Criar assistente com configuração personalizada
    assistant = JarvisAssistant()
    assistant.start()


def exemplo_com_comando_personalizado():
    """Exemplo com comando personalizado simples"""
    print("=== Exemplo com Comando Personalizado ===")
    
    def meu_comando(command_text: str) -> bool:
        """Comando personalizado de exemplo"""
        print(f"Comando recebido: {command_text}")
        
        # Usar o speech engine do assistente para responder
        # Nota: Em um comando real, você teria acesso ao speech_engine
        print("JARVIS: Comando personalizado executado!")
        
        return True  # Continuar executando
    
    # Criar assistente
    assistant = JarvisAssistant()
    
    # Adicionar comando personalizado
    assistant.add_custom_command("teste", meu_comando)
    
    print("Comando 'teste' adicionado!")
    print("Agora você pode dizer 'teste' para executar o comando personalizado.")
    
    # Iniciar assistente
    assistant.start()


def exemplo_teste_sistemas():
    """Exemplo de teste de sistemas"""
    print("=== Exemplo de Teste de Sistemas ===")
    
    # Criar assistente
    assistant = JarvisAssistant()
    
    # Testar sistemas
    print("Testando sistemas...")
    results = assistant.test_systems()
    
    print(f"Microfone: {'✓' if results.get('microphone') else '✗'}")
    print(f"Sistema de Voz: {'✓' if results.get('speech') else '✗'}")
    print(f"Configuração: {'✓' if results.get('config') else '✗'}")
    print(f"Status Geral: {'✓' if results.get('overall') else '✗'}")
    
    if results.get('overall'):
        print("\nTodos os sistemas estão funcionando!")
        
        # Calibrar se necessário
        print("Calibrando microfone...")
        if assistant.calibrate():
            print("Calibração concluída!")
        
        # Iniciar assistente
        assistant.start()
    else:
        print("\nProblemas detectados nos sistemas.")
        if 'error' in results:
            print(f"Erro: {results['error']}")


def exemplo_configuracao_avancada():
    """Exemplo de configuração avançada"""
    print("=== Exemplo de Configuração Avançada ===")
    
    from jarvis.core.config import ConfigManager
    
    # Criar gerenciador de configuração
    config = ConfigManager()
    
    # Configuração para voz mais natural
    config.set('voice.rate', 170)  # Velocidade natural
    config.set('voice.volume', 0.85)  # Volume confortável
    config.set('voice.use_gtts', True)  # Google TTS para naturalidade
    
    # Configuração para reconhecimento mais preciso
    config.set('recognition.dynamic_energy_threshold', True)  # Ajuste automático
    config.set('recognition.timeout', 8)  # Mais tempo para falar
    config.set('recognition.phrase_limit', 12)  # Frases mais longas
    
    # Configuração para máxima naturalidade
    config.set('natural_speech.use_fillers', True)  # "né", "tipo", etc.
    config.set('natural_speech.use_hesitations', True)  # "hmm", "eh", etc.
    config.set('natural_speech.use_breathing', True)  # Respiração simulada
    config.set('natural_speech.emotion_detection', True)  # Emoções
    config.set('natural_speech.conversation_flow', True)  # Fluxo conversacional
    
    # Configuração de comandos
    config.set('commands.exit_phrases', ['sair', 'tchau', 'até logo', 'encerrar'])
    config.set('commands.help_phrases', ['ajuda', 'help', 'comandos', 'o que você faz'])
    
    # Configuração do sistema
    config.set('system.log_level', 'INFO')  # Nível de log
    config.set('system.debug_mode', False)  # Modo debug desligado
    
    # Salvar configuração
    config.save()
    
    print("Configuração avançada aplicada!")
    print("- Voz otimizada para naturalidade")
    print("- Reconhecimento mais preciso")
    print("- Máxima naturalidade na fala")
    print("- Comandos personalizados")
    
    # Criar e iniciar assistente
    assistant = JarvisAssistant()
    assistant.start()


def menu_exemplos():
    """Menu para escolher exemplo"""
    print("JARVIS 5.0 - Exemplos de Uso")
    print("=" * 30)
    print("1. Exemplo Básico")
    print("2. Configuração Personalizada")
    print("3. Comando Personalizado")
    print("4. Teste de Sistemas")
    print("5. Configuração Avançada")
    print("0. Sair")
    
    while True:
        try:
            escolha = input("\nEscolha um exemplo (0-5): ").strip()
            
            if escolha == "0":
                print("Saindo...")
                break
            elif escolha == "1":
                exemplo_basico()
                break
            elif escolha == "2":
                exemplo_com_configuracao_personalizada()
                break
            elif escolha == "3":
                exemplo_com_comando_personalizado()
                break
            elif escolha == "4":
                exemplo_teste_sistemas()
                break
            elif escolha == "5":
                exemplo_configuracao_avancada()
                break
            else:
                print("Opção inválida! Escolha entre 0-5.")
        
        except KeyboardInterrupt:
            print("\nSaindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")


if __name__ == "__main__":
    menu_exemplos()
