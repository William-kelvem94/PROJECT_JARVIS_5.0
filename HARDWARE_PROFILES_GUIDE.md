# JARVIS 5.0 - Perfis de Hardware e Escala Dinâmica

A infraestrutura do JARVIS 5.0 foi projetada para rodar em hardware diverso. Diferente de IAs puras em texto, o JARVIS possui **Motores de Percepção (Visão e Audição)** que monitoram continuamente o ambiente via webcam e microfone.

Entretanto, utilizar Visão Computacional (OpenCV + MediaPipe para detecção facial e de mãos) de forma contínua consome intensamente o processador (CPU). Em notebooks ou computadores sem GPU dedicada, isso pode encavalar a memória e travar o LiveKit Worker (Worker responsável pelos Agentes).

Para contornar isso com elegância e garantir que o JARVIS rode fluidamente independentemente de quão potente seja a máquina, criamos o sistema de **Escala Dinâmica de Perfis de Hardware**.

---

## Como funciona?

Ao iniciar o launcher do sistema via `start-jarvis.bat`, ele não carrega todos os sistemas cegamente. Ele apresenta 3 perfis para você decidir até onde o hardware aguenta ir:

```text
================= CARGA DO CEREBRO =================
[1] MODO DEUS    : Visao + Voz + Texto (PC Forte)
[2] MODO FOCO    : Microfone + Texto   (Notebook)
[3] MODO ECONOMIA: Apenas Texto        (Bateria)
====================================================
```

### [1] MODO DEUS (Performance Extrema)
**Ideal para:** Desktops potentes, PCs gamers (com placas NVIDIA/AMD dedicadas).
**O que ele faz:**
- Inicia o FrontEnd UI, o BackEnd API e o LiveKit Agent Worker paralelamente.
- O Worker inicia o **Motor Visual** em ~2 FPS, rastreando expressões e identidades via Webcam.
- O Worker inicia o **Motor Auditivo**, rastreando fala e identificando o orador via Microfone.
- **Custo de CPU:** Alto (Devido a processamento paralelo pesado de imagens via WebRTC e OpenCV).

### [2] MODO FOCO (Agente Falante, porém "Cego")
**Ideal para:** Notebooks modernos e Macbooks (i5/i7) onde se quer conversar com áudio sem fritar a máquina.
**O que ele faz:**
- O Launcher detecta esta opção e injeta a variável de ambiente `JARVIS_DISABLE_CAMERA=true`.
- Dentro do código Python do Worker (`perception_manager.py`), a Thread da câmera é intencionalmente pulada.
- O sistema mantém os Microfones ligados (que exigem menos da CPU do que processamento de imagem) para interagir usando voz.
- **Custo de CPU:** Médio/Baixo. A CPU roda relaxada e deixa todos os recursos livres para o LLM (LM Studio).

### [3] MODO ECONOMIA (Apenas Cérebro)
**Ideal para:** Notebooks operando na Bateria ou computadores extremamente antigos/fracos.
**O que ele faz:**
- O Launcher **não inicia o Worker (Agentes LiveKit)**.
- Inicia apenas a API e o Frontend Next.js.
- Toda a comunicação é feita através da Interface de Chat Textual (Semelhante ao ChatGPT/Local do LM Studio).
- Sem Câmera e Sem Microfone.
- **Custo de CPU:** Mínimo (Virtualmente Nulo se o LM Studio não for acionado).

---

## Entendendo os "Gargalos"

*   **Problema Comum:** `Agent joined the room but did not complete initializing.`
*   **A Causa:** Ocorre quando o Worker tenta carregar dezenas de bibliotecas de Inteligência Artificial para Câmera e Microfone ao mesmo tempo em uma máquina que já está focada em rodar o Llama3 localmente.
*   **A Melhor Prática:** Rodar a Interface Texto (Modo Economia) consome zero rede local, permitindo focar a memória na placa RAM compartilhada, aliviando o Gargalo CPU vs GPU. Para o JARVIS ouvir (Modo Foco), o computador continuará bem, desde que a Câmera não seja usada para sobrepor as threads de VRAM.
