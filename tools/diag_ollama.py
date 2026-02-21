import requests
import subprocess
import json

def diag():
    print("--- DIAGNÓSTICO OLLAMA ---")
    
    # 1. Testar API diretamente
    print("\n1. Testando API (http://localhost:11434/api/tags)...")
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            print(f"Modelos encontrados via API: {len(models)}")
            for m in models:
                print(f" - {m['name']}")
        else:
            print(f"Erro na API: {resp.text}")
    except Exception as e:
        print(f"FALHA NA API: {e}")

    # 2. Testar CLI
    print("\n2. Testando CLI (ollama list)...")
    try:
        proc = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if proc.returncode == 0:
            print("Saída do CLI:")
            print(proc.stdout)
        else:
            print(f"Erro no CLI (código {proc.returncode}): {proc.stderr}")
    except Exception as e:
        print(f"FALHA NO CLI: {e}")

if __name__ == "__main__":
    diag()
