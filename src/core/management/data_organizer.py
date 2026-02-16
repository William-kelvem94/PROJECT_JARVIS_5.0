"""
Organizador de dados extraÃ­dos
Estrutura e salva dados em diferentes formatos
"""

import os
import json
import csv
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from src.utils.config import config
from src.utils.helpers import FileHelper, DataHelper
from src.database.models import db_manager, ExtractedData, DocumentCategory, ExportHistory

logger = logging.getLogger(__name__)

class DataOrganizer:
    """Classe para organizaÃ§Ã£o e exportaÃ§Ã£o de dados"""

    def __init__(self):
        self.exports_dir = config.DATA_DIR / "exports"
        self.templates_dir = config.DATA_DIR / "templates"

        # Criar diretÃ³rios necessÃ¡rios
        self.exports_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)

        # ConfiguraÃ§Ãµes de exportaÃ§Ã£o
        self.export_formats = {
            'json': self._export_json,
            'csv': self._export_csv,
            'excel': self._export_excel,
            'pdf': self._export_pdf,
            'txt': self._export_txt
        }

        logger.info("Organizador de dados inicializado")

    def organize_capture_data(self, capture_id: int) -> Dict[str, Any]:
        """
        Organiza dados de uma captura especÃ­fica

        Args:
            capture_id: ID da captura

        Returns:
            Dados organizados por categoria
        """
        try:
            session = db_manager.get_session()

            # Buscar dados extraÃ­dos
            extracted_data = session.query(ExtractedData)\
                                  .filter(ExtractedData.capture_id == capture_id)\
                                  .all()

            # Buscar categorias
            categories = session.query(DocumentCategory)\
                              .filter(DocumentCategory.capture_id == capture_id)\
                              .all()

            db_manager.close_session(session)

            # Organizar dados por categoria
            organized_data = {
                'capture_id': capture_id,
                'timestamp': datetime.now().isoformat(),
                'categories': [cat.category_name for cat in categories],
                'primary_category': categories[0].category_name if categories else 'unknown',
                'data_sections': {}
            }

            # Agrupar dados por tipo
            data_by_type = {}
            for item in extracted_data:
                data_type = item.data_type
                if data_type not in data_by_type:
                    data_by_type[data_type] = []

                data_by_type[data_type].append({
                    'field': item.field_name,
                    'value': item.field_value,
                    'confidence': item.confidence,
                    'validated': item.validated
                })

            organized_data['data_sections'] = data_by_type

            # Calcular estatÃ­sticas
            organized_data['statistics'] = {
                'total_fields': len(extracted_data),
                'fields_by_type': {k: len(v) for k, v in data_by_type.items()},
                'avg_confidence': sum(item.confidence for item in extracted_data) / len(extracted_data) if extracted_data else 0
            }

            return organized_data

        except Exception as e:
            logger.error(f"Erro ao organizar dados da captura {capture_id}: {e}")
            return {}

    def export_data(self, data: Dict[str, Any], format_type: str,
                   filename: Optional[str] = None) -> Optional[str]:
        """
        Exporta dados organizados

        Args:
            data: Dados a serem exportados
            format_type: Formato (json, csv, excel, pdf, txt)
            filename: Nome do arquivo (opcional)

        Returns:
            Caminho do arquivo exportado ou None se erro
        """
        try:
            if format_type not in self.export_formats:
                raise ValueError(f"Formato nÃ£o suportado: {format_type}")

            # Gerar nome de arquivo se nÃ£o fornecido
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"export_{timestamp}.{format_type}"

            file_path = self.exports_dir / filename

            # Executar exportaÃ§Ã£o
            export_func = self.export_formats[format_type]
            result_path = export_func(data, str(file_path))

            if result_path:
                # Registrar exportaÃ§Ã£o no banco
                self._register_export(format_type, result_path, data)

                logger.info(f"Dados exportados: {result_path}")
                return result_path

        except Exception as e:
            logger.error(f"Erro na exportaÃ§Ã£o: {e}")

        return None

    def _export_json(self, data: Dict[str, Any], file_path: str) -> str:
        """Exporta dados em formato JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return file_path
        except Exception as e:
            logger.error(f"Erro na exportaÃ§Ã£o JSON: {e}")
            return ""

    def _export_csv(self, data: Dict[str, Any], file_path: str) -> str:
        """Exporta dados em formato CSV"""
        try:
            # Preparar dados para CSV
            csv_data = self._flatten_data_for_csv(data)

            if not csv_data:
                # Criar CSV vazio com headers
                csv_data = [{'Campo': '', 'Valor': '', 'Tipo': '', 'ConfianÃ§a': ''}]

            # Escrever CSV
            fieldnames = csv_data[0].keys()
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)

            return file_path

        except Exception as e:
            logger.error(f"Erro na exportaÃ§Ã£o CSV: {e}")
            return ""

    def _export_excel(self, data: Dict[str, Any], file_path: str) -> str:
        """Exporta dados em formato Excel"""
        try:
            # Preparar dados para Excel
            csv_data = self._flatten_data_for_csv(data)

            if csv_data:
                df = pd.DataFrame(csv_data)
                df.to_excel(file_path, index=False, engine='openpyxl')

            return file_path

        except Exception as e:
            logger.error(f"Erro na exportaÃ§Ã£o Excel: {e}")
            return ""

    def _export_pdf(self, data: Dict[str, Any], file_path: str) -> str:
        """Exporta dados em formato PDF"""
        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # TÃ­tulo
            title = Paragraph("RelatÃ³rio de Dados ExtraÃ­dos", styles['Heading1'])
            story.append(title)

            # InformaÃ§Ãµes bÃ¡sicas
            info_text = f"""
            <b>Captura ID:</b> {data.get('capture_id', 'N/A')}<br/>
            <b>Data:</b> {data.get('timestamp', 'N/A')}<br/>
            <b>Categoria Principal:</b> {data.get('primary_category', 'N/A')}<br/>
            <b>Total de Campos:</b> {data.get('statistics', {}).get('total_fields', 0)}
            """
            story.append(Paragraph(info_text, styles['Normal']))

            # Tabela de dados
            csv_data = self._flatten_data_for_csv(data)
            if csv_data:
                # Preparar dados para tabela
                table_data = [['Campo', 'Valor', 'Tipo', 'ConfianÃ§a']]
                for item in csv_data:
                    table_data.append([
                        item.get('Campo', ''),
                        item.get('Valor', ''),
                        item.get('Tipo', ''),
                        f"{item.get('ConfianÃ§a', 0):.2f}"
                    ])

                # Criar tabela
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                story.append(table)

            doc.build(story)
            return file_path

        except Exception as e:
            logger.error(f"Erro na exportaÃ§Ã£o PDF: {e}")
            return ""

    def _export_txt(self, data: Dict[str, Any], file_path: str) -> str:
        """Exporta dados em formato texto"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("RELATÃ“RIO DE DADOS EXTRAÃDOS\n")
                f.write("=" * 50 + "\n\n")

                f.write(f"Captura ID: {data.get('capture_id', 'N/A')}\n")
                f.write(f"Data: {data.get('timestamp', 'N/A')}\n")
                f.write(f"Categoria: {data.get('primary_category', 'N/A')}\n\n")

                # Escrever dados por seÃ§Ã£o
                for section_name, items in data.get('data_sections', {}).items():
                    f.write(f"[{section_name.upper()}]\n")
                    for item in items:
                        f.write(f"  {item['field']}: {item['value']} (ConfianÃ§a: {item['confidence']:.2f})\n")
                    f.write("\n")

            return file_path

        except Exception as e:
            logger.error(f"Erro na exportaÃ§Ã£o TXT: {e}")
            return ""

    def _flatten_data_for_csv(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prepara dados para exportaÃ§Ã£o CSV/Excel"""
        flattened = []

        for section_name, items in data.get('data_sections', {}).items():
            for item in items:
                flattened.append({
                    'Campo': item['field'],
                    'Valor': item['value'],
                    'Tipo': section_name,
                    'ConfianÃ§a': item['confidence'],
                    'Validado': 'Sim' if item['validated'] else 'NÃ£o'
                })

        return flattened

    def _register_export(self, format_type: str, file_path: str, data: Dict[str, Any]):
        """Registra exportaÃ§Ã£o no banco de dados"""
        try:
            export_record = ExportHistory(
                export_type=format_type,
                file_path=file_path,
                record_count=data.get('statistics', {}).get('total_fields', 0),
                file_size_mb=FileHelper.get_file_size_mb(file_path)
            )

            db_manager.execute_in_session(lambda session: session.add(export_record))

        except Exception as e:
            logger.error(f"Erro ao registrar exportaÃ§Ã£o: {e}")

    def create_data_package(self, capture_ids: List[int], package_name: str) -> Optional[str]:
        """
        Cria pacote completo de dados para mÃºltiplas capturas

        Args:
            capture_ids: Lista de IDs de captura
            package_name: Nome do pacote

        Returns:
            Caminho do pacote criado ou None se erro
        """
        try:
            # Criar diretÃ³rio do pacote
            package_dir = self.exports_dir / package_name
            package_dir.mkdir(exist_ok=True)

            all_data = []

            # Processar cada captura
            for capture_id in capture_ids:
                capture_data = self.organize_capture_data(capture_id)
                if capture_data:
                    all_data.append(capture_data)

                    # Exportar dados individuais
                    json_file = package_dir / f"capture_{capture_id}.json"
                    self._export_json(capture_data, str(json_file))

            # Criar arquivo consolidado
            consolidated = {
                'package_name': package_name,
                'created_at': datetime.now().isoformat(),
                'total_captures': len(all_data),
                'captures': all_data
            }

            consolidated_file = package_dir / "consolidated.json"
            self._export_json(consolidated, str(consolidated_file))

            # Criar arquivo CSV consolidado
            all_flattened = []
            for capture_data in all_data:
                flattened = self._flatten_data_for_csv(capture_data)
                for item in flattened:
                    item['Captura_ID'] = capture_data['capture_id']
                    all_flattened.append(item)

            if all_flattened:
                csv_file = package_dir / "all_data.csv"
                fieldnames = ['Captura_ID'] + list(all_flattened[0].keys())
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(all_flattened)

            logger.info(f"Pacote de dados criado: {package_dir}")
            return str(package_dir)

        except Exception as e:
            logger.error(f"Erro ao criar pacote de dados: {e}")
            return None

    def get_export_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna histÃ³rico de exportaÃ§Ãµes"""
        try:
            session = db_manager.get_session()
            exports = session.query(ExportHistory)\
                           .order_by(ExportHistory.created_at.desc())\
                           .limit(limit)\
                           .all()
            db_manager.close_session(session)

            return [exp.to_dict() for exp in exports]

        except Exception as e:
            logger.error(f"Erro ao obter histÃ³rico de exportaÃ§Ãµes: {e}")
            return []

    def cleanup_old_exports(self, days_to_keep: int = 30):
        """Remove exportaÃ§Ãµes antigas"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)

            for export_file in self.exports_dir.glob("*"):
                if export_file.is_file():
                    file_age = export_file.stat().st_mtime
                    if file_age < cutoff_date:
                        export_file.unlink()
                        logger.info(f"ExportaÃ§Ã£o antiga removida: {export_file}")

        except Exception as e:
            logger.error(f"Erro ao limpar exportaÃ§Ãµes antigas: {e}")

    def get_data_templates(self) -> Dict[str, Dict[str, Any]]:
        """Retorna templates disponÃ­veis para organizaÃ§Ã£o de dados"""
        templates = {
            'invoice': {
                'name': 'Fatura',
                'fields': ['numero', 'data_emissao', 'data_vencimento', 'valor', 'pagador', 'beneficiario'],
                'required_fields': ['numero', 'valor']
            },
            'receipt': {
                'name': 'Nota Fiscal',
                'fields': ['numero', 'serie', 'data', 'valor', 'emitente', 'destinatario'],
                'required_fields': ['numero', 'valor', 'data']
            },
            'contract': {
                'name': 'Contrato',
                'fields': ['numero', 'partes', 'objeto', 'valor', 'data_inicio', 'data_fim'],
                'required_fields': ['numero', 'partes', 'objeto']
            },
            'personal_data': {
                'name': 'Dados Pessoais',
                'fields': ['nome', 'cpf', 'rg', 'endereco', 'telefone', 'email'],
                'required_fields': ['nome']
            }
        }

        return templates

    def apply_template(self, data: Dict[str, Any], template_name: str) -> Dict[str, Any]:
        """
        Aplica template de organizaÃ§Ã£o aos dados

        Args:
            data: Dados a serem organizados
            template_name: Nome do template

        Returns:
            Dados organizados segundo o template
        """
        try:
            templates = self.get_data_templates()
            template = templates.get(template_name)

            if not template:
                logger.warning(f"Template nÃ£o encontrado: {template_name}")
                return data

            organized = {
                'template_applied': template_name,
                'template_name': template['name'],
                'organized_fields': {},
                'missing_required': []
            }

            # Organizar campos segundo template
            all_fields = {}
            for section in data.get('data_sections', {}).values():
                for item in section:
                    all_fields[item['field']] = item

            # Mapear campos do template
            for template_field in template['fields']:
                if template_field in all_fields:
                    organized['organized_fields'][template_field] = all_fields[template_field]
                else:
                    organized['organized_fields'][template_field] = None

                    # Verificar se Ã© campo obrigatÃ³rio
                    if template_field in template['required_fields']:
                        organized['missing_required'].append(template_field)

            return organized

        except Exception as e:
            logger.error(f"Erro ao aplicar template {template_name}: {e}")
            return data

# InstÃ¢ncia global
data_organizer = DataOrganizer()
