#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Neuro-Sync System
==============================
Garante a integridade e saúde das redes neurais e modelos locais no startup.
Sincroniza: Ollama, ChromaDB, LocalBrain e Curiosity Engine.
"""

import logging
import os
import time
import threading
from pathlib import Path
from typing import Dict, Any

from src.utils.config import config
from src.core.intelligence.brain_router import brain_router
from src.core.intelligence.memory_manager import memory_manager
from src.core.intelligence.local_brain import local_brain
from src.interface.ui_signals import ui_signals

logger = logging.getLogger("NeuroSync")

class NeuroSync:
    """Orquestrador de Sincronização Neural"""
    
    def __init__(self):
        self._sync_active = False
        self.status = {
            "ollama": "pending",
            "memory": "pending",
            "local_brain": "pending",
            "curiosity": "pending"
        }

    def run_sync(self, blocking=False):
        """Inicia a sincronização neural"""
        if self._sync_active:
            return
        
        self._sync_active = True
        if blocking:
            self._perform_sync()
        else:
            threading.Thread(target=self._perform_sync, daemon=True, name="NeuroSyncThread").start()

    def _perform_sync(self):
        logger.info("🧠 Iniciando Sincronização Neural Stark...")
        ui_signals.update_status.emit("Iniciando Sincronização Neural...")
        
        # 1. Verificar Ollama
        try:
            brain_router._discover_ollama_models()
            models_count = len(brain_router.ollama_available_models)
            if models_count > 0:
                self.status["ollama"] = "ready"
                logger.info(f"✅ Ollama: {models_count} modelos detectados.")
            else:
                self.status["ollama"] = "warning"
                logger.warning("⚠️ Ollama: Nenhum modelo detectado. JARVIS operará em modo limitado.")
        except Exception as e:
            self.status["ollama"] = "error"
            logger.error(f"❌ Erro ao sincronizar Ollama: {e}")

        # 2. Verificar ChromaDB (Memória)
        try:
            stats = memory_manager.get_stats()
            if stats.get("chroma_available"):
                self.status["memory"] = "ready"
                logger.info(f"✅ ChromaDB: {stats.get('collection_count', 0)} memórias sincronizadas.")
            else:
                self.status["memory"] = "warning"
                logger.warning("⚠️ ChromaDB indisponível. Usando cache temporário.")
        except Exception as e:
            self.status["memory"] = "error"
            logger.error(f"❌ Erro ao sincronizar Memória: {e}")

        # 3. Verificar Dataset de Treinamento
        try:
            from src.core.management.dataset_collector import dataset_collector
            if os.path.exists(dataset_collector.logs_file):
                logger.info("✅ Dataset: Histórico de treinamento detectado.")
            else:
                logger.info("📝 Dataset: Novo histórico será criado para aprendizado.")
        except Exception:
            pass

        # 4. Verificar LocalBrain
        try:
            if local_brain:
                self.status["local_brain"] = "syncing"
                logger.info("⚡ LocalBrain: Inicialização em segundo plano ativada.")
            else:
                self.status["local_brain"] = "error"
        except Exception as e:
            self.status["local_brain"] = "error"
            logger.error(f"❌ Erro no LocalBrain: {e}")

        # 5. Functions & Actions Readiness
        try:
            from src.core.actions.system_controller import system_controller
            if system_controller:
                logger.info("🛠️ Funções: Controlador de sistema integrado e pronto.")
        except Exception:
            logger.warning("⚠️ Funções: Falha ao carregar controladores de sistema.")

        # 6. Curiosity Engine Check
        try:
            from src.learning.curiosity_engine import curiosity_engine
            if curiosity_engine:
                self.status["curiosity"] = "ready"
                logger.info("🔭 Curiosity Engine: Pronta para expansão de conhecimento.")
        except Exception:
            self.status["curiosity"] = "warning"

        self._sync_active = False
        ui_signals.update_status.emit("Sincronização Neural Concluída.")
        logger.info("🏁 Sincronização Neural Stark Finalizada.")

    def get_readiness_report(self) -> str:
        """Retorna um relatório legível da saúde neural"""
        report = "ESTADO NEURAL:\n"
        for system, state in self.status.items():
            icon = "✅" if state == "ready" else "⏳" if state == "syncing" else "⚠️" if state == "warning" else "❌"
            report += f"  {icon} {system.upper()}: {state.capitalize()}\n"
        return report

# Instância global
neuro_sync = NeuroSync()
