FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    portaudio19-dev \
    python3-dev \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar diretórios para dados
RUN mkdir -p /app/data /app/logs

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 8000

# Comando para iniciar o JARVIS v2
# Use core.main_v2 para a nova arquitetura modular
# ou core.main para a versão original
CMD ["python", "-m", "uvicorn", "core.main_v2:app", "--host", "0.0.0.0", "--port", "8000"]

