#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - LAUNCHER PRINCIPAL
Sistema 100% Local e Gratuito
"""

import os
import sys
import time
import argparse
from pathlib import Path

# Adicionar ao path
current_dir = Path(__file__).parent
jarvis_dir = current_dir / "jarvis_local"
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(jarvis_dir))

try:
    from jarvis_local.jarvis_core import JarvisCore
    from jarvis_local.download_models import ModelDownloader
except ImportError as e:
    print("❌ ERRO: Módulos JARVIS não encontrados!")
    print(f"Detalhes: {e}")
    print("\n📋 SOLUÇÕES:")
    print("1. Execute: pip install -r jarvis_local/requirements_local.txt")
    print("2. Execute: python jarvis_local/download_models.py")
    print("3. Execute: python start_jarvis_local.py --start")
    sys.exit(1)


def check_system_requirements():
    """Verificar requisitos do sistema"""
    print("🔍 Verificando requisitos do sistema...")

    issues = []

    # Verificar Python
    python_version = sys.version_info
    if python_version < (3, 8):
        issues.append(f"Python {python_version.major}.{python_version.minor} - Necessário 3.8+")

    # Verificar dependências críticas
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
    except ImportError:
        issues.append("PyTorch não instalado")

    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError:
        issues.append("OpenCV não instalado")

    try:
        import speech_recognition
        print("✅ Speech Recognition: OK")
    except ImportError:
        issues.append("Speech Recognition não instalado")

    # Verificar modelos
    models_dir = jarvis_dir / "models"
    if not models_dir.exists():
        issues.append("Diretório de modelos não encontrado")

    # Verificar se há pelo menos alguns modelos
    model_files = list(models_dir.glob("*.pt")) + list(models_dir.glob("*.gguf"))
    if len(model_files) == 0:
        issues.append("Nenhum modelo encontrado - execute download_models.py")

    if issues:
        print("⚠️ PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"  - {issue}")
        return False

    print("✅ Todos os requisitos atendidos!")
    return True


def download_models_if_needed():
    """Baixar modelos se necessário"""
    models_dir = jarvis_dir / "models"
    model_files = list(models_dir.glob("*")) if models_dir.exists() else []

    if len(model_files) < 3:  # Menos de 3 arquivos de modelo
        print("\n📥 Modelos insuficientes detectados!")
        print("Recomendação: Baixar modelos para funcionamento completo")

        response = input("Deseja baixar modelos agora? (recomendado) [S/n]: ").lower().strip()
        if response in ['', 's', 'sim', 'y', 'yes']:
            print("Iniciando download de modelos...")

            downloader = ModelDownloader(str(jarvis_dir))
            success = downloader.download_all_models(skip_large=True)  # Pular modelos grandes inicialmente

            if not success:
                print("⚠️ Alguns downloads falharam, mas continuando...")

            return True

    return True


def create_default_config():
    """Criar configuração padrão se não existir"""
    config_dir = jarvis_dir / "config"
    config_file = config_dir / "settings.json"

    if not config_file.exists():
        config_dir.mkdir(parents=True, exist_ok=True)

        default_config = {
            "system": {
                "name": "JARVIS Local 5.0",
                "version": "5.0.0",
                "privacy_mode": "local_only"
            },
            "models_dir": "./models",
            "data_dir": "./data",
            "vision": {
                "enabled": True,
                "camera_id": 0,
                "face_recognition": True,
                "object_detection": False,  # Desabilitado por padrão (precisa YOLO)
                "gesture_recognition": True
            },
            "audio": {
                "enabled": True,
                "sample_rate": 16000,
                "whisper_model": "base",
                "piper_voice": "en_US-lessac-medium"
            },
            "nlp": {
                "enabled": False,  # Desabilitado por padrão (LLM grande)
                "llm_model": "llama-2-7b-chat.Q4_0.gguf",
                "embedding_model": "local"
            },
            "memory": {
                "enabled": False,  # Desabilitado por padrão
                "vector_db": "chromadb",
                "max_memories": 1000
            },
            "learning": {
                "enabled": False,  # Desabilitado por padrão
                "continuous_learning": True,
                "fine_tuning_enabled": False
            },
            "message_bus": {
                "enabled": False,  # Desabilitado por padrão
                "port": 5555
            }
        }

        try:
            import json
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuração padrão criada: {config_file}")
        except Exception as e:
            print(f"❌ Erro ao criar configuração: {e}")


def show_welcome():
    """Exibir mensagem de boas-vindas"""
    print("=" * 70)
    print("🤖 JARVIS 5.0 - SISTEMA LOCAL COMPLETO")
    print("=" * 70)
    print("🏠 100% LOCAL | 📦 GRATUITO | 🔒 PRIVADO")
    print("=" * 70)
    print()
    print("🎯 CAPACIDADES:")
    print("  ✅ Reconhecimento de Voz Offline (Whisper)")
    print("  ✅ Síntese de Voz Local (Piper)")
    print("  ✅ Visão Computacional (OpenCV + Face Recognition)")
    print("  ✅ Reconhecimento Facial Local")
    print("  ✅ Detecção de Gestos")
    print("  ✅ Controle Completo do Windows")
    print("  ✅ Sistema de Memória Vetorial (Opcional)")
    print("  ✅ Aprendizado Contínuo Local (Opcional)")
    print("  ✅ NLP Avançado Offline (Opcional)")
    print()
    print("🔒 PRIVACIDADE:")
    print("  ✅ Zero dados enviados para nuvem")
    print("  ✅ Processamento 100% local")
    print("  ✅ Dados armazenados apenas no seu dispositivo")
    print("=" * 70)


def show_usage():
    """Exibir instruções de uso"""
    print("\n📖 INSTRUÇÕES DE USO:")
    print("=" * 40)
    print("1️⃣ INSTALAÇÃO:")
    print("   pip install -r jarvis_local/requirements_local.txt")
    print()
    print("2️⃣ DOWNLOAD DE MODELOS:")
    print("   python jarvis_local/download_models.py")
    print()
    print("3️⃣ INICIAR SISTEMA:")
    print("   python start_jarvis_local.py --start")
    print()
    print("4️⃣ TESTAR COMPONENTES:")
    print("   python jarvis_local/vision_local.py --test")
    print("   python jarvis_local/audio_local.py --test")
    print()
    print("🎮 COMANDOS DE VOZ:")
    print("   • 'Olá JARVIS'")
    print("   • 'Abrir Chrome'")
    print("   • 'Que horas são?'")
    print("   • 'Sair'")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="JARVIS 5.0 - Sistema Local Completo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python start_jarvis_local.py --start          # Iniciar sistema completo
  python start_jarvis_local.py --check          # Verificar requisitos
  python start_jarvis_local.py --download       # Baixar modelos
  python start_jarvis_local.py --config         # Criar configuração padrão
        """
    )

    parser.add_argument("--start", action="store_true",
                       help="Iniciar sistema JARVIS completo")
    parser.add_argument("--check", action="store_true",
                       help="Verificar requisitos do sistema")
    parser.add_argument("--download", action="store_true",
                       help="Baixar modelos necessários")
    parser.add_argument("--config", action="store_true",
                       help="Criar configuração padrão")
    parser.add_argument("--test", action="store_true",
                       help="Executar testes dos componentes")

    args = parser.parse_args()

    try:
        show_welcome()

        # Verificar argumentos
        if not any([args.start, args.check, args.download, args.config, args.test]):
            show_usage()
            return

        # Verificar requisitos do sistema
        if not check_system_requirements():
            print("\n❌ Sistema não atende aos requisitos mínimos!")
            print("Execute: pip install -r jarvis_local/requirements_local.txt")
            return

        # Criar configuração padrão se necessário
        create_default_config()

        # Baixar modelos se solicitado
        if args.download:
            download_models_if_needed()

        # Executar testes
        if args.test:
            print("\n🧪 Executando testes dos componentes...")

            # Testar visão
            try:
                print("👁️ Testando Visão...")
                from jarvis_local.vision_local import test_vision_system
                test_vision_system()
            except Exception as e:
                print(f"❌ Erro no teste de visão: {e}")

            # Testar áudio
            try:
                print("\n🔊 Testando Áudio...")
                from jarvis_local.audio_local import test_audio_system
                test_audio_system()
            except Exception as e:
                print(f"❌ Erro no teste de áudio: {e}")

            return

        # Iniciar sistema completo
        if args.start:
            print("\n🚀 Iniciando JARVIS Local...")

            # Baixar modelos se necessário
            download_models_if_needed()

            # Criar instância do JARVIS
            jarvis = JarvisCore()

            # Iniciar sistema
            success = jarvis.start_system()

            if success:
                print("\n🎉 JARVIS Local finalizado com sucesso!")
            else:
                print("\n❌ Erro ao iniciar JARVIS Local")
                return 1

    except KeyboardInterrupt:
        print("\n⚠️ Interrompido pelo usuário")
        return 130
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
