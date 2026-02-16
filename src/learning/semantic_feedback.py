# -*- coding: utf-8 -*-
"""
SEMANTIC FEEDBACK - Sistema de Auto-CorreÃ§Ã£o Evolutiva
JARVIS 5.0 - AnÃ¡lise semÃ¢ntica e aprendizado adaptativo real
"""

import sys
import os
import json
import logging
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import deque
import numpy as np
from dataclasses import dataclass, field, asdict

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SEMANTIC-FEEDBACK")

# Adicionar diretÃ³rio raiz
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@dataclass
class SemanticInteraction:
    """Representa uma interaÃ§Ã£o semÃ¢ntica completa"""
    interaction_id: str
    user_input: str
    ai_response: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    user_intent_vector: Optional[np.ndarray] = None
    response_quality_score: float = 0.0
    dissonance_detected: bool = False
    confidence_score: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionÃ¡rio (sem arrays numpy)"""
        data = asdict(self)
        if self.user_intent_vector is not None:
            data['user_intent_vector'] = self.user_intent_vector.tolist()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SemanticInteraction":
        """Cria a partir de dicionÃ¡rio"""
        if 'user_intent_vector' in data and data['user_intent_vector']:
            data['user_intent_vector'] = np.array(data['user_intent_vector'])
        return cls(**data)


@dataclass
class ConfidenceMetrics:
    """MÃ©tricas de confianÃ§a do sistema"""
    total_interactions: int = 0
    successful_interactions: int = 0
    dissonance_events: int = 0
    average_confidence: float = 0.5
    confidence_history: deque = field(default_factory=lambda: deque(maxlen=100))
    last_self_study: Optional[str] = None
    adaptation_cycles: int = 0

    def update_confidence(self, new_score: float):
        """Atualiza confianÃ§a com novo score"""
        self.confidence_history.append(new_score)
        self.average_confidence = float(np.mean(list(self.confidence_history)))

    def should_trigger_self_study(self, threshold: float = 0.4) -> bool:
        """Verifica se deve disparar auto-estudo"""
        return self.average_confidence < threshold and len(self.confidence_history) >= 5


class SemanticFeedbackAnalyzer:
    """
    Analisador SemÃ¢ntico para Auto-CorreÃ§Ã£o Evolutiva

    Sistema que avalia intenÃ§Ãµes do usuÃ¡rio, detecta dissonÃ¢ncias
    e dispara aprendizado adaptativo de forma invisÃ­vel.
    """

    def __init__(self, model_name: str = "microsoft/Phi-3-mini-4k-instruct"):
        logger.info(f"ðŸŽ¯ Inicializando SemanticFeedbackAnalyzer com model_name: {model_name}")
        self.model_name = model_name
        logger.info(f"âœ… Model name definido como: {self.model_name}")
        self.model = None
        self.tokenizer = None
        self.interaction_history: deque[SemanticInteraction] = deque(maxlen=50)
        self.confidence_metrics = ConfidenceMetrics()

        # ConfiguraÃ§Ãµes
        self.dissonance_threshold = 0.3  # Similaridade mÃ­nima para dissonÃ¢ncia
        self.confidence_threshold = 0.4  # Threshold para auto-reparo
        self.max_context_length = 512

        # Estado do sistema
        self.is_adapting = False
        self.last_adaptation = None

        # Carregar modelo local
        self._load_local_model()

        # Iniciar thread de anÃ¡lise assÃ­ncrona
        self.analysis_thread = threading.Thread(target=self._async_analysis_loop, daemon=True)
        self.analysis_thread.start()

        logger.info("ðŸŽ¯ Semantic Feedback Analyzer inicializado")

    def _load_local_model(self):
        """Carrega modelo local para anÃ¡lise semÃ¢ntica"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch

            logger.info(f"ðŸ“¥ Carregando modelo local para anÃ¡lise semÃ¢ntica: {self.model_name}")

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Carregar modelo em modo avaliaÃ§Ã£o apenas
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                dtype=torch.float32,
                device_map="cpu",
                low_cpu_mem_usage=True,
                ignore_mismatched_sizes=True,  # Silenciar incompatibilidade de pesos
                tie_word_embeddings=False  # Resolver aviso de tied weights
            )
            self.model.eval()

            logger.info("âœ… Modelo local carregado para anÃ¡lise semÃ¢ntica")

        except Exception as e:
            logger.error(f"âŒ Erro carregando modelo local: {e}")
            self.model = None
            self.tokenizer = None

    def analyze_user_intent(self, text: str) -> np.ndarray:
        """
        Analisa intenÃ§Ã£o semÃ¢ntica do usuÃ¡rio usando embeddings

        Args:
            text: Texto do usuÃ¡rio

        Returns:
            Vetor de embedding representando a intenÃ§Ã£o
        """
        if not self.model or not self.tokenizer:
            # Fallback: usar hash simples se modelo nÃ£o disponÃ­vel
            import hashlib
            hash_obj = hashlib.md5(text.encode())
            # Converter hash para array numpy
            hash_bytes = hash_obj.digest()
            return np.array([b / 255.0 for b in hash_bytes[:32]])  # 32 dimensÃµes

        try:
            import torch
            # Tokenizar texto
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_context_length,
                padding=True
            )

            # Obter embeddings da Ãºltima camada oculta
            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
                # Usar embeddings da Ãºltima camada
                embeddings = outputs.hidden_states[-1].mean(dim=1)  # Mean pooling

            # Converter para numpy e normalizar
            intent_vector = embeddings.squeeze().numpy()
            # Normalizar para similaridade de cosseno
            norm = np.linalg.norm(intent_vector)
            if norm > 0:
                intent_vector = intent_vector / norm

            return intent_vector

        except Exception as e:
            logger.warning(f"âš ï¸ Erro na anÃ¡lise de intenÃ§Ã£o: {e}")
            # Fallback
            return np.random.rand(768)  # DimensÃ£o tÃ­pica de embeddings

    def calculate_dissonance(self, current_interaction: SemanticInteraction,
                           previous_interactions: List[SemanticInteraction]) -> float:
        """
        Calcula dissonÃ¢ncia semÃ¢ntica entre interaÃ§Ãµes

        Args:
            current_interaction: InteraÃ§Ã£o atual
            previous_interactions: InteraÃ§Ãµes anteriores

        Returns:
            Score de dissonÃ¢ncia (0.0 = sem dissonÃ¢ncia, 1.0 = dissonÃ¢ncia mÃ¡xima)
        """
        if not previous_interactions:
            return 0.0

        max_dissonance = 0.0

        for prev_interaction in previous_interactions[-3:]:  # Ãšltimas 3 interaÃ§Ãµes
            if (prev_interaction.user_intent_vector is not None and
                current_interaction.user_intent_vector is not None):

                # Similaridade de cosseno
                similarity = np.dot(
                    prev_interaction.user_intent_vector,
                    current_interaction.user_intent_vector
                )

                # DissonÃ¢ncia = 1 - similaridade (se similaridade baixa = alta dissonÃ¢ncia)
                dissonance = 1.0 - similarity

                # Considerar tambÃ©m qualidade da resposta anterior
                quality_penalty = 1.0 - prev_interaction.response_quality_score

                # DissonÃ¢ncia combinada
                combined_dissonance = dissonance * (1.0 + quality_penalty)

                max_dissonance = max(max_dissonance, combined_dissonance)

        return min(max_dissonance, 1.0)  # Limitar a 1.0

    def evaluate_response_quality(self, user_input: str, ai_response: str) -> float:
        """
        Avalia qualidade da resposta da IA

        Args:
            user_input: Entrada do usuÃ¡rio
            ai_response: Resposta da IA

        Returns:
            Score de qualidade (0.0 = ruim, 1.0 = excelente)
        """
        if not ai_response.strip():
            return 0.0

        # MÃ©tricas simples de qualidade
        quality_score = 0.5  # Score base

        # 1. RelevÃ¢ncia (resposta nÃ£o vazia e relacionada)
        if len(ai_response) > 10:
            quality_score += 0.2

        # 2. Especificidade (nÃ£o respostas genÃ©ricas)
        generic_responses = ["nÃ£o sei", "desculpe", "nÃ£o entendi", "erro"]
        if not any(generic in ai_response.lower() for generic in generic_responses):
            quality_score += 0.2

        # 3. Comprimento apropriado
        if 20 <= len(ai_response) <= 500:
            quality_score += 0.1

        return min(quality_score, 1.0)

    def perform_ultra_auto_critique(self, dissonant_sequence: List[SemanticInteraction]) -> str:
        """
        Realiza auto-crÃ­tica usando o motor 'Ultra'

        Args:
            dissonant_sequence: SequÃªncia de interaÃ§Ãµes que causaram dissonÃ¢ncia

        Returns:
            AnÃ¡lise crÃ­tica para sÃ­ntese neural
        """
        if not dissonant_sequence:
            return "Nenhuma sequÃªncia dissonante para analisar"

        # Construir contexto da sequÃªncia
        context = "SEQUÃŠNCIA DE INTERAÃ‡Ã•ES COM DISSONÃ‚NCIA:\n\n"

        for i, interaction in enumerate(dissonant_sequence):
            context += f"InteraÃ§Ã£o {i+1}:\n"
            context += f"UsuÃ¡rio: {interaction.user_input}\n"
            context += f"IA: {interaction.ai_response}\n"
            context += f"ConfianÃ§a: {interaction.confidence_score:.2f}\n"
            context += "---\n"

        # Prompt para auto-crÃ­tica
        critique_prompt = f"""
        ANÃLISE CRÃTICA ULTRA - POR QUE EU FALHEI?

        {context}

        INSTRUÃ‡Ã•ES:
        1. Identifique o padrÃ£o de falha nesta sequÃªncia
        2. Determine qual foi a expectativa REAL do usuÃ¡rio
        3. Explique a lÃ³gica CORRETA que deveria ter sido aplicada
        4. Sugira como o sistema deve se adaptar
        5. ForneÃ§a exemplos especÃ­ficos de respostas corretas

        ANÃLISE OBJETIVA E CONSTRUTIVA:
        """

        # Usar modelo local para gerar crÃ­tica
        if self.model and self.tokenizer:
            try:
                import torch
                inputs = self.tokenizer(
                    critique_prompt,
                    return_tensors="pt",
                    truncation=True,
                    max_length=self.max_context_length
                )

                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_length=self.max_context_length + 200,
                        num_return_sequences=1,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )

                critique = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                # Remover o prompt da resposta
                critique = critique.replace(critique_prompt, "").strip()

                return critique

            except Exception as e:
                logger.warning(f"âš ï¸ Erro na auto-crÃ­tica: {e}")

        # Fallback: anÃ¡lise baseada em regras
        return f"""
        ANÃLISE DE DISSONÃ‚NCIA DETECTADA:

        PadrÃ£o identificado: Falha em manter contexto conversacional consistente
        Expectativa do usuÃ¡rio: Continuidade e aprendizado progressivo
        LÃ³gica correta: Manter estado conversacional e adaptar respostas
        AdaptaÃ§Ã£o necessÃ¡ria: Melhorar tracking de contexto e intenÃ§Ã£o

        Exemplos de melhoria:
        - Reconhecer quando usuÃ¡rio estÃ¡ construindo sobre pergunta anterior
        - Adaptar nÃ­vel de detalhe baseado no histÃ³rico
        - Antecipar follow-ups lÃ³gicos
        """

    def trigger_neural_synthesis(self, critique_analysis: str, dissonant_sequence: List[SemanticInteraction]):
        """
        Dispara sÃ­ntese neural usando RealTrainer com validaÃ§Ã£o externa

        Args:
            critique_analysis: AnÃ¡lise crÃ­tica gerada
            dissonant_sequence: SequÃªncia que causou dissonÃ¢ncia
        """
        try:
            from .real_trainer import RealTrainer
            from .truth_validator import get_truth_validator

            logger.info("ðŸ§  Iniciando SÃ­ntese Neural com ValidaÃ§Ã£o Externa")

            # 1. VALIDAR AUTO-CRÃTICA COM DADOS EXTERNOS
            truth_validator = get_truth_validator()

            # Extrair o erro principal da sequÃªncia dissonante
            jarvis_error = dissonant_sequence[-1].ai_response if dissonant_sequence else "Erro nÃ£o identificado"

            # Criar query para validaÃ§Ã£o baseada na crÃ­tica
            validation_query = f"Verificar se esta anÃ¡lise crÃ­tica estÃ¡ correta: {critique_analysis[:200]}..."

            logger.info("ðŸ” Validando auto-crÃ­tica com dados externos")
            validation_result = truth_validator.validate_fact(validation_query)

            # 2. COMPARAR E DECIDIR SOBRE O CONHECIMENTO
            comparison = truth_validator.compare_with_auto_critique(
                jarvis_error=jarvis_error,
                web_truth=validation_result.get('consolidated_truth', ''),
                auto_critique=critique_analysis
            )

            logger.info(f"âš–ï¸ ComparaÃ§Ã£o concluÃ­da - Alinhamento: {comparison['alignment_score']:.2f}")

            # 3. DECIDIR QUAL CONHECIMENTO USAR PARA TREINAMENTO
            if comparison['alignment_score'] >= 0.7:
                # Auto-crÃ­tica alinhada - usar como estÃ¡
                final_knowledge = critique_analysis
                training_source = "auto_critique_validated"
                logger.info("âœ… Usando auto-crÃ­tica validada para treinamento")
            elif comparison['alignment_score'] >= 0.4:
                # Parcialmente alinhada - combinar com verdade web
                final_knowledge = f"""
                ANÃLISE HÃBRIDA (Auto-crÃ­tica + Verdade Externa):

                Auto-crÃ­tica original: {critique_analysis}

                ValidaÃ§Ã£o externa: {validation_result.get('consolidated_truth', '')}

                RecomendaÃ§Ã£o: {comparison['recommendation']}
                """
                training_source = "hybrid_validation"
                logger.info("ðŸ”„ Usando conhecimento hÃ­brido para treinamento")
            else:
                # DiscrepÃ¢ncia significativa - usar apenas verdade externa
                final_knowledge = f"""
                CONHECIMENTO CORRIGIDO POR VALIDAÃ‡ÃƒO EXTERNA:

                Erro original detectado: {jarvis_error}

                Verdade validada externamente: {validation_result.get('consolidated_truth', '')}

                AnÃ¡lise crÃ­tica revisada baseada em fatos: {comparison['recommendation']}
                """
                training_source = "external_truth_only"
                logger.warning("âš ï¸ Usando exclusivamente verdade externa devido a discrepÃ¢ncia")

            # 4. PREPARAR DADOS DE TREINAMENTO
            synthesis_topic = f"Ground_Truth_Validated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            training_examples = [{
                "instruction": f"Aprenda desta anÃ¡lise validada externamente: {final_knowledge[:300]}...",
                "output": f"AplicaÃ§Ã£o prÃ¡tica baseada em fatos: {final_knowledge[300:600] if len(final_knowledge) > 300 else final_knowledge}",
                "source": training_source,
                "validation_confidence": validation_result.get('confidence_score', 0.0)
            }]

            # Adicionar exemplos da sequÃªncia dissonante com contexto validado
            for interaction in dissonant_sequence:
                training_examples.append({
                    "instruction": interaction.user_input,
                    "output": f"Resposta corrigida baseada em validaÃ§Ã£o externa: {final_knowledge[:200]}...",
                    "source": training_source,
                    "original_error": interaction.ai_response
                })

            # 5. EXECUTAR FINE-TUNING COM CONHECIMENTO VALIDADO
            trainer = RealTrainer()
            trainer.fine_tune_incremental(training_examples, synthesis_topic)

            # 6. ATUALIZAR MÃ‰TRICAS COM INFORMAÃ‡ÃƒO DE VALIDAÃ‡ÃƒO
            self.confidence_metrics.adaptation_cycles += 1
            self.confidence_metrics.last_self_study = datetime.now().isoformat()

            # Salvar resultado da validaÃ§Ã£o para auditoria
            validation_record = {
                "timestamp": datetime.now().isoformat(),
                "synthesis_topic": synthesis_topic,
                "validation_query": validation_query,
                "validation_result": validation_result,
                "comparison": comparison,
                "training_source": training_source,
                "final_knowledge_preview": final_knowledge[:500]
            }

            validation_log_path = Path("data/learning/validation_log.jsonl")
            validation_log_path.parent.mkdir(parents=True, exist_ok=True)

            with open(validation_log_path, 'a', encoding='utf-8') as f:
                json.dump(validation_record, f, ensure_ascii=False)
                f.write('\n')

            logger.info(f"âœ… SÃ­ntese Neural com ValidaÃ§Ã£o Externa concluÃ­da - Fonte: {training_source}")

        except Exception as e:
            logger.error(f"âŒ Erro na sÃ­ntese neural com validaÃ§Ã£o: {e}")
            # Fallback: tentar sÃ­ntese sem validaÃ§Ã£o
            try:
                logger.warning("ðŸ”„ Tentando sÃ­ntese sem validaÃ§Ã£o externa")
                self._fallback_neural_synthesis(critique_analysis, dissonant_sequence)
            except Exception as fallback_error:
                logger.error(f"âŒ Falha tambÃ©m no fallback: {fallback_error}")

    def _fallback_neural_synthesis(self, critique_analysis: str, dissonant_sequence: List[SemanticInteraction]):
        """
        MÃ©todo fallback para sÃ­ntese neural sem validaÃ§Ã£o externa

        Args:
            critique_analysis: AnÃ¡lise crÃ­tica gerada
            dissonant_sequence: SequÃªncia que causou dissonÃ¢ncia
        """
        try:
            from .real_trainer import RealTrainer

            logger.info("ðŸ§  Executando sÃ­ntese neural em modo fallback")

            synthesis_topic = f"Fallback_Auto_Correction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            training_examples = [{
                "instruction": f"Aprenda desta anÃ¡lise crÃ­tica (modo fallback): {critique_analysis[:200]}...",
                "output": f"AplicaÃ§Ã£o prÃ¡tica: {critique_analysis[200:400] if len(critique_analysis) > 200 else critique_analysis}",
                "source": "fallback_no_validation"
            }]

            for interaction in dissonant_sequence:
                training_examples.append({
                    "instruction": interaction.user_input,
                    "output": f"Melhor resposta baseada em anÃ¡lise crÃ­tica: {critique_analysis[:100]}...",
                    "source": "fallback_no_validation"
                })

            trainer = RealTrainer()
            trainer.fine_tune_incremental(training_examples, synthesis_topic)

            self.confidence_metrics.adaptation_cycles += 1
            self.confidence_metrics.last_self_study = datetime.now().isoformat()

            logger.info("âœ… SÃ­ntese Neural em modo fallback concluÃ­da")

        except Exception as e:
            logger.error(f"âŒ Erro no fallback de sÃ­ntese neural: {e}")

    def process_interaction(self, user_input: str, ai_response: str) -> SemanticInteraction:
        """
        Processa uma nova interaÃ§Ã£o e avalia dissonÃ¢ncia

        Args:
            user_input: Entrada do usuÃ¡rio
            ai_response: Resposta da IA

        Returns:
            InteraÃ§Ã£o processada
        """
        # Criar interaÃ§Ã£o
        interaction = SemanticInteraction(
            interaction_id=f"int_{datetime.now().timestamp()}",
            user_input=user_input,
            ai_response=ai_response
        )

        # Analisar intenÃ§Ã£o do usuÃ¡rio
        interaction.user_intent_vector = self.analyze_user_intent(user_input)

        # Avaliar qualidade da resposta
        interaction.response_quality_score = self.evaluate_response_quality(user_input, ai_response)

        # Calcular dissonÃ¢ncia com interaÃ§Ãµes anteriores
        recent_interactions = list(self.interaction_history)
        if recent_interactions:
            dissonance_score = self.calculate_dissonance(interaction, recent_interactions)
            interaction.dissonance_detected = dissonance_score > self.dissonance_threshold

            # Ajustar confianÃ§a baseada na dissonÃ¢ncia
            if interaction.dissonance_detected:
                interaction.confidence_score = max(0.1, interaction.response_quality_score - dissonance_score)
                self.confidence_metrics.dissonance_events += 1
            else:
                interaction.confidence_score = interaction.response_quality_score

        # Atualizar mÃ©tricas globais
        self.confidence_metrics.total_interactions += 1
        self.confidence_metrics.update_confidence(interaction.confidence_score)

        # Adicionar ao histÃ³rico
        self.interaction_history.append(interaction)

        logger.debug(f"ðŸ“Š InteraÃ§Ã£o processada - ConfianÃ§a: {interaction.confidence_score:.2f}, DissonÃ¢ncia: {interaction.dissonance_detected}")

        return interaction

    def _async_analysis_loop(self):
        """Loop assÃ­ncrono de anÃ¡lise e adaptaÃ§Ã£o"""
        while True:
            try:
                # Verificar se deve disparar auto-reparo
                if (self.confidence_metrics.should_trigger_self_study(self.confidence_threshold) and
                    not self.is_adapting):

                    self.is_adapting = True
                    logger.info("ðŸ”„ Gatilho de Auto-Reparo ativado - Iniciando adaptaÃ§Ã£o")

                    # Obter sequÃªncia dissonante recente
                    dissonant_sequence = [
                        interaction for interaction in self.interaction_history
                        if interaction.dissonance_detected
                    ][-5:]  # Ãšltimas 5 dissonÃ¢ncias

                    if dissonant_sequence:
                        # Realizar auto-crÃ­tica
                        critique = self.perform_ultra_auto_critique(dissonant_sequence)
                        logger.info("ðŸ§  Auto-crÃ­tica gerada")

                        # Disparar sÃ­ntese neural
                        self.trigger_neural_synthesis(critique, dissonant_sequence)

                    self.is_adapting = False
                    self.last_adaptation = datetime.now()

                # Aguardar antes da prÃ³xima anÃ¡lise
                threading.Event().wait(5.0)  # Verificar a cada 5 segundos

            except Exception as e:
                logger.error(f"âŒ Erro no loop de anÃ¡lise: {e}")
                self.is_adapting = False
                threading.Event().wait(10.0)  # Aguardar mais em caso de erro

    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status atual do sistema de feedback semÃ¢ntico"""
        return {
            "total_interactions": self.confidence_metrics.total_interactions,
            "average_confidence": self.confidence_metrics.average_confidence,
            "dissonance_events": self.confidence_metrics.dissonance_events,
            "adaptation_cycles": self.confidence_metrics.adaptation_cycles,
            "is_adapting": self.is_adapting,
            "last_adaptation": self.last_adaptation.isoformat() if self.last_adaptation else None,
            "interaction_history_size": len(self.interaction_history)
        }

    def save_state(self, filepath: Optional[str] = None):
        """Salva estado do sistema"""
        if not filepath:
            filepath = "data/learning/semantic_feedback_state.json"

        file_path = Path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        state = {
            "confidence_metrics": asdict(self.confidence_metrics),
            "interaction_history": [interaction.to_dict() for interaction in self.interaction_history],
            "last_adaptation": self.last_adaptation.isoformat() if self.last_adaptation else None,
            "is_adapting": self.is_adapting
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        logger.info(f"ðŸ’¾ Estado salvo em {file_path}")

    def load_state(self, filepath: Optional[str] = None):
        """Carrega estado do sistema"""
        if not filepath:
            filepath = "data/learning/semantic_feedback_state.json"

        file_path = Path(filepath)

        if not file_path.exists():
            logger.info("ðŸ“‚ Nenhum estado anterior encontrado")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                state = json.load(f)

            # Restaurar mÃ©tricas
            metrics_data = state.get("confidence_metrics", {})
            self.confidence_metrics = ConfidenceMetrics(**metrics_data)

            # Restaurar histÃ³rico
            history_data = state.get("interaction_history", [])
            self.interaction_history = deque(maxlen=50)
            for interaction_data in history_data:
                interaction = SemanticInteraction.from_dict(interaction_data)
                self.interaction_history.append(interaction)

            self.last_adaptation = datetime.fromisoformat(state["last_adaptation"]) if state.get("last_adaptation") else None
            self.is_adapting = state.get("is_adapting", False)

            logger.info(f"ðŸ“‚ Estado carregado de {filepath}")

        except Exception as e:
            logger.error(f"âŒ Erro carregando estado: {e}")


# InstÃ¢ncia global do analisador
_semantic_analyzer = None

def get_semantic_analyzer() -> SemanticFeedbackAnalyzer:
    """Retorna instÃ¢ncia global do analisador semÃ¢ntico"""
    global _semantic_analyzer
    if _semantic_analyzer is None:
        _semantic_analyzer = SemanticFeedbackAnalyzer()
    return _semantic_analyzer

def process_interaction_feedback(user_input: str, ai_response: str) -> Dict[str, Any]:
    """
    FunÃ§Ã£o principal para processar feedback de interaÃ§Ã£o

    Args:
        user_input: Entrada do usuÃ¡rio
        ai_response: Resposta da IA

    Returns:
        Resultado da anÃ¡lise semÃ¢ntica
    """
    analyzer = get_semantic_analyzer()
    interaction = analyzer.process_interaction(user_input, ai_response)

    return {
        "interaction_id": interaction.interaction_id,
        "confidence_score": interaction.confidence_score,
        "dissonance_detected": interaction.dissonance_detected,
        "system_status": analyzer.get_system_status()
    }
