# Guia: Estendendo os Brains do JARVIS 5.0

O JARVIS utiliza uma arquitetura de "cérebros" modulares para diferentes tipos de inteligência. Este guia explica como criar ou modificar um cérebro.

## 1. Arquitetura Atual
- **NativeBrain**: Processamento offline total (Ollama/LM Studio).
- **AutonomousBrain**: Lógica de decisão autônoma e uso de ferramentas.
- **EngineerBrain**: Focado em desenvolvimento de código e análise técnica.
- **VisionBrain**: Processamento de fluxos de vídeo e percepção espacial.

## 2. Como criar um novo Brain
Para criar um novo módulo de inteligência (ex: `FinancialBrain`):

1. **Crie o arquivo**: `backend/app/financial_brain.py`
2. **Implemente a classe**:
   ```python
   class FinancialBrain:
       def __init__(self, settings):
           self.settings = settings
       
       async def process(self, input_data):
           # Lógica específica aqui
           pass
   ```
3. **Integre no UnifiedMemory**: Se o cérebro precisar de memória persistente, adicione a lógica em `backend/app/unified_memory.py`.
4. **Registre as Ferramentas**: Se o cérebro precisar de ferramentas novas, adicione em `backend/app/tools/`.

## 3. Estendendo o Conhecimento (GraphRAG)
O JARVIS usa o Obsidian como "Segundo Cérebro". Para adicionar novos conhecimentos:
1. Adicione arquivos `.md` em `data/kb_local`.
2. Use links [[Markdown]] para conectar conceitos.
3. O JARVIS reindexará automaticamente através do `SecondBrainConnector`.

## 4. Melhores Práticas
- **Local-First**: Sempre prefira modelos locais (Ollama/Gemini-Local) para privacidade.
- **Async/Await**: Todo o processamento de cérebro deve ser assíncrono para não travar o WebSocket de voz.
- **Telemetry**: Use o `telemetry_server.py` para reportar o estado de processamento do cérebro para o HUD do frontend.
