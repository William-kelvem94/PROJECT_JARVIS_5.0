# 📖 API Documentation - JARVIS Training & Research System

## 🎯 Overview

This document provides comprehensive documentation for JARVIS 5.0's training and research APIs.

**Base URL**: `http://localhost:8000`

**Content-Type**: `application/json`

---

## 🚀 Training API

### 1. Get Comprehensive Training Status

**Endpoint**: `GET /api/training/comprehensive-status`

**Description**: Returns detailed status of the entire training system including auto-trainer, dataset statistics, and current configuration.

**Response**:
```json
{
  "training_status": {
    "is_training": false,
    "current_stage": "idle",
    "progress": 0.0,
    "message": "Sistema pronto"
  },
  "auto_trainer_status": {
    "auto_train_enabled": true,
    "current_quality": 0.75,
    "quality_threshold": 0.6,
    "should_train": false,
    "last_training": "2024-01-15T10:30:00",
    "next_scheduled_training": "2024-01-16T10:30:00",
    "total_trainings": 5,
    "config": {
      "min_interactions_for_training": 50,
      "min_interactions_for_incremental": 20,
      "retrain_interval_hours": 24
    }
  },
  "training_manager_status": {
    "custom_models": ["jarvis-custom"],
    "pairs_available": 150,
    "can_train": true,
    "status": "ready"
  },
  "dataset_stats": {
    "total_interactions": 150,
    "user_messages": 150,
    "assistant_messages": 150,
    "can_prepare_dataset": true,
    "min_required": 50
  },
  "latest_metrics": {},
  "configuration": {
    "model": {
      "base_model": "codellama:7b",
      "custom_model_name": "jarvis-custom",
      "model_type": "conversational",
      "temperature": 0.7
    },
    "auto_training": {
      "enabled": true,
      "quality_threshold": 0.6,
      "retrain_interval_hours": 24
    }
  }
}
```

---

### 2. Start Training Workflow

**Endpoint**: `POST /api/training/workflow`

**Description**: Starts a complete training workflow (full, incremental, or quick).

**Request Body**:
```json
{
  "type": "full",  // Options: "full", "incremental", "quick"
  "config": {      // Optional custom configuration
    "model": {
      "base_model": "codellama:7b",
      "custom_model_name": "jarvis-custom",
      "temperature": 0.7
    },
    "dataset": {
      "min_interactions": 50,
      "include_conversations": true,
      "include_code_examples": true,
      "include_documents": false
    }
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Treinamento completo finalizado",
  "dataset_info": {
    "dataset_id": "20240115_103000",
    "total_samples": 150,
    "train_samples": 120,
    "validation_samples": 15,
    "test_samples": 15
  },
  "training_result": {
    "model_name": "jarvis-custom",
    "training_pairs": 150
  },
  "validation": {
    "model_exists": true,
    "validation_passed": true
  }
}
```

**Training Types**:
- **`full`**: Complete training with dataset preparation (5-15 min)
- **`incremental`**: Add new data to existing model (2-5 min)
- **`quick`**: Fast training with existing data (1-3 min)

---

### 3. Get Training Configurations

**Endpoint**: `GET /api/training/configs`

**Description**: Lists all available training configurations.

**Response**:
```json
{
  "configs": [
    "default",
    "conversation",
    "code",
    "custom_20240115"
  ]
}
```

---

### 4. Load Training Configuration

**Endpoint**: `POST /api/training/config/load`

**Description**: Loads a specific training configuration.

**Request Body**:
```json
{
  "name": "conversation"  // Configuration name
}
```

**Response**:
```json
{
  "success": true,
  "message": "Configuração 'conversation' carregada",
  "config": {
    "model": { "base_model": "llama2:7b", "temperature": 0.8 },
    "dataset": { "include_conversations": true },
    "training": { "learning_rate": 0.00005 }
  }
}
```

---

### 5. Update Training Configuration

**Endpoint**: `POST /api/training/config/update`

**Description**: Updates an existing configuration or creates a new one.

**Request Body**:
```json
{
  "updates": {
    "model": {
      "temperature": 0.8,
      "base_model": "llama2:7b"
    },
    "dataset": {
      "min_interactions": 100
    },
    "auto_training": {
      "enabled": true,
      "quality_threshold": 0.7
    }
  },
  "save_as": "custom_config"  // Configuration name to save
}
```

**Response**:
```json
{
  "success": true,
  "message": "Configuração atualizada",
  "config": { /* full configuration */ }
}
```

---

### 6. Prepare Training Dataset

**Endpoint**: `POST /api/training/dataset/prepare`

**Description**: Prepares dataset from available data sources.

**Request Body**:
```json
{
  "include_new_only": false  // If true, includes only new data
}
```

**Response**:
```json
{
  "dataset_id": "20240115_103000",
  "created_at": "2024-01-15T10:30:00",
  "total_samples": 150,
  "train_samples": 120,
  "validation_samples": 15,
  "test_samples": 15,
  "config": {
    "min_quality_score": 0.5,
    "include_conversations": true,
    "include_code": true,
    "include_documents": false
  },
  "sources": {
    "conversation": 120,
    "code": 30,
    "document": 0
  }
}
```

---

### 7. Get Dataset Statistics

**Endpoint**: `GET /api/training/dataset/stats`

**Description**: Returns statistics about available training data.

**Response**:
```json
{
  "total_interactions": 150,
  "user_messages": 150,
  "assistant_messages": 150,
  "can_prepare_dataset": true,
  "min_required": 50
}
```

---

## 🔍 Research & Web Search API

### 8. Web Search

**Endpoint**: `GET /api/research/search`

**Description**: Performs web search using DuckDuckGo and Wikipedia.

**Query Parameters**:
- `query` (string, required): Search query
- `num_results` (integer, optional): Number of results per provider (default: 5)

**Example**:
```
GET /api/research/search?query=Python+machine+learning&num_results=3
```

**Response**:
```json
{
  "query": "Python machine learning",
  "timestamp": "2024-01-15T10:30:00",
  "total_results": 6,
  "results": [
    {
      "title": "Machine Learning in Python",
      "snippet": "Python is a popular language for machine learning...",
      "url": "https://example.com/ml-python",
      "source": "DuckDuckGo"
    },
    {
      "title": "Scikit-learn",
      "snippet": "Scikit-learn is a free software machine learning library...",
      "url": "https://en.wikipedia.org/wiki/Scikit-learn",
      "source": "Wikipedia"
    }
  ],
  "provider_results": {
    "DuckDuckGoSearch": [ /* results */ ],
    "WikipediaSearch": [ /* results */ ]
  }
}
```

---

### 9. Research Query

**Endpoint**: `POST /api/research/query`

**Description**: Performs comprehensive research on a topic with structured results.

**Request Body**:
```json
{
  "query": "machine learning algorithms",
  "deep_search": false  // If true, searches more results
}
```

**Response**:
```json
{
  "query": "machine learning algorithms",
  "findings": [
    "Machine learning algorithms are mathematical models...",
    "Common algorithms include neural networks, decision trees...",
    "Supervised learning algorithms learn from labeled data..."
  ],
  "sources": [
    "https://example.com/ml-algorithms",
    "https://en.wikipedia.org/wiki/Machine_learning",
    "https://example.com/ml-guide"
  ],
  "full_results": { /* complete search results */ },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### 10. Research Status

**Endpoint**: `GET /api/research/status`

**Description**: Returns status of research and web search systems.

**Response**:
```json
{
  "web_search_available": true,
  "research_assistant_available": true,
  "providers": [
    "DuckDuckGoSearch",
    "WikipediaSearch"
  ]
}
```

---

## 💬 Chat API (Enhanced with Research)

### 11. WebSocket Chat

**Endpoint**: `WS /ws`

**Description**: Real-time chat with streaming responses. Automatically uses web search when appropriate.

**Triggers for Web Search**:
- Keywords: "pesquise", "busque", "procure", "o que é", "quem é"
- Current events queries
- "notícias", "atual", "recente", "últimas"

**Message Format**:
```json
{
  "content": "Pesquise sobre inteligência artificial"
}
```

**Response Types**:
```json
// Stream start
{ "type": "stream_start", "content": "" }

// Token streaming
{ "type": "stream", "content": "texto " }

// Stream end
{ "type": "stream_end", "content": "resposta completa" }

// Error
{ "type": "error", "content": "Mensagem de erro" }
```

---

## 📊 Status & Monitoring

### 12. System Status

**Endpoint**: `GET /api/status`

**Description**: Returns overall system status.

**Response**:
```json
{
  "status": "online",
  "llm_provider": "ollama",
  "current_model": "codellama:7b",
  "available_models": [
    "codellama:7b",
    "llama2:7b",
    "jarvis-custom"
  ],
  "ollama_connected": true
}
```

---

## 🔑 Authentication

Currently, the API does not require authentication. In production, implement:
- API key authentication
- Rate limiting
- CORS restrictions

---

## 🚨 Error Responses

All endpoints return errors in the following format:

```json
{
  "detail": "Error message description"
}
```

**Common HTTP Status Codes**:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `500`: Internal Server Error
- `503`: Service Unavailable (component not initialized)

---

## 📝 Usage Examples

### Example 1: Train with Custom Configuration

```bash
curl -X POST http://localhost:8000/api/training/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "type": "full",
    "config": {
      "model": {
        "base_model": "codellama:7b",
        "custom_model_name": "jarvis-python",
        "temperature": 0.6
      },
      "dataset": {
        "min_interactions": 50,
        "include_code_examples": true,
        "min_quality_score": 0.6
      }
    }
  }'
```

### Example 2: Web Search

```bash
curl "http://localhost:8000/api/research/search?query=Python+asyncio&num_results=5"
```

### Example 3: Deep Research

```bash
curl -X POST http://localhost:8000/api/research/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "latest developments in AI",
    "deep_search": true
  }'
```

### Example 4: Enable Auto-Training

```bash
curl -X POST http://localhost:8000/api/training/config/update \
  -H "Content-Type: application/json" \
  -d '{
    "updates": {
      "auto_training": {
        "enabled": true,
        "quality_threshold": 0.7,
        "retrain_interval_hours": 24
      }
    },
    "save_as": "default"
  }'
```

---

## 🎓 Best Practices

1. **Training**:
   - Use `quick` for testing
   - Use `full` for first training
   - Use `incremental` for updates
   - Monitor via comprehensive-status

2. **Research**:
   - Cache search results when possible
   - Use `deep_search` sparingly (slower)
   - Check research status before using

3. **Configuration**:
   - Start with default configuration
   - Adjust based on results
   - Save custom configurations with meaningful names

4. **Monitoring**:
   - Check comprehensive-status regularly
   - Monitor auto-trainer for automatic improvements
   - Review dataset stats before training

---

## 📚 Additional Resources

- [GUIA_TREINAMENTO_AVANCADO.md](GUIA_TREINAMENTO_AVANCADO.md) - Advanced training guide
- [GUIA_TREINAMENTO.md](GUIA_TREINAMENTO.md) - Basic training guide
- [README.md](README.md) - Project overview

---

**Need Help?**
- Check logs: `docker-compose logs -f jarvis`
- API documentation: `http://localhost:8000/docs`
- GitHub Issues: [PROJECT_JARVIS_5.0](https://github.com/William-kelvem94/PROJECT_JARVIS_5.0)
