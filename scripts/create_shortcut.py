import os, sys
try:
    import win32com.client
    shell = win32com.client.Dispatch("WScript.Shell")
    desktop = shell.SpecialFolders("Desktop")
    path = os.path.join(desktop, "JARVIS 5.0.lnk")
    target = os.path.abspath("START_JARVIS.bat")
    
    shortcut = shell.CreateShortcut(path)
    shortcut.TargetPath = target
    shortcut.WorkingDirectory = os.path.dirname(target)
    shortcut.IconLocation = "shell32.dll, 238" # Ícone genérico de sistema/chip
    shortcut.save()
    print(f"✅ Atalho criado com sucesso em: {path}")
except Exception as e:
    print(f"❌ Erro ao criar atalho: {e}")
