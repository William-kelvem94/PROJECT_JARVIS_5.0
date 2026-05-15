# Protocol 89 v2: Sistema de Sandbox Híbrido (Sentinel v2)

## 1. Arquitetura de Sandbox de Camadas
O sistema de execução de código do JARVIS agora opera sob um modelo de isolamento progressivo, onde o nível de restrição é determinado pela criticidade da tarefa e a procedência do código.

### Camada 1: Processo Isolado (Low Overhead)
- **Descrição**: Execução em subprocessos com privilégios reduzidos (drop privileges).
- **Uso**: Scripts de utilidade simples, cálculos matemáticos e processamento de dados não sensíveis.
- **Mecanismo**: Utilização de `seccomp` (Linux) ou `Job Objects` (Windows) para limitar chamadas de sistema (syscalls) e consumo de recursos (CPU/RAM).

### Camada 2: Container (High Isolation)
- **Descrição**: Virtualização a nível de OS via containers efêmeros.
- **Uso**: Execução de código de terceiros, dependências complexas ou código que requer acesso a rede controlada.
- **Mecanismo**: Imagens Docker minimalistas (Alpine/Distroless) com volume de leitura apenas para o contexto necessário e rede isolada via bridge privada.

### Camada 3: Validação Semântica (AST Analysis)
- **Descrição**: Filtro estático pré-execução.
- **Uso**: Obrigatório para qualquer código que pretenda transitar da Sandbox para o Core.
- **Mecanismo**: Análise de Árvore de Sintaxe Abstrata (AST) para detectar:
    - Tentativas de acesso a arquivos fora do escopo (`fs.readFile` em caminhos absolutos).
    - Execuções de shell não autorizadas (`child_process.exec`).
    - Padrões de código maliciosos ou instabilidade (loops infinitos óbvios).

---

## 2. A Gaiola de Testes (Test Cage)
A 'Gaiola de Testes' é o ambiente de staging onde todo código gerado pelo JARVIS deve ser validado antes de qualquer proposta de integração.

### Fluxo de Operação:
1. **Deploy**: O código é injetado na Camada 2 (Container).
2. **Execução**: O código roda contra mocks de dados ou instâncias de banco de dados espelhadas.
3. **Telemetria**: Coleta de logs de STDOUT/STDERR, métricas de performance (latência, memória) e análise de crashes.
4. **Isolamento**: O sistema de arquivos da Gaiola é montado como *overlay*, garantindo que qualquer alteração seja descartada após o teste.
5. **Trava de Segurança**: A interface com o código raiz (`Root Code`) é bloqueada por um firewall de permissões. Apenas o 'Sentinel v2' pode solicitar a abertura de um canal de escrita após a validação da Gaiola.

---

## 3. Sistema de Representação de Mudança (Change Representation)
Para evitar "caixas pretas" nas atualizações, cada modificação deve ser acompanhada de um relatório técnico estruturado.

### Estrutura do Relatório:
- **Sumário Executivo**: O que foi alterado e por quê.
- **Impacto**: Lista de módulos afetados.
- **Análise Técnica**: Explicação da lógica implementada.
- **Visualização (Mermaid)**: 
    - *Diagrama de Sequência*: Para mudanças de fluxo.
    - *Diagrama de Classe/Estado*: Para mudanças de arquitetura.
- **Evidências**: Logs de sucesso da Gaiola de Testes.

---

## 4. Agendador de Atualizações (Update Scheduler)
Lógica de governança para a aplicação de patches no Core da aplicação.

### Regras de Agendamento:
- **Janelas de Manutenção**: O usuário define horários permitidos (ex: `Sábados 02:00 - 06:00`).
- **Fila de Aplicação**: Mudanças aprovadas na Gaiola são colocadas em uma fila de "Pendentes de Deployment".
- **Trigger de Execução**: 
    - `Manual`: Usuário dispara a atualização.
    - `Automático`: O agendador aplica a fila no início da janela de manutenção.
- **Rollback Automático**: Caso a aplicação no Core degrade as métricas de saúde (Health Check), o sistema reverte instantaneamente para o snapshot anterior.
