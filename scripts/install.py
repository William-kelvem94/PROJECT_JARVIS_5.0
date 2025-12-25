#!/usr/bin/env python3
"""
Script de instalação para JARVIS 5.0
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Verifica se a versão do Python é compatível"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERRO: Python 3.8 ou superior e necessario")
        print(f"   Versao atual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"Python {version.major}.{version.minor}.{version.micro} - OK")
    return True


def check_pip():
    """Verifica se pip está disponível"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      capture_output=True, check=True)
        print("pip - OK")
        return True
    except subprocess.CalledProcessError:
        print("ERRO: pip nao encontrado")
        return False


def install_requirements():
    """Instala dependências do requirements.txt"""
    requirements_file = Path(__file__).parent.parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("ERRO: Arquivo requirements.txt nao encontrado")
        return False
    
    print("Instalando dependencias...")
    
    try:
        cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Dependencias instaladas com sucesso")
            return True
        else:
            print("ERRO ao instalar dependencias:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"ERRO ao instalar dependencias: {e}")
        return False


def check_microphone():
    """Verifica se microfone está disponível"""
    try:
        import speech_recognition as sr
        
        # Tentar listar microfones
        mics = sr.Microphone.list_microphone_names()
        
        if mics:
            print(f"{len(mics)} microfone(s) detectado(s)")
            return True
        else:
            print("Nenhum microfone detectado")
            return False
            
    except ImportError:
        print("Nao foi possivel verificar microfones (speech_recognition nao instalado)")
        return False
    except Exception as e:
        print(f"Erro ao verificar microfones: {e}")
        return False


def check_audio_system():
    """Verifica sistema de áudio"""
    try:
        import pyttsx3
        
        # Tentar inicializar engine de voz
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        if voices:
            print(f"{len(voices)} voz(es) disponivel(is)")
            
            # Procurar voz em português
            portuguese_voices = [v for v in voices if 'portuguese' in v.name.lower() or 'pt' in v.name.lower()]
            if portuguese_voices:
                print(f"{len(portuguese_voices)} voz(es) em portugues encontrada(s)")
            else:
                print("Nenhuma voz em portugues encontrada")
            
            engine.stop()
            return True
        else:
            print("Nenhuma voz disponivel")
            return False
            
    except ImportError:
        print("⚠️  Não foi possível verificar sistema de áudio (pyttsx3 não instalado)")
        return False
    except Exception as e:
        print(f"⚠️  Erro ao verificar sistema de áudio: {e}")
        return False


def check_internet():
    """Verifica conexão com internet (para gTTS)"""
    try:
        import requests
        
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            print("✓ Conexão com internet - OK")
            return True
        else:
            print("⚠️  Problema na conexão com internet")
            return False
            
    except ImportError:
        print("⚠️  Não foi possível verificar internet (requests não instalado)")
        return False
    except Exception as e:
        print("⚠️  Sem conexão com internet (gTTS não funcionará)")
        return False


def create_config_file():
    """Cria arquivo de configuração se não existir"""
    config_file = Path(__file__).parent.parent / "config.json"
    
    if config_file.exists():
        print("✓ Arquivo de configuração já existe")
        return True
    
    print("📝 Criando arquivo de configuração...")
    
    config_content = """{
  "voice": {
    "rate": 180,
    "volume": 0.9,
    "language": "pt-BR",
    "use_gtts": true,
    "pitch": 50
  },
  "recognition": {
    "timeout": 5,
    "phrase_limit": 10,
    "energy_threshold": 300,
    "dynamic_energy_threshold": true
  },
  "system": {
    "os": "auto",
    "debug_mode": false,
    "log_level": "INFO"
  },
  "commands": {
    "wake_word": null,
    "exit_phrases": ["sair", "tchau", "até logo"],
    "help_phrases": ["ajuda", "help", "comandos"]
  },
  "natural_speech": {
    "use_fillers": true,
    "use_hesitations": true,
    "use_breathing": true,
    "emotion_detection": true,
    "conversation_flow": true
  }
}"""
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("✓ Arquivo de configuração criado")
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao criar arquivo de configuração: {e}")
        return False


def test_installation():
    """Testa a instalação"""
    print("\n🧪 Testando instalação...")
    
    try:
        # Tentar importar JARVIS
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from jarvis import JarvisAssistant
        
        # Tentar criar assistente
        assistant = JarvisAssistant()
        
        # Testar sistemas
        results = assistant.test_systems()
        
        if results.get('overall', False):
            print("✓ Teste de instalação - SUCESSO")
            return True
        else:
            print("⚠️  Teste de instalação - PROBLEMAS DETECTADOS")
            print("   Microfone:", "OK" if results.get('microphone') else "ERRO")
            print("   Voz:", "OK" if results.get('speech') else "ERRO")
            print("   Config:", "OK" if results.get('config') else "ERRO")
            return False
            
    except Exception as e:
        print(f"❌ ERRO no teste de instalação: {e}")
        return False


def show_system_info():
    """Mostra informações do sistema"""
    print("Informacoes do Sistema:")
    print(f"   OS: {platform.system()} {platform.version()}")
    print(f"   Arquitetura: {platform.architecture()[0]}")
    print(f"   Python: {sys.version}")
    print(f"   Diretório: {Path.cwd()}")


def main():
    """Função principal de instalação"""
    print("JARVIS 5.0 - Script de Instalacao")
    print("=" * 50)
    
    # Mostrar informações do sistema
    show_system_info()
    print()
    
    # Lista de verificações
    checks = [
        ("Versão do Python", check_python_version),
        ("pip", check_pip),
        ("Dependências", install_requirements),
        ("Microfone", check_microphone),
        ("Sistema de Áudio", check_audio_system),
        ("Internet", check_internet),
        ("Arquivo de Configuração", create_config_file),
    ]
    
    # Executar verificações
    results = []
    for name, check_func in checks:
        print(f"Verificando {name}...")
        result = check_func()
        results.append((name, result))
        print()
    
    # Testar instalação
    test_result = test_installation()
    results.append(("Teste Final", test_result))
    
    # Mostrar resumo
    print("\n📋 Resumo da Instalação:")
    print("-" * 30)
    
    all_ok = True
    for name, result in results:
        status = "✓ OK" if result else "❌ ERRO"
        print(f"{name}: {status}")
        if not result:
            all_ok = False
    
    print("-" * 30)
    
    if all_ok:
        print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        print("\nPara usar o JARVIS:")
        print("  python main_new.py")
        print("\nPara ver opções:")
        print("  python main_new.py --help")
        print("\nPara testar:")
        print("  python main_new.py --test")
    else:
        print("⚠️  INSTALAÇÃO CONCLUÍDA COM PROBLEMAS")
        print("\nAlguns componentes podem não funcionar corretamente.")
        print("Verifique os erros acima e tente resolver os problemas.")
    
    return all_ok


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstalação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro inesperado durante instalação: {e}")
        sys.exit(1)
