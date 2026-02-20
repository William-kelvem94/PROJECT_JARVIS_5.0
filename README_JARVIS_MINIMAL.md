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

2. Certifique‑se que `ollama` está instalado e que você tem um modelo local configurado.

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
- Testar o fluxo de voz localmente e confirmar o modelo Ollama a ser usado.
- Habilitar um backend STT local (Whisper/VOSK) se quiser operar sem internet.
- Treinar detector de hotword (opcional): coloque exemplos em `jarvis_minimal/wake_data/pos` e `.../neg` e rode `python -m jarvis_minimal.wakeword_trainer`.
- Conversação natural: o agente mantém contexto das últimas interações e inclui esse histórico nos prompts enviados ao modelo local (Ollama). Para limpar o contexto diga por voz "clear memory" ou "limpar memória".
- Idioma nativo: o Jarvis detecta o idioma do seu sistema (por padrão no seu notebook: Português) e valida as entradas do usuário. Se você falar em outro idioma, o Jarvis perguntará se deseja continuar nesse idioma ou se prefere que ele responda no idioma do dispositivo.
- Para melhorar a detecção de idioma, instale `langdetect` (opcional e gratuito): `pip install langdetect`. Se `langdetect` não estiver instalado, o validador é silencioso e assume o idioma do dispositivo.
- Autorizar commits/PRs quando quiser que eu grave a versão inicial no Git.
