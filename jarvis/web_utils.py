import requests
from bs4 import BeautifulSoup
import logging
import time

logger = logging.getLogger("JARVIS-WEB-UTILS")

def _get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

def search_huggingface(query: str) -> str:
    """Busca modelos e papers no HuggingFace."""
    try:
        resp = requests.get("https://huggingface.co/api/models", params={"search": query, "limit": 3}, timeout=10)
        models = resp.json() if resp.ok else []
        model_list = [m.get("modelId") for m in models]
        summary = f"HuggingFace: Modelos relevantes: {', '.join(model_list)}." if model_list else ""
        return summary
    except Exception: return ""

def search_google_scholar(query: str) -> str:
    """Busca lite no Google Scholar."""
    try:
        url = f"https://scholar.google.com/scholar?q={query}"
        resp = requests.get(url, headers=_get_headers(), timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        for item in soup.select('.gs_ri')[:2]:
            title = item.select_one('.gs_rt').text if item.select_one('.gs_rt') else "Paper"
            results.append(f"ACADÊMICO: {title}")
        return "\n".join(results)
    except Exception: return ""

def search_arxiv(query: str) -> str:
    """Busca papers técnicos GRATUITOS no ArXiv.org."""
    try:
        url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=3"
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'xml')
        results = []
        for entry in soup.find_all('entry'):
            title = entry.title.text.strip()
            summary = entry.summary.text.strip()
            results.append(f"BASE ARXIP (Gratuita): {title}\nDETALHE: {summary[:400]}")
        return "\n\n".join(results)
    except Exception: return ""

def deep_scrape_url(url: str) -> str:
    """Extrai o texto real de uma página para alimentar o cérebro."""
    try:
        if "google" in url or "duckduckgo" in url: return ""
        resp = requests.get(url, headers=_get_headers(), timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']): tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text[:2500]
    except: return ""

def search_online(query: str) -> str:
    """Orquestrador de pesquisa DEEP Multi-Fonte."""
    logger.info(f"🌌 Invocando Deep Knowledge Acquisition para: {query}")
    try:
        from .dashboard_server import log_task
        log_task(f"🔍 Iniciando ciclo de pesquisa 'deep': {query}")
    except: pass
    
    # 1. Mineração de Links Gerais
    deep_content = []
    try:
        search_url = f"https://duckduckgo.com/html/?q={query}"
        resp = requests.get(search_url, headers=_get_headers(), timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for item in soup.select('.result__body')[:2]:
            link = item.select_one('.result__a')['href']
            title = item.select_one('.result__title').text.strip()
            logger.info(f"⛏️ Minerando fundo em: {title}")
            try: log_task(f"🌐 Verificando fonte: {title}")
            except: pass
            full_text = deep_scrape_url(link)
            if full_text:
                deep_content.append(f"MINERAÇÃO WEB: {title}\nCONTEÚDO: {full_text}")
    except: pass

    # 2. Bases de Conhecimento Específicas
    try: log_task("📚 Mapeando bases acadêmicas (ArXiv/Scholar/HF)")
    except: pass
    hf = search_huggingface(query)
    scholar = search_google_scholar(query)
    arxiv = search_arxiv(query)
    
    web_data_str = "--- WEB DATA ---\n" + "\n\n".join(deep_content) if deep_content else ""
    academic_str = "--- ACADEMIC ---\n" + arxiv + "\n" + scholar if arxiv or scholar else ""
    
    hf_str = "--- HF MODELS ---\n" + hf if hf else ""
    
    combined = (
        f"{web_data_str}\n\n"
        f"{hf_str}\n\n"
        f"{academic_str}"
    )
    return combined if combined.strip() else "Nenhum dado profundo encontrado."
