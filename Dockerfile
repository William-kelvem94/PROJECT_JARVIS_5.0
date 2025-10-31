# Stage 1: Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependências do sistema para build
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Instalar apenas dependências de runtime
RUN apt-get update && apt-get install -y \
    curl \
    portaudio19-dev \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependências Python instaladas do builder
COPY --from=builder /root/.local /root/.local

# Criar diretórios para dados
RUN mkdir -p /app/data /app/logs

# Copiar código da aplicação
COPY . .

# Adicionar /root/.local/bin ao PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expor porta
EXPOSE 8000

# Comando otimizado para iniciar o JARVIS v2
# Usando uvicorn com workers para melhor performance
CMD ["python", "-m", "uvicorn", "core.main_v2:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--loop", "uvloop"]

