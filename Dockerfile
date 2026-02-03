# Dockerfile para LeitorTela Jarvis
FROM python:3.10-slim

# Instalar dependências do sistema para GUI, Áudio e OCR
RUN apt-get update && apt-get install -y \
    python3-tk \
    tk-dev \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxinerama1 \
    libxcursor1 \
    libxrandr2 \
    libxi6 \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    tesseract-ocr \
    tesseract-ocr-por \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requisitos e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# Variáveis de ambiente
ENV DISPLAY=host.docker.internal:0.0
ENV PYTHONUNBUFFERED=1

# Comando para rodar
CMD ["python", "main.py"]
