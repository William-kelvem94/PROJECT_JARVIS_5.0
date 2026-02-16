import os
import platform
import subprocess
from pathlib import Path

def create_shortcut():
    """Cria um atalho para o JARVIS no Desktop (Cross-platform)"""
    system = platform.system()
    
    # Resolver caminhos absolutos
    current_script_path = Path(__file__).resolve()
    # Assume script is in scripts/install, so project_root is 2 levels up
    project_root = current_script_path.parent.parent.parent
    
    if system == "Windows":
        target_script = project_root / "start_jarvis.bat"
        if not target_script.exists():
            print(f"❌ Arquivo de inicialização não encontrado: {target_script}")
            print("   Não foi possível criar o atalho. Verifique se o script de inicialização foi gerado corretamente.")
            return
        print(f"[LOG] Validando arquivo de inicialização: {target_script}")
        # Valida dependências/configuração antes de criar o atalho
        setup_script = project_root / "scripts" / "install" / "setup_jarvis.py"
        if setup_script.exists():
            print("[LOG] Validando dependências e configuração do projeto...")
            result = subprocess.run(["python", str(setup_script), "--quick-check"], capture_output=True)
            if result.returncode != 0:
                print("[LOG] Dependências/configuração ausentes. Executando setup completo...")
                subprocess.run(["python", str(setup_script), "--no-scripts"], check=True)
        else:
            print("[LOG] setup_jarvis.py não encontrado. Prosseguindo sem validação.")
        shortcut_name = input("Nome do atalho (padrão: JARVIS 5.0): ") or "JARVIS 5.0"
        custom_icon = project_root / "resources" / "icon.ico"
        if not custom_icon.exists():
            print("[LOG] Ícone personalizado não encontrado. Usando ícone padrão.")
        else:
            print(f"[LOG] Usando ícone personalizado: {custom_icon}")
        try:
            _create_windows_shortcut(project_root, target_script, shortcut_name, custom_icon)
            print(f"[SUCESSO] Atalho '{shortcut_name}' criado na área de trabalho.")
            print("[INFO] Para iniciar o Jarvis, basta clicar no atalho. Se houver problemas, execute novamente este script ou verifique as dependências.")
        except Exception as e:
            print(f"[ERRO] Falha ao criar o atalho: {e}")
            print("[DICA] Verifique permissões, dependências e o arquivo start_jarvis.bat.")
    elif system == "Linux":
        target_script = project_root / "start_jarvis.sh"
        if not target_script.exists():
            print(f"❌ Arquivo de inicialização não encontrado: {target_script}")
            print("   Não foi possível criar o atalho. Verifique se o script de inicialização foi gerado corretamente.")
            return
        _create_linux_shortcut(project_root, target_script)
    else:
        print(f"⚠️ Sistema {system} não suportado para criação automática de atalho.")

def _create_windows_shortcut(project_root, target_bat, shortcut_name, custom_icon):
    """Cria atalho no Windows usando PyWin32 ou PowerShell como fallback"""
    desktop = Path(os.path.expanduser("~/Desktop"))
    shortcut_path = desktop / f"{shortcut_name}.lnk"
    icon_location = str(custom_icon) if custom_icon and custom_icon.exists() else "imageres.dll,23"
    print(f"🚀 Gerando atalho {shortcut_name} para Windows...")

    # Tenta usar PyWin32 se disponível
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = str(target_bat)
        shortcut.WorkingDirectory = str(project_root)
        shortcut.IconLocation = icon_location
        shortcut.Description = f"{shortcut_name} - JARVIS 5.0"
        shortcut.Save()
        print(f"✅ Atalho '{shortcut_name}' criado com sucesso via PyWin32: {shortcut_path}")
        print("[INFO] Atalho pronto para uso na área de trabalho.")
        return
    except ImportError as e:
        print(f"⚠️ PyWin32 (win32com.client) não disponível, usando PowerShell como fallback: {e}")
        # Fallback Profissional: PowerShell (Zero-Dependency)
        try:
            ps_script = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
            $Shortcut.TargetPath = '{target_bat}'
            $Shortcut.WorkingDirectory = '{project_root}'
            $Shortcut.IconLocation = '{icon_location}'
            $Shortcut.Description = 'JARVIS 5.0 - Singularity Protocol'
            $Shortcut.Save()
            """
            subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script], check=True, capture_output=True)
            print(f"✅ Atalho criado com sucesso via PowerShell: {shortcut_path}")
        except Exception as e:
            print(f"❌ Erro ao criar atalho no Windows: {e}")

def _create_linux_shortcut(project_root, target_sh):
    """Cria um arquivo .desktop no Linux"""
    desktop = Path(os.path.expanduser("~/Desktop"))
    if not desktop.exists():
        # Tentar XDG_DESKTOP_DIR ou criar pasta Desktop se não existir
        desktop.mkdir(parents=True, exist_ok=True)

    shortcut_path = desktop / "jarvis.desktop"
    
    # Tentar encontrar um ícone personalizado no projeto
    icon_path = "utilities-terminal"
    custom_icon_png = project_root / "resources" / "icon.png"
    if custom_icon_png.exists():
        icon_path = str(custom_icon_png)

    content = f"""[Desktop Entry]
Name=JARVIS 5.0
Comment=Singularity Protocol
Exec=bash "{target_sh}"
Icon={icon_path}
Terminal=true
Type=Application
Categories=Development;AI;
"""
    try:
        with open(shortcut_path, "w") as f:
            f.write(content)
        # Tornar executável
        os.chmod(shortcut_path, 0o755)
        print(f"✅ Arquivo .desktop criado em: {shortcut_path}")
    except (OSError, IOError, PermissionError) as e:
        print(f"❌ Erro ao criar atalho no Linux: {e}")

if __name__ == "__main__":
    print("""
    =============================================
    JARVIS 5.0 - Script de Criação de Atalho
    =============================================
    Este script prepara o ambiente, valida dependências e cria um atalho personalizado na área de trabalho.
    - O atalho executa o start_jarvis.bat, que inicializa o Jarvis.
    - Você pode escolher o nome e o ícone do atalho.
    - Se houver problemas, verifique permissões, dependências ou execute novamente.
    =============================================
    """)
    create_shortcut()
