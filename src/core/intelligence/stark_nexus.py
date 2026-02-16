#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Stark Nexus (Research & Web Expansion)
====================================================
MÃ³dulo para busca externa no Google e Hugging Face.
Foca em datasets de conhecimento (.md) e Markdowns de estudo.
"""

import os
import requests
import logging
import re
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class StarkNexus:
    """O portal de expansÃ£o do JARVIS para a internet"""
    
    def __init__(self, download_path: str = "data/knowledge/nexus"):
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.google_api_key = os.environ.get("GOOGLE_API_KEY")
        self.is_enabled = True # William pode desativar via HUD
        
    def pesquisar(self, contexto: str, termo: str) -> List[Dict[str, str]]:
        """Pesquisa conhecimento externo baseado no contexto"""
        if not self.is_enabled: return []
        
        logger.info(f"ðŸ›°ï¸ Nexus ativado: Pesquisando '{termo}' no contexto {contexto}")
        
        resultados = []
        # No futuro, integrar Serper ou Google Search API aqui
        # Por enquanto, simulaÃ§Ã£o de retorno de fontes seguras
        if "programaÃ§Ã£o" in contexto.lower() or "desenvolver" in termo.lower():
            resultados.append({"title": "GitHub Knowledge Base", "url": "https://github.com/topics/knowledge-base"})
        
        return resultados

    def baixar_conhecimento(self, url: str) -> bool:
        """Faz o download de arquivos .md e limpa scripts/tags maliciosas"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # SANITIZAÃ‡ÃƒO (SeguranÃ§a Stark)
                # Remove scripts, iframes e tags perigosas
                content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL)
                content = re.sub(r'<iframe.*?>.*?</iframe>', '', content, flags=re.DOTALL)
                
                filename = re.sub(r'[^a-zA-Z0-9]', '_', url.split("/")[-1]) + ".md"
                with open(self.download_path / filename, "w", encoding="utf-8") as f:
                    f.write(content)
                
                logger.info(f"âœ… Conhecimento baixado e sanitizado: {filename}")
                return True
        except Exception as e:
            logger.error(f"âŒ Falha no Nexus ao baixar {url}: {e}")
        return False

# InstÃ¢ncia global
stark_nexus = StarkNexus()
