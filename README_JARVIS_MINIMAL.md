Jarvis Minimal (MVP)
=====================

Objetivo
-------
Criar a versão mínima do Jarvis que:
- Ouve via microfone (hotword `jarvis` por padrão)
- Transcreve a fala para texto (STT)
- Envia o texto para um modelo local via Ollama
- Responde em voz (TTS)
- Registra interações e gera sugestões de auto‑correção (trainer)

Como usar
--------
1. Crie/ative um ambiente Python e instale dependências:
   ```
   python -m venv venv-jarvis
   venv-jarvis\Scripts\activate
   pip install -r requirements-jarvis-minimal.txt
   ```

2. Certifique‑se que `ollama` está instalado. O Jarvis detecta automaticamente modelos locais (prefere nomes sem `:cloud`); você pode alterar o modelo padrão em `jarvis_minimal/config.py` (`OLLAMA_MODEL`).

3. Execute:
   ```
   python run_jarvis.py
   ```

Arquitetura mínima
------------------
- `listener.py` — captura áudio e detecta hotword (usa STT backends)
- `ollama_client.py` — wrapper mínimo para comunicar com Ollama
- `agent.py` — loop principal de conversação e logging
- `tts.py` — fala a resposta (pyttsx3)
- `trainer.py` — scaffolding para auto‑treino / auto‑correção

Observações importantes
----------------------
- O backup (`/BACKUP`) **não foi alterado** e será a base para reconstruir funcionalidades adicionais.
- Esse MVP é deliberadamente simples: serve como base para expansão e para ligar o núcleo (voz ↔ modelo ↔ aprendizagem).

Próximos passos sugeridos
------------------------
- Testar o fluxo de voz localmente e confirmar o modelo Ollama a ser usado. Um script de auto‑teste (`jarvis_minimal/system_test.py`) faz validações completas e até instala pacotes faltantes.
- O Jarvis valida dependências na inicialização e tenta instalar componentes core automaticamente se houver conexão com a internet. Ele também escolhe dinamicamente o backend de TTS/STT mais apropriado: edge-tts ou pyttsx3 para fala, Whisper/VOSK/Google para reconhecimento.
- Habilitar um backend STT local (Whisper/VOSK) se quiser operar sem internet. O sistema tenta detectar e habilitar automaticamente Whisper se estiver instalado, e busca por modelos VOSK em pastas do projeto.  
  - **Agora o Jarvis pode baixar automaticamente um modelo VOSK pt‑BR leve (~50 MB)** se detectar que o pacote `vosk` está presente e nenhum modelo foi encontrado. Basta ter Internet na primeira execução.  
  - Caso o reconhecimento retorne texto vazio, verifique volume/microfone ou insira manualmente outro modelo VOSK (defina `VOSK_MODEL_PATH` ou coloque o diretório em `jarvis_minimal/models`).
- Treinar detector de hotword (opcional): coloque exemplos em `jarvis_minimal/wake_data/pos` e `.../neg` e rode `python -m jarvis_minimal.wakeword_trainer`.
- Conversação natural: o agente mantém contexto das últimas interações e inclui esse histórico nos prompts enviados ao modelo local (Ollama). Para limpar o contexto diga por voz "clear memory" ou "limpar memória".
- **Entrada por texto**: você pode iniciar Jarvis em modo `--text` ou `--both` para digitar comandos no console em vez de usar apenas voz. Isso facilita desenvolvimento e fallback em máquinas sem microfone.
- Idioma nativo: o Jarvis detecta o idioma do seu sistema (por padrão no seu notebook: Português) e valida as entradas do usuário. Se você falar em outro idioma, o Jarvis perguntará se deseja continuar nesse idioma ou se prefere que ele responda no idioma do dispositivo.
- Para melhorar a detecção de idioma, instale `langdetect` (opcional e gratuito): `pip install langdetect`. Se `langdetect` não estiver instalado, o validador é silencioso e assume o idioma do dispositivo.
- Melhora do TTS (voz mais natural):
  - O Jarvis agora tenta usar `edge-tts` (vozes neurais on‑line) se estiver instalado e disponível — recomendado para voz natural em PT‑BR.
  - Caso prefira manter tudo local, o Jarvis ajusta automaticamente a melhor `pyttsx3` instalada; você pode listar vozes e escolher uma alterando `jarvis_minimal/config.py` (`TTS_PYTTSX3_VOICE`).

**Startup adaptativo e auto-instalação**
- No momento em que o Jarvis é iniciado, ele executa uma série de verificações (internet, CLI Ollama, dispositivos de áudio, pacotes Python).  
- Dependências essenciais ausentes são instaladas automaticamente, desde que haja conexão à Internet.  
- O Jarvis escolhe dinamicamente o backend TTS e STT mais apropriado (voz neural online vs local, VOSK vs SpeechRecognition) e registra um relatório de inicialização.  
- Um autodiagnóstico é realizado (`self_test`) para validar microfone, alto‑falante e reconhecimento de fala; resultados são exibidos no console.
- Essa lógica garante que, sempre que você iniciar o Jarvis, ele se configure e se ajuste ao ambiente sem intervenção manual.

Como testar / trocar voz
1. Instalar `edge-tts` e `playsound` (opcional, para voz neural online):
   pip install edge-tts playsound
2. Listar vozes locais (pyttsx3):
   python -c "from jarvis_minimal.tts import TTS; print('\n'.join(TTS().list_voices()))"
3. Forçar backend `edge-tts` ou `pyttsx3` editando `TTS_BACKEND_PREFERENCE` em `jarvis_minimal/config.py`.
4. Reinicie Jarvis (`python run_jarvis.py`) e fale com ele.  

Notas:
- `edge-tts` usa um serviço web gratuito da Microsoft para vozes neurais — requer internet.  
- `pyttsx3` usa vozes instaladas localmente (mais rápido e offline, mas qualidade depende das vozes do Windows).
- Autorizar commits/PRs quando quiser que eu grave a versão inicial no Git.
