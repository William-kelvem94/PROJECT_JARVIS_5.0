"""
Modelos de dados e configurações do banco de dados
Define todas as tabelas e relacionamentos do sistema
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import logging
from src.utils.config import config

logger = logging.getLogger(__name__)

Base = declarative_base()

class Capture(Base):
    """Modelo para capturas de tela"""
    __tablename__ = 'captures'

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)
    file_size_mb = Column(Float, nullable=False)
    capture_type = Column(String(50), default='screenshot')  # screenshot, recording
    capture_method = Column(String(50), default='manual')  # manual, auto, timer
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    format = Column(String(10), default='PNG')
    quality = Column(Integer, default=95)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    processing_status = Column(String(20), default='pending')  # pending, processing, completed, failed

    # Relacionamentos
    ocr_results = relationship("OCRResult", back_populates="capture", cascade="all, delete-orphan")
    extracted_data = relationship("ExtractedData", back_populates="capture", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Converte objeto para dicionário"""
        return {
            'id': self.id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'file_size_mb': self.file_size_mb,
            'capture_type': self.capture_type,
            'capture_method': self.capture_method,
            'width': self.width,
            'height': self.height,
            'format': self.format,
            'quality': self.quality,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'processing_status': self.processing_status
        }

class OCRResult(Base):
    """Modelo para resultados do OCR"""
    __tablename__ = 'ocr_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    capture_id = Column(Integer, ForeignKey('captures.id'), nullable=False)
    ocr_engine = Column(String(50), nullable=False)  # tesseract, easyocr
    language = Column(String(10), default='por')
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)  # segundos
    text_regions = Column(JSON, nullable=True)  # coordenadas das regiões de texto
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    capture = relationship("Capture", back_populates="ocr_results")

    def to_dict(self) -> Dict[str, Any]:
        """Converte objeto para dicionário"""
        return {
            'id': self.id,
            'capture_id': self.capture_id,
            'ocr_engine': self.ocr_engine,
            'language': self.language,
            'raw_text': self.raw_text,
            'cleaned_text': self.cleaned_text,
            'confidence_score': self.confidence_score,
            'processing_time': self.processing_time,
            'text_regions': self.text_regions,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ExtractedData(Base):
    """Modelo para dados extraídos"""
    __tablename__ = 'extracted_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    capture_id = Column(Integer, ForeignKey('captures.id'), nullable=False)
    data_type = Column(String(50), nullable=False)  # personal, financial, business, documents
    field_name = Column(String(100), nullable=False)
    field_value = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    pattern_used = Column(String(100), nullable=True)
    validated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    capture = relationship("Capture", back_populates="extracted_data")

    def to_dict(self) -> Dict[str, Any]:
        """Converte objeto para dicionário"""
        return {
            'id': self.id,
            'capture_id': self.capture_id,
            'data_type': self.data_type,
            'field_name': self.field_name,
            'field_value': self.field_value,
            'confidence': self.confidence,
            'pattern_used': self.pattern_used,
            'validated': self.validated,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DocumentCategory(Base):
    """Modelo para categorização de documentos"""
    __tablename__ = 'document_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    capture_id = Column(Integer, ForeignKey('captures.id'), nullable=False)
    category_name = Column(String(100), nullable=False)  # receipt, invoice, contract, etc.
    confidence_score = Column(Float, default=0.0)
    keywords_found = Column(JSON, nullable=True)  # palavras-chave que levaram à categorização
    ai_suggestion = Column(Boolean, default=False)  # se foi sugerido por IA
    manual_override = Column(Boolean, default=False)  # se foi definido manualmente
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    capture = relationship("Capture")

    def to_dict(self) -> Dict[str, Any]:
        """Converte objeto para dicionário"""
        return {
            'id': self.id,
            'capture_id': self.capture_id,
            'category_name': self.category_name,
            'confidence_score': self.confidence_score,
            'keywords_found': self.keywords_found,
            'ai_suggestion': self.ai_suggestion,
            'manual_override': self.manual_override,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ProcessingLog(Base):
    """Modelo para logs de processamento"""
    __tablename__ = 'processing_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    capture_id = Column(Integer, ForeignKey('captures.id'), nullable=True)
    log_level = Column(String(20), default='INFO')  # DEBUG, INFO, WARNING, ERROR
    module = Column(String(100), nullable=False)  # screen_capture, ocr_processor, etc.
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)  # informações adicionais em JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Converte objeto para dicionário"""
        return {
            'id': self.id,
            'capture_id': self.capture_id,
            'log_level': self.log_level,
            'module': self.module,
            'message': self.message,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ExportHistory(Base):
    """Modelo para histórico de exportações"""
    __tablename__ = 'export_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    export_type = Column(String(50), nullable=False)  # json, csv, pdf, excel
    file_path = Column(String(500), nullable=False)
    filters_used = Column(JSON, nullable=True)  # filtros aplicados na exportação
    record_count = Column(Integer, default=0)
    file_size_mb = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Converte objeto para dicionário"""
        return {
            'id': self.id,
            'export_type': self.export_type,
            'file_path': self.file_path,
            'filters_used': self.filters_used,
            'record_count': self.record_count,
            'file_size_mb': self.file_size_mb,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DatabaseManager:
    """Gerenciador do banco de dados"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()

    def _initialize_database(self):
        """Inicializa conexão com banco de dados"""
        try:
            # Criar engine SQLite
            database_url = f"sqlite:///{config.DATABASE_FILE}"
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},  # Necessário para SQLite
                echo=False  # Desabilitar logs SQL em produção
            )

            # Criar sessão
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Criar todas as tabelas
            Base.metadata.create_all(bind=self.engine)

            logger.info("Banco de dados inicializado com sucesso")

        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise

    def get_session(self):
        """Retorna uma sessão do banco de dados"""
        return self.SessionLocal()

    def close_session(self, session):
        """Fecha uma sessão do banco de dados"""
        if session:
            session.close()

    def execute_in_session(self, operation, *args, **kwargs):
        """Executa operação no banco de dados com tratamento de erro"""
        session = self.get_session()
        try:
            result = operation(session, *args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            logger.error(f"Erro na operação do banco: {e}")
            raise
        finally:
            self.close_session(session)

    def get_capture_by_hash(self, file_hash: str) -> Optional[Capture]:
        """Busca captura por hash do arquivo"""
        def _query(session):
            return session.query(Capture).filter(Capture.file_hash == file_hash).first()

        return self.execute_in_session(_query)

    def get_recent_captures(self, limit: int = 50) -> List[Capture]:
        """Busca capturas recentes"""
        def _query(session):
            return session.query(Capture)\
                         .order_by(Capture.created_at.desc())\
                         .limit(limit)\
                         .all()

        return self.execute_in_session(_query)

    def get_unprocessed_captures(self) -> List[Capture]:
        """Busca capturas não processadas"""
        def _query(session):
            return session.query(Capture)\
                         .filter(Capture.processing_status == 'pending')\
                         .order_by(Capture.created_at.asc())\
                         .all()

        return self.execute_in_session(_query)

    def update_processing_status(self, capture_id: int, status: str, processed_at: datetime = None):
        """Atualiza status de processamento de uma captura"""
        def _update(session):
            capture = session.query(Capture).filter(Capture.id == capture_id).first()
            if capture:
                capture.processing_status = status
                if processed_at:
                    capture.processed_at = processed_at
                session.commit()

        self.execute_in_session(_update)

    def search_extracted_data(self, query: str, data_type: str = None) -> List[ExtractedData]:
        """Busca dados extraídos"""
        def _search(session):
            q = session.query(ExtractedData)\
                      .filter(ExtractedData.field_value.contains(query))
            if data_type:
                q = q.filter(ExtractedData.data_type == data_type)
            return q.order_by(ExtractedData.created_at.desc()).all()

        return self.execute_in_session(_search)

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema"""
        def _stats(session):
            total_captures = session.query(Capture).count()
            processed_captures = session.query(Capture)\
                                       .filter(Capture.processing_status == 'completed')\
                                       .count()
            total_ocr_results = session.query(OCRResult).count()
            total_extracted_data = session.query(ExtractedData).count()

            # Estatísticas por tipo de dados
            data_types = session.query(
                ExtractedData.data_type,
                session.func.count(ExtractedData.id).label('count')
            ).group_by(ExtractedData.data_type).all()

            return {
                'total_captures': total_captures,
                'processed_captures': processed_captures,
                'processing_rate': processed_captures / total_captures if total_captures > 0 else 0,
                'total_ocr_results': total_ocr_results,
                'total_extracted_data': total_extracted_data,
                'data_types_breakdown': {dt.data_type: dt.count for dt in data_types}
            }

        return self.execute_in_session(_stats)

    def cleanup_old_data(self, days_to_keep: int = 365):
        """Remove dados antigos"""
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days_to_keep)

        def _cleanup(session):
            # Remover capturas antigas e seus dados relacionados (cascade delete)
            old_captures = session.query(Capture)\
                                 .filter(Capture.created_at < cutoff_date)\
                                 .all()

            count = len(old_captures)
            for capture in old_captures:
                session.delete(capture)

            session.commit()
            return count

        deleted_count = self.execute_in_session(_cleanup)
        logger.info(f"Removidos {deleted_count} registros antigos")
        return deleted_count

# Instância global do gerenciador de banco de dados
db_manager = DatabaseManager()
