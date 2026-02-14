import os, sys
try:
    import win32com.client
    shell = win32com.client.Dispatch("WScript.Shell")
    desktop = shell.SpecialFolders("Desktop")
    # Usar .lnk para o nome do arquivo
    path = os.path.join(desktop, "JARVIS 5.0.lnk")
    
    # Garantir que o target seja absoluto e aponte para o .bat
    base_path = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(base_path, ".."))
    target = os.path.join(project_root, "START_JARVIS.bat")
    
    if not os.path.exists(target):
        # Fallback se não encontrar o .bat no root relativo ao script
        target = os.path.abspath("START_JARVIS.bat")

    shortcut = shell.CreateShortcut(path)
    shortcut.TargetPath = "cmd.exe"
    # Argumentos para rodar o BAT e manter a janela aberta em caso de erro para diagnóstico
    shortcut.Arguments = f'/c "{target}"'
    shortcut.WorkingDirectory = project_root
    shortcut.IconLocation = "shell32.dll, 238" 
    shortcut.Description = "Sistema JARVIS 5.0 - Protocolo Singularity"
    shortcut.save()
    print(f"✅ Atalho criado com sucesso em: {path}")
    print(f"📍 Apontando para: {target}")
except Exception as e:
    print(f"❌ Erro ao criar atalho: {e}")
