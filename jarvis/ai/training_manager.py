#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Gerenciador de Treinamento de IA
Coordena o treinamento e aprendizado contínuo de todos os modelos de IA
"""

import os
import json
import pickle
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..core.logger import Logger


class TrainingManager:
    """Gerenciador central de treinamento de IA"""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o gerenciador de treinamento"""
        self.config = config
        self.logger = Logger("TRAINING_MANAGER", "INFO")
        
        # Diretórios de dados
        self.data_dir = Path("data")
        self.models_dir = Path("models")
        self.training_data_dir = self.data_dir / "training"
        
        # Criar diretórios se não existirem
        self._create_directories()
        
        # Dados de treinamento
        self.training_data = {
            'voice_commands': [],
            'conversations': [],
            'user_preferences': {},
            'system_interactions': [],
            'feedback_data': []
        }
        
        # Configurações de treinamento
        self.training_config = config.get('ai', {}).get('training', {})
        self.auto_save_interval = self.training_config.get('auto_save_interval', 100)
        self.max_training_samples = self.training_config.get('max_samples', 10000)
        
        # Contadores
        self.interaction_count = 0
        self.last_save_count = 0
        
        # Carregar dados existentes
        self._load_existing_data()
    
    def _create_directories(self):
        """Cria diretórios necessários"""
        directories = [
            self.data_dir,
            self.models_dir,
            self.training_data_dir,
            self.training_data_dir / "voice",
            self.training_data_dir / "conversation",
            self.training_data_dir / "preferences",
            self.training_data_dir / "feedback"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Diretórios de treinamento criados")
    
    def _load_existing_data(self):
        """Carrega dados de treinamento existentes"""
        try:
            # Carregar dados de comandos de voz
            voice_file = self.training_data_dir / "voice" / "commands.json"
            if voice_file.exists():
                with open(voice_file, 'r', encoding='utf-8') as f:
                    self.training_data['voice_commands'] = json.load(f)
            
            # Carregar dados de conversação
            conv_file = self.training_data_dir / "conversation" / "dialogues.json"
            if conv_file.exists():
                with open(conv_file, 'r', encoding='utf-8') as f:
                    self.training_data['conversations'] = json.load(f)
            
            # Carregar preferências do usuário
            pref_file = self.training_data_dir / "preferences" / "user_prefs.json"
            if pref_file.exists():
                with open(pref_file, 'r', encoding='utf-8') as f:
                    self.training_data['user_preferences'] = json.load(f)
            
            # Carregar dados de feedback
            feedback_file = self.training_data_dir / "feedback" / "feedback.json"
            if feedback_file.exists():
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    self.training_data['feedback_data'] = json.load(f)
            
            total_samples = sum(len(data) if isinstance(data, list) else len(data.keys()) 
                              for data in self.training_data.values())
            
            self.logger.info(f"Dados de treinamento carregados: {total_samples} amostras")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados existentes: {e}")
    
    def record_voice_interaction(self, command: str, response: str, success: bool = True):
        """Registra interação de voz para treinamento"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'response': response,
            'success': success,
            'command_length': len(command.split()),
            'response_length': len(response.split())
        }
        
        self.training_data['voice_commands'].append(interaction)
        self.interaction_count += 1
        
        # Limitar número de amostras
        if len(self.training_data['voice_commands']) > self.max_training_samples:
            self.training_data['voice_commands'] = self.training_data['voice_commands'][-self.max_training_samples:]
        
        self._auto_save_check()
        self.logger.debug(f"Interação de voz registrada: {command[:50]}...")
    
    def record_conversation(self, user_input: str, ai_response: str, context: Dict[str, Any] = None):
        """Registra conversação para treinamento"""
        conversation = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'ai_response': ai_response,
            'context': context or {},
            'input_sentiment': self._analyze_sentiment(user_input),
            'response_sentiment': self._analyze_sentiment(ai_response)
        }
        
        self.training_data['conversations'].append(conversation)
        self.interaction_count += 1
        
        # Limitar número de amostras
        if len(self.training_data['conversations']) > self.max_training_samples:
            self.training_data['conversations'] = self.training_data['conversations'][-self.max_training_samples:]
        
        self._auto_save_check()
        self.logger.debug(f"Conversação registrada: {user_input[:50]}...")
    
    def record_user_preference(self, category: str, preference: str, value: Any):
        """Registra preferência do usuário"""
        if category not in self.training_data['user_preferences']:
            self.training_data['user_preferences'][category] = {}
        
        self.training_data['user_preferences'][category][preference] = {
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'frequency': self.training_data['user_preferences'][category].get(preference, {}).get('frequency', 0) + 1
        }
        
        self.interaction_count += 1
        self._auto_save_check()
        self.logger.debug(f"Preferência registrada: {category}.{preference} = {value}")
    
    def record_feedback(self, interaction_id: str, feedback_type: str, rating: float, comments: str = ""):
        """Registra feedback do usuário"""
        feedback = {
            'timestamp': datetime.now().isoformat(),
            'interaction_id': interaction_id,
            'type': feedback_type,
            'rating': rating,
            'comments': comments
        }
        
        self.training_data['feedback_data'].append(feedback)
        self.interaction_count += 1
        
        # Limitar número de amostras
        if len(self.training_data['feedback_data']) > self.max_training_samples:
            self.training_data['feedback_data'] = self.training_data['feedback_data'][-self.max_training_samples:]
        
        self._auto_save_check()
        self.logger.debug(f"Feedback registrado: {feedback_type} - {rating}")
    
    def _analyze_sentiment(self, text: str) -> str:
        """Análise básica de sentimento (implementação simplificada)"""
        # Esta é uma implementação básica
        # Em produção, usaríamos bibliotecas especializadas
        
        positive_words = ['bom', 'ótimo', 'excelente', 'perfeito', 'legal', 'obrigado', 'parabéns']
        negative_words = ['ruim', 'péssimo', 'erro', 'problema', 'falha', 'não funciona']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _auto_save_check(self):
        """Verifica se deve salvar automaticamente"""
        if self.interaction_count - self.last_save_count >= self.auto_save_interval:
            self.save_training_data()
            self.last_save_count = self.interaction_count
    
    def save_training_data(self):
        """Salva todos os dados de treinamento"""
        try:
            # Salvar comandos de voz
            voice_file = self.training_data_dir / "voice" / "commands.json"
            with open(voice_file, 'w', encoding='utf-8') as f:
                json.dump(self.training_data['voice_commands'], f, indent=2, ensure_ascii=False)
            
            # Salvar conversações
            conv_file = self.training_data_dir / "conversation" / "dialogues.json"
            with open(conv_file, 'w', encoding='utf-8') as f:
                json.dump(self.training_data['conversations'], f, indent=2, ensure_ascii=False)
            
            # Salvar preferências
            pref_file = self.training_data_dir / "preferences" / "user_prefs.json"
            with open(pref_file, 'w', encoding='utf-8') as f:
                json.dump(self.training_data['user_preferences'], f, indent=2, ensure_ascii=False)
            
            # Salvar feedback
            feedback_file = self.training_data_dir / "feedback" / "feedback.json"
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(self.training_data['feedback_data'], f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Dados de treinamento salvos ({self.interaction_count} interações)")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar dados de treinamento: {e}")
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos dados de treinamento"""
        return {
            'total_interactions': self.interaction_count,
            'voice_commands': len(self.training_data['voice_commands']),
            'conversations': len(self.training_data['conversations']),
            'user_preferences': len(self.training_data['user_preferences']),
            'feedback_entries': len(self.training_data['feedback_data']),
            'last_save_count': self.last_save_count,
            'auto_save_interval': self.auto_save_interval
        }
    
    def prepare_training_dataset(self, data_type: str) -> Optional[Dict[str, Any]]:
        """Prepara dataset para treinamento de modelo específico"""
        if data_type == 'voice_commands':
            return self._prepare_voice_dataset()
        elif data_type == 'conversations':
            return self._prepare_conversation_dataset()
        elif data_type == 'preferences':
            return self._prepare_preference_dataset()
        else:
            self.logger.error(f"Tipo de dataset desconhecido: {data_type}")
            return None
    
    def _prepare_voice_dataset(self) -> Dict[str, Any]:
        """Prepara dataset de comandos de voz"""
        commands = self.training_data['voice_commands']
        
        if not commands:
            return {'features': [], 'labels': [], 'metadata': {}}
        
        features = []
        labels = []
        
        for cmd in commands:
            # Extrair características do comando
            feature_vector = [
                len(cmd['command'].split()),  # Número de palavras
                len(cmd['command']),  # Comprimento do comando
                1 if cmd['success'] else 0,  # Sucesso
                cmd['command_length'],
                cmd['response_length']
            ]
            
            features.append(feature_vector)
            labels.append(1 if cmd['success'] else 0)
        
        return {
            'features': np.array(features),
            'labels': np.array(labels),
            'metadata': {
                'total_samples': len(commands),
                'success_rate': sum(labels) / len(labels) if labels else 0,
                'feature_names': ['word_count', 'char_count', 'success', 'cmd_length', 'resp_length']
            }
        }
    
    def _prepare_conversation_dataset(self) -> Dict[str, Any]:
        """Prepara dataset de conversações"""
        conversations = self.training_data['conversations']
        
        if not conversations:
            return {'inputs': [], 'outputs': [], 'metadata': {}}
        
        inputs = []
        outputs = []
        sentiments = []
        
        for conv in conversations:
            inputs.append(conv['user_input'])
            outputs.append(conv['ai_response'])
            sentiments.append(conv['input_sentiment'])
        
        return {
            'inputs': inputs,
            'outputs': outputs,
            'sentiments': sentiments,
            'metadata': {
                'total_conversations': len(conversations),
                'avg_input_length': np.mean([len(inp.split()) for inp in inputs]),
                'avg_output_length': np.mean([len(out.split()) for out in outputs]),
                'sentiment_distribution': {
                    'positive': sentiments.count('positive'),
                    'negative': sentiments.count('negative'),
                    'neutral': sentiments.count('neutral')
                }
            }
        }
    
    def _prepare_preference_dataset(self) -> Dict[str, Any]:
        """Prepara dataset de preferências do usuário"""
        preferences = self.training_data['user_preferences']
        
        if not preferences:
            return {'categories': {}, 'metadata': {}}
        
        processed_prefs = {}
        total_prefs = 0
        
        for category, prefs in preferences.items():
            processed_prefs[category] = {}
            for pref_name, pref_data in prefs.items():
                processed_prefs[category][pref_name] = {
                    'value': pref_data['value'],
                    'frequency': pref_data['frequency'],
                    'last_updated': pref_data['timestamp']
                }
                total_prefs += 1
        
        return {
            'categories': processed_prefs,
            'metadata': {
                'total_preferences': total_prefs,
                'categories_count': len(preferences),
                'most_frequent_category': max(preferences.keys(), 
                                            key=lambda k: sum(p['frequency'] for p in preferences[k].values()))
                                          if preferences else None
            }
        }
    
    def cleanup_old_data(self, days_old: int = 30):
        """Remove dados antigos para otimizar performance"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        removed_count = 0
        
        # Limpar comandos de voz antigos
        original_count = len(self.training_data['voice_commands'])
        self.training_data['voice_commands'] = [
            cmd for cmd in self.training_data['voice_commands']
            if datetime.fromisoformat(cmd['timestamp']) > cutoff_date
        ]
        removed_count += original_count - len(self.training_data['voice_commands'])
        
        # Limpar conversações antigas
        original_count = len(self.training_data['conversations'])
        self.training_data['conversations'] = [
            conv for conv in self.training_data['conversations']
            if datetime.fromisoformat(conv['timestamp']) > cutoff_date
        ]
        removed_count += original_count - len(self.training_data['conversations'])
        
        # Limpar feedback antigo
        original_count = len(self.training_data['feedback_data'])
        self.training_data['feedback_data'] = [
            fb for fb in self.training_data['feedback_data']
            if datetime.fromisoformat(fb['timestamp']) > cutoff_date
        ]
        removed_count += original_count - len(self.training_data['feedback_data'])
        
        if removed_count > 0:
            self.save_training_data()
            self.logger.info(f"Removidos {removed_count} registros antigos (>{days_old} dias)")
        
        return removed_count
