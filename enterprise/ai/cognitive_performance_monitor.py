"""
Cognitive Performance Monitor - Monitoramento Avançado de Performance Cognitiva
Detecção de degradação e alertas proativos
"""

import time
from typing import Dict, List, Optional
from collections import deque
from datetime import datetime
from enum import Enum
from core.logger import logger

class AnomalyDetector:
    """Detector de anomalias para métricas específicas."""
    
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.values = deque(maxlen=window_size)
        self.mean = 0.0
        self.std = 0.0
    
    async def detect(self, value: float) -> bool:
        """
        Detecta se valor é anomalia.
        
        Returns:
            True se é anomalia
        """
        if len(self.values) < 10:
            # Insuficiente para detectar
            self.values.append(value)
            self._update_stats()
            return False
        
        self.values.append(value)
        self._update_stats()
        
        # Detectar usando Z-score
        if self.std > 0:
            z_score = abs(value - self.mean) / self.std
            # Anomalia se Z-score > 2.5
            return z_score > 2.5
        
        return False
    
    def _update_stats(self):
        """Atualiza estatísticas."""
        if len(self.values) < 2:
            return
        
        values_list = list(self.values)
        self.mean = sum(values_list) / len(values_list)
        
        variance = sum((x - self.mean) ** 2 for x in values_list) / len(values_list)
        self.std = variance ** 0.5

class CognitivePerformanceMonitor:
    """
    Monitoramento avançado de performance cognitiva.
    Detecção de degradação e alertas proativos.
    """
    
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)
        self.anomaly_detectors: Dict[str, AnomalyDetector] = {}
        self.degradation_alerts = []
        self.performance_baselines: Dict[str, float] = {}
        
        logger.info("Cognitive Performance Monitor inicializado")
    
    async def track_cognitive_metrics(self, cognitive_session: Dict):
        """
        Rastreia métricas de performance cognitiva.
        
        Args:
            cognitive_session: Dados da sessão cognitiva
        """
        try:
            metrics = {
                'timestamp': time.time(),
                'response_time': cognitive_session.get('response_time'),
                'confidence_score': cognitive_session.get('confidence'),
                'user_feedback': cognitive_session.get('user_feedback'),
                'model_accuracy': await self._calculate_accuracy(cognitive_session),
                'knowledge_coverage': await self._assess_knowledge_coverage(cognitive_session),
                'contextual_relevance': await self._measure_contextual_relevance(cognitive_session)
            }
            
            self.metrics_history.append(metrics)
            
            # Verificar anomalias
            await self._check_for_anomalies(metrics)
            
            # Verificar degradação
            await self._check_performance_degradation()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro rastreando métricas: {e}")
            return {}
    
    async def _calculate_accuracy(self, session: Dict) -> float:
        """Calcula acurácia baseada em feedback e confiança."""
        confidence = session.get('confidence', 0.5)
        feedback = session.get('user_feedback', {})
        
        # Score de feedback (se disponível)
        feedback_score = feedback.get('rating', 0.5) if isinstance(feedback, dict) else 0.5
        
        # Acurácia como média ponderada
        accuracy = confidence * 0.7 + feedback_score * 0.3
        
        return accuracy
    
    async def _assess_knowledge_coverage(self, session: Dict) -> float:
        """Avalia cobertura de conhecimento."""
        context_used = session.get('context_used', {})
        knowledge_items = context_used.get('knowledge_items', 0)
        
        # Score baseado em número de itens de conhecimento usados
        coverage = min(1.0, knowledge_items / 5.0)  # Normalizar para 5 itens
        
        return coverage
    
    async def _measure_contextual_relevance(self, session: Dict) -> float:
        """Mede relevância contextual."""
        quality_metrics = session.get('quality_metrics', {})
        relevance = quality_metrics.get('relevance', 0.5)
        
        return relevance
    
    async def _check_for_anomalies(self, metrics: Dict):
        """Detecta anomalias no desempenho cognitivo."""
        # Métricas a verificar
        check_metrics = [
            'response_time',
            'confidence_score',
            'model_accuracy',
            'contextual_relevance'
        ]
        
        for metric_name in check_metrics:
            value = metrics.get(metric_name)
            
            if value is None:
                continue
            
            # Criar detector se não existir
            if metric_name not in self.anomaly_detectors:
                self.anomaly_detectors[metric_name] = AnomalyDetector()
            
            # Detectar anomalia
            is_anomaly = await self.anomaly_detectors[metric_name].detect(value)
            
            if is_anomaly:
                await self._trigger_anomaly_alert(metric_name, value)
    
    async def _trigger_anomaly_alert(self, metric_name: str, value: float):
        """Dispara alerta de anomalia."""
        alert = {
            'type': 'anomaly',
            'metric': metric_name,
            'value': value,
            'timestamp': datetime.now(),
            'severity': 'medium'
        }
        
        self.degradation_alerts.append(alert)
        logger.warning(f"Anomalia detectada em {metric_name}: {value}")
    
    async def _check_performance_degradation(self):
        """Verifica degradação gradual de performance."""
        recent_metrics = list(self.metrics_history)[-50:]  # Últimas 50 medições
        
        if len(recent_metrics) < 30:
            return
        
        # Métricas críticas
        critical_metrics = {
            'response_time': 'increasing',  # Aumentar é ruim
            'model_accuracy': 'decreasing',  # Diminuir é ruim
            'contextual_relevance': 'decreasing'  # Diminuir é ruim
        }
        
        for metric, bad_trend in critical_metrics.items():
            values = [
                m[metric]
                for m in recent_metrics
                if m.get(metric) is not None
            ]
            
            if len(values) < 20:
                continue
            
            # Análise de tendência simples
            trend = await self._analyze_trend(values)
            
            if trend == bad_trend:
                await self._trigger_degradation_alert(metric, trend)
    
    async def _analyze_trend(self, values: List[float]) -> str:
        """
        Analisa tendência de valores.
        
        Returns:
            'increasing', 'decreasing', ou 'stable'
        """
        if len(values) < 2:
            return 'stable'
        
        # Dividir em duas metades
        mid = len(values) // 2
        first_half = values[:mid]
        second_half = values[mid:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        # Threshold de 5% para considerar mudança
        change = abs(second_avg - first_avg) / first_avg if first_avg > 0 else 0
        
        if change < 0.05:
            return 'stable'
        elif second_avg > first_avg:
            return 'increasing'
        else:
            return 'decreasing'
    
    async def _trigger_degradation_alert(self, metric: str, trend: str):
        """Dispara alerta de degradação."""
        alert = {
            'type': 'degradation',
            'metric': metric,
            'trend': trend,
            'timestamp': datetime.now(),
            'severity': 'high'
        }
        
        self.degradation_alerts.append(alert)
        logger.error(f"Degradação detectada em {metric}: tendência {trend}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance."""
        if not self.metrics_history:
            return {
                'total_sessions': 0,
                'avg_metrics': {},
                'alerts': []
            }
        
        recent = list(self.metrics_history)[-100:]  # Últimas 100
        
        # Calcular médias
        avg_metrics = {}
        metric_names = ['response_time', 'confidence_score', 'model_accuracy', 'contextual_relevance']
        
        for metric in metric_names:
            values = [m[metric] for m in recent if m.get(metric) is not None]
            if values:
                avg_metrics[metric] = sum(values) / len(values)
        
        return {
            'total_sessions': len(self.metrics_history),
            'recent_sessions': len(recent),
            'avg_metrics': avg_metrics,
            'alerts_count': len(self.degradation_alerts),
            'recent_alerts': self.degradation_alerts[-10:]
        }

