import os
from dotenv import load_dotenv
from google import genai

from pathlib import Path

# Encontrar a raiz do projeto (PROJECT_JARVIS_5.0)
base_dir = Path(__file__).resolve().parents[2]
env_path = base_dir / "env" / ".env"
root_env_path = base_dir / ".env"

# Tenta carregar do root ou da pasta env/
if root_env_path.exists():
    load_dotenv(root_env_path)
elif env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv() # Fallback para o diretório atual

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})

try:
    print("Listando modelos...")
    for m in client.models.list():
        # No SDK novo, o nome do modelo está em m.name
        # E os métodos suportados em m.supported_generation_methods (se existir)
        # Vamos apenas imprimir o que for relevante
        print(f"- {m.name}")
except Exception as e:
    print(f"Erro: {e}")
