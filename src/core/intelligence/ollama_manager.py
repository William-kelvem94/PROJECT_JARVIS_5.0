"""
OllamaManager - Gerencia ciclo de vida do servidor Ollama e modelos (start, load, keep-alive)

Responsabilidades:
- Verificar e iniciar o servidor Ollama quando necessário
- Verificar se um modelo está instalado e forçar seu "warm-up" (carregamento em VRAM)
- Manter um heartbeat (keep-alive) para evitar descarregamento automático

Este módulo expõe a instância singleton `ollama_manager`.
"""
from __future__ import annotations

import logging
import subprocess
import sys
import threading
import time
from typing import Dict, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    requests = None
    REQUESTS_AVAILABLE = False

from src.utils.env_manager import get_config

logger = logging.getLogger(__name__)


class OllamaManager:
    def __init__(self):
        cfg = None
        try:
            cfg = get_config()
        except Exception:
            cfg = None

        # Base server URL (without /api/...)
        self.server_url = getattr(cfg, "ollama_url", "http://localhost:11434")
        self.generate_endpoint = f"{self.server_url}/api/generate"
        self.tags_endpoint = f"{self.server_url}/api/tags"

        # keepalive state: model -> {thread, stop_event, interval}
        self._keepalive: Dict[str, Dict] = {}
        self._lock = threading.Lock()

    # ----------------------------- Server health --------------------------------
    def is_server_running(self, timeout: float = 2.0) -> bool:
        """Checa se o servidor Ollama responde à API de tags."""
        if REQUESTS_AVAILABLE and requests is not None:
            try:
                resp = requests.get(self.tags_endpoint, timeout=timeout)
                return resp.status_code == 200
            except Exception:
                return False
        else:
            # fallback: tentar via urllib (menos comum em runtime)
            try:
                import urllib.request

                with urllib.request.urlopen(self.server_url, timeout=timeout) as _:
                    return True
            except Exception:
                return False

    def ensure_server_running(self, timeout: float = 15.0) -> bool:
        """Garante que o servidor Ollama esteja ativo; tenta iniciar se necessário.

        Retorna True se o servidor estiver disponível ao final (ou já estava).
        """
        if self.is_server_running():
            logger.debug("OllamaManager: servidor já está rodando")
            return True

        # Tentar iniciar via CLI `ollama serve`
        ollama_bin = shutil_which("ollama")
        if not ollama_bin:
            logger.warning("OllamaManager: binário 'ollama' não encontrado no PATH")
            return False

        logger.info("OllamaManager: servidor offline — iniciando 'ollama serve' em background")
        try:
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW

            subprocess.Popen([ollama_bin, "serve"], creationflags=creationflags, start_new_session=True)

            # Poll até o timeout
            start = time.time()
            while time.time() - start < timeout:
                if self.is_server_running(timeout=1.0):
                    logger.info("OllamaManager: servidor iniciou com sucesso")
                    return True
                time.sleep(0.5)

            logger.error("OllamaManager: tempo esgotado ao esperar o servidor Ollama iniciar")
            return False
        except Exception as e:
            logger.error(f"OllamaManager: falha ao iniciar servidor Ollama: {e}")
            return False

    # ----------------------------- Models / Load ---------------------------------
    def list_models(self) -> list:
        """Retorna lista de modelos instalados localmente (consultando /api/tags).
        Em caso de erro, retorna lista vazia.
        """
        try:
            if not REQUESTS_AVAILABLE or requests is None:
                return []
            resp = requests.get(self.tags_endpoint, timeout=3.0)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                return [m.get("name") for m in models if m.get("name")]
            return []
        except Exception:
            return []

    def is_model_installed(self, model_name: str) -> bool:
        models = self.list_models()
        return any(model_name.lower() in (m or "").lower() for m in models)

    def ensure_model_loaded(self, model_name: str, timeout: float = 30.0) -> bool:
        """Garante que o modelo esteja instalado e 'aquecido' na memória.

        - Verifica se o serviço está rodando
        - Verifica se o modelo existe localmente (não faz pull automático por padrão)
        - Envia um small `generate` para forçar o carregamento em VRAM
        """
        if not self.ensure_server_running():
            return False

        if not model_name:
            logger.debug("OllamaManager.ensure_model_loaded: model_name vazio")
            return False

        # Se o modelo não estiver instalado, retornamos False (não puxamos automaticamente)
        if not self.is_model_installed(model_name):
            logger.warning(f"OllamaManager: modelo '{model_name}' não encontrado localmente")
            return False

        # Heartbeat / warm-up via pequena chamada ao endpoint generate
        payload = {"model": model_name, "prompt": "<keep-alive>", "stream": False}
        try:
            if not REQUESTS_AVAILABLE or requests is None:
                logger.debug("OllamaManager: requests não disponível; não é possível aquecer o modelo")
                return False

            start = time.time()
            resp = requests.post(f"{self.server_url}/api/generate", json=payload, timeout=min(10, timeout))
            if resp.status_code == 200:
                logger.info(f"OllamaManager: modelo '{model_name}' aquecido na memória")
                return True
            else:
                logger.warning(f"OllamaManager: warm-up '{model_name}' retornou status {resp.status_code}")
                return False
        except Exception as e:
            logger.debug(f"OllamaManager: erro no warm-up do modelo '{model_name}': {e}")
            return False

    # ----------------------------- Keep-Alive -----------------------------------
    @staticmethod
    def _keepalive_interval_from_keepalive_value(value) -> int:
        """Converte valores do tipo '5m'|'15m'|int para segundos.
        Retorna 0 se desativado / inválido.
        """
        if not value:
            return 0
        if isinstance(value, int) or isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            val = value.strip().lower()
            if val.endswith("m"):
                try:
                    minutes = int(val[:-1])
                    return minutes * 60
                except Exception:
                    return 0
            if val.endswith("s"):
                try:
                    return int(val[:-1])
                except Exception:
                    return 0
            try:
                return int(val)
            except Exception:
                return 0
        return 0

    def start_keepalive(self, model_name: str, keep_alive_value) -> bool:
        """Inicia um background thread que periodicamente faz warm-up do modelo.

        O `keep_alive_value` pode ser inteiro (segundos) ou string ('5m').
        Se o valor for 0/None, nada é iniciado.
        """
        interval = self._keepalive_interval_from_keepalive_value(keep_alive_value)
        if interval <= 0:
            logger.debug(f"OllamaManager.start_keepalive: keep_alive desativado para {model_name}")
            return False

        # Heartbeat: enviar warm-up a cada metade do intervalo configurado, com piso em 60s
        heartbeat = max(60, int(interval / 2))

        with self._lock:
            if model_name in self._keepalive:
                # atualizar intervalo se necessário
                entry = self._keepalive[model_name]
                entry["interval"] = heartbeat
                logger.debug(f"OllamaManager: keepalive já ativo para {model_name}, atualizando intervalo={heartbeat}s")
                return True

            stop_event = threading.Event()

            def _hb_loop(stop_evt: threading.Event, model: str, _intv: int):
                logger.info(f"OllamaManager: iniciando keep-alive para {model} (interval {_intv}s)")
                while not stop_evt.wait(_intv):
                    try:
                        # Apenas tentar aquecer — erros são silenciosos
                        self.ensure_model_loaded(model, timeout=10)
                    except Exception:
                        pass
                logger.info(f"OllamaManager: keep-alive finalizado para {model}")

            t = threading.Thread(target=_hb_loop, args=(stop_event, model_name, heartbeat), daemon=True)
            self._keepalive[model_name] = {"thread": t, "stop_event": stop_event, "interval": heartbeat}
            t.start()
            return True

    def stop_keepalive(self, model_name: str) -> bool:
        with self._lock:
            entry = self._keepalive.get(model_name)
            if not entry:
                return False
            entry["stop_event"].set()
            # thread é daemon; aguardar curto
            entry["thread"].join(timeout=2)
            del self._keepalive[model_name]
            logger.info(f"OllamaManager: keep-alive parado para {model_name}")
            return True

    def stop_all_keepalives(self):
        with self._lock:
            models = list(self._keepalive.keys())
        for m in models:
            try:
                self.stop_keepalive(m)
            except Exception:
                pass


# Helper: cross-platform shutil.which (avoid importing shutil at top to keep file small)
def shutil_which(cmd: str) -> Optional[str]:
    try:
        import shutil

        return shutil.which(cmd)
    except Exception:
        return None


# Singleton instance
ollama_manager = OllamaManager()
