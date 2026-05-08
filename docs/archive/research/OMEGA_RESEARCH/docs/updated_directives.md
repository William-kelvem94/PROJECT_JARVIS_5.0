# Atualização de Diretrizes: Projeto Ômega & Protocolo 89

## 1. Nova Hierarquia de Modelos (Prioridade Absoluta)
A ordem de tentativa para processamento de IA deve ser rigorosamente:
1. **Gemini API** (Qualidade Máxima / Primário)
2. **NVIDIA API** (Alta Performance / Secundário)
3. **LM Studio** (Local / Privacidade)
4. **OpenRouter** (Fallback Final)

## 2. Redefinição do Holodeck (Sandbox Evolutivo)
O Sandbox não deve se limitar a Docker/VM. A abordagem deve ser **Híbrida e Multi-camada**:
- **Camada Lógica:** Execução em processos isolados com permissões restritas via OS (User-level isolation).
- **Camada Virtual:** Containers efêmeros para dependências pesadas.
- **Camada de Validação:** O código nunca é movido para o core automaticamente. 
- **Fluxo de Implementação:** `Geração` $\rightarrow$ `Execução em Sandbox` $\rightarrow$ `Análise de Resultados` $\rightarrow$ `Apresentação Visual/Técnica ao Usuário` $\rightarrow$ `Autorização do Usuário` $\rightarrow$ `Agendamento de Aplicação` $\rightarrow$ `Implementação no Core`.

## 3. Sistema de Atualização Consciente (The Dream Update)
Durante o ciclo de sono ou ociosidade:
- O JARVIS desenvolve melhorias no Sandbox.
- Ele apresenta a melhoria ao usuário com:
    - **Explicação do 'Porquê'**: O que melhora?
    - **Representação Visual**: Diagrama de fluxo ou mockup da mudança.
    - **Análise de Risco**: O que pode quebrar?
- **Janela de Manutenção**: O usuário define o horário da aplicação. O JARVIS entra em modo de atualização (indisponível) e aplica as melhorias validadas.

## 4. Segurança Adicional
- **Human-in-the-Loop (HITL):** Bloqueio total de escrita no código raiz sem token de autorização do usuário.
- **Audit Log:** Registro imutável de todas as alterações sugeridas e aplicadas.
