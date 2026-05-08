# Development Master Log - JARVIS 5.0

Este documento serve como o índice cronológico central de todas as implementações, alterações e melhorias realizadas no projeto JARVIS 5.0.

## Índice de Implementações

| Data/Hora | Agente Responsável | Descrição da Alteração | Arquivos Alterados | Tipo |
| :--- | :--- | :--- | :--- | :--- |
| 2026-04-18 11:25 | William Pereira | adiciona script start-openclaude.ps1 para configuração e inicialização do ambiente | `start-openclaude.ps1` | feat |
| 2026-04-15 00:40 | William Pereira | atualiza scripts de build e adiciona novo script de construção com esbuild | `scripts/build.js`, `scripts/build-esbuild.js` | refactor |
| 2026-04-12 02:09 | William Pereira | corrige formatação do comando de instalação no README e adiciona guia de uso de skills no TODO | `README.md`, `TODO.md` | docs |
| 2026-04-11 12:27 | William Pereira | Implement feature X to enhance user experience and optimize performance | - | feat |
| 2026-04-10 17:18 | William Pereira | adiciona dependências aws-sdk, mcpb e types/semver | `package.json` | chore |
| 2026-04-10 17:10 | William Pereira | adiciona stubs de tipos TypeScript ausentes | `src/types/*.ts` | chore |
| 2026-04-10 17:08 | William Pereira | corrige opções do compilador TypeScript no tsconfig | `tsconfig.json` | chore |
| 2026-04-08 02:45 | Kevin Codex | restore default context window for unknown 3p models (#494) | `src/services/modelRegistry.ts` | fix |
| 2026-04-07 22:03 | KRATOS | handle missing skill parameter in SkillTool (#485) | `src/tools/SkillTool.ts` | fix |
| 2026-04-07 17:24 | Juan Camilo Auriti | strip Anthropic params from 3P resume paths (#479) | `src/services/sessionManager.ts` | fix |
| 2026-04-07 16:26 | ibaaaaal | restore Grep and Glob reliability on OpenAI paths (#461) | `src/tools/grep.ts`, `src/tools/glob.ts` | fix |
| 2026-04-07 16:02 | changjiaoxigua | add File polyfill for Node < 20 to prevent startup deadlock with proxy (#442) | `src/index.ts` | fix |
| 2026-04-06 22:13 | Vasanth T | address code scanning alerts (#434) | - | fix |
| 2026-04-06 19:38 | KRATOS | normalize malformed Bash tool arguments from OpenAI-compatible providers (#385) | `src/services/api/bashHandler.ts` | fix |
| 2026-04-06 16:02 | Otávio Carvalho | Fix GLM-5 and other reasoning models appearing to hang via OpenAI shim (#365) | `src/services/api/openaiShim.ts` | fix |
| 2026-04-06 18:59 | Agent_J | avoid sync github credential reads in provider manager (#428) | `src/services/providerManager.ts` | fix |
| 2026-04-06 16:04 | hsain9357 | Fixed gemini error Function call is missing a thought_signature in functionCall parts (#426) | `src/services/api/geminiProvider.ts` | fix |
| 2026-04-06 19:50 | Kevin Codex | isolate latest main suite regressions (#427) | `tests/suite.test.ts` | test |
| 2026-04-06 16:48 | Agent_J | GitHub provider lifecycle and onboarding hardening (#351) | `src/services/providers/github.ts` | feat |
| 2026-04-06 16:01 | Vasanth T | suppress startup dialogs when input is buffered (#423) | `src/ui/startup.ts` | fix |
| 2026-04-06 12:54 | NikitaBabenko | add headless gRPC server for external agent integration (#278) | `src/server/grpcServer.ts` | feat |
| 2026-04-06 06:49 | Paulo Reis | convert dragged file paths to @mentions for attachment (#382) | `src/ui/dropZone.ts` | fix |
| 2026-04-06 14:31 | Sarath Babu | Add Gemini support with thought_signature fix (#404) | `src/services/api/geminiProvider.ts` | feat |
| 2026-04-06 13:45 | Kevin Codex | release 0.1.8 | `package.json` | chore |
| 2026-04-05 15:46 | Technomancer702 | Add local OpenAI-compatible model discovery to /model (#201) | `src/commands/model.ts` | feat |
| 2026-04-04 20:23 | KRATOS | auto-allow safe read-only commands in acceptEdits mode (#341) | `src/services/security/commandGuard.ts` | fix |
| 2026-04-04 11:38 | Juan Camilo Auriti | prevent cross-provider model env var leaks and sync Codex detection (#243) | `src/services/env.ts` | fix |
| 2026-04-04 15:07 | Vasanth T | add Gemini ADC and access token auth (#312) | `src/services/api/geminiProvider.ts` | feat |
| 2026-04-04 08:26 | Yakout | OAuth tokens secure storage for Windows & Linux (#215) | `src/services/auth/tokenStore.ts` | fix |
| 2026-04-03 21:47 | JasonVon | per-agent model routing — route different agents to different providers (#238) | `src/services/routing/agentRouter.ts` | feat |
| 2026-04-03 14:52 | Vasanth T | address code scanning alerts (#240) | - | fix |
| 2026-04-02 15:50 | Urvish Lanje | initial VS Code extension for OpenClaude | `extensions/vscode/...` | feat |
| 2026-04-02 12:18 | Leonardo Grigorio | add Firecrawl backend for WebSearch and WebFetch tools | `src/services/web/firecrawl.ts` | feat |
| 2026-04-01 21:42 | Misha Skvortsov | add support for Atomic Chat provider | `src/services/providers/atomicChat.ts` | feat |
| 2026-04-01 10:19 | gnanam1990 | add intelligent smart auto-router with latency/cost scoring | `src/services/routing/autoRouter.ts` | feat |
| 2026-04-01 10:05 | gnanam1990 | add native Ollama provider for local LLM support | `src/services/providers/ollama.ts` | feat |
| 2026-03-31 23:12 | did:key:z6Mkq... | add OpenAI-compatible provider shim — use any LLM with Claude Code | `src/services/api/openaiShim.ts` | feat |

*Nota: Este log foi gerado a partir do histórico de commits do Git. Para detalhes específicos de cada melhoria, consulte a pasta `/improvements`.*
