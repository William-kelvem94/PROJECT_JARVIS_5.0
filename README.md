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

Ao executar o agente pela primeira vez (seja `python agent.py`, `python agent.py dev`,
ou em qualquer outro modo), ele tentará instalar automaticamente todas as
dependências Python necessárias. Isso inclui não apenas os pacotes essenciais,
mas também extras opcionais como motores locais.

- Se a instalação de algum motor falhar (por exemplo, `vllm` requer uma versão
do `torch` não disponível no Windows), o agente registra o erro e marca o motor
como indisponível. Essa marcação evita tentativas futuras e mantém o processo
funcionando normalmente.
- Você pode forçar a omissão de `vllm` definindo `SKIP_VLLM=1` antes de iniciar
o agente; ou deixar que ele detecte automaticamente após uma falha de instalação.

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
  Ollama (daemon requerido), HuggingFace, vllm, llama.cpp; além de Gemini e seu próprio cérebro.

  **Observação sobre Ollama:**
  1. Certifique‑se de que o executável `ollama` esteja instalado e acessível.
     no Windows ele pode residir em `%USERPROFILE%\\AppData\\Local\\Ollama`.
  2. Inicie o daemon antes de pedir algo ao Jarvis:
     ```sh
     ollama serve          # ou forneça caminho completo
     ```
     O Jarvis também pode tentar levantar o serviço automaticamente
     ou você pode executar via a ferramenta de chat `start_ollama_service`.
  3. Verifique o estado a qualquer momento com `check_ollama_status` ou
     perguntando no chat "status do Ollama".
  4. Se não estiver rodando, ouvirá avisos nos logs e o agente não usará o engine.

  Ajuste `OLLAMA_PATH` na env se o binário não estiver no PATH.
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