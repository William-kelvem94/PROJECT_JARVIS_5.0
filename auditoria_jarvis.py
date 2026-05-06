# Relocated to scripts/auditoria_jarvis.py
import subprocess, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
subprocess.run([sys.executable, "scripts/auditoria_jarvis.py"] + sys.argv[1:])
