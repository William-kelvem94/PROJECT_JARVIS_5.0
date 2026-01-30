# JARVIS Ultimate - Dockerfile
FROM python:3.11-slim

# Labels
LABEL maintainer="JARVIS Ultimate"
LABEL description="Infraestrutura de Vida Artificial - JARVIS Ultimate"
LABEL version="1.0"

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    # Para pyttsx3 (TTS)
    espeak-ng \
    libespeak-ng1 \
    speech-dispatcher \
    # Para audio processing
    alsa-utils \
    pulseaudio \
    # Para hardware monitoring
    lm-sensors \
    # Utilitários
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash jarvis
USER jarvis

# Diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro para cache de build
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --user -r requirements.txt

# Copiar código fonte
COPY . .

# Criar diretórios necessários
RUN mkdir -p data config logs

# Variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/jarvis/.local/bin:${PATH}"

# Porta da aplicação
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/status')" || exit 1

# Comando de inicialização
CMD ["python", "main.py"]