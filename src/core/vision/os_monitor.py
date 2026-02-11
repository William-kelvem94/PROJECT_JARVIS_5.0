"""
O Olho no Sistema (OS Monitor)
Monitoramento de processos e janelas ativas sem uso de OCR (Custo Zero de Performance).
"""

import sys
import psutil
import time
import logging

# Logger setup
logger = logging.getLogger(__name__)

# Cache de Contexto para evitar emissões duplicadas
_last_window_title = None

try:
    from src.utils.web_emitter import emit_context
except ImportError:
    emit_context = lambda *args: None
try:
    import win32gui
    import win32process
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False
    logger.warning("⚠️ pywin32 não encontrado. Usando fallback ctypes (menos preciso).")
    import ctypes

def get_active_window_context() -> dict:
    """
    Retorna o contexto da janela ativa no Windows.
    Retorno: {"title": str, "executable": str, "pid": int}
    """
    context = {"title": "Unknown", "executable": "Unknown", "pid": -1}
    
    try:
        if PYWIN32_AVAILABLE:
            hwnd = win32gui.GetForegroundWindow()
            pid = win32process.GetWindowThreadProcessId(hwnd)[1]
            title = win32gui.GetWindowText(hwnd)
            
            context["pid"] = pid
            context["title"] = title
            
            try:
                process = psutil.Process(pid)
                context["executable"] = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                context["executable"] = "System/Protected"
                
        else:
            # Fallback ctypes
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            
            # PID no ctypes é mais chato sem pywin32, pegando apenas Título
            context["title"] = buf.value
            context["executable"] = "Unknown (Install pywin32)"
            
    except Exception as e:
        logger.error(f"Erro ao capturar janela ativa: {e}")
        
    # 🆕 FASE 5: Emitir sinal se o contexto mudou
    global _last_window_title
    current_title = context.get("title", "Unknown")
    if current_title != _last_window_title:
        _last_window_title = current_title
        emit_context(context.get("executable", "Sistema"), current_title)
        
    return context

def analyze_process_health(process_name: str) -> dict:
    """
    Analisa saúde de processos pelo nome (ex: 'chrome.exe').
    Retorna agregado de CPU/RAM se houver múltiplas instâncias.
    """
    stats = {
        "name": process_name,
        "count": 0,
        "cpu_percent": 0.0,
        "memory_mb": 0.0,
        "status": "not_found"
    }
    
    try:
        count = 0
        total_cpu = 0.0
        total_mem = 0.0
        
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    count += 1
                    total_cpu += proc.info['cpu_percent'] or 0.0
                    total_mem += (proc.info['memory_info'].rss / 1024 / 1024) # MB
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        if count > 0:
            stats["count"] = count
            stats["cpu_percent"] = round(total_cpu, 2)
            stats["memory_mb"] = round(total_mem, 2)
            stats["status"] = "running"
            
    except Exception as e:
        logger.error(f"Erro ao analisar processo {process_name}: {e}")
        stats["status"] = "error"
        
    return stats

if __name__ == "__main__":
    # Teste rápido
    print("Módulo OS Monitor - Teste")
    time.sleep(1) # Tempo para focar janela
    print(f"Janela Ativa: {get_active_window_context()}")
    print(f"Status Python: {analyze_process_health('python')}")
