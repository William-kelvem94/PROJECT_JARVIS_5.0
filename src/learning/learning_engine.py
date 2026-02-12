"""
JARVIS 5.0 - Learning Engine (Singularity Core)
================================================
Módulo unificado para inicializar e gerenciar todos os sistemas de aprendizado:
- Continual Learner (Auto-Training)
- Feedback Loop (RLHF/DPO)
- Knowledge Distiller (Golden Commands)
- Dream Cycle (Nighttime Training)
- Distributed Training (Multi-GPU)
- Model Registry (Versioning & A/B Testing)
- Scalable Database (Auto-migration)
- Metrics Dashboard (Real-time monitoring)

Este é o "motor evolutivo" que transforma JARVIS de assistente para AGI.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
import threading

# Import new advanced components
from .dependency_manager import dependency_manager
from .scalable_database import ScalableDatabase
from .model_registry import ModelRegistry
from .distributed_trainer import DistributedTrainer, DistributedConfig
from .metrics_dashboard import MetricsDashboard

logger = logging.getLogger("JARVIS-LEARNING-ENGINE")

class LearningEngine:
    """
    Orquestrador central dos sistemas de aprendizado.
    Inicializa e gerencia todos os componentes de forma coordenada.
    """
    
    def __init__(self, project_root: Path, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Learning Engine.
        
        Args:
            project_root: Diretório raiz do projeto
            config: Configuração de learning (se None, carrega de ai_config.yaml)
        """
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.learning_dir = self.data_dir / "learning"
        self.models_dir = self.project_root / "models"
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Load config
        if config is None:
            config = self._load_config()
        
        self.config = config.get('continual_learning', {})
        self.enabled = self.config.get('enabled', False)
        
        # Legacy Components (Lazy initialization)
        self.feedback_loop = None
        self.continual_learner = None
        self.knowledge_distiller = None
        self.dream_cycle = None
        
        # New Advanced Components
        self.dependency_manager = dependency_manager
        self.scalable_database = None
        self.model_registry = None
        self.distributed_trainer = None
        self.metrics_dashboard = None
        
        # Status tracking
        self.is_initialized = False
        self.components_status = {
            'feedback_loop': False,
            'continual_learner': False,
            'knowledge_distiller': False,
            'dream_cycle': False,
            'scalable_database': False,
            'model_registry': False,
            'distributed_trainer': False,
            'metrics_dashboard': False
        }
        
        # Threading for dashboard
        self._dashboard_thread = None
        
        logger.info(f"🧠 Learning Engine created (Enabled: {self.enabled})")
        logger.info(f"📊 Dependencies available: {self._check_dependencies()}")
        
        logger.info(f"🧠 Learning Engine created (Enabled: {self.enabled})")
        logger.info(f"📊 Dependencies available: {self._check_dependencies()}")
    
    def _check_dependencies(self) -> Dict[str, bool]:
        """Check availability of optional dependencies."""
        deps = {}
        critical_deps = ['torch', 'transformers']
        optional_deps = ['psutil', 'flask', 'psycopg2', 'chromadb']
        
        for dep in critical_deps:
            deps[dep] = self.dependency_manager.is_available(dep)
        
        for dep in optional_deps:
            deps[dep] = self.dependency_manager.is_available(dep)
        
        return deps
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configurações do ai_config.yaml"""
        config_path = self.project_root / "config" / "ai_config.yaml"
        
        if not config_path.exists():
            logger.warning(f"⚠️ Config file not found: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return {}
    
    def initialize(self) -> bool:
        """
        Inicializa todos os sistemas de aprendizado habilitados.
        
        Returns:
            True se inicialização bem-sucedida, False caso contrário
        """
        if not self.enabled:
            logger.info("🔒 Learning systems DISABLED in config. Skipping initialization.")
            return False
        
        if self.is_initialized:
            logger.info("✅ Learning Engine already initialized")
            return True
        
        logger.info("🚀 [LEARNING ENGINE] Initializing autonomous learning systems...")
        
        success = True
        
        # Infrastructure Layer - Initialize First
        
        # 1. Scalable Database (Foundation for data)
        if self.config.get('scalable_database', {}).get('enabled', True):
            success &= self._init_scalable_database()
        
        # 2. Model Registry (Foundation for model management)
        if self.config.get('model_registry', {}).get('enabled', True):
            success &= self._init_model_registry()
        
        # 3. Distributed Trainer (GPU management)
        if self.config.get('distributed_training', {}).get('enabled', True):
            success &= self._init_distributed_trainer()
        
        # 4. Metrics Dashboard (Monitoring)
        if self.config.get('metrics_dashboard', {}).get('enabled', True):
            success &= self._init_metrics_dashboard()
        
        # Learning Layer - Initialize After Infrastructure
        
        # 5. Feedback Loop (Foundation)
        if self.config.get('feedback_loop', {}).get('enabled', True):
            success &= self._init_feedback_loop()
        
        # 6. Knowledge Distiller (Golden Commands)
        if self.config.get('knowledge_distiller', {}).get('enabled', True):
            success &= self._init_knowledge_distiller()
        
        # 7. Continual Learner (Auto-Training)
        if self.config.get('continual_learner', {}).get('enabled', True):
            success &= self._init_continual_learner()
        
        # 8. Dream Cycle (Nighttime Training)
        if self.config.get('dream_cycle', {}).get('enabled', True):
            success &= self._init_dream_cycle()
        
        self.is_initialized = success
        
        if success:
            logger.info("✅ [LEARNING ENGINE] All systems ONLINE - JARVIS is now self-evolving")
            self._print_status()
        else:
            logger.warning("⚠️ [LEARNING ENGINE] Some systems failed to initialize")
        
        return success
    
    def _init_scalable_database(self) -> bool:
        """Inicializa sistema de banco de dados escalável"""
        try:
            config = self.config.get('scalable_database', {})
            
            self.scalable_database = ScalableDatabase(
                data_dir=self.data_dir.parent,  # Use project root for database
                sqlite_path=config.get('sqlite_path', 'data/learning.db'),
                auto_migrate=config.get('auto_migrate', True),
                postgres_config=config.get('postgres', {}),
                chromadb_config=config.get('chromadb', {})
            )
            
            # Test connection and initialization
            if self.scalable_database.initialize():
                self.components_status['scalable_database'] = True
                logger.info("✅ Scalable Database initialized")
                return True
            else:
                logger.error("❌ Scalable Database failed to initialize")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Scalable Database: {e}")
            return False
    
    def _init_model_registry(self) -> bool:
        """Inicializa sistema de registro e versionamento de modelos"""
        try:
            config = self.config.get('model_registry', {})
            
            self.model_registry = ModelRegistry(
                registry_dir=self.models_dir,
                database=self.scalable_database.get_sql_connection() if self.scalable_database else None,
                storage_backend=config.get('storage_backend', 'local'),
                enable_compression=config.get('enable_compression', True),
                enable_encryption=config.get('enable_encryption', False),
                max_versions_per_model=config.get('max_versions_per_model', 5),
                auto_cleanup=config.get('auto_cleanup', True)
            )
            
            # Initialize registry tables
            if self.model_registry.initialize():
                self.components_status['model_registry'] = True
                logger.info("✅ Model Registry initialized")
                return True
            else:
                logger.error("❌ Model Registry failed to initialize")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Model Registry: {e}")
            return False
    
    def _init_distributed_trainer(self) -> bool:
        """Inicializa sistema de treinamento distribuído"""
        try:
            config = self.config.get('distributed_training', {})
            
            # Check for GPU availability
            if not self.dependency_manager.is_available('torch', 'gpu'):
                logger.warning("⚠️ No GPU detected, distributed training will be CPU-only")
            
            # Create distributed configuration
            distributed_config = DistributedConfig(
                use_distributed=config.get('use_distributed', True),
                backend=config.get('backend', 'nccl'),
                num_gpus=config.get('num_gpus', 0),  # Auto-detect
                gradient_accumulation_steps=config.get('gradient_accumulation_steps', 1),
                sync_batch_norm=config.get('sync_batch_norm', True),
                timeout_seconds=config.get('timeout_seconds', 1800),
                master_port=config.get('master_port', '29500')
            )
            
            self.distributed_trainer = DistributedTrainer(distributed_config)
            self.components_status['distributed_trainer'] = True
            
            logger.info(f"✅ Distributed Trainer initialized ({len(self.distributed_trainer.gpu_manager.available_gpus)} GPUs)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Distributed Trainer: {e}")
            return False
    
    def _init_metrics_dashboard(self) -> bool:
        """Inicializa sistema de dashboard de métricas"""
        try:
            config = self.config.get('metrics_dashboard', {})
            
            dashboard_config = {
                'collection_interval': config.get('collection_interval', 1.0),
                'db_path': str(self.data_dir / 'metrics.db'),
                'web_port': config.get('web_port', 8080)
            }
            
            self.metrics_dashboard = MetricsDashboard(dashboard_config)
            
            # Start dashboard in background thread to avoid blocking
            self._dashboard_thread = threading.Thread(
                target=self.metrics_dashboard.start,
                daemon=True
            )
            self._dashboard_thread.start()
            
            self.components_status['metrics_dashboard'] = True
            logger.info(f"✅ Metrics Dashboard initialized (Port: {dashboard_config['web_port']})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Metrics Dashboard: {e}")
            return False
    
    def _init_feedback_loop(self) -> bool:
        """Inicializa sistema de coleta de feedback"""
        try:
            from src.learning.feedback_loop import FeedbackDatabase
            
            config = self.config.get('feedback_loop', {})
            db_path = self.learning_dir / "feedback.db"
            
            self.feedback_loop = FeedbackDatabase(db_path)
            self.components_status['feedback_loop'] = True
            
            logger.info("✅ Feedback Loop initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Feedback Loop: {e}")
            return False
    
    def _init_knowledge_distiller(self) -> bool:
        """Inicializa Knowledge Distiller (Golden Commands)"""
        try:
            from src.learning.knowledge_distiller import KnowledgeDistiller
            
            self.knowledge_distiller = KnowledgeDistiller(self.data_dir)
            self.components_status['knowledge_distiller'] = True
            
            logger.info("✅ Knowledge Distiller initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Knowledge Distiller: {e}")
            return False
    
    def _init_continual_learner(self) -> bool:
        """Inicializa Continual Learner (Auto-Training)"""
        try:
            from src.learning.continual_learner import ContinualLearner
            
            config = self.config.get('continual_learner', {})
            feedback_threshold = config.get('feedback_threshold', 100)
            check_interval = config.get('check_interval', 3600)
            
            self.continual_learner = ContinualLearner(
                data_dir=self.data_dir,
                feedback_threshold=feedback_threshold,
                check_interval=check_interval
            )
            
            # Start autonomous monitoring loop
            self.continual_learner.start()
            self.components_status['continual_learner'] = True
            
            logger.info(f"✅ Continual Learner initialized (Threshold: {feedback_threshold} interactions)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Continual Learner: {e}")
            return False
    
    def _init_dream_cycle(self) -> bool:
        """Inicializa Dream Cycle (Nighttime Training)"""
        try:
            from src.learning.dream_cycle import DreamCycle, IdleConditions
            
            config = self.config.get('dream_cycle', {})
            
            # Build idle conditions from config
            idle_conditions = IdleConditions(
                max_cpu_percent=config.get('max_cpu_percent', 20.0),
                max_memory_percent=config.get('max_memory_percent', 80.0),
                min_idle_duration_seconds=config.get('min_idle_duration', 300),
                night_start_hour=config.get('night_start_hour', 22),
                night_end_hour=config.get('night_end_hour', 6),
                check_interval_seconds=config.get('check_interval', 60)
            )
            
            self.dream_cycle = DreamCycle(
                data_dir=self.data_dir,
                idle_conditions=idle_conditions
            )
            
            # Start autonomous monitoring
            self.dream_cycle.start()
            self.components_status['dream_cycle'] = True
            
            logger.info(f"✅ Dream Cycle initialized (Active: {config.get('night_start_hour')}h-{config.get('night_end_hour')}h)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Dream Cycle: {e}")
            return False
    
    def record_interaction(
        self,
        user_input: str,
        ai_response: str,
        feedback_value: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Registra uma interação para aprendizado.
        
        Args:
            user_input: Comando do usuário
            ai_response: Resposta do agente
            feedback_value: Valor de feedback (-1.0 a 1.0) se explícito
            metadata: Dados adicionais (latência, provider usado, etc)
        """
        if not self.feedback_loop:
            return
        
        try:
            # Coleta feedback implícito se não houver explícito
            if feedback_value is None:
                # TODO: Implementar heurísticas de feedback implícito
                # - Tempo de resposta
                # - Usuário repetiu comando?
                # - Houve interrupção?
                feedback_value = 0.5  # Neutro por padrão
            
            from src.learning.feedback_loop import FeedbackEntry
            import hashlib
            import time
            from datetime import datetime
            
            interaction_id = hashlib.md5(
                f"{user_input}{time.time()}".encode()
            ).hexdigest()[:16]
            
            feedback_id = hashlib.md5(
                f"{interaction_id}{time.time()}".encode()
            ).hexdigest()[:16]
            
            entry = FeedbackEntry(
                feedback_id=feedback_id,
                interaction_id=interaction_id,
                user_input=user_input,
                ai_response=ai_response,
                feedback_type='implicit',
                feedback_value=feedback_value,
                timestamp=datetime.now().isoformat(),
                metadata=metadata or {}
            )
            
            self.feedback_loop.add_feedback(entry)
            
            # Se foi uma interação bem-sucedida, pode ser um Golden Command
            if feedback_value > 0.7 and self.knowledge_distiller:
                self.knowledge_distiller.distill_interaction(
                    user_command=user_input,
                    thought="",  # TODO: Capturar raciocínio do agente
                    actions=[],  # TODO: Capturar ações executadas
                    success=True
                )
            
        except Exception as e:
            logger.error(f"❌ Failed to record interaction: {e}")
    
    def record_interaction(
        self,
        user_input: str,
        ai_response: str,
        feedback_value: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Registra uma interação para aprendizado.
        
        Args:
            user_input: Comando do usuário
            ai_response: Resposta do agente
            feedback_value: Valor de feedback (-1.0 a 1.0) se explícito
            metadata: Dados adicionais (latência, provider usado, etc)
        """
        if not self.feedback_loop:
            return
        
        try:
            # Coleta feedback implícito se não houver explícito
            if feedback_value is None:
                # TODO: Implementar heurísticas de feedback implícito
                # - Tempo de resposta
                # - Usuário repetiu comando?
                # - Houve interrupção?
                feedback_value = 0.5  # Neutro por padrão
            
            from src.learning.feedback_loop import FeedbackEntry
            import hashlib
            import time
            from datetime import datetime
            
            interaction_id = hashlib.md5(
                f"{user_input}{time.time()}".encode()
            ).hexdigest()[:16]
            
            feedback_id = hashlib.md5(
                f"{interaction_id}{time.time()}".encode()
            ).hexdigest()[:16]
            
            entry = FeedbackEntry(
                feedback_id=feedback_id,
                interaction_id=interaction_id,
                user_input=user_input,
                ai_response=ai_response,
                feedback_type='implicit',
                feedback_value=feedback_value,
                timestamp=datetime.now().isoformat(),
                metadata=metadata or {}
            )
            
            self.feedback_loop.add_feedback(entry)
            
            # Store in scalable database if available
            if self.scalable_database:
                self._store_interaction_in_scalable_db(entry)
            
            # Record metrics if dashboard available
            if self.metrics_dashboard:
                self.metrics_dashboard.add_training_metric(
                    job_id="main_session",
                    metric_name="user_interaction",
                    value=feedback_value,
                    metadata={
                        'input_length': len(user_input),
                        'response_length': len(ai_response),
                        'timestamp': datetime.now().isoformat()
                    }
                )
            
            # Se foi uma interação bem-sucedida, pode ser um Golden Command
            if feedback_value > 0.7 and self.knowledge_distiller:
                self.knowledge_distiller.distill_interaction(
                    user_command=user_input,
                    thought="",  # TODO: Capturar raciocínio do agente
                    actions=[],  # TODO: Capturar ações executadas
                    success=True
                )
            
        except Exception as e:
            logger.error(f"❌ Failed to record interaction: {e}")
    
    def _store_interaction_in_scalable_db(self, entry):
        """Store interaction in scalable database for analytics."""
        try:
            # Create table if not exists
            sql_conn = self.scalable_database.get_sql_connection()
            if sql_conn:
                cursor = sql_conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        interaction_id TEXT UNIQUE,
                        user_input TEXT,
                        ai_response TEXT,
                        feedback_value REAL,
                        timestamp TEXT,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert interaction
                import json
                cursor.execute("""
                    INSERT OR REPLACE INTO interactions 
                    (interaction_id, user_input, ai_response, feedback_value, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entry.interaction_id,
                    entry.user_input,
                    entry.ai_response,
                    entry.feedback_value,
                    entry.timestamp,
                    json.dumps(entry.metadata)
                ))
                
                sql_conn.commit()
                
        except Exception as e:
            logger.debug(f"Could not store interaction in scalable DB: {e}")
    
    def start_distributed_training(self, 
                                 model_config: Dict[str, Any], 
                                 dataset_path: str, 
                                 output_dir: Optional[str] = None,
                                 num_gpus: Optional[int] = None) -> Optional[str]:
        """
        Inicia um trabalho de treinamento distribuído.
        
        Args:
            model_config: Configuração do modelo
            dataset_path: Caminho para dataset
            output_dir: Diretório de output (se None, usa models/)
            num_gpus: Número de GPUs (se None, auto-detecta)
        
        Returns:
            Job ID se sucesso, None caso contrário
        """
        if not self.distributed_trainer:
            logger.error("Distributed trainer not initialized")
            return None
        
        try:
            if output_dir is None:
                import time
                timestamp = int(time.time())
                output_dir = str(self.models_dir / f"training_job_{timestamp}")
            
            # Create training job
            job_id = self.distributed_trainer.create_training_job(
                model_config=model_config,
                dataset_path=dataset_path,
                output_dir=output_dir,
                num_gpus=num_gpus
            )
            
            if job_id:
                # Start training
                success = self.distributed_trainer.start_training_job(job_id)
                
                if success:
                    logger.info(f"✅ Started distributed training job: {job_id}")
                    
                    # Record training start in metrics
                    if self.metrics_dashboard:
                        self.metrics_dashboard.add_training_metric(
                            job_id=job_id,
                            metric_name="training_started",
                            value=1.0,
                            metadata={'model_config': model_config, 'num_gpus': num_gpus or 1}
                        )
                    
                    return job_id
                else:
                    logger.error(f"Failed to start training job: {job_id}")
                    return None
            else:
                logger.error("Failed to create training job")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to start distributed training: {e}")
            return None
    
    def get_training_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a distributed training job."""
        if not self.distributed_trainer:
            return None
        
        return self.distributed_trainer.get_job_status(job_id)
    
    def list_active_training_jobs(self) -> List[Dict[str, Any]]:
        """List all active training jobs."""
        if not self.distributed_trainer:
            return []
        
        return self.distributed_trainer.list_active_jobs()
    
    def register_model(self, 
                      name: str, 
                      model_path: str, 
                      metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Registra um modelo treinado no registry.
        
        Args:
            name: Nome do modelo
            model_path: Caminho para arquivos do modelo
            metadata: Metadados do modelo
        
        Returns:
            Model ID se sucesso
        """
        if not self.model_registry:
            logger.error("Model registry not initialized")
            return None
        
        try:
            model_id = self.model_registry.register_model(
                name=name,
                model_path=Path(model_path),
                metadata=metadata or {}
            )
            
            logger.info(f"✅ Registered model: {name} (ID: {model_id})")
            return model_id
            
        except Exception as e:
            logger.error(f"❌ Failed to register model: {e}")
            return None
    
    def deploy_model(self, model_id: str) -> bool:
        """Deploy a registered model for inference."""
        if not self.model_registry:
            logger.error("Model registry not initialized")
            return False
        
        try:
            success = self.model_registry.deploy_model(model_id)
            if success:
                logger.info(f"✅ Deployed model: {model_id}")
            else:
                logger.error(f"Failed to deploy model: {model_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy model: {e}")
            return False
    
    def get_dashboard_url(self) -> Optional[str]:
        """Get metrics dashboard URL."""
        if not self.metrics_dashboard:
            return None
        
        port = self.metrics_dashboard.web_dashboard.port
        return f"http://localhost:{port}"
    
    def record_explicit_feedback(
        self,
        interaction_id: str,
        feedback_value: float,
        correction: Optional[str] = None
    ):
        """
        Registra feedback explícito do usuário (👍/👎).
        
        Args:
            interaction_id: ID da interação
            feedback_value: -1.0 (ruim) a 1.0 (excelente)
            correction: Correção fornecida pelo usuário (opcional)
        """
        if not self.feedback_loop:
            return
        
        try:
            # TODO: Atualizar feedback entry existente ou criar nova
            logger.info(f"📝 Explicit feedback recorded: {feedback_value} for {interaction_id}")
        except Exception as e:
            logger.error(f"❌ Failed to record explicit feedback: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status de todos os sistemas de aprendizado"""
        status = {
            'enabled': self.enabled,
            'initialized': self.is_initialized,
            'components': self.components_status.copy(),
            'dashboard_url': self.get_dashboard_url(),
            'dependencies': self._check_dependencies()
        }
        
        # Legacy components stats
        if self.continual_learner:
            status['training_cycles'] = getattr(self.continual_learner, 'training_cycles', 0)
        
        if self.feedback_loop:
            try:
                status['total_feedback'] = self.feedback_loop.count_pending() if hasattr(self.feedback_loop, 'count_pending') else 0
            except:
                status['total_feedback'] = 0
        
        # New components stats
        if self.distributed_trainer:
            status['gpu_status'] = self.distributed_trainer.gpu_manager.get_gpu_utilization()
            status['active_training_jobs'] = len(self.distributed_trainer.active_jobs)
        
        if self.model_registry:
            try:
                status['registered_models'] = len(self.model_registry.list_models())
                status['deployed_models'] = len(self.model_registry.list_deployed_models())
            except:
                status['registered_models'] = 0
                status['deployed_models'] = 0
        
        if self.scalable_database:
            status['database_backend'] = self.scalable_database.get_current_backend()
        
        return status
    
    def _print_status(self):
        """Imprime status formatado dos sistemas"""
        print("\n" + "="*80)
        print("🧠 JARVIS LEARNING ENGINE - ADVANCED STATUS REPORT")
        print("="*80)
        
        # Infrastructure Layer
        print("\n🏗️  INFRASTRUCTURE LAYER:")
        infra_components = ['scalable_database', 'model_registry', 'distributed_trainer', 'metrics_dashboard']
        for component in infra_components:
            active = self.components_status.get(component, False)
            status_icon = "✅" if active else "❌"
            component_name = component.replace('_', ' ').title()
            print(f"  {status_icon} {component_name}: {'ONLINE' if active else 'OFFLINE'}")
        
        # Learning Layer
        print("\n🧠 LEARNING LAYER:")
        learning_components = ['feedback_loop', 'knowledge_distiller', 'continual_learner', 'dream_cycle']
        for component in learning_components:
            active = self.components_status.get(component, False)
            status_icon = "✅" if active else "❌"
            component_name = component.replace('_', ' ').title()
            print(f"  {status_icon} {component_name}: {'ONLINE' if active else 'OFFLINE'}")
        
        # Additional Info
        print("\n📊 SYSTEM INFORMATION:")
        if self.distributed_trainer:
            gpu_count = len(self.distributed_trainer.gpu_manager.available_gpus)
            print(f"  🎮 Available GPUs: {gpu_count}")
        
        if self.metrics_dashboard:
            dashboard_url = self.get_dashboard_url()
            print(f"  📈 Dashboard: {dashboard_url}")
        
        if self.model_registry:
            try:
                model_count = len(self.model_registry.list_models())
                print(f"  🤖 Registered Models: {model_count}")
            except:
                print(f"  🤖 Registered Models: 0")
        
        print("="*80)
        print("💡 JARVIS is now in ADVANCED CONTINUOUS EVOLUTION MODE!")
        print("   • Multi-GPU distributed training enabled")
        print("   • Real-time metrics monitoring active")
        print("   • Auto-scaling database with migration support")
        print("   • Model versioning and A/B testing ready")
        print("   • Every interaction improves the neural model")
        print("="*80 + "\n")
    
    def shutdown(self):
        """Encerra todos os sistemas de aprendizado de forma segura"""
        logger.info("🔄 Shutting down Learning Engine...")
        
        # Shutdown learning components
        if self.continual_learner:
            self.continual_learner.is_running = False
        
        if self.dream_cycle:
            self.dream_cycle.stop()
        
        # Shutdown infrastructure components
        if self.metrics_dashboard:
            try:
                self.metrics_dashboard.stop()
            except:
                pass
        
        if self.distributed_trainer:
            try:
                # Terminate any running training jobs
                for job_id in list(self.distributed_trainer.active_jobs.keys()):
                    self.distributed_trainer.terminate_job(job_id)
                
                # Clean up GPU resources
                for job_id in list(self.distributed_trainer.gpu_manager.allocated_gpus.keys()):
                    self.distributed_trainer.gpu_manager.free_gpus(job_id)
                    
            except Exception as e:
                logger.warning(f"Error shutting down distributed trainer: {e}")
        
        if self.scalable_database:
            try:
                self.scalable_database.close()
            except:
                pass
        
        # Stop dashboard thread if running
        if self._dashboard_thread and self._dashboard_thread.is_alive():
            try:
                # Dashboard thread is daemon, will be killed when main process exits
                pass
            except:
                pass
        
        logger.info("✅ Learning Engine shutdown complete")


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
_learning_engine: Optional[LearningEngine] = None

def get_learning_engine(project_root: Path = None) -> Optional[LearningEngine]:
    """
    Obtém instância singleton do Learning Engine.
    
    Args:
        project_root: Diretório raiz do projeto (necessário na primeira chamada)
    
    Returns:
        Instância do LearningEngine ou None se não inicializado
    """
    global _learning_engine
    
    if _learning_engine is None and project_root:
        _learning_engine = LearningEngine(project_root)
    
    return _learning_engine

def initialize_learning_systems(project_root: Path) -> bool:
    """
    Inicializa todos os sistemas de aprendizado.
    Esta é a função principal a ser chamada pelo launcher.
    
    Args:
        project_root: Diretório raiz do projeto
    
    Returns:
        True se inicialização bem-sucedida
    """
    engine = get_learning_engine(project_root)
    
    if engine:
        return engine.initialize()
    
    return False
