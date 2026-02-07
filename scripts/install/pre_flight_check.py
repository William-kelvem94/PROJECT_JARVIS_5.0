"""
JARVIS SINGULARITY - Pre-flight Check System
Validates hardware, dependencies, and environment before launch.
"""
import sys
import os
import logging
import subprocess
from pathlib import Path

def validate():
    """Returns exit code 0 if OK, non-zero otherwise"""
    print("🧠 Starting JARVIS Pre-flight Sequence...")
    
    # 1. NumPy Version Check (CRITICAL)
    try:
        import numpy as np
        version = np.__version__
        if int(version.split('.')[0]) >= 2:
            print(f"❌ INCOMPATIBILIDADE: NumPy {version} detectado.")
            print("   PyTorch e outras libs requerem NumPy < 2.0 (1.26.4 recomendado).")
            return 1
        print(f"✅ NumPy {version} validado.")
    except ImportError:
        print("❌ NumPy não encontrado!")
        return 2

    # 2. PyTorch DLL Check (Error 1114 / c10.dll)
    try:
        import torch
        # Trigger a real operation to test DLL loading
        _ = torch.zeros(1).cuda() if torch.cuda.is_available() else torch.zeros(1)
        print(f"✅ PyTorch {torch.__version__} pronto (CUDA: {torch.cuda.is_available()})")
    except Exception as e:
        if "c10.dll" in str(e) or "1114" in str(e):
            print("❌ ERRO CRÍTICO: Falha na DLL c10.dll do PyTorch.")
            print("   Execute: START_JARVIS.bat --repair-pytorch")
            return 4
        print(f"⚠️  PyTorch Warning: {e}")
        # Not returning 4 if it's just a general error, we might still start in degraded mode

    # 3. Directory Structure
    critical_dirs = [
        "data/logs", "data/faces", "data/models", "data/cache", "data/temp"
    ]
    for d in critical_dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✅ Estrutura de diretórios sincronizada.")

    # 4. Critical Files
    if not Path("config.yaml").exists() and not Path("config.json").exists():
        print("❌ Arquivo de configuração ausente!")
        return 6

    # 5. P0/P1 Critical Libraries Auto-Install (🆕 JARVIS 5.0)
    print("\n🔍 Validando bibliotecas P0/P1 World-Class...")
    missing_libs = []
    
    # P0.6 Wake Word Detection
    try:
        import pvporcupine
        print(f"✅ pvporcupine - Wake Word Detection")
    except ImportError:
        print("⚠️  pvporcupine ausente (P0.6 Wake Word)")
        missing_libs.append("pvporcupine==3.0.0")
    
    # P0.7 Voice Cloning (opcional mas recomendado)
    try:
        import TTS
        print(f"✅ TTS - Voice Cloning XTTS-v2")
    except ImportError:
        print("⚠️  TTS ausente (P0.7 Voice Cloning) - Requer Visual C++ Build Tools")
        missing_libs.append("TTS==0.22.0")
    
    # P1.2 Noise Reduction
    try:
        import noisereduce
        print(f"✅ noisereduce - Audio Enhancement (+20% STT accuracy)")
    except ImportError:
        print("⚠️  noisereduce ausente (P1.2 Noise Reduction)")
        missing_libs.append("noisereduce==3.0.2")
    
    # P1.3 Response Caching
    try:
        import pygame
        print(f"✅ pygame {pygame.version.ver} - Response Cache Playback")
    except ImportError:
        print("⚠️  pygame ausente (P1.3 Response Caching)")
        missing_libs.append("pygame==2.6.1")
    
    # P1.4 RAG Reranking
    try:
        from sentence_transformers import CrossEncoder
        print("✅ CrossEncoder - RAG Reranking (+15% relevance)")
    except ImportError:
        print("⚠️  CrossEncoder ausente (P1.4 RAG Reranking)")
        missing_libs.append("sentence-transformers[all]")
    
    # Auto-install missing P0/P1 libraries
    if missing_libs:
        print(f"\n📦 {len(missing_libs)} bibliotecas P0/P1 necessitam instalação:")
        for lib in missing_libs:
            print(f"   - {lib}")
        
        print("\n[AUTO-INSTALL] Instalando bibliotecas P0/P1...")
        for lib in missing_libs:
            try:
                # TTS pode falhar no Windows sem Visual C++ Build Tools
                is_tts = "TTS" in lib
                timeout_duration = 120 if is_tts else 180  # 2min para TTS, 3min para outros
                
                if is_tts:
                    print(f"⏳ Instalando {lib} (pode falhar sem Visual C++ Build Tools, timeout: 2min)...")
                else:
                    print(f"⏳ Instalando {lib}...")
                
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", lib, "--quiet"],
                    capture_output=True,
                    text=True,
                    timeout=timeout_duration
                )
                
                if result.returncode == 0:
                    print(f"   ✅ {lib} instalado com sucesso!")
                else:
                    if is_tts:
                        print(f"   ⚠️  {lib} falhou (esperado sem Visual C++ Build Tools)")
                        print("      Sistema funcionará com Edge-TTS/pyttsx3 alternativos.")
                    else:
                        stderr_short = result.stderr[:300] if result.stderr else "Sem detalhes"
                        print(f"   ❌ Erro ao instalar {lib}")
                        print(f"      {stderr_short}")
            except subprocess.TimeoutExpired:
                if is_tts:
                    print(f"   ⏱️  Timeout ao instalar {lib} (2min)")
                    print(f"      TTS compilação falhou. Sistema usará Edge-TTS/pyttsx3.")
                else:
                    print(f"   ⏱️  Timeout ao instalar {lib}")
            except Exception as e:
                print(f"   ❌ Exceção ao instalar {lib}: {str(e)[:200]}")
        
        print("\n✅ Instalação P0/P1 concluída!")
    else:
        print("✅ Todas as bibliotecas P0/P1 estão instaladas!")

    # 6. ML Models (Soft Check)
    print("\n🔍 Validando modelos ML...")
    models = [
        "models/yolov8n.pt",
        "models/hand_landmarker.task"
    ]
    missing = []
    for m in models:
        if not Path(m).exists():
            print(f"🟡 AVISO: Modelo ausente: {m}")
            missing.append(m)
            
    if missing:
        print("\n[PROPOSTA] Componentes de visão ausentes detectados.")
        choice = input("Gostaria de baixar os modelos necessários agora? (S/N): ").strip().lower()
        if choice == 's':
            try:
                subprocess.run([sys.executable, "scripts/install/download_models.py"], check=True)
                print("✅ Modelos sincronizados.")
            except Exception as e:
                print(f"❌ Falha ao invocar o downloader: {e}")
        else:
            print("ℹ️ Continuando sem modelos (funcionalidades reduzidas).")

    print("\n🚀 Pre-flight concluído com sucesso!")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(validate())
