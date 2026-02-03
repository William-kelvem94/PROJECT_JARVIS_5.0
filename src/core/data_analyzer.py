"""
Analisador inteligente de dados extraídos
Categoriza e processa dados usando IA e regras
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from datetime import datetime
from src.utils.config import config
from src.utils.helpers import TextHelper, DataHelper
from src.database.models import db_manager, ExtractedData, DocumentCategory

logger = logging.getLogger(__name__)

class DataAnalyzer:
    """Classe para análise inteligente de dados extraídos"""

    def __init__(self):
        self.nlp = None
        self.keywords_cache = {}

        # Carregar modelo de linguagem natural
        self._load_nlp_model()

        # Carregar padrões de extração
        self.extraction_patterns = config.EXTRACTION_PATTERNS.copy()
        self.data_categories = config.DATA_CATEGORIES.copy()

        # Padrões de categorização por documento
        self.document_patterns = self._load_document_patterns()

        logger.info("Analisador de dados inicializado")

    def _load_nlp_model(self):
        """Carrega modelo de processamento de linguagem natural"""
        try:
            # Importar spacy primeiro
            import spacy

            # Tentar carregar modelo para português
            self.nlp = spacy.load("pt_core_news_sm")
            logger.info("Modelo spaCy carregado com sucesso")
        except (OSError, ImportError):
            logger.warning("Modelo spaCy não encontrado. Alguns recursos estarão limitados.")
            try:
                # Fallback para modelo básico
                spacy.cli.download("pt_core_news_sm")
                self.nlp = spacy.load("pt_core_news_sm")
            except Exception as e:
                logger.error(f"Erro ao baixar modelo spaCy: {e}")
                self.nlp = None

    def _load_document_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Carrega padrões para categorização de documentos"""
        return {
            "receipt": {
                "keywords": ["nota fiscal", "cupom fiscal", "recibo", "comprovante"],
                "patterns": [r"nota\s+fiscal", r"cupom\s+fiscal", r"recibo\s+de\s+pagamento"],
                "confidence_boost": 0.8
            },
            "invoice": {
                "keywords": ["fatura", "conta", "boleto", "cobrança"],
                "patterns": [r"fatura\s+\w+", r"boleto\s+bancário", r"conta\s+de\s+luz|água|telefone"],
                "confidence_boost": 0.7
            },
            "contract": {
                "keywords": ["contrato", "acordo", "termo", "convenção"],
                "patterns": [r"contrato\s+de\s+\w+", r"termo\s+de\s+acordo"],
                "confidence_boost": 0.9
            },
            "report": {
                "keywords": ["relatório", "relatorio", "laudo", "parecer"],
                "patterns": [r"relatório\s+\w+", r"laudo\s+técnico"],
                "confidence_boost": 0.6
            },
            "form": {
                "keywords": ["formulário", "formulario", "cadastro", "registro"],
                "patterns": [r"formulário\s+de\s+\w+", r"cadastro\s+\w+"],
                "confidence_boost": 0.5
            },
            "id_document": {
                "keywords": ["rg", "cpf", "cnh", "passaporte", "identidade"],
                "patterns": [r"rg\s*[\d\.\-\s]+", r"cpf\s*[\d\.\-\s]+"],
                "confidence_boost": 0.9
            },
            "financial": {
                "keywords": ["extrato", "saldo", "transferência", "transferencia", "pagamento"],
                "patterns": [r"extrato\s+bancário", r"saldo\s+atual"],
                "confidence_boost": 0.7
            }
        }

    def analyze_text(self, text: str, capture_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Analisa texto extraído e extrai dados estruturados

        Args:
            text: Texto a ser analisado
            capture_id: ID da captura no banco (opcional)

        Returns:
            Dicionário com dados extraídos e categorização
        """
        try:
            if not text or not text.strip():
                return {'extracted_data': [], 'categories': [], 'confidence': 0}

            # Limpar e normalizar texto
            cleaned_text = TextHelper.clean_ocr_text(text)
            normalized_text = TextHelper.normalize_text(cleaned_text)

            # Extrair dados usando padrões
            extracted_data = self._extract_data_with_patterns(cleaned_text)

            # Categorizar documento
            categories = self._categorize_document(cleaned_text, normalized_text)

            # Análise adicional com NLP se disponível
            if self.nlp:
                nlp_analysis = self._analyze_with_nlp(cleaned_text)
                extracted_data.extend(nlp_analysis.get('entities', []))

            # Calcular confiança geral
            avg_confidence = sum(item.get('confidence', 0) for item in extracted_data) / len(extracted_data) if extracted_data else 0

            result = {
                'extracted_data': extracted_data,
                'categories': categories,
                'confidence': avg_confidence,
                'text_length': len(cleaned_text),
                'data_points_found': len(extracted_data)
            }

            # Salvar no banco se capture_id fornecido
            if capture_id:
                self._save_analysis_results(capture_id, result)

            logger.info(f"Análise concluída: {len(extracted_data)} dados extraídos, {len(categories)} categorias")
            return result

        except Exception as e:
            logger.error(f"Erro na análise de texto: {e}")
            return {'extracted_data': [], 'categories': [], 'confidence': 0, 'error': str(e)}

    def _extract_data_with_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Extrai dados usando padrões regex"""
        extracted_data = []

        # Extrair usando padrões pré-definidos
        pattern_results = TextHelper.extract_patterns(text, self.extraction_patterns)

        for pattern_name, matches in pattern_results.items():
            data_type = self._get_data_type_for_pattern(pattern_name)

            for match in matches:
                # Validar dados específicos
                validated_value = self._validate_extracted_data(pattern_name, match)

                if validated_value:
                    extracted_data.append({
                        'field_name': pattern_name,
                        'field_value': validated_value,
                        'data_type': data_type,
                        'pattern_used': pattern_name,
                        'confidence': self._calculate_pattern_confidence(pattern_name, match),
                        'validated': True
                    })

        # Extrair dados contextuais
        contextual_data = self._extract_contextual_data(text)
        extracted_data.extend(contextual_data)

        return extracted_data

    def _get_data_type_for_pattern(self, pattern_name: str) -> str:
        """Retorna o tipo de dados para um padrão"""
        pattern_to_type = {
            'cpf': 'personal',
            'cnpj': 'business',
            'email': 'personal',
            'phone': 'personal',
            'cep': 'personal',
            'money': 'financial',
            'date': 'documents',
            'url': 'documents'
        }
        return pattern_to_type.get(pattern_name, 'documents')

    def _validate_extracted_data(self, pattern_name: str, value: str) -> Optional[str]:
        """Valida dados extraídos"""
        try:
            if pattern_name == 'cpf':
                return value if DataHelper.validate_cpf(value) else None
            elif pattern_name == 'cnpj':
                return value if DataHelper.validate_cnpj(value) else None
            elif pattern_name == 'email':
                # Validação básica de email
                if '@' in value and '.' in value.split('@')[1]:
                    return value.lower().strip()
            elif pattern_name == 'phone':
                # Limpar e validar telefone
                clean_phone = re.sub(r'[^\d]', '', value)
                if 10 <= len(clean_phone) <= 11:
                    return DataHelper.format_phone(value)
            elif pattern_name == 'cep':
                clean_cep = re.sub(r'[^\d]', '', value)
                if len(clean_cep) == 8:
                    return f"{clean_cep[:5]}-{clean_cep[5:]}"
            elif pattern_name == 'money':
                return DataHelper.format_money(value)
            elif pattern_name == 'date':
                parsed_date = DataHelper.parse_date(value)
                return parsed_date.strftime('%d/%m/%Y') if parsed_date else None

            # Para outros padrões, retornar valor limpo
            return value.strip()

        except Exception as e:
            logger.error(f"Erro na validação de {pattern_name}: {e}")
            return value.strip()

    def _calculate_pattern_confidence(self, pattern_name: str, value: str) -> float:
        """Calcula confiança para dados extraídos"""
        base_confidence = {
            'cpf': 0.95,
            'cnpj': 0.95,
            'email': 0.90,
            'phone': 0.85,
            'cep': 0.90,
            'money': 0.80,
            'date': 0.75,
            'url': 0.85
        }

        confidence = base_confidence.get(pattern_name, 0.70)

        # Ajustar baseado na qualidade do match
        if len(value.strip()) < 3:
            confidence *= 0.5

        return min(confidence, 1.0)

    def _extract_contextual_data(self, text: str) -> List[Dict[str, Any]]:
        """Extrai dados contextuais usando análise de texto"""
        contextual_data = []

        try:
            # Procurar por nomes próprios
            name_patterns = [
                r'Sr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'Sra\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'Dr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'Nome:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            ]

            for pattern in name_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match.strip()) > 2:
                        contextual_data.append({
                            'field_name': 'nome',
                            'field_value': match.strip(),
                            'data_type': 'personal',
                            'pattern_used': 'contextual_name',
                            'confidence': 0.7,
                            'validated': False
                        })

            # Procurar por endereços
            address_patterns = [
                r'Endereço:?\s*([^\n\r]{10,80})',
                r'Rua\s+[^,]{5,50},\s*\d+',
                r'Av\.?\s+[^,]{5,50},\s*\d+'
            ]

            for pattern in address_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match.strip()) > 10:
                        contextual_data.append({
                            'field_name': 'endereco',
                            'field_value': match.strip(),
                            'data_type': 'personal',
                            'pattern_used': 'contextual_address',
                            'confidence': 0.6,
                            'validated': False
                        })

        except Exception as e:
            logger.error(f"Erro na extração contextual: {e}")

        return contextual_data

    def _categorize_document(self, text: str, normalized_text: str) -> List[Dict[str, Any]]:
        """Categoriza documento baseado no conteúdo"""
        categories = []

        try:
            for doc_type, patterns in self.document_patterns.items():
                confidence = 0.0
                keywords_found = []

                # Verificar palavras-chave
                for keyword in patterns['keywords']:
                    if keyword.lower() in normalized_text:
                        confidence += 0.3
                        keywords_found.append(keyword)

                # Verificar padrões regex
                for pattern in patterns['patterns']:
                    if re.search(pattern, text, re.IGNORECASE):
                        confidence += 0.4
                        break

                # Aplicar boost de confiança
                confidence *= patterns['confidence_boost']

                # Adicionar categoria se confiança suficiente
                if confidence >= 0.4:
                    categories.append({
                        'category_name': doc_type,
                        'confidence_score': min(confidence, 1.0),
                        'keywords_found': keywords_found,
                        'ai_suggestion': True
                    })

            # Ordenar por confiança
            categories.sort(key=lambda x: x['confidence_score'], reverse=True)

        except Exception as e:
            logger.error(f"Erro na categorização: {e}")

        return categories[:3]  # Top 3 categorias

    def _analyze_with_nlp(self, text: str) -> Dict[str, Any]:
        """Analisa texto usando processamento de linguagem natural"""
        analysis_result = {'entities': []}

        try:
            if not self.nlp:
                return analysis_result

            doc = self.nlp(text)

            # Extrair entidades nomeadas
            for ent in doc.ents:
                entity_type = self._map_spacy_entity(ent.label_)

                if entity_type:
                    analysis_result['entities'].append({
                        'field_name': ent.label_.lower(),
                        'field_value': ent.text,
                        'data_type': entity_type,
                        'pattern_used': 'spacy_ner',
                        'confidence': 0.8,
                        'validated': False
                    })

            # Análise de sentimento (básica)
            sentiment_score = self._calculate_basic_sentiment(doc)
            analysis_result['sentiment'] = sentiment_score

        except Exception as e:
            logger.error(f"Erro na análise NLP: {e}")

        return analysis_result

    def _map_spacy_entity(self, spacy_label: str) -> Optional[str]:
        """Mapeia labels do spaCy para nossos tipos de dados"""
        mapping = {
            'PERSON': 'personal',
            'ORG': 'business',
            'GPE': 'personal',  # Localizações geográficas
            'LOC': 'personal',
            'MONEY': 'financial',
            'DATE': 'documents',
            'TIME': 'documents'
        }
        return mapping.get(spacy_label)

    def _calculate_basic_sentiment(self, doc) -> float:
        """Calcula sentimento básico baseado em palavras positivas/negativas"""
        positive_words = {'bom', 'ótimo', 'excelente', 'positivo', 'aprovado', 'aceito'}
        negative_words = {'ruim', 'péssimo', 'negativo', 'reprovado', 'recusado', 'erro'}

        positive_count = sum(1 for token in doc if token.lemma_.lower() in positive_words)
        negative_count = sum(1 for token in doc if token.lemma_.lower() in negative_words)

        total_words = len([token for token in doc if token.is_alpha])

        if total_words == 0:
            return 0.5

        sentiment = (positive_count - negative_count) / total_words
        return max(0, min(1, (sentiment + 1) / 2))  # Normalizar para 0-1

    def _save_analysis_results(self, capture_id: int, analysis_result: Dict[str, Any]):
        """Salva resultados da análise no banco de dados"""
        try:
            # Salvar dados extraídos
            for data_item in analysis_result.get('extracted_data', []):
                extracted_data = ExtractedData(
                    capture_id=capture_id,
                    data_type=data_item['data_type'],
                    field_name=data_item['field_name'],
                    field_value=data_item['field_value'],
                    confidence=data_item['confidence'],
                    pattern_used=data_item.get('pattern_used'),
                    validated=data_item.get('validated', False)
                )
                db_manager.execute_in_session(lambda session: session.add(extracted_data))

            # Salvar categorizações
            for category in analysis_result.get('categories', []):
                doc_category = DocumentCategory(
                    capture_id=capture_id,
                    category_name=category['category_name'],
                    confidence_score=category['confidence_score'],
                    keywords_found=category['keywords_found'],
                    ai_suggestion=category.get('ai_suggestion', True)
                )
                db_manager.execute_in_session(lambda session: session.add(doc_category))

        except Exception as e:
            logger.error(f"Erro ao salvar resultados da análise: {e}")

    def get_data_summary(self, capture_id: int) -> Dict[str, Any]:
        """Retorna resumo dos dados extraídos para uma captura"""
        try:
            session = db_manager.get_session()

            # Buscar dados extraídos
            extracted = session.query(ExtractedData)\
                             .filter(ExtractedData.capture_id == capture_id)\
                             .all()

            # Buscar categorias
            categories = session.query(DocumentCategory)\
                              .filter(DocumentCategory.capture_id == capture_id)\
                              .all()

            db_manager.close_session(session)

            # Organizar por tipo
            data_by_type = {}
            for item in extracted:
                if item.data_type not in data_by_type:
                    data_by_type[item.data_type] = []
                data_by_type[item.data_type].append(item.to_dict())

            return {
                'total_data_points': len(extracted),
                'data_by_type': data_by_type,
                'categories': [cat.to_dict() for cat in categories],
                'confidence_avg': sum(item.confidence for item in extracted) / len(extracted) if extracted else 0
            }

        except Exception as e:
            logger.error(f"Erro ao obter resumo de dados: {e}")
            return {'total_data_points': 0, 'data_by_type': {}, 'categories': [], 'confidence_avg': 0}

    def improve_extraction_patterns(self, feedback_data: Dict[str, Any]):
        """
        Aprende com feedback do usuário para melhorar padrões de extração

        Args:
            feedback_data: Dados de feedback com correções
        """
        try:
            # Implementação básica de aprendizado
            # Em produção, isso seria mais sofisticado
            for correction in feedback_data.get('corrections', []):
                field_name = correction.get('field_name')
                correct_value = correction.get('correct_value')
                incorrect_value = correction.get('incorrect_value')

                if field_name and correct_value and incorrect_value:
                    # Atualizar padrões baseado no feedback
                    logger.info(f"Aprendizado: {field_name} - '{incorrect_value}' -> '{correct_value}'")

        except Exception as e:
            logger.error(f"Erro no aprendizado: {e}")

# Instância global
data_analyzer = DataAnalyzer()
