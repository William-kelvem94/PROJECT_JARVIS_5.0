"""
Motor de Decisão Inteligente
Sistema de tomada de decisões baseado em contexto e aprendizado
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import random
from ..core.logger import default_logger


class Priority(Enum):
    """Níveis de prioridade para ações"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class DecisionEngine:
    """Motor de decisão inteligente do JARVIS"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        
        # Base de conhecimento para decisões
        self.knowledge_base = {
            'user_preferences': {},
            'learned_patterns': {},
            'context_rules': {},
            'safety_rules': {},
            'performance_metrics': {}
        }
        
        # Regras de segurança críticas
        self.safety_rules = {
            'system_shutdown': {
                'requires_confirmation': True,
                'admin_required': True,
                'cooldown_seconds': 30
            },
            'file_deletion': {
                'requires_confirmation': True,
                'backup_first': True,
                'restricted_paths': [
                    'C:\\Windows\\System32',
                    'C:\\Program Files',
                    'C:\\Users\\*\\AppData\\Roaming\\Microsoft'
                ]
            },
            'registry_modification': {
                'requires_confirmation': True,
                'admin_required': True,
                'backup_first': True
            },
            'network_access': {
                'trusted_domains_only': True,
                'ssl_required': True,
                'rate_limit': 10  # requests per minute
            }
        }
        
        # Contexto atual
        self.current_context = {
            'user_activity': 'active',
            'system_load': 'normal',
            'time_of_day': 'day',
            'last_commands': [],
            'active_applications': [],
            'current_focus': None
        }
        
        # Histórico de decisões
        self.decision_history = []
        
        # Métricas de performance
        self.performance_metrics = {
            'total_decisions': 0,
            'successful_decisions': 0,
            'failed_decisions': 0,
            'average_decision_time': 0.0,
            'user_satisfaction_score': 0.0
        }
        
        self.logger.info("Decision Engine inicializado")
    
    def make_decision(self, action_plan: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Toma decisão sobre um plano de ação
        
        Args:
            action_plan: Lista de ações propostas
            context: Contexto atual da situação
            
        Returns:
            Decisão final com ações aprovadas/modificadas
        """
        start_time = time.time()
        
        try:
            # Atualizar contexto atual
            self._update_context(context)
            
            # Analisar cada ação
            approved_actions = []
            rejected_actions = []
            modified_actions = []
            
            for action in action_plan:
                decision = self._evaluate_action(action, context)
                
                if decision['approved']:
                    if decision.get('modified'):
                        modified_actions.append(decision['action'])
                    else:
                        approved_actions.append(action)
                else:
                    rejected_actions.append({
                        'action': action,
                        'reason': decision['reason']
                    })
            
            # Priorizar ações aprovadas
            prioritized_actions = self._prioritize_actions(approved_actions + modified_actions)
            
            # Verificar conflitos
            final_actions = self._resolve_conflicts(prioritized_actions)
            
            # Gerar decisão final
            decision_result = {
                'approved_actions': final_actions,
                'rejected_actions': rejected_actions,
                'total_actions': len(action_plan),
                'approved_count': len(final_actions),
                'rejected_count': len(rejected_actions),
                'decision_time': time.time() - start_time,
                'confidence': self._calculate_confidence(final_actions, context),
                'safety_score': self._calculate_safety_score(final_actions),
                'execution_order': self._determine_execution_order(final_actions)
            }
            
            # Registrar decisão
            self._record_decision(decision_result, context)
            
            # Atualizar métricas
            self._update_metrics(decision_result)
            
            self.logger.info(f"Decisão tomada: {len(final_actions)} ações aprovadas de {len(action_plan)}")
            
            return decision_result
            
        except Exception as e:
            self.logger.error(f"Erro no motor de decisão: {e}")
            return {
                'approved_actions': [],
                'rejected_actions': [{'action': action, 'reason': f'Erro interno: {e}'} for action in action_plan],
                'error': str(e),
                'decision_time': time.time() - start_time
            }
    
    def _evaluate_action(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia uma ação individual"""
        action_type = action.get('type', 'unknown')
        
        # Verificar regras de segurança
        safety_check = self._check_safety_rules(action)
        if not safety_check['safe']:
            return {
                'approved': False,
                'reason': f"Violação de segurança: {safety_check['reason']}"
            }
        
        # Verificar permissões
        permission_check = self._check_permissions(action)
        if not permission_check['allowed']:
            return {
                'approved': False,
                'reason': f"Permissão negada: {permission_check['reason']}"
            }
        
        # Verificar contexto
        context_check = self._check_context_appropriateness(action, context)
        if not context_check['appropriate']:
            # Tentar modificar ação para contexto atual
            modified_action = self._adapt_action_to_context(action, context)
            if modified_action:
                return {
                    'approved': True,
                    'modified': True,
                    'action': modified_action,
                    'reason': 'Ação adaptada ao contexto atual'
                }
            else:
                return {
                    'approved': False,
                    'reason': f"Inadequado para contexto atual: {context_check['reason']}"
                }
        
        # Verificar recursos do sistema
        resource_check = self._check_system_resources(action)
        if not resource_check['available']:
            return {
                'approved': False,
                'reason': f"Recursos insuficientes: {resource_check['reason']}"
            }
        
        # Verificar preferências do usuário
        preference_check = self._check_user_preferences(action)
        if not preference_check['matches']:
            # Sugerir alternativa baseada em preferências
            alternative = self._suggest_alternative(action)
            if alternative:
                return {
                    'approved': True,
                    'modified': True,
                    'action': alternative,
                    'reason': 'Adaptado às preferências do usuário'
                }
        
        # Ação aprovada
        return {
            'approved': True,
            'confidence': self._calculate_action_confidence(action, context)
        }
    
    def _check_safety_rules(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica regras de segurança"""
        action_type = action.get('type', '')
        
        # Verificar ações críticas do sistema
        if action_type == 'system_command':
            command = action.get('action', '').lower()
            
            if any(dangerous in command for dangerous in ['shutdown', 'restart', 'format', 'delete']):
                rule = self.safety_rules.get('system_shutdown', {})
                if rule.get('requires_confirmation', True):
                    return {
                        'safe': False,
                        'reason': 'Ação crítica requer confirmação do usuário'
                    }
        
        # Verificar operações de arquivo
        elif action_type == 'file_operation':
            operation = action.get('operation', '').lower()
            file_path = action.get('file_path', '')
            
            if 'delet' in operation:
                rule = self.safety_rules.get('file_deletion', {})
                restricted_paths = rule.get('restricted_paths', [])
                
                for restricted in restricted_paths:
                    if restricted.replace('*', '') in file_path:
                        return {
                            'safe': False,
                            'reason': f'Caminho restrito: {file_path}'
                        }
        
        # Verificar acesso à rede
        elif action_type == 'web_action':
            url = action.get('url', '')
            rule = self.safety_rules.get('network_access', {})
            
            if rule.get('ssl_required', True) and not url.startswith('https://'):
                return {
                    'safe': False,
                    'reason': 'SSL obrigatório para acesso web'
                }
        
        return {'safe': True}
    
    def _check_permissions(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica permissões necessárias"""
        action_type = action.get('type', '')
        
        # Ações que requerem privilégios administrativos
        admin_required_actions = [
            'system_shutdown', 'system_restart', 'registry_modification',
            'service_control', 'driver_installation'
        ]
        
        if action_type in admin_required_actions:
            # Verificar se tem privilégios admin (simulado)
            has_admin = self.config.get('system', {}).get('admin_privileges', False)
            
            if not has_admin:
                return {
                    'allowed': False,
                    'reason': 'Privilégios administrativos necessários'
                }
        
        return {'allowed': True}
    
    def _check_context_appropriateness(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica se a ação é apropriada para o contexto atual"""
        action_type = action.get('type', '')
        
        # Verificar horário
        current_hour = datetime.now().hour
        
        # Ações ruidosas durante horário de silêncio
        if 22 <= current_hour or current_hour <= 6:  # 22h às 6h
            noisy_actions = ['audio_playback', 'system_notification', 'voice_synthesis']
            if action_type in noisy_actions:
                return {
                    'appropriate': False,
                    'reason': 'Horário de silêncio (22h-6h)'
                }
        
        # Verificar carga do sistema
        system_load = context.get('system_load', 'normal')
        if system_load == 'high':
            resource_intensive = ['video_processing', 'large_file_operation', 'system_scan']
            if action_type in resource_intensive:
                return {
                    'appropriate': False,
                    'reason': 'Sistema com alta carga'
                }
        
        # Verificar atividade do usuário
        user_activity = context.get('user_activity', 'active')
        if user_activity == 'away':
            interactive_actions = ['user_input_required', 'confirmation_dialog']
            if action_type in interactive_actions:
                return {
                    'appropriate': False,
                    'reason': 'Usuário ausente'
                }
        
        return {'appropriate': True}
    
    def _check_system_resources(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica disponibilidade de recursos do sistema"""
        # Simulação de verificação de recursos
        # Em implementação real, usaria psutil para verificar CPU, memória, disco
        
        action_type = action.get('type', '')
        
        # Ações que consomem muitos recursos
        resource_intensive = {
            'video_processing': {'cpu': 80, 'memory': 70},
            'large_file_operation': {'disk': 90, 'memory': 50},
            'system_scan': {'cpu': 60, 'disk': 80},
            'ai_processing': {'cpu': 70, 'memory': 80}
        }
        
        if action_type in resource_intensive:
            requirements = resource_intensive[action_type]
            
            # Simular verificação (em implementação real, usar psutil)
            current_usage = {
                'cpu': random.randint(20, 90),
                'memory': random.randint(30, 85),
                'disk': random.randint(10, 70)
            }
            
            for resource, required in requirements.items():
                if current_usage.get(resource, 0) + required > 95:
                    return {
                        'available': False,
                        'reason': f'{resource.upper()} insuficiente ({current_usage[resource]}% + {required}% > 95%)'
                    }
        
        return {'available': True}
    
    def _check_user_preferences(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica preferências do usuário"""
        user_prefs = self.knowledge_base.get('user_preferences', {})
        action_type = action.get('type', '')
        
        # Verificar preferências específicas
        if action_type in user_prefs:
            prefs = user_prefs[action_type]
            
            # Verificar se ação conflita com preferências
            if prefs.get('disabled', False):
                return {
                    'matches': False,
                    'reason': 'Tipo de ação desabilitado pelo usuário'
                }
            
            # Verificar configurações específicas
            preferred_method = prefs.get('preferred_method')
            if preferred_method and action.get('method') != preferred_method:
                return {
                    'matches': False,
                    'reason': f'Método preferido: {preferred_method}'
                }
        
        return {'matches': True}
    
    def _adapt_action_to_context(self, action: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Adapta ação ao contexto atual"""
        action_type = action.get('type', '')
        
        # Adaptar ações ruidosas para horário silencioso
        current_hour = datetime.now().hour
        if 22 <= current_hour or current_hour <= 6:
            if action_type == 'audio_playback':
                modified = action.copy()
                modified['volume'] = min(action.get('volume', 50), 20)  # Volume baixo
                return modified
            
            elif action_type == 'voice_synthesis':
                modified = action.copy()
                modified['method'] = 'text_display'  # Mostrar texto em vez de falar
                return modified
        
        # Adaptar para sistema com alta carga
        system_load = context.get('system_load', 'normal')
        if system_load == 'high':
            if action_type == 'video_processing':
                modified = action.copy()
                modified['quality'] = 'low'  # Reduzir qualidade
                modified['priority'] = 'background'  # Executar em background
                return modified
        
        return None
    
    def _suggest_alternative(self, action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sugere alternativa baseada em preferências"""
        user_prefs = self.knowledge_base.get('user_preferences', {})
        action_type = action.get('type', '')
        
        if action_type in user_prefs:
            prefs = user_prefs[action_type]
            preferred_method = prefs.get('preferred_method')
            
            if preferred_method:
                alternative = action.copy()
                alternative['method'] = preferred_method
                return alternative
        
        return None
    
    def _prioritize_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioriza ações por importância"""
        def get_priority_value(action):
            priority = action.get('priority', 'medium')
            priority_map = {
                'critical': 1,
                'high': 2,
                'medium': 3,
                'low': 4,
                'background': 5
            }
            return priority_map.get(priority, 3)
        
        return sorted(actions, key=get_priority_value)
    
    def _resolve_conflicts(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve conflitos entre ações"""
        resolved_actions = []
        conflicting_types = set()
        
        # Definir tipos conflitantes
        conflicts = {
            'audio_playback': ['voice_synthesis', 'system_notification'],
            'system_shutdown': ['file_operation', 'web_action'],
            'full_screen_app': ['window_management', 'desktop_interaction']
        }
        
        for action in actions:
            action_type = action.get('type', '')
            
            # Verificar se conflita com ações já aprovadas
            has_conflict = False
            for conflicting_type in conflicting_types:
                if action_type in conflicts.get(conflicting_type, []):
                    has_conflict = True
                    break
            
            if not has_conflict:
                resolved_actions.append(action)
                conflicting_types.add(action_type)
        
        return resolved_actions
    
    def _determine_execution_order(self, actions: List[Dict[str, Any]]) -> List[int]:
        """Determina ordem de execução das ações"""
        # Ordenar por prioridade e dependências
        execution_order = []
        
        # Primeiro: ações críticas e de alta prioridade
        for i, action in enumerate(actions):
            priority = action.get('priority', 'medium')
            if priority in ['critical', 'high']:
                execution_order.append(i)
        
        # Segundo: ações de média prioridade
        for i, action in enumerate(actions):
            priority = action.get('priority', 'medium')
            if priority == 'medium' and i not in execution_order:
                execution_order.append(i)
        
        # Terceiro: ações de baixa prioridade e background
        for i, action in enumerate(actions):
            if i not in execution_order:
                execution_order.append(i)
        
        return execution_order
    
    def _calculate_confidence(self, actions: List[Dict[str, Any]], context: Dict[str, Any]) -> float:
        """Calcula confiança na decisão"""
        if not actions:
            return 0.0
        
        total_confidence = 0.0
        
        for action in actions:
            action_confidence = self._calculate_action_confidence(action, context)
            total_confidence += action_confidence
        
        return min(total_confidence / len(actions), 1.0)
    
    def _calculate_action_confidence(self, action: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calcula confiança em uma ação específica"""
        confidence = 0.5  # Base
        
        # Aumentar confiança baseado em fatores
        action_type = action.get('type', '')
        
        # Ações bem conhecidas
        if action_type in ['system_command', 'file_operation']:
            confidence += 0.2
        
        # Contexto apropriado
        if self._check_context_appropriateness(action, context)['appropriate']:
            confidence += 0.2
        
        # Recursos disponíveis
        if self._check_system_resources(action)['available']:
            confidence += 0.1
        
        # Histórico de sucesso
        success_rate = self._get_action_success_rate(action_type)
        confidence += success_rate * 0.2
        
        return min(confidence, 1.0)
    
    def _calculate_safety_score(self, actions: List[Dict[str, Any]]) -> float:
        """Calcula pontuação de segurança"""
        if not actions:
            return 1.0
        
        total_safety = 0.0
        
        for action in actions:
            safety_check = self._check_safety_rules(action)
            action_safety = 1.0 if safety_check['safe'] else 0.0
            total_safety += action_safety
        
        return total_safety / len(actions)
    
    def _get_action_success_rate(self, action_type: str) -> float:
        """Obtém taxa de sucesso histórica para tipo de ação"""
        metrics = self.performance_metrics.get(action_type, {})
        total = metrics.get('total_attempts', 0)
        successful = metrics.get('successful_attempts', 0)
        
        if total == 0:
            return 0.5  # Neutro para ações sem histórico
        
        return successful / total
    
    def _record_decision(self, decision: Dict[str, Any], context: Dict[str, Any]):
        """Registra decisão no histórico"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'decision': decision,
            'context': context,
            'performance': {
                'decision_time': decision['decision_time'],
                'confidence': decision['confidence'],
                'safety_score': decision['safety_score']
            }
        }
        
        self.decision_history.append(record)
        
        # Manter apenas últimas 100 decisões
        if len(self.decision_history) > 100:
            self.decision_history = self.decision_history[-100:]
    
    def _update_context(self, new_context: Dict[str, Any]):
        """Atualiza contexto atual"""
        self.current_context.update(new_context)
        
        # Atualizar horário do dia
        current_hour = datetime.now().hour
        if 6 <= current_hour < 12:
            self.current_context['time_of_day'] = 'morning'
        elif 12 <= current_hour < 18:
            self.current_context['time_of_day'] = 'afternoon'
        elif 18 <= current_hour < 22:
            self.current_context['time_of_day'] = 'evening'
        else:
            self.current_context['time_of_day'] = 'night'
    
    def _update_metrics(self, decision: Dict[str, Any]):
        """Atualiza métricas de performance"""
        self.performance_metrics['total_decisions'] += 1
        self.performance_metrics['average_decision_time'] = (
            (self.performance_metrics['average_decision_time'] * 
             (self.performance_metrics['total_decisions'] - 1) + 
             decision['decision_time']) / 
            self.performance_metrics['total_decisions']
        )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Retorna relatório de performance"""
        return {
            'total_decisions': self.performance_metrics['total_decisions'],
            'average_decision_time': self.performance_metrics['average_decision_time'],
            'recent_decisions': len([
                d for d in self.decision_history 
                if datetime.fromisoformat(d['timestamp']) > datetime.now() - timedelta(hours=24)
            ]),
            'safety_compliance': sum(
                d['decision']['safety_score'] for d in self.decision_history[-10:]
            ) / min(len(self.decision_history), 10) if self.decision_history else 1.0,
            'average_confidence': sum(
                d['decision']['confidence'] for d in self.decision_history[-10:]
            ) / min(len(self.decision_history), 10) if self.decision_history else 0.0
        }
