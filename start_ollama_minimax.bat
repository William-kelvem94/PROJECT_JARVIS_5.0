@echo off
REM Atalho para rodar o modelo Ollama minimax-m2.5:cloud e enviar arquivos para análise

REM Caminho do projeto
cd /d %~dp0

REM Instrução para rodar o modelo
ollama run minimax-m2.5:cloud

REM Instruções:
REM 1. Copie e cole o conteúdo dos arquivos principais (main.py, config.py, models.py, requirements.txt, conftest.py, .gitignore) no prompt do modelo.
REM 2. Aguarde o feedback do modelo e aplique as sugestões.

pause
