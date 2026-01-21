"""
Dataset Preparation - Preparação Avançada de Datasets
Coleta, processa e prepara dados de múltiplas fontes para treinamento
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
import re
from dataclasses import dataclass, asdict
from core.logger import logger
from core.training_config import DatasetConfig
from modules.memory.persistent_memory import PersistentMemory


@dataclass
class TrainingSample:
    """Amostra individual de treinamento."""
    input: str
    output: str
    source: str  # conversation, code, document, web
    quality_score: float
    timestamp: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return asdict(self)


class DataQualityFilter:
    """Filtro de qualidade para dados de treinamento."""
    
    def __init__(self, min_quality_score: float = 0.5):
        """
        Inicializa filtro de qualidade.
        
        Args:
            min_quality_score: Score mínimo de qualidade (0-1)
        """
        self.min_quality_score = min_quality_score
    
    def calculate_quality_score(self, sample: TrainingSample) -> float:
        """
        Calcula score de qualidade de uma amostra.
        
        Args:
            sample: Amostra para avaliar
            
        Returns:
            Score de qualidade (0-1)
        """
        scores = []
        
        # 1. Comprimento apropriado
        input_len = len(sample.input)
        output_len = len(sample.output)
        
        length_score = 0.0
        if 10 <= input_len <= 500 and 20 <= output_len <= 2000:
            length_score = 1.0
        elif input_len < 10 or output_len < 20:
            length_score = 0.3
        else:
            length_score = 0.7
        
        scores.append(length_score)
        
        # 2. Diversidade de vocabulário
        input_words = set(sample.input.lower().split())
        output_words = set(sample.output.lower().split())
        vocab_score = min(len(input_words) / 10, 1.0) * 0.5 + min(len(output_words) / 20, 1.0) * 0.5
        scores.append(vocab_score)
        
        # 3. Ausência de padrões ruins
        bad_patterns = [
            r'^erro[:\s]',  # Começa com erro
            r'desculpe.*não.*consigo',  # Respostas negativas
            r'não.*tenho.*acesso',  # Limitações
            r'^\s*$',  # Vazio
        ]
        
        has_bad_pattern = any(re.search(pattern, sample.output.lower()) for pattern in bad_patterns)
        pattern_score = 0.2 if has_bad_pattern else 1.0
        scores.append(pattern_score)
        
        # 4. Completude da resposta
        # Respostas completas geralmente terminam com pontuação
        completeness_score = 1.0 if sample.output.rstrip()[-1] in '.!?' else 0.7
        scores.append(completeness_score)
        
        # Score final é a média ponderada
        final_score = sum(scores) / len(scores)
        return final_score
    
    def filter_samples(self, samples: List[TrainingSample]) -> List[TrainingSample]:
        """
        Filtra amostras por qualidade.
        
        Args:
            samples: Lista de amostras
            
        Returns:
            Lista de amostras filtradas
        """
        filtered = []
        for sample in samples:
            quality = self.calculate_quality_score(sample)
            if quality >= self.min_quality_score:
                sample.quality_score = quality
                filtered.append(sample)
            else:
                logger.debug(f"Amostra removida por baixa qualidade ({quality:.2f}): {sample.input[:50]}...")
        
        logger.info(f"Filtro de qualidade: {len(filtered)}/{len(samples)} amostras mantidas")
        return filtered


class ConversationDataCollector:
    """Coletor de dados de conversação."""
    
    def __init__(self, memory: PersistentMemory):
        """
        Inicializa coletor de conversação.
        
        Args:
            memory: Instância de memória persistente
        """
        self.memory = memory
    
    def collect(self, limit: int = 1000, since: Optional[datetime] = None) -> List[TrainingSample]:
        """
        Coleta dados de conversação do histórico.
        
        Args:
            limit: Número máximo de interações
            since: Coletar apenas após esta data
            
        Returns:
            Lista de amostras de treinamento
        """
        try:
            # Buscar histórico de conversas
            history = self.memory.get_conversation_history(limit=limit * 2)
            
            # Agrupar por pares user-assistant
            samples = []
            current_user = None
            current_timestamp = None
            
            for msg in history:
                # Filtrar por data se especificado
                if since and msg.get("timestamp"):
                    msg_time = datetime.fromisoformat(msg["timestamp"])
                    if msg_time < since:
                        continue
                
                if msg["role"] == "user":
                    current_user = msg["content"]
                    current_timestamp = msg.get("timestamp")
                elif msg["role"] == "assistant" and current_user:
                    # Criar amostra de treinamento
                    sample = TrainingSample(
                        input=current_user,
                        output=msg["content"],
                        source="conversation",
                        quality_score=0.5,  # Será recalculado pelo filtro
                        timestamp=current_timestamp or datetime.now().isoformat(),
                        metadata={
                            "original_metadata": msg.get("metadata", {}),
                            "message_id": msg.get("id")
                        }
                    )
                    samples.append(sample)
                    current_user = None
            
            logger.info(f"Coletadas {len(samples)} amostras de conversação")
            return samples
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados de conversação: {e}")
            return []


class CodeDataCollector:
    """Coletor de dados de código."""
    
    def __init__(self, memory: PersistentMemory):
        """
        Inicializa coletor de código.
        
        Args:
            memory: Instância de memória persistente
        """
        self.memory = memory
    
    def collect(self, limit: int = 500) -> List[TrainingSample]:
        """
        Coleta exemplos de código do histórico.
        
        Args:
            limit: Número máximo de exemplos
            
        Returns:
            Lista de amostras de código
        """
        try:
            # Buscar conversas que contêm código
            history = self.memory.get_conversation_history(limit=limit * 3)
            
            samples = []
            current_user = None
            
            for msg in history:
                if msg["role"] == "user":
                    current_user = msg["content"]
                elif msg["role"] == "assistant" and current_user:
                    # Verificar se contém código (marcadores comuns)
                    content = msg["content"]
                    has_code = any([
                        '```' in content,  # Markdown code block
                        'def ' in content,  # Python function
                        'class ' in content,  # Class definition
                        'import ' in content,  # Import statement
                        'function ' in content,  # JavaScript function
                        'const ' in content,  # JavaScript const
                    ])
                    
                    if has_code:
                        sample = TrainingSample(
                            input=current_user,
                            output=content,
                            source="code",
                            quality_score=0.7,  # Código geralmente tem boa qualidade
                            timestamp=msg.get("timestamp") or datetime.now().isoformat(),
                            metadata={
                                "contains_code": True,
                                "original_metadata": msg.get("metadata", {})
                            }
                        )
                        samples.append(sample)
                    
                    current_user = None
            
            logger.info(f"Coletadas {len(samples)} amostras de código")
            return samples
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados de código: {e}")
            return []


class DocumentDataCollector:
    """Coletor de dados de documentos."""
    
    def __init__(self, documents_dir: str = "./data/documents"):
        """
        Inicializa coletor de documentos.
        
        Args:
            documents_dir: Diretório com documentos
        """
        self.documents_dir = Path(documents_dir)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
    
    def collect(self, limit: int = 100) -> List[TrainingSample]:
        """
        Coleta dados de documentos.
        
        Args:
            limit: Número máximo de amostras
            
        Returns:
            Lista de amostras de documentos
        """
        try:
            samples = []
            
            # Processar arquivos de texto e markdown
            for ext in ['*.txt', '*.md']:
                for doc_path in self.documents_dir.glob(ext):
                    if len(samples) >= limit:
                        break
                    
                    try:
                        with open(doc_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Dividir em seções (por parágrafos ou títulos)
                        sections = self._split_into_sections(content)
                        
                        for section_title, section_content in sections:
                            if len(samples) >= limit:
                                break
                            
                            if len(section_content) < 50:
                                continue
                            
                            sample = TrainingSample(
                                input=f"Explique sobre: {section_title}",
                                output=section_content[:1000],  # Limitar tamanho
                                source="document",
                                quality_score=0.6,
                                timestamp=datetime.now().isoformat(),
                                metadata={
                                    "file": str(doc_path.name),
                                    "section": section_title
                                }
                            )
                            samples.append(sample)
                    
                    except Exception as e:
                        logger.warning(f"Erro ao processar documento {doc_path}: {e}")
            
            logger.info(f"Coletadas {len(samples)} amostras de documentos")
            return samples
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados de documentos: {e}")
            return []
    
    def _split_into_sections(self, content: str) -> List[Tuple[str, str]]:
        """Divide conteúdo em seções."""
        sections = []
        
        # Dividir por títulos markdown (# ou ##)
        parts = re.split(r'\n#+\s+(.+)\n', content)
        
        if len(parts) > 1:
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    title = parts[i].strip()
                    text = parts[i + 1].strip()
                    sections.append((title, text))
        else:
            # Sem títulos, dividir por parágrafos
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            for i, para in enumerate(paragraphs):
                sections.append((f"Seção {i+1}", para))
        
        return sections


class DatasetPreparation:
    """
    Sistema completo de preparação de datasets.
    Coleta dados de múltiplas fontes, filtra e prepara para treinamento.
    """
    
    def __init__(
        self,
        config: DatasetConfig,
        memory: PersistentMemory,
        output_dir: str = "./data/training/datasets"
    ):
        """
        Inicializa preparação de dataset.
        
        Args:
            config: Configuração do dataset
            memory: Instância de memória persistente
            output_dir: Diretório para salvar datasets
        """
        self.config = config
        self.memory = memory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar coletores
        self.quality_filter = DataQualityFilter(config.min_quality_score)
        self.conversation_collector = ConversationDataCollector(memory)
        self.code_collector = CodeDataCollector(memory)
        self.document_collector = DocumentDataCollector()
        
        logger.info("DatasetPreparation inicializado")
    
    def prepare_dataset(
        self,
        include_new_only: bool = False,
        since_timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Prepara dataset completo para treinamento.
        
        Args:
            include_new_only: Se True, inclui apenas dados novos
            since_timestamp: Incluir apenas dados após esta data
            
        Returns:
            Estatísticas do dataset preparado
        """
        try:
            logger.info("Iniciando preparação de dataset...")
            
            all_samples = []
            
            # 1. Coletar dados de conversação
            if self.config.include_conversations:
                conv_samples = self.conversation_collector.collect(
                    limit=self.config.max_samples,
                    since=since_timestamp
                )
                all_samples.extend(conv_samples)
            
            # 2. Coletar dados de código
            if self.config.include_code_examples:
                code_samples = self.code_collector.collect(
                    limit=self.config.max_samples // 2
                )
                all_samples.extend(code_samples)
            
            # 3. Coletar dados de documentos
            if self.config.include_documents:
                doc_samples = self.document_collector.collect(
                    limit=self.config.max_samples // 4
                )
                all_samples.extend(doc_samples)
            
            logger.info(f"Total de amostras coletadas: {len(all_samples)}")
            
            # 4. Filtrar por qualidade
            filtered_samples = self.quality_filter.filter_samples(all_samples)
            
            # 5. Limitar ao máximo configurado
            if len(filtered_samples) > self.config.max_samples:
                # Manter as melhores amostras
                filtered_samples.sort(key=lambda x: x.quality_score, reverse=True)
                filtered_samples = filtered_samples[:self.config.max_samples]
            
            # 6. Dividir em train/validation/test
            train_samples, val_samples, test_samples = self._split_dataset(filtered_samples)
            
            # 7. Salvar datasets
            dataset_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            dataset_info = {
                "dataset_id": dataset_id,
                "created_at": datetime.now().isoformat(),
                "total_samples": len(filtered_samples),
                "train_samples": len(train_samples),
                "validation_samples": len(val_samples),
                "test_samples": len(test_samples),
                "config": {
                    "min_quality_score": self.config.min_quality_score,
                    "include_conversations": self.config.include_conversations,
                    "include_code": self.config.include_code_examples,
                    "include_documents": self.config.include_documents
                },
                "sources": self._count_by_source(filtered_samples)
            }
            
            self._save_dataset(dataset_id, train_samples, val_samples, test_samples, dataset_info)
            
            logger.info(f"✅ Dataset preparado: {dataset_id}")
            logger.info(f"  - Train: {len(train_samples)} amostras")
            logger.info(f"  - Validation: {len(val_samples)} amostras")
            logger.info(f"  - Test: {len(test_samples)} amostras")
            
            return dataset_info
            
        except Exception as e:
            logger.error(f"Erro ao preparar dataset: {e}")
            return {
                "error": str(e),
                "total_samples": 0
            }
    
    def _split_dataset(
        self,
        samples: List[TrainingSample]
    ) -> Tuple[List[TrainingSample], List[TrainingSample], List[TrainingSample]]:
        """Divide dataset em train/validation/test."""
        import random
        random.shuffle(samples)
        
        train_size = int(len(samples) * self.config.train_test_split)
        val_size = int(len(samples) * self.config.validation_split)
        
        train_samples = samples[:train_size]
        val_samples = samples[train_size:train_size + val_size]
        test_samples = samples[train_size + val_size:]
        
        return train_samples, val_samples, test_samples
    
    def _count_by_source(self, samples: List[TrainingSample]) -> Dict[str, int]:
        """Conta amostras por fonte."""
        counts = {}
        for sample in samples:
            source = sample.source
            counts[source] = counts.get(source, 0) + 1
        return counts
    
    def _save_dataset(
        self,
        dataset_id: str,
        train: List[TrainingSample],
        val: List[TrainingSample],
        test: List[TrainingSample],
        info: Dict[str, Any]
    ):
        """Salva dataset em arquivos."""
        dataset_dir = self.output_dir / dataset_id
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        # Salvar splits
        self._save_split(dataset_dir / "train.json", train)
        self._save_split(dataset_dir / "validation.json", val)
        self._save_split(dataset_dir / "test.json", test)
        
        # Salvar informações
        with open(dataset_dir / "info.json", 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dataset salvo em: {dataset_dir}")
    
    def _save_split(self, path: Path, samples: List[TrainingSample]):
        """Salva um split do dataset."""
        data = [sample.to_dict() for sample in samples]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas dos dados disponíveis."""
        history = self.memory.get_conversation_history(limit=5000)
        
        user_messages = [m for m in history if m["role"] == "user"]
        assistant_messages = [m for m in history if m["role"] == "assistant"]
        
        return {
            "total_interactions": len(history) // 2,
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "can_prepare_dataset": len(user_messages) >= self.config.min_interactions,
            "min_required": self.config.min_interactions
        }
