import os
import shutil
from loguru import logger

def clean_project():
    """Remove arquivos temporários, logs e arquivos de backup redundantes."""
    logger.info(" iniciando faxina no JARVIS 5.0...")
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Padrões de arquivos e pastas para deletar
    targets = [
        "backend/app/__pycache__",
        "backend/app/perception/__pycache__",
        "backend/app/utils/__pycache__",
        "backend/data/memories.json", # Backup antigo do mem0
        "backend/requirements.txt.mem0",
        "launcher-run.txt",
        "temp-debug.bat",
        "debug.log",
    ]
    
    for target in targets:
        full_path = os.path.join(root_dir, target)
        if os.path.exists(full_path):
            try:
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                    logger.info(f"📁 Pasta removida: {target}")
                else:
                    os.remove(full_path)
                    logger.info(f"📄 Arquivo removido: {target}")
            except Exception as e:
                logger.error(f"❌ Falha ao remover {target}: {e}")
                
    logger.success("✨ Faxina concluída! Projeto limpo e otimizado.")

if __name__ == "__main__":
    clean_project()
