import os
import sys
import asyncio
import logging
from pathlib import Path

# Adicionar o diretório raiz ao sys.path para importações
sys.path.append(str(Path(__name__).parent.absolute()))

from src.core.audio.voice_controller import VoiceController

async def test_engine():
    logging.basicConfig(level=logging.INFO)
    print("🚀 Inciando Teste da Stark Hybrid Voice Engine...")
    
    vc = VoiceController()
    
    # Texto de teste com pontuação preservada
    test_text = "Olá, eu sou o JARVIS! A Stark Hybrid Voice Engine está operacional? Vamos verificar o cache..."
    
    print(f"\n📢 Sintetizando: \"{test_text}\"")
    # Teste de fala (Sincrono para acompanhar)
    vc.speak(test_text, wait=True)
    
    print("\n✅ Teste de fala concluído. Verificando cache...")
    
    # Verificar se o arquivo foi criado no cache
    import hashlib
    text_hash = hashlib.md5(test_text.lower().strip().encode('utf-8')).hexdigest()
    cache_file = Path(f"data/audio_cache/{text_hash}.wav")
    
    if cache_file.exists():
        print(f"🎯 Sucesso! Arquivo de cache encontrado: {cache_file}")
        print("🔄 Testando reprodução via cache (deve ser instantânea)...")
        vc.speak(test_text, wait=True)
    else:
        print("❌ Erro: Arquivo de cache não encontrado.")

if __name__ == "__main__":
    asyncio.run(test_engine())
