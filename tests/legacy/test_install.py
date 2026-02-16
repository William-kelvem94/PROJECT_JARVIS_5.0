# test_install.py
import sys
import subprocess
import os

print("\n" + "="*50)
print("🔍 TESTANDO INSTALAÇÃO JARVIS 5.0")
print("="*50)

# Testa PyTorch
try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
    from packaging import version
    if version.parse(torch.__version__.split('+')[0]) < version.parse("2.4.0"):
        print(f"❌ PyTorch muito antigo ({torch.__version__})! Necessário >= 2.4.0")
        # sys.exit(1)
    else:
        print("   -> Versão compatível.")
except ImportError:
    print("❌ PyTorch não instalado")
    # sys.exit(1)

# Testa dlib
try:
    import dlib
    print(f"✅ dlib: {dlib.__version__}")
except ImportError:
    print("❌ dlib não instalado")

# Testa face_recognition
try:
<<<<<<< Updated upstream
    import face_recognition
    print("✅ face_recognition: Carregado com sucesso")
    # Tenta importar modelos
    import face_recognition_models
=======
    import face_recognition  # noqa: F401

    print("✅ face_recognition: Carregado com sucesso")
    # Tenta importar modelos
    import face_recognition_models  # noqa: F401

>>>>>>> Stashed changes
    print("✅ face_recognition_models: Encontrado")
except ImportError as e:
    print(f"❌ Erro no face_recognition: {e}")

# Testa Transformers
try:
    import transformers
    import tokenizers
    print(f"✅ Transformers: {transformers.__version__}")
    print(f"✅ Tokenizers: {tokenizers.__version__}")
except ImportError as e:
    print(f"❌ Erro em IA Core: {e}")

# Testa Voice
try:
<<<<<<< Updated upstream
    import webrtcvad
=======
    import webrtcvad  # noqa: F401

>>>>>>> Stashed changes
    print("✅ webrtcvad OK")
except ImportError:
    print("❌ webrtcvad não instalado")

print("\n" + "="*50)
print("Dica: Se tudo estiver ✅, execute: python main.py")
print("="*50)
