import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

# Garantir que o output suporte UTF-8 (para emojis no Windows)
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

# Configuração de Caminhos
# O script está em scripts/maintenance/unify_memory.py
# parent.parent.parent do script leva à raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MEMORY_DIR = DATA_DIR / "memory"

# Candidatos à migração
SOURCE_BRAIN = MEMORY_DIR / "neural"  # O "Vencedor" (Maior tamanho)
TARGET_BRAIN = MEMORY_DIR / "vector_store" # O destino oficial do Manifesto
BACKUP_DIR = DATA_DIR / "backups" / f"memory_fragmented_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def perform_surgery():
    print(f"🏥 Iniciando Cirurgia de Memória JARVIS...")
    
    # 1. Criar backup de segurança
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True)
        print(f"📦 Diretório de backup criado: {BACKUP_DIR}")

    # 2. Identificar e mover "órgãos" conflitantes
    conflicts = [
        MEMORY_DIR / "chroma.sqlite3",
        MEMORY_DIR / "chroma_db",
        DATA_DIR / "tests" / "chromadb"
    ]

    for conflict in conflicts:
        if conflict.exists():
            dest = BACKUP_DIR / conflict.name
            print(f"⚠️ Conflito detectado: {conflict.name}. Movendo para quarentena...")
            try:
                shutil.move(str(conflict), str(dest))
            except Exception as e:
                print(f"❌ Falha ao mover {conflict.name}: {e}")

    # 3. Transplante do Cérebro Principal
    if SOURCE_BRAIN.exists():
        if TARGET_BRAIN.exists():
            # Se o destino já existe e tem conteúdo, arquiva
            if any(TARGET_BRAIN.iterdir()):
                print(f"ℹ️ O destino {TARGET_BRAIN.name} já existe e não está vazio. Arquivando o antigo antes de substituir.")
                shutil.move(str(TARGET_BRAIN), str(BACKUP_DIR / "vector_store_old"))
            else:
                # Se está vazio, apenas remove para permitir o move do SOURCE_BRAIN
                TARGET_BRAIN.rmdir()
        
        print(f"🧠 Migrando dados neurais ({SOURCE_BRAIN.name}) para a nova estrutura ({TARGET_BRAIN.name})...")
        shutil.move(str(SOURCE_BRAIN), str(TARGET_BRAIN))
        print(f"✅ Transplante concluído com sucesso.")
    else:
        print(f"❌ ERRO: Fonte neural {SOURCE_BRAIN} não encontrada.")
        if not TARGET_BRAIN.exists():
            print(f"Creating empty vector store directory as fallback.")
            TARGET_BRAIN.mkdir(parents=True, exist_ok=True)

    print(f"🏁 Cirurgia finalizada. O JARVIS agora tem uma Única Fonte da Verdade.")

if __name__ == "__main__":
    perform_surgery()
