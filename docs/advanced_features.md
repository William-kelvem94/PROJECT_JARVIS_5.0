# ⚡ Funcionalidades Avançadas - Leitor de Tela Inteligente

Este guia explora recursos avançados e técnicas especializadas do Leitor de Tela Inteligente.

## 🧠 Análise Inteligente

### Reconhecimento de Documentos

O sistema identifica automaticamente tipos de documento:

#### Documentos Suportados
- **📄 Notas Fiscais** - Extração de CNPJ, valores, datas
- **🧾 Faturas** - Identificação de vencimentos, valores
- **📋 Contratos** - Reconhecimento de partes, objetos
- **📊 Relatórios** - Categorização de conteúdo
- **📝 Formulários** - Extração de campos preenchidos

#### Como Funciona
```python
# Análise automática
from src.core.data_analyzer import data_analyzer

text = "NOTA FISCAL Nº 123456 VALOR R$ 1.234,56"
result = data_analyzer.analyze_text(text)

print(result['categories'])
# [{'category_name': 'receipt', 'confidence_score': 0.89}]
```

### Extração de Entidades

#### Padrões Reconhecidos
- **Pessoal:** CPF, CNPJ, emails, telefones, endereços
- **Financeiro:** Valores monetários, contas bancárias
- **Documentos:** Datas, códigos, números de referência

#### Exemplo de Extração
```json
{
  "extracted_data": [
    {
      "field_name": "cpf",
      "field_value": "123.456.789-00",
      "data_type": "personal",
      "confidence": 0.95
    },
    {
      "field_name": "money",
      "field_value": "R$ 1.234,56",
      "data_type": "financial",
      "confidence": 0.90
    }
  ]
}
```

## 🎬 Gravação e Monitoramento

### Gravação de Tela

#### Recursos Avançados
```python
from src.core.screen_capture import screen_capture

# Gravação com configurações avançadas
screen_capture.start_screen_recording(
    region=(100, 100, 800, 600),  # Área específica
    duration=300,                  # 5 minutos
    output_path="gravacao.mp4"
)
```

#### Compressão Inteligente
- **Formatos:** AVI, MP4
- **Codecs:** XVID, H264
- **Qualidade:** Ajustável (10-30 FPS)
- **Compressão:** Automática por tamanho

### Monitoramento Contínuo

#### Captura por Timer
```bash
# Captura a cada 30 segundos
python main.py capture --timer 30 --process --export --format json
```

#### Monitoramento de Janelas
```python
# Monitorar janela específica
screen_capture.start_timer_capture(
    interval_seconds=60,
    window_title="Sistema ERP",
    max_captures=100
)
```

## 🔍 OCR Avançado

### Engines Disponíveis

#### Tesseract OCR
- **Vantagens:** Rápido, preciso para texto claro
- **Configuração:**
```json
{
  "ocr": {
    "engine": "tesseract",
    "config": "--oem 3 --psm 6",
    "timeout": 30
  }
}
```

#### EasyOCR
- **Vantagens:** Melhor com texto distorcido, suporta mais idiomas
- **Configuração:**
```json
{
  "ocr": {
    "engine": "easyocr",
    "gpu": true,
    "detect_network": "craft"
  }
}
```

#### Modo Híbrido
- **Combina:** Melhor dos dois engines
- **Quando usar:** Texto complexo ou baixa qualidade

### Pré-processamento de Imagens

#### Técnicas Aplicadas
1. **Conversão para escala de cinza**
2. **Ajuste de contraste**
3. **Redimensionamento inteligente**
4. **Redução de ruído**
5. **Detecção de orientação**

#### Configuração
```json
{
  "ocr": {
    "preprocessing": true,
    "enhance_contrast": 2.0,
    "max_width": 2000
  }
}
```

## 📊 Organização Inteligente

### Sistema de Categorias

#### Categorias Automáticas
```python
from src.core.data_organizer import data_organizer

# Organizar dados capturados
organized = data_organizer.organize_capture_data(capture_id=123)

print(organized['primary_category'])  # 'receipt'
print(organized['statistics'])        # Estatísticas detalhadas
```

#### Templates Personalizados
```python
# Aplicar template específico
result = data_organizer.apply_template(organized_data, 'invoice')

# Campos organizados segundo template
print(result['organized_fields'])
# {'numero': 'NF123', 'valor': 'R$ 100,00', 'data': '2023-12-01'}
```

### Exportação Avançada

#### Formatos Especiais
```python
# Exportação com filtros
data_organizer.export_data(
    data=organized_data,
    format_type='excel',
    filename='relatorio_filtrado.xlsx',
    filters={'data_type': 'financial'}
)
```

#### Pacotes de Dados
```python
# Criar pacote completo
package_path = data_organizer.create_data_package(
    capture_ids=[1, 2, 3, 4, 5],
    package_name='relatorio_mensal'
)

print(f"Pacote criado: {package_path}")
# data/exports/relatorio_mensal/
# ├── consolidated.json
# ├── all_data.csv
# └── capture_1.json
```

## 🔗 APIs e Integração

### API REST Local

#### Endpoints Disponíveis
```python
from fastapi import FastAPI
from src.api.server import app

# Endpoints principais
# GET  /captures          - Listar capturas
# POST /capture           - Nova captura
# GET  /capture/{id}      - Detalhes da captura
# POST /process/{id}      - Processar captura
# GET  /exports           - Listar exportações
# POST /export            - Criar exportação
```

#### Uso da API
```bash
# Iniciar servidor
python -c "from src.api.server import run_server; run_server()"

# Exemplos de uso
curl -X POST http://localhost:8000/capture
curl -X GET http://localhost:8000/captures
curl -X POST http://localhost:8000/process/123
```

### Webhooks

#### Configuração
```json
{
  "webhooks": {
    "on_capture_complete": "http://meu-sistema.com/webhook/captura",
    "on_processing_complete": "http://meu-sistema.com/webhook/processamento",
    "on_export_complete": "http://meu-sistema.com/webhook/exportacao"
  }
}
```

#### Integração com Sistemas Externos
```python
# Enviar dados para sistema externo
import requests

def send_to_external_system(data):
    response = requests.post(
        'https://api.sistema-externo.com/import',
        json=data,
        headers={'Authorization': 'Bearer TOKEN'}
    )
    return response.status_code == 200
```

## 🔧 Personalização Avançada

### Padrões de Extração Customizados

#### Adicionar Novos Padrões
```python
from src.utils.config import config

# Adicionar padrão personalizado
config.extraction_patterns['codigo_produto'] = r'PROD-\d{6}'

# Usar na análise
result = data_analyzer.analyze_text("Produto: PROD-123456")
print(result['extracted_data'][0]['field_value'])  # 'PROD-123456'
```

### Criação de Templates

#### Template Personalizado
```python
# Definir template
custom_template = {
    'name': 'Recibo Personalizado',
    'fields': ['numero_recibo', 'valor_pago', 'data_pagamento'],
    'required_fields': ['numero_recibo', 'valor_pago']
}

# Registrar template
data_organizer.templates['custom_receipt'] = custom_template
```

## ⚡ Performance e Otimização

### Configurações de Performance

#### Processamento Paralelo
```json
{
  "processing": {
    "max_workers": 4,
    "batch_size": 10,
    "timeout": 30
  }
}
```

#### Cache Inteligente
- **Resultados OCR:** Evita reprocessamento
- **Análises:** Cache de padrões encontrados
- **Imagens:** Compressão automática

### Monitoramento de Recursos

#### Status do Sistema
```python
from src.utils.helpers import system_helper

info = system_helper.get_system_info()
print(f"CPU: {info['cpu_count']} cores")
print(f"Memória: {info['memory_total']:.1f}GB total")
print(f"Disco: {info['disk_free']:.1f}GB livre")
```

## 🔒 Segurança e Privacidade

### Criptografia de Dados

#### Configuração de Segurança
```json
{
  "storage": {
    "encryption": true,
    "key_file": "config/encryption.key",
    "sensitive_fields": ["cpf", "cnpj", "email"]
  }
}
```

### Limpeza Automática

#### Políticas de Retenção
```python
# Limpar dados antigos
from src.database.models import db_manager

# Remover capturas com mais de 1 ano
db_manager.cleanup_old_data(days_to_keep=365)

# Limpar exportações antigas
data_organizer.cleanup_old_exports(days_to_keep=30)
```

## 📈 Análise Estatística

### Métricas de Uso

#### Estatísticas do Sistema
```python
stats = db_manager.get_statistics()
print(f"Total de capturas: {stats['total_captures']}")
print(f"Taxa de processamento: {stats['processing_rate']:.1%}")
print(f"Tipos de dados: {stats['data_types_breakdown']}")
```

#### Relatórios de Performance
```python
# Análise de performance
performance_report = {
    'avg_ocr_time': 2.3,  # segundos
    'success_rate': 0.94, # 94%
    'most_common_errors': ['low_quality_image', 'timeout'],
    'storage_used': '2.4GB'
}
```

## 🚀 Automação Avançada

### Scripts de Automação

#### Exemplo: Monitoramento Contínuo
```python
#!/usr/bin/env python3
"""
Script de monitoramento automático
"""

import time
import schedule
from src.core.screen_capture import screen_capture
from src.core.ocr_processor import ocr_processor
from src.core.data_analyzer import data_analyzer

def job_monitoramento():
    """Job de monitoramento periódico"""
    # Capturar dashboard
    capture_path = screen_capture.capture_window("Dashboard ERP")

    if capture_path:
        # Processar
        ocr_result = ocr_processor.process_image(capture_path)

        # Analisar
        analysis = data_analyzer.analyze_text(ocr_result['cleaned_text'])

        # Verificar alertas
        check_alerts(analysis)

def check_alerts(analysis):
    """Verificar condições de alerta"""
    for data_item in analysis['extracted_data']:
        if data_item['field_name'] == 'saldo' and float(data_item['field_value']) < 1000:
            send_alert("Saldo baixo detectado!")

# Agendar execução
schedule.every(5).minutes.do(job_monitoramento)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Integração com Tarefas Agendadas

#### Windows Task Scheduler
```xml
<!-- Task Scheduler XML -->
<Task version="1.2">
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2023-12-01T09:00:00</StartBoundary>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>python.exe</Command>
      <Arguments>C:\path\to\leitor-tela\scripts\backup_diario.py</Arguments>
    </Exec>
  </Actions>
</Task>
```

## 🔧 Desenvolvimento de Plugins

### Estrutura de Plugin

#### Exemplo de Plugin
```python
# plugins/extrator_nfe.py
from src.core.plugin_base import PluginBase

class NFEExtractorPlugin(PluginBase):
    """Plugin para extração específica de NF-e"""

    def get_name(self):
        return "NF-e Extractor"

    def get_version(self):
        return "1.0.0"

    def can_handle(self, text: str) -> bool:
        return "nota fiscal eletrônica" in text.lower()

    def extract_data(self, text: str) -> dict:
        # Lógica específica para NF-e
        nfe_data = {
            'chave_acesso': self.extract_chave_acesso(text),
            'numero': self.extract_numero(text),
            'serie': self.extract_serie(text)
        }
        return nfe_data

    def extract_chave_acesso(self, text: str) -> str:
        # Lógica específica
        import re
        match = re.search(r'\b\d{44}\b', text)
        return match.group(0) if match else ""
```

## 📚 Casos de Uso Avançados

### 1. Integração com ERPs

```python
def integrar_com_erp(dados_extraidos):
    """Integra dados extraídos com sistema ERP"""
    # Mapear campos do Leitor para campos do ERP
    mapeamento = {
        'numero_nf': dados_extraidos.get('numero'),
        'valor_total': dados_extraidos.get('valor'),
        'data_emissao': dados_extraidos.get('data')
    }

    # Enviar para API do ERP
    requests.post('https://erp.empresa.com/api/notas-fiscais', json=mapeamento)
```

### 2. Validação em Tempo Real

```python
def validar_em_tempo_real(capture_path):
    """Validação imediata de documentos"""
    # Processar rapidamente
    ocr_result = ocr_processor.process_image(capture_path)

    # Verificar campos obrigatórios
    required_fields = ['numero', 'valor', 'data']
    extracted_fields = [item['field_name'] for item in ocr_result['extracted_data']]

    missing_fields = set(required_fields) - set(extracted_fields)

    if missing_fields:
        return False, f"Campos obrigatórios faltando: {missing_fields}"

    return True, "Documento válido"
```

### 3. Relatórios Automatizados

```python
def gerar_relatorio_mensal():
    """Gera relatório mensal de extrações"""
    # Buscar dados do mês
    monthly_data = db_manager.get_data_by_date_range(
        start_date='2023-12-01',
        end_date='2023-12-31'
    )

    # Criar relatório
    report = {
        'periodo': 'Dezembro 2023',
        'total_capturas': len(monthly_data),
        'categorias': {},
        'performance': {}
    }

    # Análise estatística
    for item in monthly_data:
        cat = item.category
        report['categorias'][cat] = report['categorias'].get(cat, 0) + 1

    # Exportar
    data_organizer.export_data(report, 'pdf', 'relatorio_dezembro_2023.pdf')
```

---

## 🎯 Conclusão

O Leitor de Tela Inteligente oferece recursos avançados para cenários complexos de extração de dados. Com APIs extensíveis, automação poderosa e capacidades de integração, é possível criar soluções sofisticadas para diversos casos de uso empresariais e pessoais.

**Próximos passos:**
- Explore a [API de Integração](api.md)
- Aprenda sobre [Plugins Personalizados](plugins.md)
- Veja exemplos em [Casos de Uso](use_cases.md)
