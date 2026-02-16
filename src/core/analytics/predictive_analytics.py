#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Predictive Analytics System  
=================================================
Sistema de anÃ¡lise preditiva que usa machine learning para prever falhas
e otimizar distribiÃ§Ã£o de tarefas na rede democrÃ¡tica.
"""

import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import time
import pickle
from collections import deque
from enum import Enum
from functools import lru_cache

# Imports cientÃ­ficos
try:
    from sklearn.ensemble import RandomForestRegressor, IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("âš ï¸ scikit-learn nÃ£o disponÃ­vel. Usando analytics bÃ¡sicos.")

class PredictionType(Enum):
    """Tipos de prediÃ§Ãµes suportadas"""
    HARDWARE_FAILURE = "hardware_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"  
    MEMORY_OVERFLOW = "memory_overflow"
    NETWORK_CONGESTION = "network_congestion"
    TASK_COMPLETION_TIME = "task_completion_time"
    OPTIMAL_DEVICE_SELECTION = "optimal_device_selection"

class AlertSeverity(Enum):
    """Severidade dos alertas preditivos"""
    INFO = 1
    WARNING = 2
    CRITICAL = 3
    EMERGENCY = 4

@dataclass
class SystemMetrics:
    """ðŸ“Š MÃ©tricas do sistema em um ponto no tempo"""
    timestamp: datetime
    device_id: str
    # MÃ©tricas de hardware
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    gpu_percent: float
    gpu_memory_mb: float
    # MÃ©tricas de rede
    network_latency_ms: float
    bandwidth_mbps: float
    # MÃ©tricas de aplicaÃ§Ã£o
    active_tasks: int
    completed_tasks_hour: int
    error_count_hour: int
    # MÃ©tricas ambientais
    uptime_hours: float
    temperature_c: float

@dataclass
class PredictiveAlert:
    """ðŸš¨ Alerta preditivo gerado pelo sistema"""
    alert_id: str
    prediction_type: PredictionType
    severity: AlertSeverity
    device_id: str
    predicted_event: str
    confidence_score: float  # 0.0 - 1.0
    time_to_event_hours: float
    current_metrics: SystemMetrics
    recommendation: str
    created_at: datetime

@dataclass
class DevicePerformanceProfile:
    """ðŸ‘¤ Perfil de performance de um dispositivo"""
    device_id: str
    device_name: str
    # PadrÃµes histÃ³ricos
    typical_cpu_range: Tuple[float, float]
    typical_memory_range: Tuple[float, float]
    peak_performance_hours: List[int]  # HorÃ¡rios de melhor performance
    # PadrÃµes de falha
    common_failure_patterns: List[str]
    mean_task_completion_time: float
    reliability_score: float  # 0.0 - 1.0
    # AnÃ¡lise temporal
    performance_trend: str  # "improving", "stable", "degrading"
    last_updated: datetime

class DemocraticPredictiveAnalytics:
    """
    ðŸ”® SISTEMA DE ANÃLISE PREDITIVA DEMOCRÃTICO
    
    Funcionalidades:
    - Coleta contÃ­nua de mÃ©tricas de todos dispositivos
    - Machine learning para prediÃ§Ã£o de falhas
    - OtimizaÃ§Ã£o de distribuiÃ§Ã£o de tarefas
    - Alertas preditivos com recomendaÃ§Ãµes
    - Perfis de performance por dispositivo
    """
    
    def __init__(self, jarvis_core, democratic_network):
        self.jarvis_core = jarvis_core
        self.democratic_network = democratic_network
        self.config_path = Path(jarvis_core.config['system']['base_path']) / "data" / "predictive_analytics"
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Estado do sistema
        self.is_running = False
        self.metrics_history: Dict[str, deque] = {}  # device_id -> deque of metrics
        self.device_profiles: Dict[str, DevicePerformanceProfile] = {}
        self.active_alerts: Dict[str, PredictiveAlert] = {}
        
        # Modelos ML
        self.ml_models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.model_trained = False
        
        # ConfiguraÃ§Ãµes
        self.metrics_retention_hours = 168  # 1 semana
        self.collection_interval = 30  # segundos
        self.prediction_interval = 300  # 5 minutos
        self.max_metrics_per_device = 2016  # ~1 semana de dados com 30s interval
        
        # Threading
        self.collection_thread = None
        self.prediction_thread = None
        self.stop_event = threading.Event()
        
        # Callbacks
        self.on_predictive_alert: Optional[Callable] = None
        
        # Cache para otimizaÃ§Ãµes
        self._prediction_cache: Dict[str, Tuple[Any, datetime]] = {}
        self._cache_ttl_seconds = 300  # 5 minutos
        
        # Carregar dados existentes
        self._load_historical_data()
        
        print("ðŸ”® Predictive Analytics inicializado")
    
    def start_analytics(self):
        """ðŸš€ INICIA ANÃLISE PREDITIVA"""
        if self.is_running:
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        # Thread para coluna de mÃ©tricas
        self.collection_thread = threading.Thread(target=self._metrics_collection_loop, daemon=True)
        self.collection_thread.start()
        
        # Thread para prediÃ§Ãµes periÃ³dicas
        self.prediction_thread = threading.Thread(target=self._prediction_loop, daemon=True) 
        self.prediction_thread.start()
        
        print("ðŸ“Š Predictive Analytics: AnÃ¡lise ativada")
    
    def stop_analytics(self):
        """â¹ï¸ PARA ANÃLISE PREDITIVA"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.stop_event.set()
        
        for thread in [self.collection_thread, self.prediction_thread]:
            if thread and thread.is_alive():
                thread.join(timeout=5)
        
        # Salvar dados antes de parar
        self._save_historical_data()
        
        print("ðŸ›‘ Predictive Analytics: AnÃ¡lise parada")
    
    def _get_cached_prediction(self, cache_key: str) -> Optional[Any]:
        """ðŸ” Buscar prediÃ§Ã£o em cache com TTL"""
        if cache_key in self._prediction_cache:
            result, timestamp = self._prediction_cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self._cache_ttl_seconds:
                return result
            else:
                # Cache expirado, remover
                del self._prediction_cache[cache_key]
        return None
    
    def _set_cached_prediction(self, cache_key: str, result: Any):
        """ðŸ’¾ Armazenar prediÃ§Ã£o em cache"""
        self._prediction_cache[cache_key] = (result, datetime.now())
    
    def _metrics_collection_loop(self):
        """ðŸ“ˆ LOOP DE COLETA DE MÃ‰TRICAS"""
        while not self.stop_event.wait(self.collection_interval):
            try:
                # Coletar mÃ©tricas locais
                local_metrics = self._collect_local_metrics()
                if local_metrics:
                    self._store_metrics(local_metrics)
                
                # Coletar mÃ©tricas de dispositivos da rede democrÃ¡tica
                if self.democratic_network and self.democratic_network.is_running:
                    asyncio.run(self._collect_network_metrics())
                
                # Limpar mÃ©tricas antigas
                self._cleanup_old_metrics()
                
            except Exception as e:
                print(f"âŒ Erro na coleta de mÃ©tricas: {e}")
    
    def _prediction_loop(self):
        """ðŸ”® LOOP DE PREDIÃ‡Ã•ES"""
        while not self.stop_event.wait(self.prediction_interval):
            try:
                # Treinar modelos se temos dados suficientes
                if not self.model_trained and self._has_sufficient_data():
                    asyncio.run(self._train_predictive_models())
                
                # Executar prediÃ§Ãµes
                if self.model_trained:
                    asyncio.run(self._run_predictions())
                
                # Atualizar perfis de dispositivo
                self._update_device_profiles()
                
            except Exception as e:
                print(f"âŒ Erro na anÃ¡lise preditiva: {e}")
    
    def _collect_local_metrics(self) -> Optional[SystemMetrics]:
        """ðŸ“Š COLETA MÃ‰TRICAS LOCAIS"""
        try:
            import psutil
            
            # MÃ©tricas bÃ¡sicas
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # MÃ©tricas de GPU (se disponÃ­vel)
            gpu_percent = 0.0
            gpu_memory_mb = 0.0
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    gpu_percent = gpu.load * 100
                    gpu_memory_mb = gpu.memoryUsed
            except:
                pass
            
            # MÃ©tricas de rede
            network_latency_ms = self._measure_network_latency()
            bandwidth_mbps = self._estimate_bandwidth()
            
            # MÃ©tricas de aplicaÃ§Ã£o JARVIS
            active_tasks = self._count_active_tasks()
            completed_tasks_hour = self._count_completed_tasks_last_hour()
            error_count_hour = self._count_errors_last_hour()
            
            # MÃ©tricas de sistema
            uptime_hours = time.time() - psutil.boot_time()
            uptime_hours = uptime_hours / 3600  # converter para horas
            
            # Temperatura (se disponÃ­vel)
            temperature_c = self._get_system_temperature()
            
            return SystemMetrics(
                timestamp=datetime.now(),
                device_id=self.democratic_network.device_id if self.democratic_network else "local",
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                gpu_percent=gpu_percent,
                gpu_memory_mb=gpu_memory_mb,
                network_latency_ms=network_latency_ms,
                bandwidth_mbps=bandwidth_mbps,
                active_tasks=active_tasks,
                completed_tasks_hour=completed_tasks_hour,
                error_count_hour=error_count_hour,
                uptime_hours=uptime_hours,
                temperature_c=temperature_c
            )
            
        except Exception as e:
            print(f"âŒ Erro coletando mÃ©tricas locais: {e}")
            return None
    
    async def _collect_network_metrics(self):
        """ðŸŒ COLETA MÃ‰TRICAS DE DISPOSITIVOS DA REDE"""
        try:
            # Obter status de todos dispositivos conectados
            network_status = self.democratic_network.get_network_status()
            
            for device_id, device_info in network_status.get('connected_devices', {}).items():
                if device_id != self.democratic_network.device_id:  # Salar local
                    # Simular coleta de mÃ©tricas remotas
                    # Em implementaÃ§Ã£o real, seria uma chamada de rede
                    remote_metrics = self._simulate_remote_metrics(device_id, device_info)
                    if remote_metrics:
                        self._store_metrics(remote_metrics)
                        
        except Exception as e:
            print(f"âŒ Erro coletando mÃ©tricas de rede: {e}")
    
    def _simulate_remote_metrics(self, device_id: str, device_info: Dict) -> Optional[SystemMetrics]:
        """ðŸŽ­ SIMULA MÃ‰TRICAS REMOTAS (placeholder)"""
        # Em implementaÃ§Ã£o real, faria request para o dispositivo remoto
        # Por ora, simular baseado em device_info
        
        try:
            specs = device_info.get('specs', {})
            
            return SystemMetrics(
                timestamp=datetime.now(),
                device_id=device_id,
                cpu_percent=np.random.normal(50, 20),  # Simular CPU variÃ¡vel
                memory_percent=np.random.normal(60, 15),
                disk_percent=np.random.normal(40, 10),
                gpu_percent=np.random.normal(30, 25),
                gpu_memory_mb=np.random.normal(2000, 500),
                network_latency_ms=np.random.normal(20, 10),
                bandwidth_mbps=np.random.normal(100, 30),
                active_tasks=np.random.randint(0, 5),
                completed_tasks_hour=np.random.randint(5, 50),
                error_count_hour=np.random.randint(0, 3),
                uptime_hours=np.random.normal(72, 24),  # ~3 dias mÃ©dia
                temperature_c=np.random.normal(45, 10)
            )
        except:
            return None
    
    def _store_metrics(self, metrics: SystemMetrics):
        """ðŸ’¾ ARMAZENA MÃ‰TRICAS NO HISTÃ“RICO"""
        device_id = metrics.device_id
        
        if device_id not in self.metrics_history:
            self.metrics_history[device_id] = deque(maxlen=self.max_metrics_per_device)
        
        self.metrics_history[device_id].append(metrics)
    
    def _cleanup_old_metrics(self):
        """ðŸ§¹ LIMPA MÃ‰TRICAS ANTIGAS"""
        cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)
        
        for device_id, metrics_queue in self.metrics_history.items():
            # Remover mÃ©tricas antigas do inÃ­cio da deque
            while metrics_queue and metrics_queue[0].timestamp < cutoff_time:
                metrics_queue.popleft()
    
    def _has_sufficient_data(self) -> bool:
        """âœ… VERIFICA SE TEM DADOS SUFICIENTES PARA TREINAR"""
        total_samples = sum(len(queue) for queue in self.metrics_history.values())
        return total_samples >= 100  # MÃ­nimo 100 amostras
    
    async def _train_predictive_models(self):
        """ðŸŽ“ TREINA MODELOS DE ML"""
        if not SKLEARN_AVAILABLE:
            print("âš ï¸ Sklearn nÃ£o disponÃ­vel. Pulando treinamento ML.")
            return
        
        print("ðŸŽ“ Treinando modelos preditivos...")
        
        try:
            # Preparar dataset
            df = self._prepare_training_dataset()
            if df.empty:
                print("âŒ Dataset vazio para treinamento")
                return
            
            # Treinar modelo para prediÃ§Ã£o de falhas de hardware
            await self._train_hardware_failure_model(df)
            
            # Treinar modelo para prediÃ§Ã£o de tempo de conclusÃ£o de tarefas
            await self._train_task_completion_model(df)
            
            # Treinar modelo para detecÃ§Ã£o de anomalias
            await self._train_anomaly_detection_model(df)
            
            self.model_trained = True
            print("âœ… Modelos treinados com sucesso")
            
        except Exception as e:
            print(f"âŒ Erro treinando modelos: {e}")
    
    def _prepare_training_dataset(self) -> pd.DataFrame:
        """ðŸ“Š PREPARA DATASET PARA TREINAMENTO"""
        data_rows = []
        
        for device_id, metrics_queue in self.metrics_history.items():
            for metrics in metrics_queue:
                row = asdict(metrics)
                row['timestamp'] = metrics.timestamp.timestamp()
                data_rows.append(row)
        
        df = pd.DataFrame(data_rows)
        
        if not df.empty:
            # Criar features adicionais
            df['hour_of_day'] = pd.to_datetime(df['timestamp'], unit='s').dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp'], unit='s').dt.dayofweek
            
            # Criar targets para prediÃ§Ã£o
            df = self._create_prediction_targets(df)
        
        return df
    
    def _create_prediction_targets(self, df: pd.DataFrame) -> pd.DataFrame:
        """ðŸŽ¯ CRIA TARGETS PARA PREDIÃ‡ÃƒO"""
        df = df.sort_values(['device_id', 'timestamp'])
        
        for device_id in df['device_id'].unique():
            device_df = df[df['device_id'] == device_id].copy()
            
            # Target: falha de hardware (CPU > 95% ou Memory > 90%)
            device_df['hardware_failure_risk'] = (
                (device_df['cpu_percent'] > 95) | 
                (device_df['memory_percent'] > 90)
            ).astype(int)
            
            # Target: degradaÃ§Ã£o de performance (rolling mean)
            device_df['performance_degrading'] = (
                device_df['cpu_percent'].rolling(5).mean() > 
                device_df['cpu_percent'].rolling(20).mean() + 10
            ).astype(int)
            
            # Atualizar no DataFrame principal
            df.loc[df['device_id'] == device_id, 'hardware_failure_risk'] = device_df['hardware_failure_risk']
            df.loc[df['device_id'] == device_id, 'performance_degrading'] = device_df['performance_degrading']
        
        return df
    
    async def _train_hardware_failure_model(self, df: pd.DataFrame):
        """âš™ï¸ TREINA MODELO DE FALHA DE HARDWARE"""
        try:
            features = ['cpu_percent', 'memory_percent', 'disk_percent', 'gpu_percent', 
                       'temperature_c', 'error_count_hour', 'uptime_hours']
            
            X = df[features].fillna(0)
            y = df['hardware_failure_risk'].fillna(0)
            
            if len(y.unique()) > 1:  # Precisa ter both classes
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                # Scaler
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Modelo
                model = RandomForestRegressor(n_estimators=50, random_state=42)
                model.fit(X_train_scaled, y_train)
                
                # Avaliar
                y_pred = model.predict(X_test_scaled)
                mae = mean_absolute_error(y_test, y_pred)
                
                print(f"   ðŸ“Š Hardware Failure Model MAE: {mae:.3f}")
                
                # Salvar
                self.ml_models['hardware_failure'] = model
                self.scalers['hardware_failure'] = scaler
                
        except Exception as e:
            print(f"âŒ Erro treinando modelo de falha de hardware: {e}")
    
    async def _train_task_completion_model(self, df: pd.DataFrame):
        """â±ï¸ TREINA MODELO DE TEMPO DE CONCLUSÃƒO"""
        try:
            features = ['cpu_percent', 'memory_percent', 'active_tasks', 'gpu_percent']
            
            X = df[features].fillna(0)
            y = df['active_tasks'] + np.random.normal(0, 0.5, len(df))  # Simular task completion time
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scaler
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Modelo
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Avaliar
            y_pred = model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            
            print(f"   ðŸ“Š Task Completion Model MAE: {mae:.3f}")
            
            # Salvar
            self.ml_models['task_completion'] = model
            self.scalers['task_completion'] = scaler
            
        except Exception as e:
            print(f"âŒ Erro treinando modelo de task completion: {e}")
    
    async def _train_anomaly_detection_model(self, df: pd.DataFrame):
        """ðŸš¨ TREINA MODELO DE DETECÃ‡ÃƒO DE ANOMALIAS"""
        try:
            features = ['cpu_percent', 'memory_percent', 'disk_percent', 'network_latency_ms', 
                       'error_count_hour', 'temperature_c']
            
            X = df[features].fillna(0)
            
            # Scaler
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Modelo de detecÃ§Ã£o de anomalias
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(X_scaled)
            
            print("   ðŸ” Anomaly Detection Model treinado")
            
            # Salvar
            self.ml_models['anomaly_detection'] = model
            self.scalers['anomaly_detection'] = scaler
            
        except Exception as e:
            print(f"âŒ Erro treinando modelo de detecÃ§Ã£o de anomalias: {e}")
    
    async def _run_predictions(self):
        """ðŸ”® EXECUTA PREDIÃ‡Ã•ES"""
        print("ðŸ”® Executando prediÃ§Ãµes...")
        
        for device_id, metrics_queue in self.metrics_history.items():
            if len(metrics_queue) < 5:  # Precisa ter histÃ³rico mÃ­nimo
                continue
            
            latest_metrics = metrics_queue[-1]
            recent_metrics = list(metrics_queue)[-10:]  # Ãšltimas 10 amostras
            
            # PrediÃ§Ã£o de falha de hardware
            await self._predict_hardware_failure(device_id, latest_metrics, recent_metrics)
            
            # PrediÃ§Ã£o de anomalias
            await self._predict_anomalies(device_id, latest_metrics)
            
            # PrediÃ§Ã£o de performance Ã³tima
            await self._predict_optimal_performance(device_id, recent_metrics)
    
    async def _predict_hardware_failure(self, device_id: str, latest: SystemMetrics, recent: List[SystemMetrics]):
        """âš™ï¸ PREDIZ FALHA DE HARDWARE"""
        if 'hardware_failure' not in self.ml_models:
            return
        
        try:
            model = self.ml_models['hardware_failure']
            scaler = self.scalers['hardware_failure']
            
            # Preparar features
            features = [latest.cpu_percent, latest.memory_percent, latest.disk_percent, 
                       latest.gpu_percent, latest.temperature_c, latest.error_count_hour, 
                       latest.uptime_hours]
            
            features_scaled = scaler.transform([features])
            risk_score = model.predict(features_scaled)[0]
            
            # Se risco alto, gerar alerta
            if risk_score > 0.7:
                alert = PredictiveAlert(
                    alert_id=f"hw_failure_{device_id}_{int(time.time())}",
                    prediction_type=PredictionType.HARDWARE_FAILURE,
                    severity=AlertSeverity.CRITICAL if risk_score > 0.9 else AlertSeverity.WARNING,
                    device_id=device_id,
                    predicted_event=f"Falha de hardware iminente (risco: {risk_score:.1%})",
                    confidence_score=risk_score,
                    time_to_event_hours=max(1, (1 - risk_score) * 24),  # Simular tempo
                    current_metrics=latest,
                    recommendation=self._get_hardware_failure_recommendation(latest),
                    created_at=datetime.now()
                )
                
                await self._emit_alert(alert)
                
        except Exception as e:
            print(f"âŒ Erro predizendo falha de hardware: {e}")
    
    async def _predict_anomalies(self, device_id: str, latest: SystemMetrics):
        """ðŸš¨ PREDIZ ANOMALIAS NO SISTEMA"""
        cache_key = f"anomalies_{device_id}_{latest.timestamp.isoformat()}"
        
        # Verificar cache
        cached_result = self._get_cached_prediction(cache_key)
        if cached_result is not None:
            return cached_result
            
        if 'anomaly_detection' not in self.ml_models:
            return
        
        try:
            model = self.ml_models['anomaly_detection']
            scaler = self.scalers['anomaly_detection']
            
            # Preparar features
            features = [latest.cpu_percent, latest.memory_percent, latest.disk_percent,
                       latest.network_latency_ms, latest.error_count_hour, latest.temperature_c]
            
            features_scaled = scaler.transform([features])
            anomaly_score = model.decision_function(features_scaled)[0]
            is_anomaly = model.predict(features_scaled)[0] == -1
            
            if is_anomaly:
                alert = PredictiveAlert(
                    alert_id=f"anomaly_{device_id}_{int(time.time())}",
                    prediction_type=PredictionType.PERFORMANCE_DEGRADATION,
                    severity=AlertSeverity.WARNING,
                    device_id=device_id,
                    predicted_event=f"Comportamento anÃ´malo detectado (score: {anomaly_score:.3f})",
                    confidence_score=abs(anomaly_score) / 2,  # Normalizar
                    time_to_event_hours=0,  # Anomalia atual
                    current_metrics=latest,
                    recommendation="Verificar logs do sistema e processos anÃ´malos",
                    created_at=datetime.now()
                )
                
                await self._emit_alert(alert)
                
        except Exception as e:
            print(f"âŒ Erro detectando anomalias: {e}")
        
        # Armazenar em cache (mesmo se erro, para evitar tentativas repetidas)
        self._set_cached_prediction(cache_key, True)
    
    async def _predict_optimal_performance(self, device_id: str, recent: List[SystemMetrics]):
        """ðŸš€ PREDIZ JANELA DE PERFORMANCE Ã“TIMA"""
        try:
            # Analisar padrÃµes de performance
            cpu_trend = np.mean([m.cpu_percent for m in recent])
            memory_trend = np.mean([m.memory_percent for m in recent])
            
            current_hour = datetime.now().hour
            
            # Se sistema estÃ¡ subutilizado, recomendar tarefas
            if cpu_trend < 30 and memory_trend < 50:
                alert = PredictiveAlert(
                    alert_id=f"optimal_window_{device_id}_{int(time.time())}",
                    prediction_type=PredictionType.OPTIMAL_DEVICE_SELECTION,
                    severity=AlertSeverity.INFO,
                    device_id=device_id,
                    predicted_event=f"Janela de performance Ã³tima detectada",
                    confidence_score=0.8,
                    time_to_event_hours=0,
                    current_metrics=recent[-1],
                    recommendation=f"Sistema subutilizado. Ideal para tarefas pesadas (CPU: {cpu_trend:.1f}%, RAM: {memory_trend:.1f}%)",
                    created_at=datetime.now()
                )
                
                await self._emit_alert(alert)
                
        except Exception as e:
            print(f"âŒ Erro predizendo janela Ã³tima: {e}")
    
    def _update_device_profiles(self):
        """ðŸ‘¤ ATUALIZA PERFIS DE DISPOSITIVOS"""
        for device_id, metrics_queue in self.metrics_history.items():
            if len(metrics_queue) < 20:  # Precisa de histÃ³rico mÃ­nimo
                continue
            
            recent_metrics = list(metrics_queue)[-100:]  # Ãšltimas 100 amostras
            
            # Calcular estatÃ­sticas
            cpu_values = [m.cpu_percent for m in recent_metrics]
            memory_values = [m.memory_percent for m in recent_metrics]
            task_completion_times = [m.completed_tasks_hour for m in recent_metrics]
            
            # Calcular reliability score baseado em erros
            total_errors = sum(m.error_count_hour for m in recent_metrics)
            total_hours = len(recent_metrics) * (self.collection_interval / 3600)
            reliability_score = max(0, 1 - (total_errors / max(total_hours, 1)) / 10)
            
            # Determinar trend
            if len(recent_metrics) >= 50:
                first_half_cpu = np.mean([m.cpu_percent for m in recent_metrics[:25]])
                second_half_cpu = np.mean([m.cpu_percent for m in recent_metrics[-25:]])
                trend = "improving" if second_half_cpu < first_half_cpu - 5 else \
                       "degrading" if second_half_cpu > first_half_cpu + 5 else "stable"
            else:
                trend = "stable"
            
            # Atualizar/criar perfil
            profile = DevicePerformanceProfile(
                device_id=device_id,
                device_name=f"Device-{device_id[-8:]}",
                typical_cpu_range=(float(np.percentile(cpu_values, 25)), float(np.percentile(cpu_values, 75))),
                typical_memory_range=(float(np.percentile(memory_values, 25)), float(np.percentile(memory_values, 75))),
                peak_performance_hours=self._identify_peak_hours(recent_metrics),
                common_failure_patterns=self._identify_failure_patterns(recent_metrics),
                mean_task_completion_time=float(np.mean(task_completion_times)),
                reliability_score=reliability_score,
                performance_trend=trend,
                last_updated=datetime.now()
            )
            
            self.device_profiles[device_id] = profile
    
    # ===== MÃ‰TODOS DE UTILIDADE =====
    
    def _get_hardware_failure_recommendation(self, metrics: SystemMetrics) -> str:
        """ðŸ’¡ RECOMENDAÃ‡ÃƒO PARA FALHA DE HARDWARE"""
        recommendations = []
        
        if metrics.cpu_percent > 90:
            recommendations.append("Reduzir carga de CPU")
        if metrics.memory_percent > 85:
            recommendations.append("Liberar memÃ³ria")
        if metrics.temperature_c > 70:
            recommendations.append("Verificar cooling")
        if metrics.error_count_hour > 5:
            recommendations.append("Investigar logs de erro")
        
        return "; ".join(recommendations) if recommendations else "Monitorar sistema"
    
    def _identify_peak_hours(self, metrics: List[SystemMetrics]) -> List[int]:
        """ðŸ“ˆ IDENTIFICA HORAS DE PICO"""
        hour_performance = {}
        
        for metric in metrics:
            hour = metric.timestamp.hour
            if hour not in hour_performance:
                hour_performance[hour] = []
            
            # Performance score inverso (menor CPU/memory = melhor performance)
            performance_score = 100 - (metric.cpu_percent + metric.memory_percent) / 2
            hour_performance[hour].append(performance_score)
        
        # Encontrar horas com melhor performance mÃ©dia
        hour_avg = {hour: np.mean(scores) for hour, scores in hour_performance.items()}
        peak_hours = [hour for hour, avg in hour_avg.items() if avg > np.percentile(list(hour_avg.values()), 75)]
        
        return sorted(peak_hours)
    
    def _identify_failure_patterns(self, metrics: List[SystemMetrics]) -> List[str]:
        """ðŸ” IDENTIFICA PADRÃ•ES DE FALHA"""
        patterns = []
        
        cpu_values = [m.cpu_percent for m in metrics]
        memory_values = [m.memory_percent for m in metrics]
        error_counts = [m.error_count_hour for m in metrics]
        
        # PadrÃ£o: picos de CPU
        if np.max(cpu_values) > 95:
            patterns.append("CPU spikes")
        
        # PadrÃ£o: memory leak
        if len(memory_values) > 10 and np.corrcoef(range(len(memory_values)), memory_values)[0,1] > 0.7:
            patterns.append("Memory leak trend")
        
        # PadrÃ£o: erros frequentes
        if np.mean(error_counts) > 2:
            patterns.append("Frequent errors")
        
        return patterns
    
    async def _emit_alert(self, alert: PredictiveAlert):
        """ðŸ“¢ EMITE ALERTA PREDITIVO"""
        self.active_alerts[alert.alert_id] = alert
        
        print(f"\nðŸš¨ ALERTA PREDITIVO:")
        print(f"   ðŸŽ¯ Tipo: {alert.prediction_type.value}")
        print(f"   âš ï¸ Severidade: {alert.severity.name}")
        print(f"   ðŸ“± Device: {alert.device_id}")
        print(f"   ðŸ”® Evento: {alert.predicted_event}")
        print(f"   ðŸ“Š ConfianÃ§a: {alert.confidence_score:.1%}")
        print(f"   â° Tempo estimado: {alert.time_to_event_hours:.1f}h")
        print(f"   ðŸ’¡ RecomendaÃ§Ã£o: {alert.recommendation}")
        
        # Callback se definido
        if self.on_predictive_alert:
            self.on_predictive_alert(alert)
        
        # Auto-executar recomendaÃ§Ãµes crÃ­ticas se possÃ­vel
        if alert.severity == AlertSeverity.EMERGENCY:
            await self._auto_execute_emergency_response(alert)
    
    async def _auto_execute_emergency_response(self, alert: PredictiveAlert):
        """ðŸš‘ RESPOSTA AUTOMÃTICA DE EMERGÃŠNCIA"""
        print(f"ðŸš‘ Executando resposta automÃ¡tica para: {alert.alert_id}")
        
        # Se Ã© falha de hardware crÃ­tica, solicitar takeover na rede democrÃ¡tica
        if (alert.prediction_type == PredictionType.HARDWARE_FAILURE and 
            self.democratic_network and self.democratic_network.is_running):
            
            # Solicitar que outros dispositivos assumam tarefas
            task_id = await self.democratic_network.request_distributed_task(
                task_type=self.democratic_network.TaskType.HEAVY_INFERENCE,
                duration_min=30,
                priority=10,
                data_size_mb=50.0,
                can_be_distributed=True,
                min_devices=1
            )
            
            print(f"   ðŸ”„ Solicitado takeover de emergÃªncia: {task_id}")
    
    # ===== MÃ‰TRICAS PLACEHOLDER =====
    
    def _measure_network_latency(self) -> float:
        """ðŸ“¡ Mede latÃªncia da rede"""
        return np.random.normal(20, 10)  # Simular latÃªncia
    
    def _estimate_bandwidth(self) -> float:
        """ðŸ“Š Estima bandwidth"""
        return np.random.normal(100, 30)  # Simular bandwidth
    
    def _count_active_tasks(self) -> int:
        """ðŸ“ Conta tarefas ativas"""
        return np.random.randint(0, 5)
    
    def _count_completed_tasks_last_hour(self) -> int:
        """âœ… Conta tarefas completadas na Ãºltima hora"""
        return np.random.randint(5, 50)
    
    def _count_errors_last_hour(self) -> int:
        """âŒ Conta erros na Ãºltima hora"""
        return np.random.randint(0, 3)
    
    def _get_system_temperature(self) -> float:
        """ðŸŒ¡ï¸ Temperatura do sistema"""
        return np.random.normal(45, 10)
    
    # ===== PERSISTÃŠNCIA =====
    
    def _save_historical_data(self):
        """ðŸ’¾ SALVA DADOS HISTÃ“RICOS"""
        try:
            # Salvar mÃ©tricas
            metrics_file = self.config_path / "metrics_history.json"
            metrics_data = {}
            
            for device_id, metrics_queue in self.metrics_history.items():
                metrics_data[device_id] = [asdict(m) for m in metrics_queue]
                # Converter timestamps para string
                for metric_dict in metrics_data[device_id]:
                    metric_dict['timestamp'] = metric_dict['timestamp'].isoformat()
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            # Salvar perfis
            profiles_file = self.config_path / "device_profiles.json"
            profiles_data = {}
            for device_id, profile in self.device_profiles.items():
                profile_dict = asdict(profile)
                profile_dict['last_updated'] = profile.last_updated.isoformat()
                profiles_data[device_id] = profile_dict
            
            with open(profiles_file, 'w') as f:
                json.dump(profiles_data, f, indent=2)
            
            # Salvar modelos ML (se disponÃ­vel)
            if SKLEARN_AVAILABLE and self.ml_models:
                models_file = self.config_path / "ml_models.pkl"
                with open(models_file, 'wb') as f:
                    pickle.dump({
                        'models': self.ml_models,
                        'scalers': self.scalers
                    }, f)
            
            print("ðŸ’¾ Dados preditivos salvos")
            
        except Exception as e:
            print(f"âŒ Erro salvando dados: {e}")
    
    def _load_historical_data(self):
        """ðŸ“ CARREGA DADOS HISTÃ“RICOS"""
        try:
            # Carregar mÃ©tricas
            metrics_file = self.config_path / "metrics_history.json"
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    metrics_data = json.load(f)
                
                for device_id, metrics_list in metrics_data.items():
                    self.metrics_history[device_id] = deque(maxlen=self.max_metrics_per_device)
                    
                    for metric_dict in metrics_list:
                        # Converter timestamp de string
                        metric_dict['timestamp'] = datetime.fromisoformat(metric_dict['timestamp'])
                        metrics = SystemMetrics(**metric_dict)
                        self.metrics_history[device_id].append(metrics)
            
            # Carregar perfis
            profiles_file = self.config_path / "device_profiles.json"
            if profiles_file.exists():
                with open(profiles_file, 'r') as f:
                    profiles_data = json.load(f)
                
                for device_id, profile_dict in profiles_data.items():
                    profile_dict['last_updated'] = datetime.fromisoformat(profile_dict['last_updated'])
                    profile = DevicePerformanceProfile(**profile_dict)
                    self.device_profiles[device_id] = profile
            
            # Carregar modelos ML
            if SKLEARN_AVAILABLE:
                models_file = self.config_path / "ml_models.pkl"
                if models_file.exists():
                    with open(models_file, 'rb') as f:
                        model_data = pickle.load(f)
                        self.ml_models = model_data['models']
                        self.scalers = model_data['scalers']
                        self.model_trained = True
            
            print("ðŸ“ Dados preditivos carregados")
            
        except Exception as e:
            print(f"âŒ Erro carregando dados: {e}")
    
    # ===== MÃ‰TODOS PÃšBLICOS =====
    
    def get_analytics_status(self) -> Dict[str, Any]:
        """ðŸ“Š STATUS DOS ANALYTICS"""
        return {
            'is_running': self.is_running,
            'devices_monitored': len(self.metrics_history),
            'total_samples': sum(len(queue) for queue in self.metrics_history.values()),
            'models_trained': self.model_trained,
            'active_alerts': len(self.active_alerts),
            'device_profiles': len(self.device_profiles),
            'ml_models': list(self.ml_models.keys()) if self.ml_models else []
        }
    
    def get_device_recommendations(self, task_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """ðŸ’¡ RECOMENDAÃ‡Ã•ES DE DISPOSITIVOS PARA TAREFAS"""
        recommendations = []
        
        for device_id, profile in self.device_profiles.items():
            # Score baseado em reliability e performance trend
            base_score = profile.reliability_score
            
            if profile.performance_trend == "improving":
                base_score *= 1.2
            elif profile.performance_trend == "degrading":
                base_score *= 0.8
            
            # Verificar se estÃ¡ em horÃ¡rio de pico
            current_hour = datetime.now().hour
            if current_hour in profile.peak_performance_hours:
                base_score *= 1.1
            
            recommendations.append({
                'device_id': device_id,
                'device_name': profile.device_name,
                'recommendation_score': min(1.0, base_score),
                'reliability': profile.reliability_score,
                'trend': profile.performance_trend,
                'peak_hours': profile.peak_performance_hours,
                'typical_cpu_range': profile.typical_cpu_range,
                'typical_memory_range': profile.typical_memory_range
            })
        
        # Ordenar por score
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return recommendations

# Para uso no jarvis_core.py:
# self.predictive_analytics = DemocraticPredictiveAnalytics(self, self.democratic_system.democratic_network)
# self.predictive_analytics.start_analytics()
