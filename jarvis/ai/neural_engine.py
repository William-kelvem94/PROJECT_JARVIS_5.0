"""
Motor Neural do JARVIS - IA Real com Aprendizado Contínuo
Sistema de inteligência artificial que aprende e evolui continuamente
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import threading
import time

# Machine Learning
try:
    from sklearn.neural_network import MLPClassifier, MLPRegressor
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import accuracy_score, classification_report
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Deep Learning (opcional)
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, Dataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from ..core.logger import default_logger


class NeuralMemory:
    """Sistema de memória neural para aprendizado"""
    
    def __init__(self, memory_path: str):
        self.memory_path = memory_path
        self.short_term = []  # Memória de curto prazo
        self.long_term = {}   # Memória de longo prazo
        self.patterns = {}    # Padrões aprendidos
        self.experiences = [] # Experiências para treinamento
        
        self._load_memory()
    
    def add_experience(self, input_data: Any, output_data: Any, context: Dict[str, Any], success: bool):
        """Adiciona experiência para aprendizado"""
        experience = {
            'timestamp': datetime.now().isoformat(),
            'input': input_data,
            'output': output_data,
            'context': context,
            'success': success,
            'feedback_score': 1.0 if success else 0.0
        }
        
        self.experiences.append(experience)
        self.short_term.append(experience)
        
        # Manter apenas últimas 1000 experiências em memória
        if len(self.short_term) > 1000:
            self.short_term = self.short_term[-1000:]
    
    def get_training_data(self) -> Tuple[List, List]:
        """Extrai dados para treinamento"""
        X, y = [], []
        
        for exp in self.experiences:
            if isinstance(exp['input'], (str, dict)):
                # Converter entrada para features numéricas
                features = self._extract_features(exp['input'], exp['context'])
                X.append(features)
                y.append(exp['feedback_score'])
        
        return X, y
    
    def _extract_features(self, input_data: Any, context: Dict[str, Any]) -> List[float]:
        """Extrai features numéricas dos dados"""
        features = []
        
        # Features do input
        if isinstance(input_data, str):
            features.extend([
                len(input_data),  # Comprimento do texto
                input_data.count(' '),  # Número de palavras
                input_data.count('?'),  # Número de perguntas
                input_data.count('!'),  # Número de exclamações
                1.0 if any(word in input_data.lower() for word in ['por favor', 'obrigado']) else 0.0  # Polidez
            ])
        
        # Features do contexto
        features.extend([
            context.get('user_satisfaction', 0.5),
            context.get('task_complexity', 0.5),
            context.get('response_time', 1.0),
            1.0 if context.get('time_of_day') == 'morning' else 0.0,
            1.0 if context.get('time_of_day') == 'afternoon' else 0.0,
            1.0 if context.get('time_of_day') == 'evening' else 0.0,
            1.0 if context.get('time_of_day') == 'night' else 0.0
        ])
        
        return features
    
    def save_memory(self):
        """Salva memória em disco"""
        try:
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            
            memory_data = {
                'long_term': self.long_term,
                'patterns': self.patterns,
                'experiences': self.experiences[-10000:],  # Manter últimas 10k experiências
                'last_save': datetime.now().isoformat()
            }
            
            with open(self.memory_path, 'wb') as f:
                pickle.dump(memory_data, f)
                
        except Exception as e:
            print(f"Erro ao salvar memória: {e}")
    
    def _load_memory(self):
        """Carrega memória do disco"""
        try:
            if os.path.exists(self.memory_path):
                with open(self.memory_path, 'rb') as f:
                    memory_data = pickle.load(f)
                
                self.long_term = memory_data.get('long_term', {})
                self.patterns = memory_data.get('patterns', {})
                self.experiences = memory_data.get('experiences', [])
                
        except Exception as e:
            print(f"Erro ao carregar memória: {e}")


class ConversationalAI:
    """IA Conversacional com Aprendizado Neural"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        
        self._load_model()
    
    def _load_model(self):
        """Carrega modelo treinado"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.label_encoder = model_data['label_encoder']
                self.is_trained = True
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}")
    
    def train(self, X: List, y: List):
        """Treina o modelo neural"""
        if not ML_AVAILABLE or len(X) < 10:
            return False
        
        try:
            X = np.array(X)
            y = np.array(y)
            
            # Normalizar features
            X_scaled = self.scaler.fit_transform(X)
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Criar e treinar modelo neural
            self.model = MLPClassifier(
                hidden_layer_sizes=(100, 50, 25),
                activation='relu',
                solver='adam',
                alpha=0.001,
                batch_size='auto',
                learning_rate='constant',
                learning_rate_init=0.001,
                max_iter=1000,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1
            )
            
            self.model.fit(X_train, y_train)
            
            # Avaliar modelo
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"Modelo treinado com acurácia: {accuracy:.2f}")
            
            self.is_trained = True
            self._save_model()
            
            return True
            
        except Exception as e:
            print(f"Erro no treinamento: {e}")
            return False
    
    def predict(self, features: List[float]) -> Tuple[float, float]:
        """Faz predição com o modelo"""
        if not self.is_trained or not self.model:
            return 0.5, 0.0  # Predição neutra
        
        try:
            features = np.array(features).reshape(1, -1)
            features_scaled = self.scaler.transform(features)
            
            prediction = self.model.predict_proba(features_scaled)[0]
            confidence = max(prediction)
            
            return float(prediction[1]), float(confidence)
            
        except Exception as e:
            print(f"Erro na predição: {e}")
            return 0.5, 0.0
    
    def _save_model(self):
        """Salva modelo treinado"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'trained_at': datetime.now().isoformat()
            }
            
            joblib.dump(model_data, self.model_path)
            
        except Exception as e:
            print(f"Erro ao salvar modelo: {e}")


class NeuralEngine:
    """Motor Neural Principal do JARVIS"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = default_logger
        
        # Caminhos dos modelos
        self.models_dir = config.get('ai', {}).get('models_dir', 'models')
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Sistemas neurais
        self.memory = NeuralMemory(os.path.join(self.models_dir, 'neural_memory.pkl'))
        self.conversation_ai = ConversationalAI(os.path.join(self.models_dir, 'conversation_model.pkl'))
        
        # Configurações de aprendizado
        self.learning_config = {
            'auto_train_interval': 3600,  # 1 hora
            'min_experiences_for_training': 50,
            'retrain_threshold': 0.1,  # Retreinar se acurácia cair 10%
            'save_interval': 300  # 5 minutos
        }
        
        # Estado do sistema
        self.is_learning = True
        self.last_training = None
        self.training_thread = None
        
        # Métricas de performance
        self.performance_metrics = {
            'total_interactions': 0,
            'successful_interactions': 0,
            'learning_sessions': 0,
            'model_accuracy': 0.0,
            'avg_response_quality': 0.0
        }
        
        # Iniciar sistema de aprendizado
        self._start_learning_system()
        
        self.logger.info("Neural Engine inicializado com aprendizado contínuo")
    
    def process_interaction(self, input_data: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa interação usando IA neural
        
        Args:
            input_data: Entrada do usuário
            context: Contexto da interação
            
        Returns:
            Resultado do processamento neural
        """
        try:
            # Extrair features
            features = self.memory._extract_features(input_data, context)
            
            # Fazer predição
            quality_score, confidence = self.conversation_ai.predict(features)
            
            # Gerar resposta baseada na predição
            response = self._generate_neural_response(input_data, context, quality_score, confidence)
            
            # Registrar interação
            self.performance_metrics['total_interactions'] += 1
            
            return {
                'response': response,
                'quality_score': quality_score,
                'confidence': confidence,
                'neural_features': features,
                'learning_active': self.is_learning
            }
            
        except Exception as e:
            self.logger.error(f"Erro no processamento neural: {e}")
            return {
                'response': "Desculpe, tive um problema no processamento neural.",
                'quality_score': 0.5,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def learn_from_feedback(self, input_data: str, output_data: str, context: Dict[str, Any], 
                           user_feedback: Optional[float] = None, success: bool = True):
        """
        Aprende com feedback do usuário
        
        Args:
            input_data: Entrada original
            output_data: Saída gerada
            context: Contexto da interação
            user_feedback: Feedback do usuário (0.0 a 1.0)
            success: Se a interação foi bem-sucedida
        """
        try:
            # Calcular score de feedback
            if user_feedback is not None:
                feedback_score = user_feedback
            else:
                feedback_score = 1.0 if success else 0.0
            
            # Adicionar experiência à memória
            enhanced_context = context.copy()
            enhanced_context['user_feedback'] = feedback_score
            enhanced_context['timestamp'] = datetime.now().isoformat()
            
            self.memory.add_experience(input_data, output_data, enhanced_context, success)
            
            # Atualizar métricas
            if success:
                self.performance_metrics['successful_interactions'] += 1
            
            self.performance_metrics['avg_response_quality'] = (
                self.performance_metrics['successful_interactions'] / 
                max(self.performance_metrics['total_interactions'], 1)
            )
            
            self.logger.debug(f"Feedback registrado: {feedback_score:.2f}")
            
        except Exception as e:
            self.logger.error(f"Erro ao processar feedback: {e}")
    
    def _generate_neural_response(self, input_data: str, context: Dict[str, Any], 
                                 quality_score: float, confidence: float) -> str:
        """Gera resposta usando IA neural"""
        
        # Analisar padrões aprendidos
        patterns = self._analyze_learned_patterns(input_data, context)
        
        # Gerar resposta baseada na qualidade prevista
        if quality_score > 0.8 and confidence > 0.7:
            # Alta confiança - resposta elaborada
            response_style = "elaborated"
        elif quality_score > 0.6:
            # Média confiança - resposta padrão
            response_style = "standard"
        else:
            # Baixa confiança - resposta cautelosa
            response_style = "cautious"
        
        # Aplicar padrões aprendidos
        response = self._apply_learned_patterns(input_data, context, response_style, patterns)
        
        return response
    
    def _analyze_learned_patterns(self, input_data: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa padrões aprendidos relevantes"""
        patterns = {
            'common_phrases': [],
            'successful_responses': [],
            'user_preferences': {},
            'context_patterns': {}
        }
        
        # Analisar experiências similares
        for exp in self.memory.experiences[-100:]:  # Últimas 100 experiências
            if exp['success'] and isinstance(exp['input'], str):
                # Verificar similaridade
                similarity = self._calculate_similarity(input_data, exp['input'])
                
                if similarity > 0.7:
                    patterns['successful_responses'].append(exp['output'])
                    
                    # Extrair preferências do usuário
                    if 'user_preferences' in exp['context']:
                        patterns['user_preferences'].update(exp['context']['user_preferences'])
        
        return patterns
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade entre textos"""
        # Implementação simples de similaridade
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _apply_learned_patterns(self, input_data: str, context: Dict[str, Any], 
                               style: str, patterns: Dict[str, Any]) -> str:
        """Aplica padrões aprendidos na geração de resposta"""
        
        # Base de respostas por estilo
        response_templates = {
            'elaborated': [
                "Com base no que aprendi, posso te ajudar com isso de forma detalhada.",
                "Interessante! Baseado em experiências anteriores, acredito que a melhor abordagem é:",
                "Ótima pergunta! Pelo que observei em situações similares:"
            ],
            'standard': [
                "Entendi! Posso ajudar com isso.",
                "Claro! Vou cuidar disso para você.",
                "Perfeito! Já sei como proceder."
            ],
            'cautious': [
                "Hmm, deixe-me pensar na melhor forma de ajudar.",
                "Interessante. Vou tentar uma abordagem cuidadosa.",
                "Entendi. Vou proceder com cuidado neste caso."
            ]
        }
        
        # Selecionar template base
        import random
        base_response = random.choice(response_templates[style])
        
        # Personalizar baseado em padrões aprendidos
        if patterns['user_preferences']:
            # Aplicar preferências do usuário
            if patterns['user_preferences'].get('formal_style', False):
                base_response = base_response.replace('Ótima', 'Excelente')
                base_response = base_response.replace('Claro!', 'Certamente.')
        
        # Adicionar contexto específico se disponível
        if patterns['successful_responses']:
            # Usar elementos de respostas bem-sucedidas anteriores
            successful_elements = [
                "como fizemos antes",
                "seguindo o padrão que funcionou",
                "da forma que você gosta"
            ]
            
            if random.random() < 0.3:  # 30% de chance
                base_response += f" {random.choice(successful_elements)}"
        
        return base_response
    
    def _start_learning_system(self):
        """Inicia sistema de aprendizado contínuo"""
        if not ML_AVAILABLE:
            self.logger.warning("Sistema de ML não disponível - aprendizado limitado")
            return
        
        def learning_loop():
            while self.is_learning:
                try:
                    # Verificar se é hora de treinar
                    if self._should_retrain():
                        self._perform_training()
                    
                    # Salvar memória periodicamente
                    self.memory.save_memory()
                    
                    # Aguardar próximo ciclo
                    time.sleep(self.learning_config['save_interval'])
                    
                except Exception as e:
                    self.logger.error(f"Erro no loop de aprendizado: {e}")
                    time.sleep(60)  # Aguardar 1 minuto em caso de erro
        
        self.training_thread = threading.Thread(target=learning_loop, daemon=True)
        self.training_thread.start()
        
        self.logger.info("Sistema de aprendizado contínuo iniciado")
    
    def _should_retrain(self) -> bool:
        """Verifica se deve retreinar o modelo"""
        # Verificar número mínimo de experiências
        if len(self.memory.experiences) < self.learning_config['min_experiences_for_training']:
            return False
        
        # Verificar intervalo de tempo
        if self.last_training:
            time_since_training = datetime.now() - self.last_training
            if time_since_training.total_seconds() < self.learning_config['auto_train_interval']:
                return False
        
        # Verificar se há experiências novas suficientes
        new_experiences = len([
            exp for exp in self.memory.experiences 
            if self.last_training is None or 
            datetime.fromisoformat(exp['timestamp']) > self.last_training
        ])
        
        return new_experiences >= 20  # Pelo menos 20 novas experiências
    
    def _perform_training(self):
        """Executa treinamento do modelo"""
        try:
            self.logger.info("Iniciando sessão de auto-treinamento...")
            
            # Obter dados de treinamento
            X, y = self.memory.get_training_data()
            
            if len(X) < 10:
                self.logger.warning("Dados insuficientes para treinamento")
                return
            
            # Treinar modelo
            success = self.conversation_ai.train(X, y)
            
            if success:
                self.performance_metrics['learning_sessions'] += 1
                self.last_training = datetime.now()
                
                self.logger.info("Auto-treinamento concluído com sucesso!")
            else:
                self.logger.warning("Falha no auto-treinamento")
                
        except Exception as e:
            self.logger.error(f"Erro durante treinamento: {e}")
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de aprendizado"""
        return {
            'performance_metrics': self.performance_metrics.copy(),
            'memory_stats': {
                'total_experiences': len(self.memory.experiences),
                'short_term_memory': len(self.memory.short_term),
                'learned_patterns': len(self.memory.patterns)
            },
            'model_stats': {
                'is_trained': self.conversation_ai.is_trained,
                'last_training': self.last_training.isoformat() if self.last_training else None,
                'learning_active': self.is_learning
            },
            'system_info': {
                'ml_available': ML_AVAILABLE,
                'torch_available': TORCH_AVAILABLE,
                'models_dir': self.models_dir
            }
        }
    
    def stop_learning(self):
        """Para o sistema de aprendizado"""
        self.is_learning = False
        self.memory.save_memory()
        self.logger.info("Sistema de aprendizado parado")
    
    def force_training(self) -> bool:
        """Força treinamento imediato"""
        try:
            self._perform_training()
            return True
        except Exception as e:
            self.logger.error(f"Erro no treinamento forçado: {e}")
            return False
