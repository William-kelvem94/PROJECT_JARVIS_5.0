# JARVIS 5.0 - API Reference

## Core Classes

### JarvisAssistant

Classe principal do assistente.

```python
from jarvis import JarvisAssistant

assistant = JarvisAssistant(config_path="config.json")
assistant.start()
```

#### Métodos

**`__init__(config_path: str = "config.json")`**
- Inicializa o assistente com configuração especificada

**`start() -> None`**
- Inicia o loop principal do assistente

**`stop() -> None`**
- Para o assistente graciosamente

**`reload_config() -> bool`**
- Recarrega configuração do arquivo
- Retorna True se sucesso

**`get_status() -> dict`**
- Retorna status atual de todos os componentes

**`test_systems() -> dict`**
- Testa todos os sistemas e retorna resultados

**`calibrate() -> bool`**
- Calibra sistema de reconhecimento
- Retorna True se sucesso

**`add_custom_command(keyword: str, handler: Callable) -> bool`**
- Adiciona comando personalizado
- `keyword`: palavra-chave que ativa o comando
- `handler`: função que processa o comando

### ConfigManager

Gerenciador de configurações.

```python
from jarvis.core.config import ConfigManager

config = ConfigManager("minha_config.json")
rate = config.get('voice.rate', 180)
config.set('voice.volume', 0.8)
config.save()
```

#### Métodos

**`get(key_path: str, default: Any = None) -> Any`**
- Obtém valor usando notação de ponto
- Exemplo: `config.get('voice.rate')`

**`set(key_path: str, value: Any) -> None`**
- Define valor usando notação de ponto
- Exemplo: `config.set('voice.rate', 200)`

**`save() -> bool`**
- Salva configuração no arquivo

**`reload() -> None`**
- Recarrega configuração do arquivo

**`reset_to_default() -> None`**
- Reseta para configuração padrão

### SpeechEngine

Engine de síntese de voz.

```python
from jarvis.voice.speech_engine import SpeechEngine

engine = SpeechEngine(config)
engine.speak("Olá mundo!", emotion="entusiasta")
```

#### Métodos

**`speak(text: str, emotion: str = None, speed: int = None, final_pause: float = 0.8) -> bool`**
- Fala texto com naturalidade extrema
- `emotion`: 'entusiasta', 'preocupado', 'pensativo', 'aliviado'
- `speed`: velocidade específica (sobrescreve config)
- `final_pause`: pausa final em segundos

**`test_voice() -> bool`**
- Testa sistema de voz

**`cleanup()`**
- Limpa recursos do engine

### RecognitionEngine

Engine de reconhecimento de voz.

```python
from jarvis.voice.recognition_engine import RecognitionEngine

engine = RecognitionEngine(config)
command = engine.listen()
```

#### Métodos

**`listen() -> Optional[str]`**
- Escuta e reconhece fala do microfone
- Retorna texto reconhecido ou None

**`listen_for_wake_word(wake_word: str, timeout: float = 30.0) -> bool`**
- Escuta por palavra de ativação específica
- Retorna True se detectada

**`test_microphone() -> bool`**
- Testa se microfone está funcionando

**`calibrate() -> bool`**
- Calibra recognizer para ambiente atual

**`get_microphone_list() -> list`**
- Retorna lista de microfones disponíveis

### CommandProcessor

Processador central de comandos.

```python
from jarvis.commands.command_processor import CommandProcessor

processor = CommandProcessor(config, speech_engine, recognition_engine)
should_continue = processor.process_command("abrir navegador")
```

#### Métodos

**`process_command(command_text: str) -> bool`**
- Processa comando de texto
- Retorna True para continuar, False para sair

**`add_custom_command(keyword: str, handler: Callable)`**
- Adiciona comando personalizado

**`remove_command(keyword: str) -> bool`**
- Remove comando existente

**`get_available_commands() -> list`**
- Retorna lista de comandos disponíveis

## Configuração

### Estrutura Completa

```json
{
  "voice": {
    "rate": 180,
    "volume": 0.9,
    "language": "pt-BR",
    "use_gtts": true,
    "pitch": 50
  },
  "recognition": {
    "timeout": 5,
    "phrase_limit": 10,
    "energy_threshold": 300,
    "dynamic_energy_threshold": true
  },
  "system": {
    "os": "auto",
    "debug_mode": false,
    "log_level": "INFO"
  },
  "commands": {
    "wake_word": null,
    "exit_phrases": ["sair", "tchau", "até logo"],
    "help_phrases": ["ajuda", "help", "comandos"]
  },
  "natural_speech": {
    "use_fillers": true,
    "use_hesitations": true,
    "use_breathing": true,
    "emotion_detection": true,
    "conversation_flow": true
  }
}
```

### Parâmetros de Voz

**`rate`**: Velocidade da fala (80-300)
**`volume`**: Volume da voz (0.0-1.0)
**`language`**: Idioma para reconhecimento
**`use_gtts`**: Usar Google TTS quando disponível
**`pitch`**: Tom da voz (20-100)

### Parâmetros de Reconhecimento

**`timeout`**: Timeout para escuta (segundos)
**`phrase_limit`**: Limite de duração da frase (segundos)
**`energy_threshold`**: Threshold de energia do microfone
**`dynamic_energy_threshold`**: Ajuste automático de threshold

### Parâmetros de Fala Natural

**`use_fillers`**: Usar fillers conversacionais ("né", "tipo")
**`use_hesitations`**: Usar hesitações humanas ("hmm", "eh")
**`use_breathing`**: Simular respiração em frases longas
**`emotion_detection`**: Detectar e aplicar emoções
**`conversation_flow`**: Controle de fluxo conversacional

## Eventos de Log

### Tipos de Evento

**VOICE_EVENT**: Eventos de síntese/reconhecimento
```python
logger.voice_event("speak_start", "text_length=50")
```

**COMMAND**: Execução de comandos
```python
logger.command_event("open_browser", "success")
```

**PERFORMANCE**: Métricas de performance
```python
logger.performance_log("command_processing", 0.5)
```

## Comandos Personalizados

### Exemplo Básico

```python
def meu_comando_personalizado(command_text: str) -> bool:
    """
    Handler para comando personalizado
    
    Args:
        command_text: Texto completo do comando
        
    Returns:
        True para continuar executando, False para sair
    """
    # Processar comando
    print(f"Executando comando: {command_text}")
    
    # Usar speech engine se necessário
    # self.speech_engine.speak("Comando executado!")
    
    return True

# Registrar comando
assistant = JarvisAssistant()
assistant.add_custom_command("minha_palavra", meu_comando_personalizado)
```

### Exemplo Avançado

```python
class MeuModuloComandos:
    def __init__(self, config, speech_engine):
        self.config = config
        self.speech_engine = speech_engine
    
    def comando_complexo(self, command_text: str) -> bool:
        # Extrair parâmetros do comando
        import re
        match = re.search(r'fazer (.+)', command_text)
        
        if match:
            parametro = match.group(1)
            
            # Executar lógica
            resultado = self.processar_parametro(parametro)
            
            # Responder com emoção apropriada
            if resultado:
                self.speech_engine.speak(
                    f"Pronto! Executei {parametro} com sucesso.",
                    emotion='entusiasta'
                )
            else:
                self.speech_engine.speak(
                    f"Ops! Não consegui executar {parametro}.",
                    emotion='preocupado'
                )
        
        return True
    
    def processar_parametro(self, parametro: str) -> bool:
        # Sua lógica aqui
        return True

# Usar módulo
modulo = MeuModuloComandos(config, speech_engine)
assistant.add_custom_command("fazer", modulo.comando_complexo)
```

## Emoções Disponíveis

### Tipos de Emoção

**`entusiasta`**
- Voz mais animada e rápida
- Pitch mais alto
- Volume ligeiramente maior

**`preocupado`**
- Tom mais grave
- Velocidade reduzida
- Pausas mais longas

**`pensativo`**
- Velocidade moderadamente reduzida
- Hesitações mais frequentes
- Tom neutro

**`aliviado`**
- Tom ligeiramente mais alto
- Velocidade normal
- Expressões de alívio

### Uso de Emoções

```python
# Sucesso
speech_engine.speak("Pronto! Tarefa concluída.", emotion='entusiasta')

# Erro
speech_engine.speak("Ops! Algo deu errado.", emotion='preocupado')

# Processando
speech_engine.speak("Deixa eu pensar...", emotion='pensativo')

# Problema resolvido
speech_engine.speak("Ufa! Consegui resolver.", emotion='aliviado')
```
