"""
Continuous Training System - Sistema de Treinamento Contínuo
Treina o modelo continuamente enquanto o JARVIS é usado
Integra modelos treinados localmente e no Docker
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import json
import shutil
from core.logger import logger
from core.training_orchestrator import TrainingOrchestrator
from modules.memory.persistent_memory import PersistentMemory


class ModelRegistry:
    """Registro de modelos treinados."""
    
    def __init__(self, registry_path: str = "./data/models/registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.models = self._load_registry()
        logger.info("ModelRegistry inicializado")
    
    def _load_registry(self) -> Dict[str, Any]:
        """Carrega registro de modelos."""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {
            'models': {},
            'best_model': None,
            'active_model': None
        }
    
    def _save_registry(self):
        """Salva registro de modelos."""
        with open(self.registry_path, 'w') as f:
            json.dump(self.models, f, indent=2)
    
    def register_model(
        self,
        model_name: str,
        model_info: Dict[str, Any]
    ):
        """
        Registra novo modelo.
        
        Args:
            model_name: Nome do modelo
            model_info: Informações do modelo (métricas, config, etc)
        """
        self.models['models'][model_name] = {
            **model_info,
            'registered_at': datetime.now().isoformat(),
            'source': model_info.get('source', 'local'),  # local ou docker
            'version': len(self.models['models']) + 1
        }
        self._save_registry()
        logger.info(f"Modelo registrado: {model_name}")
    
    def get_best_model(self) -> Optional[str]:
        """Retorna o melhor modelo baseado em métricas."""
        if not self.models['models']:
            return None
        
        best_model = None
        best_score = 0
        
        for model_name, info in self.models['models'].items():
            # Score baseado em qualidade e recência
            quality = info.get('quality_score', 0.5)
            age_days = (datetime.now() - datetime.fromisoformat(info['registered_at'])).days
            recency_factor = max(0, 1 - (age_days / 30))  # Decai ao longo de 30 dias
            
            score = quality * 0.7 + recency_factor * 0.3
            
            if score > best_score:
                best_score = score
                best_model = model_name
        
        return best_model
    
    def set_active_model(self, model_name: str):
        """Define modelo ativo."""
        if model_name in self.models['models']:
            self.models['active_model'] = model_name
            self._save_registry()
            logger.info(f"Modelo ativo definido: {model_name}")
    
    def get_active_model(self) -> Optional[str]:
        """Retorna modelo ativo."""
        return self.models.get('active_model')
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Lista todos os modelos registrados."""
        return [
            {'name': name, **info}
            for name, info in self.models['models'].items()
        ]
    
    def compare_models(self, model_a: str, model_b: str) -> Dict[str, Any]:
        """Compara dois modelos."""
        if model_a not in self.models['models'] or model_b not in self.models['models']:
            return {'error': 'Modelo não encontrado'}
        
        info_a = self.models['models'][model_a]
        info_b = self.models['models'][model_b]
        
        return {
            'model_a': model_a,
            'model_b': model_b,
            'comparison': {
                'quality': {
                    'a': info_a.get('quality_score', 0),
                    'b': info_b.get('quality_score', 0),
                    'winner': 'a' if info_a.get('quality_score', 0) > info_b.get('quality_score', 0) else 'b'
                },
                'training_samples': {
                    'a': info_a.get('training_samples', 0),
                    'b': info_b.get('training_samples', 0)
                },
                'age': {
                    'a': info_a.get('registered_at'),
                    'b': info_b.get('registered_at'),
                    'newer': 'a' if info_a.get('registered_at', '') > info_b.get('registered_at', '') else 'b'
                }
            }
        }


class ContinuousTrainingSystem:
    """
    Sistema de treinamento contínuo que:
    - Treina enquanto o JARVIS é usado
    - Integra modelos de diferentes fontes
    - Sempre mantém o melhor modelo ativo
    """
    
    def __init__(
        self,
        training_orchestrator: TrainingOrchestrator,
        memory: PersistentMemory
    ):
        self.orchestrator = training_orchestrator
        self.memory = memory
        self.model_registry = ModelRegistry()
        
        # Configurações de treinamento contínuo
        self.continuous_training_enabled = True
        self.training_interval_minutes = 60  # Verificar a cada hora
        self.min_new_interactions = 20  # Mínimo de novas interações para treinar
        self.quality_improvement_threshold = 0.05  # 5% de melhoria para trocar modelo
        
        # Estado
        self.last_training_check = datetime.now()
        self.training_in_progress = False
        self.stats = {
            'total_continuous_trainings': 0,
            'model_switches': 0,
            'last_model_switch': None
        }
        
        logger.info("ContinuousTrainingSystem inicializado")
    
    async def start_continuous_training_loop(self):
        """Inicia loop de treinamento contínuo."""
        logger.info("🔄 Iniciando loop de treinamento contínuo...")
        
        while self.continuous_training_enabled:
            try:
                await asyncio.sleep(self.training_interval_minutes * 60)
                
                if not self.training_in_progress:
                    await self._check_and_train()
                
            except Exception as e:
                logger.error(f"Erro no loop de treinamento contínuo: {e}")
                await asyncio.sleep(60)  # Aguardar 1 minuto antes de retry
    
    def _check_and_train(self):
        """Verifica se deve treinar e executa treinamento."""
        try:
            # Verificar se há dados novos suficientes
            dataset_stats = self.orchestrator.dataset_preparation.get_statistics()
            
            if dataset_stats['total_interactions'] < self.min_new_interactions:
                logger.debug(f"Não há interações suficientes para treinar: {dataset_stats['total_interactions']}/{self.min_new_interactions}")
                return
            
            # Verificar qualidade atual
            auto_trainer_status = self.orchestrator.auto_trainer.get_status()
            current_quality = auto_trainer_status.get('current_quality', 0.5)
            
            # Decidir se deve treinar - FIX: use total_seconds() ao invés de seconds
            time_since_check = (datetime.now() - self.last_training_check).total_seconds()
            should_train = (
                dataset_stats['total_interactions'] >= self.min_new_interactions and
                time_since_check >= self.training_interval_minutes * 60
            )
            
            if should_train:
                logger.info("📚 Iniciando treinamento contínuo...")
                self.training_in_progress = True
                
                # Executar treinamento incremental
                result = await self.orchestrator.start_training_workflow(
                    training_type='incremental'
                )
                
                if result.get('success'):
                    # Registrar modelo
                    model_name = result.get('result', {}).get('model_name', 'jarvis-custom')
                    self.model_registry.register_model(
                        model_name,
                        {
                            'quality_score': current_quality,
                            'training_samples': dataset_stats['total_interactions'],
                            'source': 'continuous_local',
                            'training_type': 'incremental'
                        }
                    )
                    
                    # Verificar se deve trocar de modelo
                    await self._evaluate_and_switch_model()
                    
                    self.stats['total_continuous_trainings'] += 1
                    logger.info("✅ Treinamento contínuo concluído")
                
                self.training_in_progress = False
                self.last_training_check = datetime.now()
                
        except Exception as e:
            logger.error(f"Erro no treinamento contínuo: {e}")
            self.training_in_progress = False
    
    async def _evaluate_and_switch_model(self):
        """Avalia modelos e troca para o melhor se necessário."""
        best_model = self.model_registry.get_best_model()
        current_active = self.model_registry.get_active_model()
        
        if best_model and best_model != current_active:
            # Comparar qualidade
            models = self.model_registry.models['models']
            
            best_quality = models[best_model].get('quality_score', 0)
            current_quality = models.get(current_active, {}).get('quality_score', 0) if current_active else 0
            
            improvement = best_quality - current_quality
            
            if improvement >= self.quality_improvement_threshold:
                logger.info(f"🔄 Trocando modelo: {current_active} -> {best_model} (melhoria: {improvement:.2%})")
                self.model_registry.set_active_model(best_model)
                self.stats['model_switches'] += 1
                self.stats['last_model_switch'] = datetime.now().isoformat()
    
    async def integrate_docker_model(
        self,
        model_path: str,
        model_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Integra modelo treinado no Docker.
        
        Args:
            model_path: Caminho do modelo no Docker
            model_info: Informações do modelo
        """
        try:
            logger.info(f"Integrando modelo do Docker: {model_path}")
            
            # Copiar modelo do Docker para local
            local_model_dir = Path("./data/models/docker_models")
            local_model_dir.mkdir(parents=True, exist_ok=True)
            
            model_name = model_info.get('name', f"docker_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            local_path = local_model_dir / model_name
            
            # Em produção, usar docker cp ou volume compartilhado
            # Por enquanto, assumir que modelo já está acessível
            
            # Registrar modelo
            self.model_registry.register_model(
                model_name,
                {
                    **model_info,
                    'source': 'docker',
                    'path': str(local_path)
                }
            )
            
            # Avaliar se deve trocar de modelo
            await self._evaluate_and_switch_model()
            
            return {
                'success': True,
                'model_name': model_name,
                'message': 'Modelo Docker integrado com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao integrar modelo Docker: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de treinamento contínuo."""
        return {
            'enabled': self.continuous_training_enabled,
            'training_in_progress': self.training_in_progress,
            'last_training_check': self.last_training_check.isoformat(),
            'stats': self.stats,
            'model_registry': {
                'total_models': len(self.model_registry.models['models']),
                'best_model': self.model_registry.get_best_model(),
                'active_model': self.model_registry.get_active_model(),
                'models': self.model_registry.list_models()
            },
            'config': {
                'training_interval_minutes': self.training_interval_minutes,
                'min_new_interactions': self.min_new_interactions,
                'quality_improvement_threshold': self.quality_improvement_threshold
            }
        }
    
    def enable(self):
        """Habilita treinamento contínuo."""
        self.continuous_training_enabled = True
        logger.info("Treinamento contínuo habilitado")
    
    def disable(self):
        """Desabilita treinamento contínuo."""
        self.continuous_training_enabled = False
        logger.info("Treinamento contínuo desabilitado")
    
    async def force_training(self, training_type: str = 'incremental') -> Dict[str, Any]:
        """Força treinamento imediato."""
        if self.training_in_progress:
            return {
                'success': False,
                'message': 'Treinamento já em andamento'
            }
        
        logger.info(f"Forçando treinamento: {training_type}")
        self.training_in_progress = True
        
        try:
            result = await self.orchestrator.start_training_workflow(
                training_type=training_type
            )
            
            if result.get('success'):
                # Registrar modelo
                model_name = result.get('training_result', {}).get('model_name', 'jarvis-custom')
                dataset_info = result.get('dataset_info', {})
                
                self.model_registry.register_model(
                    model_name,
                    {
                        'quality_score': 0.7,  # Assumir qualidade boa
                        'training_samples': dataset_info.get('total_samples', 0),
                        'source': 'forced_local',
                        'training_type': training_type
                    }
                )
                
                await self._evaluate_and_switch_model()
            
            return result
            
        finally:
            self.training_in_progress = False


# Instância global
_continuous_training_system = None


def get_continuous_training_system(
    orchestrator: TrainingOrchestrator,
    memory: PersistentMemory
) -> ContinuousTrainingSystem:
    """Retorna instância global do sistema de treinamento contínuo."""
    global _continuous_training_system
    if _continuous_training_system is None:
        _continuous_training_system = ContinuousTrainingSystem(orchestrator, memory)
    return _continuous_training_system
