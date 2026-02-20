# ============================================================================
# JARVIS 5.0 - Script de Limpeza de Dependências (Fase 1)
# ============================================================================
# Objetivo: Remover bibliotecas pesadas e garantir PyTorch otimizado
# Economia Esperada: ~2.5GB de dependências + otimização de CPU

# ============================================================================
# PASSO 1: Remover Dependências Pesadas
# ============================================================================

# Remover TTS Coqui (2GB)
pip uninstall -y TTS

# Remover pyannote.audio (500MB) - Speaker Diarization não utilizado
pip uninstall -y pyannote.audio

# ============================================================================
# PASSO 2: Garantir PyTorch CPU Otimizado
# ============================================================================

# Reinstalar PyTorch CPU com --no-deps para evitar dependências desnecessárias
pip install --upgrade --no-deps torch==2.4.1+cpu torchvision==0.19.1+cpu torchaudio==2.4.1+cpu --index-url https://download.pytorch.org/whl/cpu

# ============================================================================
# PASSO 3: Verificar Instalação
# ============================================================================

# Verificar versão do PyTorch e suporte a INT8
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'INT8 Support: {torch.backends.quantized.engine}')"

# Verificar se Faster-Whisper suporta INT8
python -c "from faster_whisper import WhisperModel; print('Faster-Whisper: OK')"

# ============================================================================
# RESULTADO ESPERADO
# ============================================================================
# - TTS removido: -2GB
# - pyannote.audio removido: -500MB
# - PyTorch otimizado: sem dependências extras
# - Total economizado: ~2.5GB de disco e RAM potencial
