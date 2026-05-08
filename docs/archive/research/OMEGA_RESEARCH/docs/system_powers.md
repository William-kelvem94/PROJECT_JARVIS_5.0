# System-God v2: System Powers

## Status: Em Implementação
**Objetivo:** Prover ao JARVIS controle total e adaptativo do dispositivo.

## Matriz de Controle (Capabilities)

### 1. Consciência Espacial
- **Detecção de Monitores:** Capacidade de identificar a quantidade de telas conectadas.
- **Mapeamento de Resolução:** Leitura em tempo real da resolução e posição de cada monitor para capturas e interações precisas.

### 2. Controle de Hardware
- **Áudio:** Ajuste de volume do sistema e controle de mudo.
- **Brilho:** Manipulação da intensidade luminosa dos monitores.
- **Periféricos:** 
    - Controle total do cursor do mouse (movimento e cliques).
    - Simulação de digitação e teclas de atalho do teclado.

### 3. Visão de Sistema
- **Captura Multi-Tela:** Capacidade de capturar screenshots de telas específicas ou de todo o desktop expandido.

## Interface de Comando (API)
As funções serão expostas via dispatcher para o LLM:
- `set_volume(level: int)`
- `set_brightness(level: int)`
- `capture_screen(screen_id: int)`
- `input_keyboard(keys: str)`
- `input_mouse(action: str, x: int, y: int)`

## Camada de Segurança: O Sentinela
Todos os comandos acima são interceptados pelo **Sentinela**, que valida a segurança da operação antes da execução no kernel/sistema.
