# JARVIS 5.0 - Arquitetura do Sistema

## Visão Geral

O JARVIS 5.0 foi projetado com uma arquitetura modular que separa responsabilidades e facilita manutenção e extensibilidade.

## Estrutura de Módulos

### 🏗️ Core (`jarvis/core/`)

Módulos centrais que fornecem funcionalidades base:

- **`assistant.py`**: Classe principal que orquestra todos os componentes
- **`config.py`**: Gerenciamento robusto de configurações
- **`logger.py`**: Sistema de logging estruturado

### 🎤 Voice (`jarvis/voice/`)

Processamento de áudio e voz:

- **`speech_engine.py`**: Síntese de voz com gTTS e pyttsx3
- **`recognition_engine.py`**: Reconhecimento de fala com speech_recognition
- **`natural_speech.py`**: Processamento para naturalidade extrema

### ⚡ Commands (`jarvis/commands/`)

Sistema de comandos modular:

- **`command_processor.py`**: Processador central de comandos
- **`system_commands.py`**: Comandos relacionados ao sistema operacional
- **`utility_commands.py`**: Comandos utilitários (hora, data, cálculos, etc.)

## Fluxo de Dados

```
Usuário fala → RecognitionEngine → CommandProcessor → [SystemCommands|UtilityCommands] → SpeechEngine → Resposta falada
```

## Padrões de Design

### 1. **Dependency Injection**
Componentes recebem suas dependências via construtor:
```python
def __init__(self, config, speech_engine, recognition_engine):
```

### 2. **Strategy Pattern**
Diferentes engines de voz (gTTS vs pyttsx3) implementam a mesma interface.

### 3. **Observer Pattern**
Sistema de logging observa eventos de todos os componentes.

### 4. **Factory Pattern**
ConfigManager cria configurações baseadas em arquivos ou padrões.

## Configuração

### Hierarquia de Configuração
1. Arquivo especificado pelo usuário
2. `config.json` padrão
3. Configuração hardcoded como fallback

### Estrutura de Configuração
```json
{
  "voice": { ... },
  "recognition": { ... },
  "system": { ... },
  "commands": { ... },
  "natural_speech": { ... }
}
```

## Sistema de Logging

### Níveis de Log
- **DEBUG**: Informações detalhadas para desenvolvimento
- **INFO**: Eventos normais de operação
- **WARNING**: Situações que merecem atenção
- **ERROR**: Erros que não impedem funcionamento
- **CRITICAL**: Erros que impedem funcionamento

### Tipos de Eventos
- **VOICE_EVENT**: Eventos relacionados à síntese/reconhecimento
- **COMMAND**: Execução de comandos
- **PERFORMANCE**: Métricas de tempo de execução

## Tratamento de Erros

### Estratégias por Módulo

**Voice Engine:**
- Fallback automático gTTS → pyttsx3
- Retry com configurações diferentes
- Mensagens de erro contextuais

**Recognition Engine:**
- Timeout configurável
- Calibração automática
- Tratamento de ruído ambiente

**Command Processor:**
- Validação de entrada
- Sugestões para comandos não reconhecidos
- Execução segura de comandos do sistema

## Extensibilidade

### Adicionando Novos Comandos
1. Criar função handler
2. Registrar no CommandProcessor
3. Adicionar testes

### Adicionando Novos Engines
1. Implementar interface comum
2. Registrar no factory
3. Adicionar configuração

### Adicionando Novas Emoções
1. Definir parâmetros de voz
2. Adicionar ao NaturalSpeechProcessor
3. Configurar triggers contextuais

## Performance

### Otimizações Implementadas
- Lazy loading de módulos pesados
- Cache de configurações
- Processamento assíncrono quando possível
- Limpeza automática de recursos temporários

### Métricas Monitoradas
- Tempo de resposta por comando
- Uso de memória por componente
- Taxa de sucesso de reconhecimento
- Latência de síntese de voz

## Segurança

### Validação de Comandos
- Lista branca de comandos seguros
- Lista negra de comandos perigosos
- Sanitização de parâmetros
- Timeout para execução

### Proteções Implementadas
- Não execução de scripts arbitrários
- Validação de caminhos de arquivo
- Limitação de recursos do sistema
- Logging de tentativas suspeitas

## Testes

### Tipos de Teste
- **Unitários**: Cada módulo isoladamente
- **Integração**: Interação entre módulos
- **Sistema**: Funcionalidade end-to-end
- **Performance**: Benchmarks de velocidade

### Cobertura
- Todos os comandos principais
- Cenários de erro
- Configurações diferentes
- Diferentes sistemas operacionais
