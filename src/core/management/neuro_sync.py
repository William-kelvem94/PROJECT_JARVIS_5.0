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

# Optional imports with graceful fallbacks
try:
    from src.core.intelligence.brain_router import brain_router
    BRAIN_ROUTER_AVAILABLE = True
except (ImportError, OSError):
    brain_router = None
    BRAIN_ROUTER_AVAILABLE = False

try:
    from src.core.intelligence.memory import memory_manager
    MEMORY_AVAILABLE = True
except (ImportError, OSError):
    memory_manager = None
    MEMORY_AVAILABLE = False

try:
    from src.core.intelligence.local_brain import local_brain
    LOCAL_BRAIN_AVAILABLE = True
except (ImportError, OSError):
    local_brain = None
    LOCAL_BRAIN_AVAILABLE = False

try:
    from src.interface.ui_signals import ui_signals
    UI_SIGNALS_AVAILABLE = True
except (ImportError, OSError):
    ui_signals = None
    UI_SIGNALS_AVAILABLE = False

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
        
        # Emit UI signal only if available
        if UI_SIGNALS_AVAILABLE and ui_signals:
            try:
                ui_signals.update_status.emit("Iniciando Sincronização Neural...")
            except:
                pass  # UI not available, continue silently
        
        # 1. Verificar Ollama
        if BRAIN_ROUTER_AVAILABLE and brain_router:
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
        else:
            self.status["ollama"] = "unavailable"
            logger.info("ℹ️  Brain Router não disponível (modo CLI)")

        # 2. Verificar ChromaDB (Memória)
        if MEMORY_AVAILABLE and memory_manager:
            try:
                stats = memory_manager.get_stats()
                if stats.get("chroma_available"):
                    self.status["memory"] = "ready"
                    logger.info(f"✅ ChromaDB: {stats.get('memories_count', 0)} memórias sincronizadas.")
                else:
                    self.status["memory"] = "warning"
                    logger.warning("⚠️ ChromaDB indisponível. Usando cache temporário.")
            except Exception as e:
                self.status["memory"] = "error"
                logger.error(f"❌ Erro ao sincronizar Memória: {e}")
        else:
            self.status["memory"] = "unavailable"
            logger.info("ℹ️  Memory Manager não disponível (modo CLI)")

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
        if LOCAL_BRAIN_AVAILABLE and local_brain:
            try:
                self.status["local_brain"] = "syncing"
                logger.info("⚡ LocalBrain: Inicialização em segundo plano ativada.")
            except Exception as e:
                self.status["local_brain"] = "error"
                logger.error(f"❌ Erro no LocalBrain: {e}")
        else:
            self.status["local_brain"] = "unavailable"
            logger.info("ℹ️  LocalBrain não disponível (modo CLI)")

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
