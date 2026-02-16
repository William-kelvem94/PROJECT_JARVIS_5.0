import os
import platform
import subprocess
from pathlib import Path

def create_shortcut():
    """Cria um atalho para o JARVIS no Desktop (Cross-platform)"""
    system = platform.system()
    
    # Resolver caminhos absolutos
    current_script_path = Path(__file__).resolve()
    project_root = current_script_path.parent.parent.parent
    target_bat = project_root / "start_jarvis.bat"
    
    if not target_bat.exists():
        target_bat = project_root / "jarvis.bat"

    if system == "Windows":
        _create_windows_shortcut(project_root, target_bat)
    elif system == "Linux":
        _create_linux_shortcut(project_root, target_bat)
    else:
        print(f"⚠️ Sistema {system} não suportado para criação automática de atalho.")

def _create_windows_shortcut(project_root, target_bat):
    """Cria atalho no Windows usando PyWin32 ou PowerShell como fallback"""
    desktop = Path(os.path.expanduser("~/Desktop"))
    shortcut_path = desktop / "JARVIS 5.0.lnk"
    icon_location = "imageres.dll,23" # Ícone de olho/câmera (visão computacional, mais apropriado para IA)
    
    print("🚀 Gerando atalho JARVIS 5.0 para Windows...")

    # Tenta usar PyWin32 se disponível
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = "cmd.exe"
        shortcut.Arguments = f'/c "{target_bat}"'
        shortcut.WorkingDirectory = str(project_root)
        shortcut.IconLocation = icon_location
        shortcut.Description = "JARVIS 5.0 - Singularity Protocol"
        shortcut.save()
        print(f"✅ Atalho criado com sucesso via PyWin32: {shortcut_path}")
        return
    except ImportError:
        pass # Fallback para PowerShell

    # Fallback Profissional: PowerShell (Zero-Dependency)
    try:
        ps_script = f"""
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "cmd.exe"
        $Shortcut.Arguments = '/c "{target_bat}"'
        $Shortcut.WorkingDirectory = "{project_root}"
        $Shortcut.IconLocation = "{icon_location}"
        $Shortcut.Description = "JARVIS 5.0 - Singularity Protocol"
        $Shortcut.Save()
        """
        subprocess.run(["powershell", "-Command", ps_script], check=True, capture_output=True)
        print(f"✅ Atalho criado com sucesso via PowerShell: {shortcut_path}")
    except Exception as e:
        print(f"❌ Erro ao criar atalho no Windows: {e}")

def _create_linux_shortcut(project_root, target_bat):
    """Cria um arquivo .desktop no Linux"""
    desktop = Path(os.path.expanduser("~/Desktop"))
    shortcut_path = desktop / "jarvis.desktop"
    
    content = f"""[Desktop Entry]
Name=JARVIS 5.0
Comment=Singularity Protocol
Exec=bash "{target_bat}"
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=Development;AI;
Path={project_root}
"""
    try:
        with open(shortcut_path, "w") as f:
            f.write(content)
        # Tornar executável
        os.chmod(shortcut_path, 0o755)
        print(f"✅ Arquivo .desktop criado em: {shortcut_path}")
    except Exception as e:
        print(f"❌ Erro ao criar atalho no Linux: {e}")

if __name__ == "__main__":
    create_shortcut()
