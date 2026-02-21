import subprocess
import shlex
import json
import requests
import re
import time
from typing import Optional, List, Dict

def select_best_model(complexity: str = "low") -> str:
    """Seleciona o melhor modelo disponível baseado na complexidade da tarefa."""
    models = get_ollama_models()
    if not models:
        from .config import OLLAMA_MODEL
        return OLLAMA_MODEL

    # Nomes de modelos preferenciais por categoria
    reasoning_keywords = ["r1", "phi3", "mistral", "mixtral", "70b"]
    fast_keywords = ["8b", "7b", "3b", "1b", "tiny", "llama3"]

    # Se a complexidade for alta (estudo/pesquisa), busca modelos 'reasoning'
    if complexity == "high":
        for m in models:
            if any(k in m["name"].lower() for k in reasoning_keywords):
                return m["name"]
    
    # Caso contrário, ou se não achou raciocínio, pega o mais leve/comum
    for m in models:
        if any(k in m["name"].lower() for k in fast_keywords):
            return m["name"]

    return models[0]["name"]

def query_ollama(model: str, prompt: str, timeout: int = 120) -> str:
    # Se o modelo for adaptativo, escolhe agora
    if model == "ADAPTIVE":
        # Heurística simples: se o prompt for longo ou tiver keywords de estudo, complexity=high
        complexity = "high" if len(prompt) > 500 or "estude" in prompt.lower() or "pesquisa" in prompt.lower() else "low"
        model = select_best_model(complexity)
        from .dashboard_server import log_task
        log_task(f"🤖 Modo Adaptativo: selecionado o modelo '{model}' para esta tarefa ({complexity}).")

    """Consome a API do Ollama (localhost:11434) para gerar respostas limpas.
    Caso a API falhe, tenta o CLI como fallback.
    """
    # 1. Tenta via API HTTP (Mais limpo, evita lixo de terminal)
    for host in ["http://127.0.0.1:11434", "http://localhost:11434"]:
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_ctx": 4096}
            }
            resp = requests.post(f"{host}/api/generate", json=payload, timeout=timeout)
            if resp.status_code == 200:
                return resp.json().get("response", "").strip()
        except Exception:
            continue

    # 2. Fallback para CLI (Pode conter lixo visual, mas é a última tentativa)
    try:
        # Tenta extrair apenas a resposta usando subprocess
        proc = subprocess.run(["ollama", "run", model, prompt], capture_output=True, text=True, timeout=timeout, encoding='utf-8', errors='replace')
        out = proc.stdout.strip()
        if out:
            # Limpeza agressiva de ANSI e lixo de manifest
            clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', out) # Remove ANSI
            clean = re.sub(r'pulling manifest.*?\n', '', clean, flags=re.IGNORECASE)
            clean = re.sub(r'verifying sha.*?\n', '', clean, flags=re.IGNORECASE)
            # Remove caracteres de controle de terminal comuns no Ollama
            clean = clean.replace('â ', '').replace('â', '').replace('â™', '').replace('â‹', '')
            return clean.strip()
    except Exception as e:
        return f"Erro Crítico: Não foi possível comunicar com o Ollama em {model}. Verifique se ele está rodando."

    return "Erro: O Ollama não retornou dados para este modelo."

_MODEL_CACHE = {"models": [], "last_sync": 0}

def get_ollama_models() -> List[Dict]:
    """Lista modelos locais sincronizados."""
    now = time.time()
    if now - _MODEL_CACHE["last_sync"] < 10:
        return _MODEL_CACHE["models"]
    
    models = []
    for host in ["http://127.0.0.1:11434", "http://localhost:11434"]:
        try:
            resp = requests.get(f"{host}/api/tags", timeout=2)
            if resp.status_code == 200:
                raw = resp.json().get("models", [])
                models = [{"name": m["name"], "size": m.get("size", 0)} for m in raw]
                break
        except:
            continue
    
    if not models:
        try:
            proc = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            if proc.returncode == 0:
                for line in proc.stdout.splitlines()[1:]:
                    if not line.strip(): continue
                    parts = line.split()
                    if len(parts) >= 1:
                        models.append({"name": parts[0], "size": 0})
        except:
            pass

    _MODEL_CACHE["models"] = models
    _MODEL_CACHE["last_sync"] = now
    return models
