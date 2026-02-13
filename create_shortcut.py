import os, sys
from pathlib import Path

def create_shortcut():
    try:
        # Tentar importar win32com (instalado com pywin32)
        try:
            import win32com.client
        except ImportError:
            print("❌ Erro: Biblioteca 'pywin32' não encontrada.")
            print("👉 Execute: pip install pywin32")
            return

        # Caminhos Base - Detectar root indepedente de onde o script é chamado
        script_dir = Path(__file__).parent.absolute()
        root_dir = script_dir # Assume que está no root
        
        target_bat = root_dir / "START_JARVIS.bat"
        if not target_bat.exists():
             # Se disparado de scripts/install/ (caso alguém mova)
             if (root_dir.parent / "START_JARVIS.bat").exists():
                 root_dir = root_dir.parent
             elif (root_dir.parent.parent / "START_JARVIS.bat").exists():
                 root_dir = root_dir.parent.parent
             target_bat = root_dir / "START_JARVIS.bat"

        if not target_bat.exists():
            print(f"❌ Erro: START_JARVIS.bat não encontrado em {root_dir}")
            return

        shell = win32com.client.Dispatch("WScript.Shell")
        desktop = shell.SpecialFolders("Desktop")
        path = os.path.join(desktop, "JARVIS 5.0.lnk")
        
        shortcut = shell.CreateShortcut(path)
        shortcut.TargetPath = str(target_bat)
        shortcut.WorkingDirectory = str(root_dir)
        shortcut.IconLocation = "shell32.dll, 238" 
        shortcut.Description = "Protocolo JARVIS 5.0 - Singularity"
        shortcut.save()
        
        print(f"✅ Atalho criado com sucesso em: {path}")
        print(f"📍 Apontando para: {target_bat}")
        
    except Exception as e:
        print(f"❌ Erro ao criar atalho: {e}")

if __name__ == "__main__":
    create_shortcut()
