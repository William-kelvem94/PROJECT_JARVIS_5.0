# 📚 Guia: Knowledge Base e HuggingFace Integration

## ✅ Sistema de Conhecimento Persistente

### O que faz

O **Knowledge Base** armazena conhecimento aprendido das interações em um banco de dados vetorial:

1. **Extrai conhecimento** automaticamente de cada interação
2. **Armazena** em banco vetorial (ChromaDB) para busca semântica
3. **Aprende** continuamente conforme você usa o JARVIS
4. **Reutiliza** conhecimento em novas respostas

### Como funciona

#### 1. Extração Automática

A cada interação, o sistema extrai:
- **Respostas completas** - Pergunta + Resposta como conhecimento
- **Fatos** - Informações afirmativas mencionadas
- **Conceitos** - Palavras-chave e conceitos importantes

#### 2. Armazenamento Vetorial

Todo conhecimento é:
- Convertido em embeddings (vetores)
- Armazenado no ChromaDB
- Indexado para busca rápida

#### 3. Reutilização

Ao responder, o sistema:
- Busca conhecimento relevante
- Injeta no prompt do LLM
- Melhora respostas com contexto aprendido

### APIs Disponíveis

#### Buscar Conhecimento
```bash
GET /api/knowledge/search?query=python&limit=5
```

#### Estatísticas
```bash
GET /api/knowledge/stats
```

#### Aprendizado Automático
```bash
POST /api/knowledge/learn
{
  "limit": 100
}
```

---

## 🤗 Integração com HuggingFace

### O que faz

A **HuggingFace Integration** permite:

1. **Buscar modelos** gratuitos no HuggingFace Hub
2. **Encontrar modelos compatíveis** com Ollama
3. **Obter informações** de modelos
4. **Sugerir modelos** baseado em tarefa

### Funcionalidades

#### 1. Buscar Modelos

```bash
GET /api/huggingface/models/search?query=llama&limit=10
```

Retorna lista de modelos do HuggingFace que correspondem à busca.

#### 2. Modelos Compatíveis com Ollama

```bash
GET /api/huggingface/models/ollama-compatible?query=code&limit=20
```

Encontra modelos que podem ser usados no Ollama (formato GGUF ou suportados).

#### 3. Informações de Modelo

```bash
GET /api/huggingface/models/microsoft/DialoGPT-medium
```

Obtém informações detalhadas e instruções de download.

#### 4. Sugerir Modelos

```bash
POST /api/huggingface/models/suggest
{
  "task": "gerar código python"
}
```

Sugere os melhores modelos para uma tarefa específica.

### Exemplos de Uso

#### Buscar modelos para código

```bash
curl "http://localhost:8000/api/huggingface/models/search?query=code&task=text-generation&limit=5"
```

#### Encontrar alternativas ao codellama

```bash
curl "http://localhost:8000/api/huggingface/models/ollama-compatible?query=codellama&limit=10"
```

#### Sugerir modelo para conversação

```bash
curl -X POST "http://localhost:8000/api/huggingface/models/suggest" \
  -H "Content-Type: application/json" \
  -d '{"task": "conversação e chat"}'
```

---

## 🔄 Integração Automática

### Como funciona juntas

1. **Durante interação:**
   - Knowledge Base extrai e armazena conhecimento
   - HuggingFace pode sugerir modelos melhores

2. **Ao responder:**
   - Knowledge Base busca contexto relevante
   - Contexto é injetado no prompt do LLM
   - Resposta melhora com conhecimento aprendido

3. **Melhoria contínua:**
   - Quanto mais você usa, mais conhecimento é armazenado
   - Respostas ficam mais contextualizadas
   - Sistema aprende seus padrões de uso

---

## 📊 Monitoramento

### Ver Estatísticas

```bash
GET /api/knowledge/stats
```

Retorna:
- Número de documentos armazenados
- Status do ChromaDB
- Estatísticas de embeddings

### Limpar Conhecimento

Se necessário, você pode limpar toda a base de conhecimento (não recomendado, pois perde aprendizado).

---

## 🎯 Casos de Uso

### 1. Aprender sobre um Tópico

1. Faça várias perguntas sobre um tópico
2. Sistema extrai e armazena conhecimento
3. Próximas perguntas usam contexto aprendido

### 2. Encontrar Melhor Modelo

1. Use `/api/huggingface/models/suggest` com sua tarefa
2. Veja sugestões de modelos
3. Baixe e use o modelo sugerido

### 3. Aprendizado em Massa

1. Use `/api/knowledge/learn` com limit alto
2. Sistema processa histórico completo
3. Extrai todo conhecimento disponível

---

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# HuggingFace Token (opcional, para modelos privados)
HUGGINGFACE_API_TOKEN=your_token_here
```

### Instalação

Dependências já estão em `requirements.txt`:
- `chromadb` - Banco vetorial
- `sentence-transformers` - Embeddings
- `huggingface_hub` - Integração HuggingFace

---

## 🚀 Próximos Passos

- [ ] Aprendizado incremental automático
- [ ] Exportar/importar base de conhecimento
- [ ] Integração direta com download de modelos HuggingFace
- [ ] Fine-tuning usando datasets do HuggingFace

---

**✅ Sistema completo de conhecimento e integração implementado!**

O JARVIS agora:
- ✅ Aprende e armazena conhecimento
- ✅ Reutiliza conhecimento aprendido
- ✅ Busca modelos externos gratuitos
- ✅ Melhora continuamente

