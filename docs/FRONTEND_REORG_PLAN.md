# Plano de Reorganização: Frontend JARVIS 5.0 (Nativo)

Este plano visa limpar definitivamente as "cicatrizes" do LiveKit e estabelecer uma arquitetura de UI leve, rápida e 100% local.

## 1. Nova Gestão de Estado (Context API)
Atualmente, as informações de voz estão soltas no hook `useJarvisVoice`. Vamos criar um `JarvisProvider` que envolverá toda a aplicação.

- **Objetivo:** Acabar com os erros de "No session provided".
- **Ação:** Criar `frontend/context/JarvisContext.tsx` para gerenciar conexão, mensagens e estados da IA.

## 2. Refatoração de Visualizadores (Aura, Wave, etc.)
Os visualizadores atuais quebram porque tentam ler o `audioTrack` do LiveKit.
- **Ação:** Usar a `AudioContext` nativa do navegador para capturar o volume da sua voz e da voz do Jarvis, repassando para as orbes vibrarem sincronizadas.

## 3. Simplificação da Estrutura de Pastas
Vamos unificar os componentes para evitar confusão entre "app" e "agents-ui".

```text
frontend/
  components/
    jarvis/
      Avatar/ (Orbes e Vanta)
      Controls/ (Botões e Inputs)
      Display/ (Transcrição e Logs)
      HUD/ (Percepção e Status)
```

## 4. Lógica de Funcionamento
O Frontend deixará de ser um "cliente de sala" (WebRTC) para ser um **Terminal de Streaming**.
1. Você clica em Iniciar.
2. O WebSocket abre.
3. O Microfone captura áudio e manda pro Python.
4. O Python devolve a Fala e o Jarvis brilha na tela.

---

### Análise do Obsidian (D:\Documents\GitHub\Will-obsidian)
A organização do seu Obsidian está **EXCELENTE**. Você já tem a estrutura de `Skill`, `Projetos` e o núcleo `JARVIS`. 

**O que falta organizar:**
- **JARVIS/System:** Criar uma pasta para guardarmos os diagramas da arquitetura que estou gerando agora.
- **JARVIS/Logs:** Criar um lugar para ele salvar os logs técnicos de erros que ele mesmo resolver no notebook.
- **Templates:** Adicionar um template de "Padrão de Código" para o Jarvis sempre ler antes de te ajudar a programar no OpenCode.

---

### Pergunta para o Chefe:
Posso começar a **Refatoração do Frontend** agora? Vou começar criando o `JarvisContext` para matar todos aqueles erros de tela vermelha de uma vez.
