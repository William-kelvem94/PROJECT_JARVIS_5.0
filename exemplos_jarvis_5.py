"""
Exemplo de uso do JARVIS 5.0 com novos recursos
Demonstra as principais funcionalidades implementadas
"""

import time
from datetime import datetime, timedelta

# Exemplo 1: Usando Whisper para STT de alta qualidade
def exemplo_whisper():
    """Demonstra uso do Whisper para reconhecimento de voz."""
    print("\n" + "="*60)
    print("EXEMPLO 1: Whisper STT - Reconhecimento de Voz")
    print("="*60)
    
    try:
        from modules.input.whisper_module import WhisperModule
        
        print("\n📝 Inicializando Whisper (modelo base)...")
        whisper = WhisperModule(model_name="base", language="pt")
        
        print("✅ Whisper inicializado com sucesso!")
        print(f"   Modelo: base (74M parâmetros)")
        print(f"   Idioma: Português")
        print(f"   Disponível: {whisper.is_available()}")
        
        # Informações sobre modelos
        print("\n📊 Modelos disponíveis:")
        for model in WhisperModule.get_available_models():
            info = WhisperModule.get_model_info(model)
            print(f"   - {model}: {info.get('params', 'N/A')} parâmetros, "
                  f"qualidade {info.get('quality', 'N/A')}")
        
        # Nota: Não vamos gravar áudio automaticamente
        print("\n💡 Para usar: whisper.listen(duration=5.0)")
        print("   Ou: whisper.transcribe_file('audio.wav')")
        
    except ImportError as e:
        print(f"❌ Whisper não disponível: {e}")
        print("   Instale com: pip install openai-whisper sounddevice soundfile")
    except Exception as e:
        print(f"❌ Erro: {e}")


# Exemplo 2: Usando Coqui TTS para voz natural
def exemplo_tts():
    """Demonstra uso do Coqui TTS."""
    print("\n" + "="*60)
    print("EXEMPLO 2: Coqui TTS - Voz Natural de Alta Qualidade")
    print("="*60)
    
    try:
        from modules.input.advanced_tts import AdvancedTTSModule
        
        print("\n📢 Inicializando Coqui TTS...")
        tts = AdvancedTTSModule(backend="coqui", language="pt")
        
        if tts.is_available():
            print("✅ Coqui TTS inicializado com sucesso!")
            print(f"   Backend: coqui")
            print(f"   Modelo: {tts.model_name}")
            
            # Listar speakers se disponível
            speakers = tts.get_available_speakers()
            if speakers:
                print(f"   Speakers disponíveis: {len(speakers)}")
            
            print("\n💡 Para usar: tts.speak('Olá, eu sou o JARVIS!')")
            print("   Ou: tts.speak_async('Texto') para modo assíncrono")
        else:
            print("❌ TTS não disponível")
        
    except ImportError as e:
        print(f"❌ Coqui TTS não disponível: {e}")
        print("   Instale com: pip install TTS sounddevice soundfile")
    except Exception as e:
        print(f"❌ Erro: {e}")


# Exemplo 3: Wake Word Detector
def exemplo_wake_word():
    """Demonstra wake word detector."""
    print("\n" + "="*60)
    print("EXEMPLO 3: Wake Word Detector - 'Hey JARVIS'")
    print("="*60)
    
    try:
        from modules.input.wake_word_detector import SimpleWakeWordDetector
        
        print("\n👂 Inicializando detector de wake word...")
        
        def on_wake_word(keyword):
            print(f"\n✅ Wake word detectada: '{keyword}'")
            print("   JARVIS ativado!")
        
        detector = SimpleWakeWordDetector(
            keywords=["jarvis", "hey jarvis"],
            callback=on_wake_word
        )
        
        print("✅ Detector inicializado!")
        print(f"   Keywords: {detector.keywords}")
        print(f"   Status: {'Ativo' if detector.is_active() else 'Inativo'}")
        
        print("\n💡 Para usar: detector.start()")
        print("   O detector roda em background e chama callback quando detectar")
        
    except ImportError as e:
        print(f"❌ Wake Word Detector não disponível: {e}")
        print("   Instale com: pip install SpeechRecognition")
    except Exception as e:
        print(f"❌ Erro: {e}")


# Exemplo 4: Sistema de Segurança
def exemplo_seguranca():
    """Demonstra sistema de segurança."""
    print("\n" + "="*60)
    print("EXEMPLO 4: Sistema de Segurança e Permissões")
    print("="*60)
    
    try:
        from modules.system.security_module import SecurityManager, PermissionLevel
        
        print("\n🔒 Inicializando sistema de segurança...")
        security = SecurityManager()
        
        print("✅ Sistema de segurança ativo!")
        
        # Mostrar configuração
        stats = security.get_stats()
        print(f"\n📊 Configuração:")
        print(f"   Autenticação requerida: {stats['authentication_required']}")
        print(f"   Whitelist habilitada: {stats['whitelist_enabled']}")
        print(f"   Sandboxing habilitado: {stats['sandboxing_enabled']}")
        print(f"   Confirmações habilitadas: {stats['confirmation_enabled']}")
        print(f"   Nível atual: {stats['permission_level']}")
        
        # Testar permissões
        print("\n🧪 Testando permissões:")
        
        comandos_teste = [
            ("search", "Pesquisar no Google"),
            ("open_app", "Abrir aplicativo"),
            ("delete_file", "Deletar arquivo"),
            ("shutdown", "Desligar sistema")
        ]
        
        for cmd, desc in comandos_teste:
            permitido = security.check_permission(cmd)
            simbolo = "✅" if permitido else "❌"
            print(f"   {simbolo} {desc} ({cmd}): {'Permitido' if permitido else 'Bloqueado'}")
        
        # Testar comando perigoso
        print("\n🚨 Testando bloqueio de comandos perigosos:")
        is_safe, reason = security.is_safe_command("rm -rf /")
        print(f"   Comando: rm -rf /")
        print(f"   Seguro: {'Sim' if is_safe else 'Não'}")
        if not is_safe:
            print(f"   Motivo: {reason}")
        
        print("\n💡 Para usar:")
        print("   security.check_permission('comando')")
        print("   security.is_safe_command('comando')")
        print("   security.request_confirmation('comando', 'descrição')")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


# Exemplo 5: Task Decomposition
def exemplo_task_decomposition():
    """Demonstra decomposição de tarefas."""
    print("\n" + "="*60)
    print("EXEMPLO 5: Task Decomposition - Planejamento de Tarefas")
    print("="*60)
    
    try:
        from modules.processing.task_decomposition import TaskDecomposer, TaskExecutor, Task
        
        print("\n🧠 Inicializando sistema de planejamento...")
        decomposer = TaskDecomposer()
        executor = TaskExecutor()
        
        print("✅ Sistema de planejamento ativo!")
        
        # Exemplo de decomposição simples
        print("\n📝 Exemplo de decomposição:")
        print("   Requisição: 'Enviar email para João'")
        
        plan = decomposer.decompose("Enviar email para João")
        
        print(f"\n✅ Plano criado: {plan.plan_id}")
        print(f"   Descrição: {plan.description}")
        print(f"   Número de tarefas: {len(plan.tasks)}")
        
        print("\n📋 Tarefas no plano:")
        for i, task in enumerate(plan.tasks, 1):
            deps = f" (depende: {', '.join(task.dependencies)})" if task.dependencies else ""
            print(f"   {i}. {task.description} - {task.action}{deps}")
        
        # Registrar handlers de exemplo
        print("\n🔧 Registrando handlers de exemplo...")
        
        def mock_handler(params):
            print(f"      Executando: {params}")
            return {"success": True}
        
        for task in plan.tasks:
            executor.register_handler(task.action, mock_handler)
        
        print("   Handlers registrados!")
        
        print("\n💡 Para executar:")
        print("   success = executor.execute_plan(plan)")
        print("   status = executor.get_plan_status()")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


# Exemplo 6: Integrações (Calendar e Email)
def exemplo_integracoes():
    """Demonstra integrações com Calendar e Email."""
    print("\n" + "="*60)
    print("EXEMPLO 6: Integrações - Calendar e Email")
    print("="*60)
    
    # Calendar
    print("\n📅 Calendar Integration:")
    try:
        from modules.action.calendar_integration import CalendarIntegration
        
        calendar = CalendarIntegration(provider="google")
        
        if calendar.is_available():
            print("   ✅ Google Calendar disponível!")
            print("   💡 Para usar:")
            print("      calendar.create_event('Reunião', start_time, ...)")
            print("      events = calendar.list_events(max_results=5)")
            print("      next_event = calendar.get_next_event()")
        else:
            print("   ⚠️  Google Calendar não configurado")
            print("   📝 Configure em: config/calendar_credentials.json")
            print("   🔗 Obtenha credenciais: https://console.cloud.google.com/")
    except Exception as e:
        print(f"   ❌ Calendar não disponível: {e}")
    
    # Email
    print("\n📧 Email Integration:")
    try:
        from modules.action.email_integration import EmailIntegration
        
        email = EmailIntegration(provider="gmail")
        
        if email.is_available():
            print("   ✅ Gmail disponível!")
            print("   💡 Para usar:")
            print("      email.send_email(to, subject, body)")
            print("      messages = email.list_messages(query='is:unread')")
            print("      latest = email.get_latest_messages(count=5)")
        else:
            print("   ⚠️  Gmail não configurado")
            print("   📝 Configure em: config/email_credentials.json")
            print("   🔗 Obtenha credenciais: https://console.cloud.google.com/")
    except Exception as e:
        print(f"   ❌ Email não disponível: {e}")


# Exemplo 7: Integração Completa
def exemplo_integracao_completa():
    """Demonstra uso da integração completa."""
    print("\n" + "="*60)
    print("EXEMPLO 7: JARVIS 5.0 - Integração Completa")
    print("="*60)
    
    try:
        from jarvis_integration import JarvisCore, quick_start
        
        print("\n🚀 Inicializando JARVIS 5.0...")
        
        # Modo básico (sem dependências pesadas)
        jarvis = quick_start(mode="basic", wake_word=False)
        
        print("✅ JARVIS 5.0 inicializado!")
        
        # Status do sistema
        status = jarvis.get_status()
        
        print("\n📊 Status do Sistema:")
        print(f"   Voz disponível: {status['voice_available']}")
        print(f"   Calendar disponível: {status['calendar_available']}")
        print(f"   Email disponível: {status['email_available']}")
        print(f"   Segurança ativa: {status['security_enabled']}")
        print(f"   Planejamento de tarefas: {status['task_planning_enabled']}")
        print(f"   Wake word ativo: {status['wake_word_active']}")
        
        print("\n💡 Modos de inicialização:")
        print("   jarvis = quick_start(mode='basic')  # Recursos básicos")
        print("   jarvis = quick_start(mode='voice')  # Com voz avançada")
        print("   jarvis = quick_start(mode='full')   # Todos os recursos")
        
        print("\n💡 Uso:")
        print("   jarvis.speak_and_process('Como posso ajudar?')")
        print("   jarvis.start_wake_word_mode()  # Modo hands-free")
        print("   response = jarvis.process_command('comando')")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


# Exemplo 8: Memória Persistente
def exemplo_memoria():
    """Demonstra sistema de memória."""
    print("\n" + "="*60)
    print("EXEMPLO 8: Memória Persistente")
    print("="*60)
    
    try:
        from modules.memory.persistent_memory import PersistentMemory
        
        print("\n💾 Inicializando sistema de memória...")
        memory = PersistentMemory()
        
        print("✅ Memória persistente ativa!")
        
        # Salvar algumas conversas de exemplo
        print("\n📝 Salvando conversas de exemplo...")
        memory.save_conversation("user", "Qual é o clima hoje?")
        memory.save_conversation("assistant", "O clima está ensolarado com 25°C")
        memory.save_conversation("user", "E amanhã?")
        memory.save_conversation("assistant", "Amanhã haverá chuva")
        
        # Recuperar histórico
        print("\n📖 Recuperando histórico...")
        history = memory.get_conversation_history(limit=4)
        
        print(f"   Conversas recuperadas: {len(history)}")
        for msg in history:
            role = "Você" if msg['role'] == "user" else "JARVIS"
            print(f"   {role}: {msg['content']}")
        
        # Preferências
        print("\n⚙️  Salvando preferências de usuário...")
        memory.save_user_preference("idioma", "pt-BR")
        memory.save_user_preference("voz_velocidade", 150)
        
        idioma = memory.get_user_preference("idioma")
        velocidade = memory.get_user_preference("voz_velocidade")
        
        print(f"   Idioma: {idioma}")
        print(f"   Velocidade da voz: {velocidade}")
        
        # Estatísticas
        stats = memory.get_stats()
        print(f"\n📊 Estatísticas:")
        print(f"   Conversas: {stats['conversations']}")
        print(f"   Preferências: {stats['preferences']}")
        print(f"   Sessões: {stats['sessions']}")
        print(f"   Tamanho do banco: {stats['db_size_mb']:.2f} MB")
        
        print("\n💡 Para usar:")
        print("   memory.save_conversation(role, content)")
        print("   history = memory.get_conversation_history(limit=50)")
        print("   memory.save_user_preference(key, value)")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


# Função principal
def main():
    """Executa todos os exemplos."""
    print("\n" + "="*60)
    print("    🤖 JARVIS 5.0 - Demonstração de Recursos")
    print("="*60)
    print("\nEste script demonstra os novos recursos implementados:")
    print("  1. Whisper STT - Reconhecimento de voz de alta qualidade")
    print("  2. Coqui TTS - Voz natural")
    print("  3. Wake Word Detector - 'Hey JARVIS'")
    print("  4. Sistema de Segurança - Permissões e proteções")
    print("  5. Task Decomposition - Planejamento de tarefas")
    print("  6. Integrações - Calendar e Email")
    print("  7. Integração Completa - JarvisCore")
    print("  8. Memória Persistente - Histórico e preferências")
    
    print("\n⚠️  NOTA: Alguns recursos requerem instalação adicional")
    print("Consulte MELHORIAS_JARVIS_5.0.md para detalhes\n")
    
    # Executar exemplos
    exemplos = [
        exemplo_memoria,           # Começa com o que já funciona
        exemplo_seguranca,         # Sistema de segurança
        exemplo_task_decomposition, # Planejamento de tarefas
        exemplo_integracoes,       # Integrações
        exemplo_integracao_completa, # Integração completa
        exemplo_whisper,           # Whisper (requer instalação)
        exemplo_tts,              # TTS (requer instalação)
        exemplo_wake_word,        # Wake word (requer instalação)
    ]
    
    for exemplo in exemplos:
        try:
            exemplo()
            time.sleep(0.5)  # Pequena pausa entre exemplos
        except Exception as e:
            print(f"\n❌ Erro ao executar exemplo: {e}")
    
    print("\n" + "="*60)
    print("    ✅ Demonstração Concluída!")
    print("="*60)
    print("\n📖 Para mais informações, consulte:")
    print("   - MELHORIAS_JARVIS_5.0.md (documentação completa)")
    print("   - jarvis_integration.py (código de integração)")
    print("   - requirements.txt (dependências)")
    print("\n🚀 Próximos passos:")
    print("   1. Instalar dependências opcionais")
    print("   2. Configurar credenciais do Google")
    print("   3. Testar integração completa")
    print("   4. Personalizar configurações\n")


if __name__ == "__main__":
    main()
