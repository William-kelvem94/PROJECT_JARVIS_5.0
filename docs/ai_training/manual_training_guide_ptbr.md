# Guia de Treinamento Manual para a IA JARVIS 5.0

## Objetivo
Este documento orienta como realizar o treinamento manual da IA do JARVIS 5.0, permitindo alimentar o sistema com novos dados, exemplos, correções e feedbacks para aprimorar o desempenho dos modelos locais e da memória neural.

---

## 1. Estrutura Recomendada para Treinamento Manual

### a) Dados de Texto (Conversas, Perguntas e Respostas, Correções, Contextos)
- **Local:** `data/learning/`, `data/knowledge/` ou `data/memories/`
- **Formato:** `.jsonl`, `.csv` ou `.txt`
- **Campos recomendados:**
  - `prompt`: Entrada do usuário ou pergunta
  - `response`: Resposta ideal ou corrigida
  - `context` (opcional): Situação, perfil do usuário ou estado do sistema
  - `tags` (opcional): Ex: `["matemática", "hardware", "erro"]`
  - `feedback` (opcional): Avaliação ou observação do usuário
- **Exemplo de arquivo:**
  - `data/learning/manual_training.jsonl`
  - Cada linha: `{ "prompt": "Como reiniciar o sistema?", "response": "Use o comando 'restart' no dashboard.", "tags": ["sistema", "comandos"] }`

### b) Dados de Imagem (Visão Computacional, UI, FaceID, OCR)
- **Local:** `data/training_dataset/`, `data/vision/`, `data/faces/`, `data/exports/`
- **Formato:** Pastas por categoria, com metadados opcionais em `.json`
- **Estrutura recomendada:**
  - `data/training_dataset/faces/usuario/` (imagens de rosto por usuário)
  - `data/training_dataset/ui_elements/botoes/` (prints de elementos de interface)
  - `data/training_dataset/ocr_samples/` (imagens com texto de referência)
  - Metadados: `{ "label": "botao_ok", "bbox": [x, y, w, h], "text": "OK" }`

### c) Dados de Voz (Áudio, Verificação de Locutor, Comandos)
- **Local:** `data/voice/`, `data/voice_signatures/`, `data/voice/manual_samples/`
- **Formato:** `.wav`, `.mp3` + metadados em `.json`
- **Estrutura recomendada:**
  - `data/voice/manual_samples/usuario/` (amostras de áudio por usuário)
  - `data/voice_signatures/usuario1.json` (embedding, labels)
  - Metadados: `{ "transcript": "Ligar as luzes", "intent": "ativar_luzes" }`

---

## 2. Pipeline de Treinamento Manual (Passo a Passo)

### Passo 1: Preparação dos Dados
- Organize os dados nas pastas e subpastas corretas por tipo e categoria.
- Use nomes de arquivos consistentes: `AAAAMMDD_descricao.ext` ou `usuario_label.ext`.
- Para texto, garanta codificação UTF-8 e escape de caracteres problemáticos.
- Para imagens, prefira PNG/JPG, 256x256 ou maior, claras e rotuladas.
- Para áudio, use WAV mono 16kHz para melhor compatibilidade.
- Documente a origem e qualidade de cada dataset em um README na pasta.

### Passo 2: Validação dos Dados
- Execute `scripts/validate_dependencies.py` para checar dependências Python e do sistema.
- Use ou crie scripts em `scripts/` para checar:
  - Formato e codificação dos arquivos
  - Duplicatas e valores ausentes
  - Consistência entre dados e metadados
  - Para imagens: arquivos corrompidos, dimensões corretas
  - Para áudio: duração, silêncio, clipping
- Exemplo de script de validação para texto:
```python
import json
with open('data/learning/manual_training.jsonl') as f:
    for i, line in enumerate(f, 1):
        try:
            item = json.loads(line)
            assert 'prompt' in item and 'response' in item
        except Exception as e:
            print(f"Erro na linha {i}: {e}")
```

### Passo 3: Ingestão Manual na Memória Neural
- Use ou crie `scripts/manual_ingest.py` para importar dados na ChromaDB:
```python
from src.core.intelligence.neural_memory import neural_memory
import json
with open('data/learning/manual_training.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        neural_memory.store_interaction(item['prompt'], item['response'], metadata=item.get('tags', {}))
```
- Para imagens e áudio, use ou adapte scripts em `scripts/` ou módulos em `src/core/intelligence/`.
- Após ingestão, verifique logs em `data/logs/` para erros ou avisos.

### Passo 4: Treinamento de Modelos Locais (Opcional/Avançado)
- Para ajuste fino de modelos de linguagem:
  - Prepare dataset no formato HuggingFace (`.jsonl`, `.csv`)
  - Use `scripts/train_local_model.py` (crie se necessário) com HuggingFace Transformers ou PyTorch Lightning
  - Exemplo de comando:
    ```bash
    python scripts/train_local_model.py --data data/learning/manual_training.jsonl --epochs 3 --model qwen2.5:7b
    ```
- Para modelos de visão (YOLO, OCR):
  - Organize imagens e labels conforme Ultralytics YOLO ou PaddleOCR
  - Use/adapte scripts em `scripts/optimization/` ou `src/core/vision/`
- Para modelos de voz:
  - Use `data/voice/` e `data/voice_signatures/` como entrada para adaptação de locutor ou reconhecimento de comandos

### Passo 5: Testes e Validação
- Execute testes em `tests/` para validar aprendizado e integração:
  - `tests/test_brain.py` (entendimento de linguagem)
  - `tests/test_memory.py` (memória neural)
  - `tests/test_face_recognition.py` (visão)
  - `tests/test_vision.py` (OCR/UI)
  - `tests/test_mic.py` (áudio)
- Adicione novos casos de teste para seus dados manuais se possível.
- Revise logs em `data/logs/` e saídas em `data/exports/`.

---

## 3. Boas Práticas para Treinamento do JARVIS
- Sempre faça backup de todos os dados e modelos antes de treinar ou ingerir.
- Documente cada sessão de treinamento: data, objetivo, dados usados, scripts executados, resultados.
- Use feedback do usuário (`data/learning/feedbacks.jsonl` ou interface) para refinar prompts e respostas.
- Prefira dados reais, diversos e recentes para melhor generalização.
- Evite overfitting: não repita excessivamente os mesmos pares prompt/resposta.
- Para dados sensíveis, anonimizar ou mascarar informações pessoais.
- Use controle de versão (Git) para scripts e receitas de dados.

---

## 4. Automação, Feedback e Integração
- Automatize ingestão e validação com scripts em `scripts/` e tarefas agendadas.
- Integre feedback dos usuários via HUD, dashboard ou logs:
  - Exemplo: Usuário corrige uma resposta → feedback é logado → script ingere correção na memória
- Use `data/logs/` e `data/exports/` para monitorar o impacto do treinamento manual.
- Para usuários avançados: implemente um ciclo de feedback onde o sistema sugere melhorias com base nas correções do usuário.
- Considere usar os módulos `src/core/learning/` e `src/core/intelligence/` para pipelines customizados.

---

## 5. Solução de Problemas e Dicas
- Se a ingestão falhar, verifique:
  - Problemas de codificação (use UTF-8)
  - IDs duplicados ou campos obrigatórios ausentes
  - Arquivos de imagem/áudio corrompidos ou não suportados
  - Erros de carregamento do ChromaDB ou modelo (veja os logs)
- Se a performance do modelo cair após o treinamento:
  - Restaure o backup anterior
  - Verifique qualidade dos dados ou overfitting
  - Re-treine com dados mais diversos
- Para grandes volumes de dados, divida a ingestão em lotes e monitore o uso de memória.
- Use o `scripts/auto_healer.py` para reparo automatizado de problemas comuns.

---

## 6. Referências e Leituras Complementares
- [Documentação HuggingFace](https://huggingface.co/docs/transformers/training)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Ultralytics YOLO Docs](https://docs.ultralytics.com/)
- [PaddleOCR Docs](https://github.com/PaddlePaddle/PaddleOCR)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [Código-fonte JARVIS: src/core/intelligence/](../../src/core/intelligence/)
- [Código-fonte JARVIS: src/core/learning/](../../src/core/learning/)

---

*Este guia está em constante evolução. Expanda conforme novas rotinas, tipos de dados e módulos forem adicionados ao projeto JARVIS.*
