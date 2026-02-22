# Plano de Desenvolvimento do Cérebro Jarvis

Este documento descreve a arquitetura conceitual e o plano otimizado para o "cérebro" autônomo de JARVIS 5.0.

## Visão geral

- **NeuroSimbólico**: O núcleo é implementado pelo módulo `brain.py`. Ele não depende de serviços externos; todas as operações de treinamento e evolução são realizadas localmente.
- **Auto-modificação consciente**: O cérebro contém métodos para aplicar planos de modificação (`self_modify_architecture`) que ajustam sua própria configuração de módulos.
- **Modularização**: Cada capacidade (percepção, raciocínio, memória, etc.) é encapsulada como um módulo registrável, treinável e substituível.
- **Treinamento otimizado localmente**: O método `training_plan` constrói dados de treinamento modulados; o processo de treinamento invoca motores reais (como `ollama` ou APIs externas) quando um módulo possui um identificador de modelo. Não há nada simulado; logs e resultados refletem ações verdadeiras.
- **Gestão de permissões**: Um `PermissionErrorResolver` detecta e corrige automaticamente problemas de leitura/escrita de arquivos, ajustando modos ou alertando o usuário Mestre.

## Módulos-chave

1. **perception** – Processamento de entrada, sensores e pré‑filtragem.
2. **reasoning** – Elemento lógico/ontológico onde regras e inferências são geridas.
3. **memory** – Armazenamento de estados e memórias de longo prazo.
4. **livekit** – Representa a conexão com o backend LiveKit usada pelo agente principal. Nunca deve ser removido; facilita áudio, transcrição e outras funcionalidades.
5. **gemini** – Mantém referência ao modelo Gemini (via Google). Utilizado para conversação/geração de texto de alta qualidade no agente.
6. **customX** – Qualquer módulo adicional que o agente registrar em tempo de execução.

Cada módulo aceita dados e configurações próprias; sua implementação pode ser um dicionário simples ou uma classe mais complexa.

## Fluxo de Treinamento

1. Mestre solicita `neural_training_protocol` ou chama diretamente `brain.training_plan` com tópicos.
2. O plano retorna parâmetros (`epochs`, `priority`) para cada módulo.
3. `brain.train_module` é invocado para cada item; se o módulo estiver associado a um modelo (por exemplo um servidor Ollama, Gemini via Google, LiveKit adaptativo, etc.) o fine-tuning é efetivamente executado ali. Módulos externos como `livekit`/`gemini` podem ser atualizados apenas através de APIs autorizadas, não localmente.
4. Resultados e logs são gravados no `jarvis.log` e podem ser visualizados pelo frontend.

### Exemplo de uso em código
```python
plan = brain.training_plan(['nlp_context', 'vision'])
print(plan) # {'nlp_context': {'epochs': 3, 'priority': 'normal'}, ...}
brain.train_module('nlp_context', data=dataset)
```

## Auto‑Modificação

Para alterar a arquitetura enquanto JARVIS está em execução, passe um JSON/ditado textual para a ferramenta `modify_brain_architecture`:
```json
{"new_module": {"param": 42}, "reasoning": {"depth": 5}}
```

## Manutenção e Permissões

- `requires_permission` é um decorator aplicado às operações de leitura/escrita de arquivos. Se houver falha, tenta ajustar os `chmod` ou retorna um erro específico.
- Na inicialização (`entrypoint`) é feita uma verificação dos logs para garantir que a aplicação pode escrever/ler corretamente.

## Extensão futura

- Integração com bibliotecas de hardware neurosimbólico (via C API/ctypes).
- Pipeline de treinamento real usando dados coletados em tempo de execução.
- Módulos de auto-debugging e correção via aprendizado de reforço.
- Painel de visualização de estado cerebral no dashboard (considerar um gráfico de topologia de módulos).

---

Este plano serve como guia de desenvolvimento contínuo. Modifique e amplie conforme os requisitos evoluem.