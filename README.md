# Projeto JARVIS 5.0

Este repositório contém o agente Python `jarvis` e a interface de dashboard em React/Next.js.
As duas partes convivem em um único projeto (anteriormente haviam sido mantidas como repositórios separados).

## Estrutura

```
.
├── agent.py           # código principal do agente
├── brain.py           # cérebro neurosimbólico
├── prompts.py         # instruções para o LLM
├── requirements.txt   # dependências Python
├── dashboard/         # aplicação frontend Next.js (interface do agente)
│   ├── app/           # código da aplicação (Next 13+)
│   ├── components/    # UI personalizada
│   ├── public/        # assets estáticos
│   └── package.json   # gerenciador de pacotes do frontend
└── ...
```

A pasta `dashboard` faz parte do mesmo repositório; não há mais dois projetos git distintos.
O `package.json` na raiz contém scripts convenientes para trabalhar com a interface.

## Configuração inicial (conforme vídeo do tutorial)

1. **Instalar Node.js** (https://nodejs.org/pt-br). Verifique com `node -v`.
2. **Instalar pnpm**: `npm install -g pnpm` ou usar `npx pnpm` se não estiver globalmente instalado.
   - Verifique com `pnpm -v` ou `npx pnpm -v`.
3. **Instalar LiveKit CLI**: `winget install LiveKit.LiveKitCLI` (Windows) ou siga instruções
   em https://docs.livekit.io/cli.
4. **Instalar dependências do frontend**:
   ```sh
   pnpm dashboard:install
   # ou: cd dashboard && pnpm install
   ```
5. **Rodar o dashboard em modo desenvolvimento**:
   ```sh
   pnpm dashboard:dev
   # acessível em http://localhost:3000
   ```
6. **Configurar variáveis de ambiente** via `.env` (veja `.env.example`).
   Inclua chaves para LiveKit, Google (Gemini), modelos locais (HF_MODEL, VLLM_MODEL, LLAMA_MODEL_PATH), etc.

## Funcionalidades nuevas e próximas etapas

- O agente agora detecta automaticamente motores locais:
  Ollama, HuggingFace, vllm, llama.cpp; além de Gemini e seu próprio cérebro.
- Você pode reconfigurar dinamicamente a lista de engines via comando `configure_engines` ou
  variável `ENGINE_LIST`.
- Há novas ferramentas: `train_huggingface_model`, `get_engine_stats`, `list_engines`.
- O dashboard exibe automaticamente o status dos motores ao conectar e oferece um botão
  dedicado para requisitar informações novamente.

## Extensões sugeridas

1. Adicionar suporte a outros LLMs locais (vllm, llama.cpp) conforme detectado
   automaticamente; já implementado.
2. Ferramenta de treino utilizando `Trainer` do HuggingFace; já disponível.
3. Expor estatísticas mais detalhadas via dashboard (gráficos, uso de CPU, etc.).
4. Permitir edição da lista de motores diretamente no painel (botão/textarea).
5. Centralizar tudo em um único fluxo de inicialização sem modos especiais.
   Atualmente a inicialização é automática.

## Uso

Execute o agente com:
```sh
python agent.py
```

Durante a sessão no dashboard, você pode perguntar por status de motores, treinar modelos,
configurar permissões, etc. Todas as interações via chat serão registradas e exibidas
na interface.


---

Mantenha o projeto atualizado com `git pull` e revise `improvement_suggestions.txt` para ideias de evolução. Boa viagem, Mestre.