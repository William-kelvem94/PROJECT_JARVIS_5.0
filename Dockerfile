# JARVIS 5.0 - Dockerfile para IA Completa
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    # Dependências básicas
    build-essential \
    cmake \
    pkg-config \
    wget \
    curl \
    git \
    # Dependências de áudio
    libasound2-dev \
    portaudio19-dev \
    pulseaudio \
    alsa-utils \
    # Dependências de visão computacional
    libopencv-dev \
    python3-opencv \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Dependências de GUI (para testes)
    libgtk-3-dev \
    libcanberra-gtk-module \
    libcanberra-gtk3-module \
    # Limpeza
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd -m -u 1000 jarvis && \
    mkdir -p /app && \
    chown jarvis:jarvis /app

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Baixar modelo spaCy português
RUN python -m spacy download pt_core_news_sm || \
    python -m spacy download en_core_web_sm

# Copiar código do projeto
COPY . .

# Ajustar permissões
RUN chown -R jarvis:jarvis /app

# Mudar para usuário não-root
USER jarvis

# Criar diretórios necessários
RUN mkdir -p models logs .cursor

# Expor porta (se necessário para APIs futuras)
EXPOSE 8000

# Comando padrão
CMD ["python", "main.py"]
