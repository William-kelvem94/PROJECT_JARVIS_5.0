#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Analisador de Contexto Stark
=========================================
Detecta a intenção e o domínio do comando do William.
"""

import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AnalisadorContexto:
    """O 'Lóbulo Frontal' do Jarvis para detecção de intenção"""
    
    def __init__(self):
        self.categorias = {
            "PROGRAMACAO": ["api", "json", "python", "backend", "deploy", "bug", "log", "código", "desenvolver", "git", "stack", "react", "node", "database", "sql"],
            "PSICOLOGIA": ["relacionamento", "namorada", "sentimento", "trauma", "terapia", "mente", "psicologia", "emoção", "conversa"],
            "HARDWARE": ["cpu", "gpu", "ram", "swap", "temperatura", "clima", "brilho", "volume", "processamento", "iris"],
            "MULTIMIDIA": ["música", "youtube", "ouvir", "video", "play", "pause", "navegador", "chrome", "edge", "spotify"],
            "AUTONOMIA": ["estude", "estudar", "treine", "treinar", "aprenda", "aprender", "pesquise", "pesquisar", "nexus", "sonhe", "sonhar", "idle", "evoluir"],
            "NEGOCIOS": ["aluguel", "gestor", "vendas", "cliente", "projeto", "financeiro", "planilha"]
        }
    
    def analisar(self, comando: str, vision_text: str = "", window_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Retorna o contexto predominante e metadados do comando + visão + janela ativa"""
        window_title = window_info.get('title', '') if window_info else ''
        process_name = window_info.get('process_name', '') if window_info else ''
        
        merged_text = f"{comando} {vision_text} {window_title} {process_name}".lower()
        scores = {cat: 0 for cat in self.categorias}
        
        # Universal Discovery: Detectar se é um novo programa
        discovered_app = None
        if process_name and process_name.lower() not in ["explorer.exe", "svchost.exe", "python.exe"]:
             discovered_app = process_name
        
        for categoria, palavras in self.categorias.items():
            for palavra in palavras:
                if palavra in merged_text:
                    # Pesos baseados na origem da informação
                    weight = 1.5
                    if vision_text and palavra in vision_text.lower(): weight = 3.0
                    if window_title and palavra in window_title.lower(): weight = 4.0
                    
                    if categoria == "AUTONOMIA": weight += 1.0
                    scores[categoria] += weight
        
        # LÓGICA DE PRECEDÊNCIA STARK: 
        if scores["AUTONOMIA"] >= 2.5:
             scores["AUTONOMIA"] += 5.0

        contexto_principal = max(scores, key=scores.get)
        
        if scores[contexto_principal] < 1.0:
            contexto_principal = "GERAL"
            
        logger.info(f"🧠 Contexto: {contexto_principal} | App: {process_name} | Win: {window_title}")
        
        return {
            "contexto": contexto_principal,
            "scores": scores,
            "tokens": merged_text.split(),
            "active_app": process_name,
            "window_title": window_title,
            "discovered_app": discovered_app
        }

# Instância global
analisador_contexto = AnalisadorContexto()
