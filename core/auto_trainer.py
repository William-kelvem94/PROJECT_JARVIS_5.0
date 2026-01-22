"""
Auto Trainer - Sistema de Auto-Treinamento Automático
Monitora qualidade e dispara treinamento quando necessário
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from core.logger import logger
from core.training_manager import TrainingManager
from enterprise.ai.continuous_learning import ContinuousLearningLoop
from modules.memory.persistent_memory import PersistentMemory

class AutoTrainer:
    """
    Sistema de auto-treinamento que:
    1. Monitora qualidade das respostas
    2. Coleta feedback implícito e explícito
    3. Dispara treinamento quando necessário
    4. Agenda treinamento incremental periódico
    """
    
    def __init__(
        self,
        training_manager: TrainingManager,
        learning_loop: ContinuousLearningLoop,
        memory: PersistentMemory,
        base_model: str = "codellama:7b"
    ):
        """
        Inicializa Auto Trainer.
        
        Args:
            training_manager: Instância do TrainingManager
            learning_loop: Instância do ContinuousLearningLoop
            memory: Instância de memória persistente
            base_model: Modelo base para treinamento
        """
        self.training_manager = training_manager
        self.learning_loop = learning_loop
        self.memory = memory
        self.base_model = base_model
        self.custom_model_name = "jarvis-custom"
        
        # Configurações de auto-treinamento
        self.auto_train_enabled = True
        self.min_interactions_for_training = 50
        self.min_interactions_for_incremental = 20
        self.quality_threshold = 0.6  # Qualidade mínima aceitável
        self.retrain_interval_hours = 24  # Retreino diário
        self.last_training_time = None
        
        # Estatísticas
        self.stats = {
            "total_trainings": 0,
            "last_training": None,
            "next_scheduled_training": None,
            "quality_trend": []
        }
        
        logger.info("AutoTrainer inicializado")
    
    async def monitor_interaction(
        self,
        user_query: str,
        assistant_response: str,
        quality_metrics: Dict[str, float] = None
    ):
        """
        Monitora uma interação e decide se deve treinar.
        
        Args:
            user_query: Query do usuário
            assistant_response: Resposta do assistente
            quality_metrics: Métricas de qualidade (opcional)
        """
        if not self.auto_train_enabled:
            return
        
        try:
            # Calcular qualidade desta interação específica
            interaction_quality = self._calculate_interaction_quality(user_query, assistant_response)
            
            # Verificar qualidade média recente
            recent_quality = self._calculate_recent_quality()
            
            # Atualizar tendência de qualidade
            self.stats["quality_trend"].append({
                "timestamp": datetime.now().isoformat(),
                "quality": interaction_quality
            })
            
            # Manter apenas últimas 100 medições
            if len(self.stats["quality_trend"]) > 100:
                self.stats["quality_trend"] = self.stats["quality_trend"][-100:]
            
            # Decidir se deve treinar (não treinar a cada interação, apenas quando necessário)
            # Verificar a cada 10 interações ou se qualidade caiu muito
            if len(self.stats["quality_trend"]) % 10 == 0:
                should_train = self._should_train_now(recent_quality)
                
                if should_train:
                    logger.info("⚠️ Qualidade baixa detectada - agendando treinamento...")
                    await self.schedule_training(reason="low_quality", quality=recent_quality)
            
            # Verificar treinamento incremental periódico (menos frequente)
            if len(self.stats["quality_trend"]) % 50 == 0:
                if self._should_incremental_train():
                    logger.info("📅 Hora do treinamento incremental periódico...")
                    await self.schedule_training(reason="scheduled", incremental=True)
                    
        except Exception as e:
            logger.error(f"Erro ao monitorar interação: {e}")
    
    def _calculate_interaction_quality(self, query: str, response: str) -> float:
        """Calcula qualidade de uma interação específica."""
        try:
            # Métricas simples
            length_score = min(len(response) / 100, 1.0)  # Preferir respostas > 100 chars
            query_length_score = min(len(query) / 20, 1.0)  # Queries > 20 chars são melhores
            
            # Resposta muito curta indica problema
            if len(response) < 10:
                length_score = 0.3
            
            # Resposta muito longa pode ser verbosa
            if len(response) > 2000:
                length_score = 0.8
            
            quality = (length_score * 0.7 + query_length_score * 0.3)
            return quality
            
        except Exception as e:
            logger.error(f"Erro ao calcular qualidade: {e}")
            return 0.5
    
    def _calculate_recent_quality(self) -> float:
        """Calcula qualidade média das interações recentes."""
        try:
            # Buscar últimas interações
            history = self.memory.get_conversation_history(limit=50)
            
            # Calcular qualidade baseada em métricas implícitas
            # Comprimento de resposta, uso de contexto, etc.
            qualities = []
            
            for msg in history:
                if msg["role"] == "assistant":
                    content = msg.get("content", "")
                    metadata = msg.get("metadata", {})
                    
                    # Métricas simples
                    length_score = min(len(content) / 100, 1.0)  # Preferir respostas > 100 chars
                    has_context = 1.0 if metadata.get("used_context") else 0.5
                    
                    quality = (length_score * 0.5 + has_context * 0.5)
                    qualities.append(quality)
            
            if qualities:
                return sum(qualities) / len(qualities)
            return 0.5  # Default
            
        except Exception as e:
            logger.error(f"Erro ao calcular qualidade: {e}")
            return 0.5
    
    def _should_train_now(self, recent_quality: float) -> bool:
        """
        Decide se deve treinar agora baseado em qualidade.
        
        Args:
            recent_quality: Qualidade média recente
        
        Returns:
            True se deve treinar
        """
        # Treinar se qualidade está abaixo do threshold
        if recent_quality < self.quality_threshold:
            # Verificar se já treinou recentemente (evitar loops)
            if self.last_training_time:
                time_since_training = datetime.now() - self.last_training_time
                if time_since_training < timedelta(hours=1):
                    return False  # Treinou há menos de 1 hora
            
            # Verificar se tem dados suficientes
            status = self.training_manager.get_training_status()
            if status.get("can_train", False):
                return True
        
        return False
    
    def _should_incremental_train(self) -> bool:
        """Verifica se está na hora do treinamento incremental periódico."""
        if not self.last_training_time:
            # Nunca treinou - verificar se tem dados suficientes
            status = self.training_manager.get_training_status()
            return status.get("can_train", False)
        
        # Verificar intervalo desde último treinamento
        time_since_training = datetime.now() - self.last_training_time
        if time_since_training >= timedelta(hours=self.retrain_interval_hours):
            # Verificar se tem novas interações suficientes
            status = self.training_manager.get_training_status()
            interactions = status.get("available_interactions", 0)
            
            # Precisa pelo menos min_interactions_for_incremental novas
            return interactions >= self.min_interactions_for_incremental
        
        return False
    
    async def schedule_training(
        self,
        reason: str = "manual",
        incremental: bool = False,
        quality: float = None
    ) -> Dict[str, Any]:
        """
        Agenda e executa treinamento.
        
        Args:
            reason: Razão do treinamento (low_quality, scheduled, manual)
            incremental: Se True, faz treinamento incremental
            quality: Qualidade atual (opcional)
        
        Returns:
            Resultado do treinamento
        """
        try:
            logger.info(f"🚀 Iniciando treinamento (reason: {reason}, incremental: {incremental})")
            
            if incremental:
                result = self.training_manager.incremental_training(
                    base_model=self.base_model,
                    custom_model_name=self.custom_model_name,
                    batch_size=self.min_interactions_for_incremental
                )
            else:
                result = self.training_manager.train_model(
                    base_model=self.base_model,
                    custom_model_name=self.custom_model_name,
                    min_interactions=self.min_interactions_for_training,
                    force_retrain=False
                )
            
            if result.get("success"):
                self.last_training_time = datetime.now()
                self.stats["total_trainings"] += 1
                self.stats["last_training"] = self.last_training_time.isoformat()
                
                # Salvar estatísticas
                self.memory.save_context("auto_trainer_stats", self.stats)
                
                logger.info(f"✅ Treinamento concluído: {result.get('message')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao executar treinamento: {e}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }
    
    async def start_periodic_training(self, check_interval_minutes: int = 60):
        """
        Inicia loop de verificação periódica para treinamento.
        
        Args:
            check_interval_minutes: Intervalo de verificação em minutos
        """
        logger.info(f"🔄 Iniciando monitoramento periódico (verificação a cada {check_interval_minutes} minutos)")
        
        while True:
            try:
                await asyncio.sleep(check_interval_minutes * 60)
                
                if self.auto_train_enabled:
                    # Verificar se deve fazer treinamento incremental
                    if self._should_incremental_train():
                        await self.schedule_training(reason="scheduled", incremental=True)
                    
                    # Verificar qualidade geral
                    quality = self._calculate_recent_quality()
                    self.stats["quality_trend"].append({
                        "timestamp": datetime.now().isoformat(),
                        "quality": quality
                    })
                    
                    # Manter apenas últimas 100 medições
                    if len(self.stats["quality_trend"]) > 100:
                        self.stats["quality_trend"] = self.stats["quality_trend"][-100:]
                    
                    # Salvar estatísticas
                    self.memory.save_context("auto_trainer_stats", self.stats)
                    
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(60)  # Aguardar 1 minuto antes de retry
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do auto-trainer."""
        training_status = self.training_manager.get_training_status()
        quality = self._calculate_recent_quality()
        
        # Calcular próximo treinamento
        next_training = None
        if self.last_training_time:
            next_training_time = self.last_training_time + timedelta(hours=self.retrain_interval_hours)
            if next_training_time > datetime.now():
                next_training = next_training_time.isoformat()
        
        return {
            "auto_train_enabled": self.auto_train_enabled,
            "current_quality": quality,
            "quality_threshold": self.quality_threshold,
            "should_train": quality < self.quality_threshold,
            "last_training": self.stats.get("last_training"),
            "next_scheduled_training": next_training,
            "total_trainings": self.stats["total_trainings"],
            "training_status": training_status,
            "config": {
                "min_interactions_for_training": self.min_interactions_for_training,
                "min_interactions_for_incremental": self.min_interactions_for_incremental,
                "retrain_interval_hours": self.retrain_interval_hours
            }
        }
    
    def enable(self):
        """Habilita auto-treinamento."""
        self.auto_train_enabled = True
        logger.info("Auto-treinamento habilitado")
    
    def disable(self):
        """Desabilita auto-treinamento."""
        self.auto_train_enabled = False
        logger.info("Auto-treinamento desabilitado")

