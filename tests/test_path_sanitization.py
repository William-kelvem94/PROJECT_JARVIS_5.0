import sys
import os

# Adicionar o root do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.audio.voice_controller import VoiceController

def test_sanitization():
    vc = VoiceController()
    
    test_cases = [
        ("O arquivo está em C:\\Users\\Admin\\Documents\\test.txt", "O arquivo está em o local do sistema"),
        ("Acesse /home/user/project/main.py agora", "Acesse o caminho do arquivo agora"),
        ("Erro no diretório D:\\Games\\Skyrim\\data", "Erro no diretório o local do sistema"),
        ("Running ```python main.py``` check it", "Running  check it")
    ]
    
    print("\n🧪 Testando Higienização Nuclear de Caminhos...\n")
    all_passed = True
    
    for input_text, expected in test_cases:
        result = vc.clean_text_for_speech(input_text)
        if result == expected:
            print(f"✅ PASS: '{input_text}' -> '{result}'")
        else:
            print(f"❌ FAIL: '{input_text}'")
            print(f"   Expected: '{expected}'")
            print(f"   Got:      '{result}'")
            all_passed = False
            
    if all_passed:
        print("\n🎉 Todos os testes de higienização passaram!")
    else:
        print("\n⚠️ Falha na higienização de caminhos.")

if __name__ == "__main__":
    test_sanitization()
