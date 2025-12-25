#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Monitor de IA
Monitora e otimiza o desempenho dos sistemas de IA em tempo real
"""

import time
import threading
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path

from ..core.logger import Logger


class AIMonitor:
    """Monitor de performance e saúde dos sistemas de IA"""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o monitor de IA"""
        self.config = config
        self.logger = Logger("AI_MONITOR", "INFO")
        
        # Métricas de performance
        self.metrics = {
            'response_times': [],
            'accuracy_scores': [],
            'memory_usage': [],
            'training_progress': 0,
            'active_models': 0,
            'total_interactions': 0,
            'successful_interactions': 0,
            'failed_interactions': 0
        }
        
        # Configurações de monitoramento
        self.monitor_config = config.get('ai', {}).get('monitor', {})
        self.check_interval = self.monitor_config.get('check_interval', 30)  # segundos
        self.max_response_time = self.monitor_config.get('max_response_time', 5.0)  # segundos
        self.min_accuracy = self.monitor_config.get('min_accuracy', 0.7)
        
        # Estado do monitor
        self.running = False
        self.monitor_thread = None
        self.last_check = time.time()
        
        # Alertas
        self.alerts = []
        self.performance_warnings = []
        
    def start_monitoring(self):
        """Inicia o monitoramento contínuo"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Monitor de IA iniciado")
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.running = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Monitor de IA parado")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.running:
            try:
                self._check_system_health()
                self._analyze_performance()
                self._check_training_progress()
                self._cleanup_old_metrics()
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no monitoramento: {e}")
                time.sleep(10)
    
    def record_interaction(self, interaction_type: str, response_time: float, 
                          success: bool, accuracy: float = None):
        """Registra uma interação para monitoramento"""
        self.metrics['total_interactions'] += 1
        
        if success:
            self.metrics['successful_interactions'] += 1
        else:
            self.metrics['failed_interactions'] += 1
        
        # Registrar tempo de resposta
        self.metrics['response_times'].append({
            'timestamp': time.time(),
            'type': interaction_type,
            'time': response_time,
            'success': success
        })
        
        # Registrar precisão se fornecida
        if accuracy is not None:
            self.metrics['accuracy_scores'].append({
                'timestamp': time.time(),
                'type': interaction_type,
                'accuracy': accuracy
            })
        
        # Verificar alertas imediatos
        if response_time > self.max_response_time:
            self._add_alert(f"Tempo de resposta alto: {response_time:.2f}s para {interaction_type}")
        
        if accuracy is not None and accuracy < self.min_accuracy:
            self._add_alert(f"Precisão baixa: {accuracy:.2f} para {interaction_type}")
    
    def _check_system_health(self):
        """Verifica a saúde geral do sistema"""
        current_time = time.time()
        
        # Verificar se há interações recentes
        recent_interactions = [
            m for m in self.metrics['response_times']
            if current_time - m['timestamp'] < 300  # últimos 5 minutos
        ]
        
        if len(recent_interactions) == 0 and self.metrics['total_interactions'] > 0:
            self._add_warning("Nenhuma interação nos últimos 5 minutos")
        
        # Verificar taxa de sucesso
        if self.metrics['total_interactions'] > 10:
            success_rate = self.metrics['successful_interactions'] / self.metrics['total_interactions']
            if success_rate < 0.8:
                self._add_warning(f"Taxa de sucesso baixa: {success_rate:.2f}")
    
    def _analyze_performance(self):
        """Analisa métricas de performance"""
        current_time = time.time()
        
        # Analisar tempos de resposta recentes
        recent_times = [
            m['time'] for m in self.metrics['response_times']
            if current_time - m['timestamp'] < 600  # últimos 10 minutos
        ]
        
        if recent_times:
            avg_response_time = sum(recent_times) / len(recent_times)
            max_response_time = max(recent_times)
            
            if avg_response_time > self.max_response_time * 0.8:
                self._add_warning(f"Tempo médio de resposta alto: {avg_response_time:.2f}s")
            
            if max_response_time > self.max_response_time * 2:
                self._add_alert(f"Tempo máximo de resposta muito alto: {max_response_time:.2f}s")
        
        # Analisar precisão recente
        recent_accuracy = [
            m['accuracy'] for m in self.metrics['accuracy_scores']
            if current_time - m['timestamp'] < 600  # últimos 10 minutos
        ]
        
        if recent_accuracy:
            avg_accuracy = sum(recent_accuracy) / len(recent_accuracy)
            
            if avg_accuracy < self.min_accuracy:
                self._add_warning(f"Precisão média baixa: {avg_accuracy:.2f}")
    
    def _check_training_progress(self):
        """Verifica progresso do treinamento"""
        # Verificar se há dados de treinamento sendo gerados
        data_dir = Path("data/training")
        
        if data_dir.exists():
            # Contar arquivos de dados recentes
            recent_files = 0
            cutoff_time = time.time() - 3600  # última hora
            
            for file_path in data_dir.rglob("*.json"):
                if file_path.stat().st_mtime > cutoff_time:
                    recent_files += 1
            
            if recent_files == 0 and self.metrics['total_interactions'] > 50:
                self._add_warning("Nenhum dado de treinamento gerado na última hora")
    
    def _cleanup_old_metrics(self):
        """Remove métricas antigas para economizar memória"""
        current_time = time.time()
        cutoff_time = current_time - 3600  # manter apenas última hora
        
        # Limpar tempos de resposta antigos
        self.metrics['response_times'] = [
            m for m in self.metrics['response_times']
            if m['timestamp'] > cutoff_time
        ]
        
        # Limpar scores de precisão antigos
        self.metrics['accuracy_scores'] = [
            m for m in self.metrics['accuracy_scores']
            if m['timestamp'] > cutoff_time
        ]
        
        # Limpar alertas antigos
        self.alerts = [
            alert for alert in self.alerts
            if current_time - alert['timestamp'] < 1800  # manter por 30 minutos
        ]
        
        # Limpar warnings antigos
        self.performance_warnings = [
            warning for warning in self.performance_warnings
            if current_time - warning['timestamp'] < 3600  # manter por 1 hora
        ]
    
    def _add_alert(self, message: str):
        """Adiciona um alerta crítico"""
        alert = {
            'timestamp': time.time(),
            'message': message,
            'level': 'ALERT'
        }
        
        self.alerts.append(alert)
        self.logger.warning(f"ALERTA: {message}")
        
        # Limitar número de alertas
        if len(self.alerts) > 50:
            self.alerts = self.alerts[-50:]
    
    def _add_warning(self, message: str):
        """Adiciona um aviso de performance"""
        warning = {
            'timestamp': time.time(),
            'message': message,
            'level': 'WARNING'
        }
        
        self.performance_warnings.append(warning)
        self.logger.info(f"AVISO: {message}")
        
        # Limitar número de warnings
        if len(self.performance_warnings) > 100:
            self.performance_warnings = self.performance_warnings[-100:]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Gera relatório de performance"""
        current_time = time.time()
        
        # Calcular métricas recentes
        recent_times = [
            m['time'] for m in self.metrics['response_times']
            if current_time - m['timestamp'] < 600
        ]
        
        recent_accuracy = [
            m['accuracy'] for m in self.metrics['accuracy_scores']
            if current_time - m['timestamp'] < 600
        ]
        
        # Calcular taxa de sucesso
        success_rate = 0
        if self.metrics['total_interactions'] > 0:
            success_rate = self.metrics['successful_interactions'] / self.metrics['total_interactions']
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_interactions': self.metrics['total_interactions'],
            'success_rate': success_rate,
            'recent_response_times': {
                'count': len(recent_times),
                'average': sum(recent_times) / len(recent_times) if recent_times else 0,
                'max': max(recent_times) if recent_times else 0,
                'min': min(recent_times) if recent_times else 0
            },
            'recent_accuracy': {
                'count': len(recent_accuracy),
                'average': sum(recent_accuracy) / len(recent_accuracy) if recent_accuracy else 0,
                'max': max(recent_accuracy) if recent_accuracy else 0,
                'min': min(recent_accuracy) if recent_accuracy else 0
            },
            'active_alerts': len(self.alerts),
            'active_warnings': len(self.performance_warnings),
            'system_health': self._calculate_health_score()
        }
        
        return report
    
    def _calculate_health_score(self) -> float:
        """Calcula score de saúde do sistema (0-1)"""
        score = 1.0
        
        # Penalizar por alertas
        score -= len(self.alerts) * 0.1
        
        # Penalizar por warnings
        score -= len(self.performance_warnings) * 0.05
        
        # Penalizar por baixa taxa de sucesso
        if self.metrics['total_interactions'] > 10:
            success_rate = self.metrics['successful_interactions'] / self.metrics['total_interactions']
            if success_rate < 0.9:
                score -= (0.9 - success_rate)
        
        # Garantir que o score não seja negativo
        return max(0.0, score)
    
    def get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Retorna alertas recentes"""
        return self.alerts.copy()
    
    def get_recent_warnings(self) -> List[Dict[str, Any]]:
        """Retorna warnings recentes"""
        return self.performance_warnings.copy()
    
    def reset_metrics(self):
        """Reinicia todas as métricas"""
        self.metrics = {
            'response_times': [],
            'accuracy_scores': [],
            'memory_usage': [],
            'training_progress': 0,
            'active_models': 0,
            'total_interactions': 0,
            'successful_interactions': 0,
            'failed_interactions': 0
        }
        
        self.alerts.clear()
        self.performance_warnings.clear()
        
        self.logger.info("Métricas de IA reiniciadas")
