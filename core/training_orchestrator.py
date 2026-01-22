"""
Training Orchestrator - Orquestrador Central de Treinamento
Coordena todo o processo de treinamento: configuração, preparação de dados, treinamento e monitoramento
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import asyncio
from core.logger import logger
from core.training_config import ComprehensiveTrainingConfig, TrainingConfigManager
from core.dataset_preparation import DatasetPreparation
from core.training_manager import TrainingManager
from core.auto_trainer import AutoTrainer
from modules.memory.persistent_memory import PersistentMemory
from enterprise.ai.continuous_learning import ContinuousLearningLoop
from enterprise.ai.training_pipeline import DistributedTrainingPipeline, TrainingDataset


class TrainingMetrics:
    """Métricas de treinamento."""
    
    def __init__(self):
        self.metrics_history = []
        self.current_metrics = {}
    
    def update(self, metrics: Dict[str, Any]):
        """Atualiza métricas."""
        self.current_metrics = {
            **metrics,
            "timestamp": datetime.now().isoformat()
        }
        self.metrics_history.append(self.current_metrics)
        
        # Manter apenas últimas 1000 métricas
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
    
    def get_latest(self) -> Dict[str, Any]:
        """Retorna métricas mais recentes."""
        return self.current_metrics
    
    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retorna histórico de métricas."""
        return self.metrics_history[-limit:]


class TrainingOrchestrator:
    """
    Orquestrador central de treinamento.
    Coordena todos os componentes do sistema de treinamento.
    """
    
    def __init__(
        self,
        memory: PersistentMemory,
        ollama_base_url: str = "http://localhost:11434"
    ):
        """
        Inicializa o orquestrador de treinamento.
        
        Args:
            memory: Instância de memória persistente
            ollama_base_url: URL base do Ollama
        """
        self.memory = memory
        self.ollama_base_url = ollama_base_url
        
        # Gerenciamento de configuração
        self.config_manager = TrainingConfigManager()
        self.current_config = self.config_manager.get_current_config()
        
        # Componentes principais
        self.dataset_preparation = DatasetPreparation(
            config=self.current_config.dataset,
            memory=memory
        )
        self.training_manager = TrainingManager(
            ollama_base_url=ollama_base_url,
            memory=memory
        )
        self.learning_loop = ContinuousLearningLoop()
        self.auto_trainer = AutoTrainer(
            training_manager=self.training_manager,
            learning_loop=self.learning_loop,
            memory=memory,
            base_model=self.current_config.model.base_model
        )
        self.distributed_pipeline = DistributedTrainingPipeline()
        
        # Métricas e estado
        self.metrics = TrainingMetrics()
        self.training_status = {
            "is_training": False,
            "current_stage": "idle",
            "progress": 0.0,
            "message": "Sistema pronto"
        }
        
        # Atualizar configurações do auto_trainer
        self._sync_auto_trainer_config()
        
        logger.info("TrainingOrchestrator inicializado")
    
    def _sync_auto_trainer_config(self):
        """Sincroniza configurações com o auto_trainer."""
        auto_config = self.current_config.auto_training
        self.auto_trainer.auto_train_enabled = auto_config.enabled
        self.auto_trainer.quality_threshold = auto_config.quality_threshold
        self.auto_trainer.retrain_interval_hours = auto_config.retrain_interval_hours
        self.auto_trainer.min_interactions_for_training = auto_config.min_interactions_for_training
        self.auto_trainer.min_interactions_for_incremental = auto_config.min_interactions_for_incremental
    
    async def start_training_workflow(
        self,
        training_type: str = "full",  # full, incremental, quick
        custom_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Inicia workflow completo de treinamento.
        
        Args:
            training_type: Tipo de treinamento (full, incremental, quick)
            custom_config: Configuração customizada (opcional)
            
        Returns:
            Resultado do treinamento
        """
        if self.training_status["is_training"]:
            return {
                "success": False,
                "message": "Treinamento já em andamento"
            }
        
        try:
            self.training_status["is_training"] = True
            self.training_status["current_stage"] = "initializing"
            self.training_status["progress"] = 0.0
            
            logger.info(f"🚀 Iniciando workflow de treinamento: {training_type}")
            
            # Aplicar configuração customizada se fornecida
            if custom_config:
                self._apply_custom_config(custom_config)
            
            result = {}
            
            if training_type == "full":
                result = await self._full_training_workflow()
            elif training_type == "incremental":
                result = await self._incremental_training_workflow()
            elif training_type == "quick":
                result = await self._quick_training_workflow()
            else:
                return {
                    "success": False,
                    "message": f"Tipo de treinamento inválido: {training_type}"
                }
            
            self.training_status["is_training"] = False
            self.training_status["current_stage"] = "completed"
            self.training_status["progress"] = 100.0
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no workflow de treinamento: {e}")
            self.training_status["is_training"] = False
            self.training_status["current_stage"] = "error"
            self.training_status["message"] = str(e)
            
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }
    
    async def _full_training_workflow(self) -> Dict[str, Any]:
        """Workflow completo de treinamento."""
        logger.info("Executando treinamento completo...")
        
        # Stage 1: Preparar dataset (0-30%)
        self._update_status("preparing_dataset", 5.0, "Preparando dataset...")
        dataset_info = self.dataset_preparation.prepare_dataset()
        
        if dataset_info.get("total_samples", 0) < self.current_config.dataset.min_interactions:
            return {
                "success": False,
                "message": f"Amostras insuficientes: {dataset_info.get('total_samples', 0)}/{self.current_config.dataset.min_interactions}"
            }
        
        self._update_status("preparing_dataset", 30.0, f"Dataset preparado: {dataset_info['total_samples']} amostras")
        
        # Stage 2: Treinar modelo com Ollama (30-80%)
        self._update_status("training_model", 35.0, "Iniciando treinamento do modelo...")
        
        training_result = self.training_manager.train_model(
            base_model=self.current_config.model.base_model,
            custom_model_name=self.current_config.model.custom_model_name,
            min_interactions=self.current_config.dataset.min_interactions,
            force_retrain=True
        )
        
        if not training_result.get("success"):
            return training_result
        
        self._update_status("training_model", 80.0, "Modelo treinado com sucesso")
        
        # Stage 3: Validação e métricas (80-95%)
        self._update_status("validating", 85.0, "Validando modelo...")
        
        validation_result = await self._validate_trained_model(training_result)
        
        self._update_status("validating", 95.0, "Validação concluída")
        
        # Stage 4: Finalização (95-100%)
        self._update_status("finalizing", 98.0, "Finalizando...")
        
        # Atualizar métricas
        self.metrics.update({
            "training_type": "full",
            "dataset_samples": dataset_info["total_samples"],
            "model_name": training_result.get("model_name"),
            "validation": validation_result,
            "timestamp": datetime.now().isoformat()
        })
        
        self._update_status("completed", 100.0, "Treinamento concluído com sucesso!")
        
        return {
            "success": True,
            "message": "Treinamento completo finalizado",
            "dataset_info": dataset_info,
            "training_result": training_result,
            "validation": validation_result
        }
    
    async def _incremental_training_workflow(self) -> Dict[str, Any]:
        """Workflow de treinamento incremental."""
        logger.info("Executando treinamento incremental...")
        
        self._update_status("incremental_training", 10.0, "Verificando novos dados...")
        
        # Coletar apenas dados novos
        dataset_info = self.dataset_preparation.prepare_dataset(
            include_new_only=True
        )
        
        self._update_status("incremental_training", 40.0, "Treinando incrementalmente...")
        
        result = self.training_manager.incremental_training(
            base_model=self.current_config.model.base_model,
            custom_model_name=self.current_config.model.custom_model_name,
            batch_size=self.current_config.auto_training.min_interactions_for_incremental
        )
        
        self._update_status("incremental_training", 90.0, "Treinamento incremental concluído")
        
        self.metrics.update({
            "training_type": "incremental",
            "new_samples": dataset_info.get("total_samples", 0),
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": result.get("success", False),
            "message": "Treinamento incremental concluído",
            "result": result
        }
    
    async def _quick_training_workflow(self) -> Dict[str, Any]:
        """Workflow de treinamento rápido (apenas com Ollama Modelfile)."""
        logger.info("Executando treinamento rápido...")
        
        self._update_status("quick_training", 20.0, "Coletando dados recentes...")
        
        # Usar dados já existentes sem preparação completa
        training_pairs = self.training_manager.collect_training_data(
            min_interactions=self.current_config.dataset.min_interactions
        )
        
        if len(training_pairs) < self.current_config.dataset.min_interactions:
            return {
                "success": False,
                "message": f"Interações insuficientes: {len(training_pairs)}/{self.current_config.dataset.min_interactions}"
            }
        
        self._update_status("quick_training", 50.0, "Criando modelo...")
        
        # Criar Modelfile e treinar
        modelfile_path = self.training_manager.create_modelfile(
            base_model=self.current_config.model.base_model,
            training_pairs=training_pairs,
            model_name=self.current_config.model.custom_model_name
        )
        
        success = self.training_manager._create_ollama_model(
            modelfile_path,
            self.current_config.model.custom_model_name
        )
        
        self._update_status("quick_training", 90.0, "Treinamento rápido concluído")
        
        return {
            "success": success,
            "message": "Treinamento rápido concluído",
            "training_pairs": len(training_pairs),
            "model_name": self.current_config.model.custom_model_name
        }
    
    async def _validate_trained_model(self, training_result: Dict[str, Any]) -> Dict[str, Any]:
        """Valida modelo treinado."""
        # Validação básica - pode ser expandida
        model_name = training_result.get("model_name")
        
        # Verificar se modelo existe
        models = self.training_manager._list_ollama_models()
        exists = model_name in models
        
        return {
            "model_exists": exists,
            "model_name": model_name,
            "validation_passed": exists,
            "timestamp": datetime.now().isoformat()
        }
    
    def _update_status(self, stage: str, progress: float, message: str):
        """Atualiza status do treinamento."""
        self.training_status["current_stage"] = stage
        self.training_status["progress"] = progress
        self.training_status["message"] = message
        logger.info(f"[{progress:.1f}%] {message}")
    
    def _apply_custom_config(self, custom_config: Dict[str, Any]):
        """Aplica configuração customizada."""
        # Atualizar configuração atual
        if "model" in custom_config:
            for key, value in custom_config["model"].items():
                if hasattr(self.current_config.model, key):
                    setattr(self.current_config.model, key, value)
        
        if "dataset" in custom_config:
            for key, value in custom_config["dataset"].items():
                if hasattr(self.current_config.dataset, key):
                    setattr(self.current_config.dataset, key, value)
        
        # Recriar dataset_preparation com nova config
        self.dataset_preparation = DatasetPreparation(
            config=self.current_config.dataset,
            memory=self.memory
        )
    
    async def start_auto_training(self):
        """Inicia sistema de auto-treinamento."""
        logger.info("🔄 Iniciando sistema de auto-treinamento...")
        
        # Habilitar auto-trainer
        self.auto_trainer.enable()
        
        # Iniciar loop de monitoramento periódico (não bloqueante)
        asyncio.create_task(self.auto_trainer.start_periodic_training(
            check_interval_minutes=60
        ))
        
        logger.info("✅ Auto-treinamento ativo")
    
    def stop_auto_training(self):
        """Para sistema de auto-treinamento."""
        self.auto_trainer.disable()
        logger.info("Auto-treinamento desabilitado")
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema de treinamento."""
        return {
            "training_status": self.training_status,
            "auto_trainer_status": self.auto_trainer.get_status(),
            "training_manager_status": self.training_manager.get_training_status(),
            "dataset_stats": self.dataset_preparation.get_statistics(),
            "latest_metrics": self.metrics.get_latest(),
            "configuration": {
                "model": self.current_config.model.__dict__,
                "auto_training": self.current_config.auto_training.__dict__
            }
        }
    
    def update_configuration(
        self,
        config_updates: Dict[str, Any],
        save_as: str = "default"
    ) -> Dict[str, Any]:
        """
        Atualiza configuração do sistema.
        
        Args:
            config_updates: Atualizações de configuração
            save_as: Nome para salvar a configuração
            
        Returns:
            Resultado da atualização
        """
        try:
            self.config_manager.update_config(config_updates, save_as)
            self.current_config = self.config_manager.get_current_config()
            self._sync_auto_trainer_config()
            
            return {
                "success": True,
                "message": "Configuração atualizada",
                "config": self.current_config.to_dict()
            }
        except Exception as e:
            logger.error(f"Erro ao atualizar configuração: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def list_available_configs(self) -> List[str]:
        """Lista configurações disponíveis."""
        return self.config_manager.list_configs()
    
    def load_configuration(self, name: str) -> Dict[str, Any]:
        """
        Carrega configuração específica.
        
        Args:
            name: Nome da configuração
            
        Returns:
            Resultado do carregamento
        """
        try:
            self.current_config = self.config_manager.load_config(name)
            self._sync_auto_trainer_config()
            
            # Recriar componentes com nova config
            self.dataset_preparation = DatasetPreparation(
                config=self.current_config.dataset,
                memory=self.memory
            )
            
            return {
                "success": True,
                "message": f"Configuração '{name}' carregada",
                "config": self.current_config.to_dict()
            }
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def monitor_interaction(
        self,
        user_query: str,
        assistant_response: str,
        quality_metrics: Dict[str, float] = None
    ):
        """
        Monitora interação para auto-treinamento.
        
        Args:
            user_query: Query do usuário
            assistant_response: Resposta do assistente
            quality_metrics: Métricas de qualidade (opcional)
        """
        if self.current_config.auto_training.enabled:
            await self.auto_trainer.monitor_interaction(
                user_query,
                assistant_response,
                quality_metrics
            )
