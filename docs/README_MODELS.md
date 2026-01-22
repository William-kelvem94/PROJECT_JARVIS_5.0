# Documentação de instalação de modelos LLM locais

## Modelos suportados
- Llama.cpp
- GPT4All
- DeepSeek

### Llama.cpp
1. Baixe o executável e o modelo em: https://github.com/ggerganov/llama.cpp
2. Coloque o executável e o modelo na pasta desejada
3. Ajuste o caminho em `core/local_llm.py`

### GPT4All
1. Instale via pip: `pip install gpt4all`
2. Baixe o modelo em: https://gpt4all.io/index.html
3. Veja exemplos em https://github.com/nomic-ai/gpt4all

### DeepSeek
1. Siga instruções em: https://github.com/deepseek-ai/DeepSeek-LLM
2. Modelos podem ser baixados e rodados localmente

---

## Plugins de voz/texto
- TTS: pyttsx3 (offline)
- STT: SpeechRecognition (pode usar Google, mas há alternativas offline)

Instale dependências:
```
pip install pyttsx3 SpeechRecognition
```

Para STT offline, veja alternativas como Vosk ou Whisper.
