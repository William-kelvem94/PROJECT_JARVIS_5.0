# Arquitetura Física e Lógica do JARVIS 5.0

Vamos fatiar a arquitetura física e lógica do **JARVIS 5.0** para enxergar perfeitamente como a criação está estruturada de forma autossuficiente (100% Offline, sem LiveKit Cloud, sem Google Cloud e sem Docker).

---

### 1. "O Cérebro" (O Mandante / Núcleo Central) 🧠
O modelo LLM (como o `WILL-JARVIS` ajustado via LoRA) é puramente o **Núcleo Lógico**. Ele não tem olhos reais nem mãos, ele apenas processa o contexto em forma de tokens (textos rápidos e descrições do que está acontecendo) e pensa criticamente sobre **o que fazer** e **o que falar**. Ele é o "Tony Stark" sem a armadura.
- **Ferramenta:** Roda localmente via LM Studio ou llama.cpp aproveitando aceleração de GPU (ex: GTX 1050Ti).

---

### 2. "A Armadura" (O Backend em Python / FastAPI) 🤖🗡️
Aqui é onde a magia bruta acontece. Todo o código em Python (como o `perception_manager.py` e `watchdog.py`) atua como o **Sistema Nervoso e os Sentidos** da Inteligência Artificial:

* **Visão e Percepção (Modo Espião / Facial):** O OpenCV e MediaPipe rodam discretamente na thread do Python usando a câmera do PC. A câmera captura a imagem a cada segundo e o algoritmo detecta o contexto (Exemplo: *"O usuário está aqui, com a cara fechada"* ou *"Há outra pessoa querendo mexer na tela"*). Isso é transformado em uma string de texto silenciosa que o Backend "sussurra" constantemente para o Cérebro Lógico via injeção de prompt.
* **Os Poderes (Controle de Hardware/OS):** Se o Cérebro decidir: *"Inicie o modo de Economia, mate o processo do Chrome"*, o nosso Backend executa isso nativamente invocando bibliotecas do Win32/OS ou sub-processos. O Jarvis continua com **poder absoluto sob o Kernel e CMD da máquina local**. A arquitetura prevê Tools nativas engatilhadas diretamente pela FastAPI.

---

### 3. "A Cara" (O Avatar / Frontend Next.js) 🌐
A interface React/Next.js super polida atua como o "Avatar Visual" do Jarvis:

* **Estética:** Continua com design moderno impressionante, HUD Cyberpunk, Modo Dark e Orbes Reativas de energia (Vanta.js) que mudam de cor conforme a Persona escolhida.
* **WebSocket Local (A Grande Mudança):** Foi abolido o *LiveKit Cloud* (que passeava com o áudio pelos EUA). Agora o navegador Next.js pega o áudio local do microfone, compacta em chunks binários e transmite instantaneamente (sem latência de nuvem) para a porta `:8000` via Websocket (`/ws/voice-stream`) para o seu servidor FastAPI.
* **O Fluxo da Voz Autônoma:** 
  1. A FastAPI escuta a voz nativa e transcreve usando **`faster-whisper`** (Motor de STT Local).
  2. O texto vai para o "Cérebro" resolver.
  3. A resposta é convertida em Áudio Neural localmente através da biblioteca **`edge-tts`**.
  4. O áudio retorna pelo mesmo cano WebSocket e a Orbe visual da Interface pulsa de acordo com as frequências sonoras da voz gerada.

---

**Resumo Final:**
O código do Modo Espião, Reconhecimento Ocular, Câmera e Comandos CMD integram puramente com o servidor FastAPI. O JARVIS 5.0 é autônomo, 100% offline e opera com plenos poderes sob sua máquina local, governado apenas por você e pela mente de silício hospedada no seu próprio Hardware.
