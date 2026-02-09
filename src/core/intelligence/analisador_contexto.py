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
            "PROGRAMACAO": ["api", "json", "python", "backend", "deploy", "bug", "log", "código", "desenvolver", "git"],
            "PSICOLOGIA": ["relacionamento", "namorada", "sentimento", "trauma", "terapia", "mente", "psicologia", "emoção"],
            "HARDWARE": ["cpu", "gpu", "ram", "swap", "temperatura", "clima", "brilho", "volume"],
            "MULTIMIDIA": ["música", "youtube", "ouvir", "video", "play", "pause", "navegador", "chrome", "edge"],
            "AUTONOMIA": ["estude", "estudar", "treine", "treinar", "aprenda", "aprender", "pesquise", "pesquisar", "nexus", "sonhe", "sonhar", "idle"]
        }
    
    def analisar(self, comando: str) -> Dict[str, Any]:
        """Retorna o contexto predominante e metadados do comando"""
        comando_limpo = comando.lower()
        scores = {cat: 0 for cat in self.categorias}
        
        for categoria, palavras in self.categorias.items():
            for palavra in palavras:
                if palavra in comando_limpo:
                    # PESOS DINÂMICOS: Verbos de ação em AUTONOMIA valem mais
                    weight = 2.5 if categoria == "AUTONOMIA" else 1.5
                    scores[categoria] += weight
        
        # LÓGICA DE PRECEDÊNCIA STARK: 
        # Se houver comando de estudo/treino, o container principal é AUTONOMIA
        # mesmo que o conteúdo seja de outra categoria.
        if scores["AUTONOMIA"] >= 2.5:
             # Eleva AUTONOMIA para ser o contexto mestre
             scores["AUTONOMIA"] += 5.0

        # Diferenciação complexa (ex: 'desenvolver API' vs 'desenvolver relacionamento')
        if "desenvolver" in comando_limpo:
            if scores["PSICOLOGIA"] > scores["PROGRAMACAO"]:
                scores["PSICOLOGIA"] += 2.0
            else:
                scores["PROGRAMACAO"] += 2.0

        contexto_principal = max(scores, key=scores.get)
        
        # Se nenhum score for significativo, padrão é GERAL
        if scores[contexto_principal] < 1.0:
            contexto_principal = "GERAL"
            
        logger.info(f"🧠 Contexto detectado: {contexto_principal} (Scores: {scores})")
        
        return {
            "contexto": contexto_principal,
            "scores": scores,
            "tokens": comando_limpo.split()
        }

# Instância global
analisador_contexto = AnalisadorContexto()
