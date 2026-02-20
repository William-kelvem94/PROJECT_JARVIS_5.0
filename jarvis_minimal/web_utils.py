"""Utilities for performing simple web searches.

Currently uses DuckDuckGo instant-answer API and HuggingFace model search as
fallback.  Results are returned as plain text summaries suitable for feeding
back to the user or the training pipeline.
"""

import requests


def search_online(query: str) -> str:
    """Return a short summary found on the web for *query*.

    The function first queries DuckDuckGo's instant answer API.  If that API
    delivers a non-empty ``AbstractText`` we return it.  Otherwise we fall back
    to searching the HuggingFace model hub and listing a few matching models
    (this is just a placeholder for a real web crawl).

    Errors are swallowed and a generic failure message is returned.
    """
    q = query or ""
    q = q.strip()
    if not q:
        return "Nenhum termo de busca fornecido."

    # try DuckDuckGo instant answer (no API key required)
    try:
        resp = requests.get("https://api.duckduckgo.com/", params={"q": q, "format": "json"}, timeout=5)
        if resp.ok:
            data = resp.json()
            text = data.get("AbstractText")
            if text:
                return text
    except Exception:
        pass

    # fallback: search HuggingFace models
    try:
        resp = requests.get("https://huggingface.co/api/models", params={"search": q}, timeout=10)
        if resp.ok:
            models = resp.json()
            names = [m.get("modelId") for m in models[:5] if m.get("modelId")]
            if names:
                return "Encontrei modelos no HuggingFace: " + ", ".join(names)
    except Exception:
        pass

    return "Não consegui encontrar nada relevante na web."