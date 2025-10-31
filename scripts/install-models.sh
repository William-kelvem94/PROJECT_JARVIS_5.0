#!/bin/bash
# Script para baixar modelos do Ollama (Linux/Mac)

echo "=== BAIXANDO MODELOS PARA JARVIS ==="

MODELS=(
    "codellama:7b"
    "deepseek-coder:6.7b"
    "llama2:7b"
    "mistral:7b"
)

for model in "${MODELS[@]}"; do
    echo "Baixando $model..."
    ollama pull "$model"
done

echo "=== MODELOS INSTALADOS ==="
ollama list

