import os
import sys
from pathlib import Path

def create_shortcut():
    try:
        import win32com.client
    except ImportError:
        print("❌ Biblioteca 'pywin32' não encontrada. Instale com: pip install pywin32")
        return

    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        desktop = shell.SpecialFolders("Desktop")
        shortcut_path = os.path.join(desktop, "JARVIS 5.0.lnk")
        
        # O script agora reside em scripts/install/
        # base_path = project_root/scripts/install
        current_script_path = Path(__file__).resolve()
        project_root = current_script_path.parent.parent.parent
        
        # Preferimos usar o start_jarvis.bat que é o launcher profissional
        target = project_root / "start_jarvis.bat"
        
        if not target.exists():
            # Fallback para jarvis.bat se start_jarvis não existir
            target = project_root / "jarvis.bat"

        if not target.exists():
            print(f"❌ Erro: Lançador não encontrado em: {project_root}")
            return

        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = "cmd.exe"
        
        # /c fecha o terminal após o término (opcional), /k mantém aberto
        # Usamos /c para o atalho de produção, permitindo que o log do JARVIS assuma
        shortcut.Arguments = f'/c "{target}"'
        shortcut.WorkingDirectory = str(project_root)
        
        # Ícone de chip/IA do shell32 (índice 13 ou similar)
        # 13: Chip, 238: Configurações, 173: Monitor
        shortcut.IconLocation = "shell32.dll, 13" 
        shortcut.Description = "JARVIS 5.0 - Singularity Protocol"
        shortcut.save()
        
        print(f"✅ Atalho criado com sucesso: {shortcut_path}")
        print(f"📍 Apontando para: {target}")
        print(f"📂 Diretório de trabalho: {project_root}")
        
    except Exception as e:
        print(f"❌ Erro ao criar atalho: {e}")

if __name__ == "__main__":
    create_shortcut()
