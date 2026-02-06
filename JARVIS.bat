@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

:: ============================================================================
:: JARVIS SINGULARITY - LAUNCHER AUTÔNOMO v2.0
:: ============================================================================
:: Sistema de inicialização inteligente e robusto:
:: ✓ Auto-detecção e instalação de Python
:: ✓ Ambiente virtual isolado e gerenciado
:: ✓ Instalação inteligente de dependências
:: ✓ Validação completa do projeto
:: ✓ Auto-restart em caso de falhas
:: ✓ Logs detalhados para diagnóstico
:: ============================================================================

:: -------------------------------------------------------------------------
:: CONFIGURAÇÕES GLOBAIS
:: -------------------------------------------------------------------------
set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%venv"
set "LOG_FILE=%PROJECT_DIR%jarvis_launcher.log"
set "ERROR_LOG=%PROJECT_DIR%jarvis_errors.log"
set "PYTHON_MIN_VERSION=3.10"
set "MAX_RETRIES=3"
set "RETRY_COUNT=0"
set "STARTUP_TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "STARTUP_TIMESTAMP=%STARTUP_TIMESTAMP: =0%"

:: Cores para output (se disponível)
set "COLOR_RESET=[0m"
set "COLOR_GREEN=[92m"
set "COLOR_YELLOW=[93m"
set "COLOR_RED=[91m"
set "COLOR_BLUE=[94m"
set "COLOR_CYAN=[96m"

:: -------------------------------------------------------------------------
:: ROTACIONAR LOGS
:: -------------------------------------------------------------------------
if exist "%LOG_FILE%.3" del "%LOG_FILE%.3" >nul 2>&1
if exist "%LOG_FILE%.2" ren "%LOG_FILE%.2" "jarvis_launcher.log.3" >nul 2>&1
if exist "%LOG_FILE%.1" ren "%LOG_FILE%.1" "jarvis_launcher.log.2" >nul 2>&1
if exist "%LOG_FILE%" ren "%LOG_FILE%" "jarvis_launcher.log.1" >nul 2>&1

:: Iniciar novo log
call :log_header "JARVIS SINGULARITY LAUNCHER - INICIANDO"
call :log_info "Timestamp: %STARTUP_TIMESTAMP%"
call :log_info "Diretorio: %PROJECT_DIR%"
call :log_separator

:: -------------------------------------------------------------------------
:: VERIFICAR PRIVILÉGIOS (SE NECESSÁRIO)
:: -------------------------------------------------------------------------
:: Admin só é necessário para instalar Python automaticamente
set "NEEDS_ADMIN=0"
set "RUNNING_AS_ADMIN=0"

:: Verificar se já está rodando como admin
net session >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "RUNNING_AS_ADMIN=1"
    call :log_info "Executando com privilegios de administrador"
)

:: Verificar se Python existe
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set "NEEDS_ADMIN=1"
    if "!RUNNING_AS_ADMIN!"=="0" (
        call :log_warning "Python nao encontrado - pode ser necessario privilegios de admin"
        call :log_info "Tentando solicitar elevacao..."
        powershell -Command "Start-Process '%~f0' -Verb RunAs" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            call :log_info "Relancando com privilegios de administrador..."
            exit /b 0
        ) else (
            call :log_warning "Falha ao elevar privilegios - continuando sem admin"
        )
    )
)

cls
echo.
echo %COLOR_CYAN%╔════════════════════════════════════════════════════════════════════════╗%COLOR_RESET%
echo %COLOR_CYAN%║              JARVIS SINGULARITY - LAUNCHER v2.0                        ║%COLOR_RESET%
echo %COLOR_CYAN%║                 Inicializador Autônomo e Inteligente                   ║%COLOR_RESET%
echo %COLOR_CYAN%╚════════════════════════════════════════════════════════════════════════╝%COLOR_RESET%
echo.

:: ============================================================================
:: ETAPA 1: VERIFICAR/INSTALAR PYTHON
:: ============================================================================
call :log_step "1" "7" "Verificando Python"

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    call :log_warning "Python nao encontrado no PATH"
    call :log_info "Tentando localizar Python instalado..."
    
    :: Tentar localizar Python em locais comuns
    set "PYTHON_FOUND=0"
    for %%P in (
        "C:\Python311\python.exe"
        "C:\Python310\python.exe"
        "C:\Python312\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    ) do (
        if exist %%P (
            call :log_success "Python encontrado em %%P"
            set "PYTHON_CMD=%%P"
            set "PYTHON_FOUND=1"
            goto :python_found
        )
    )
    
    :python_not_found
    if "!PYTHON_FOUND!"=="0" (
        call :log_error "Python nao encontrado em locais padroes"
        call :install_python
        if !ERRORLEVEL! NEQ 0 (
            call :log_error "Falha ao instalar Python"
            call :log_info "Instale manualmente: https://www.python.org/downloads/"
            call :log_info "IMPORTANTE: Marque 'Add Python to PATH' durante instalacao"
            pause
            exit /b 1
        )
        :: Tentar novamente após instalação
        where python >nul 2>&1
        if !ERRORLEVEL! NEQ 0 (
            call :log_error "Python ainda nao encontrado apos instalacao"
            call :log_info "Por favor, feche e reabra o terminal"
            pause
            exit /b 1
        )
    )
    
    :python_found
    if not defined PYTHON_CMD set "PYTHON_CMD=python"
) else (
    set "PYTHON_CMD=python"
)

:: Verificar versão do Python
for /f "tokens=2" %%V in ('%PYTHON_CMD% --version 2^>^&1') do set "PYTHON_VERSION=%%V"
call :log_success "Python %PYTHON_VERSION% disponivel"

:: Validar versão mínima
%PYTHON_CMD% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    call :log_error "Python %PYTHON_VERSION% e muito antigo (minimo: %PYTHON_MIN_VERSION%)"
    call :log_info "Atualize em: https://www.python.org/downloads/"
    pause
    exit /b 1
)

:: ============================================================================
:: ETAPA 2: AMBIENTE VIRTUAL
:: ============================================================================
call :log_step "2" "7" "Configurando Ambiente Virtual"

if exist "%VENV_DIR%\Scripts\python.exe" (
    call :log_info "Ambiente virtual existente encontrado"
    :: Verificar integridade
    "%VENV_DIR%\Scripts\python.exe" --version >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        call :log_warning "Ambiente virtual corrompido - recriando..."
        rmdir /s /q "%VENV_DIR%" >nul 2>&1
        goto :create_venv
    )
    call :log_success "Ambiente virtual validado"
) else (
    :create_venv
    call :log_info "Criando novo ambiente virtual..."
    %PYTHON_CMD% -m venv "%VENV_DIR%" --clear
    if !ERRORLEVEL! NEQ 0 (
        call :log_error "Falha ao criar ambiente virtual"
        call :log_info "Verifique se o modulo venv esta instalado"
        pause
        exit /b 1
    )
    call :log_success "Ambiente virtual criado"
)

:: Ativar ambiente virtual
call :log_info "Ativando ambiente virtual..."
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    call :log_error "Script de ativacao nao encontrado"
    pause
    exit /b 1
)

call "%VENV_DIR%\Scripts\activate.bat"
if %ERRORLEVEL% NEQ 0 (
    call :log_error "Falha ao ativar ambiente virtual"
    pause
    exit /b 1
)
call :log_success "Ambiente virtual ativado"

:: Verificar que estamos usando o Python do venv
where python | findstr /i "venv" >nul
if %ERRORLEVEL% NEQ 0 (
    call :log_warning "Ambiente virtual pode nao estar ativo corretamente"
)

:: ============================================================================
:: ETAPA 3: ATUALIZAR PIP
:: ============================================================================
call :log_step "3" "7" "Atualizando pip"

python -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    call :log_error "pip nao encontrado"
    pause
    exit /b 1
)

call :log_info "Atualizando pip para ultima versao..."
python -m pip install --upgrade pip --quiet
if %ERRORLEVEL% EQU 0 (
    call :log_success "pip atualizado"
) else (
    call :log_warning "Falha ao atualizar pip - continuando com versao atual"
)

:: ============================================================================
:: ETAPA 4: VALIDAR ARQUIVOS DO PROJETO
:: ============================================================================
call :log_step "4" "7" "Validando Arquivos do Projeto"

call :validate_project_files
if %ERRORLEVEL% NEQ 0 (
    call :log_error "Arquivos criticos do projeto nao encontrados"
    call :log_info "Verifique se voce esta no diretorio correto"
    pause
    exit /b 1
)
call :log_success "Todos os arquivos criticos presentes"

:: ============================================================================
:: ETAPA 5: INSTALAR DEPENDÊNCIAS
:: ============================================================================
call :log_step "5" "7" "Instalando Dependencias"

:: Verificar se já tem dependências instaladas
python -c "import PyQt6; import torch; import cv2" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    call :log_success "Dependencias principais ja instaladas"
    goto :skip_install
)

call :log_info "Instalando dependencias (pode demorar 5-15 minutos)..."
call :log_warning "NOTA: Alguns pacotes podem falhar (ex: dlib) - isto e NORMAL"
call :log_info "O sistema funcionara mesmo sem dependencias opcionais"
echo.

:: Tentar instalação via setup.py primeiro
if exist "setup.py" (
    call :log_info "Executando setup.py..."
    python setup.py
    set "SETUP_CODE=!ERRORLEVEL!"
    
    if !SETUP_CODE! EQU 0 (
        call :log_success "Setup concluido com sucesso"
        goto :verify_install
    ) else (
        call :log_warning "Setup retornou codigo !SETUP_CODE! - tentando instalacao manual"
    )
)

:: Instalação manual em etapas
call :log_info "Instalando pacotes criticos em ordem..."

:: Pacote 1: NumPy (DEVE ser 1.26.4 para compatibilidade)
call :log_info "[1/8] Instalando numpy==1.26.4..."
python -m pip install numpy==1.26.4 --quiet
if %ERRORLEVEL% NEQ 0 (
    call :log_error "Falha ao instalar numpy - CRITICO"
    goto :install_error
)

:: Pacote 2: PyQt6 (Interface gráfica)
call :log_info "[2/8] Instalando PyQt6..."
python -m pip install PyQt6==6.6.1 --quiet
if %ERRORLEVEL% NEQ 0 (
    call :log_error "Falha ao instalar PyQt6 - CRITICO"
    goto :install_error
)

:: Pacote 3: OpenCV (Visão computacional)
call :log_info "[3/8] Instalando opencv-python..."
python -m pip install opencv-python --quiet
if %ERRORLEVEL% NEQ 0 (
    call :log_warning "Falha ao instalar opencv - continuando"
)

:: Pacote 4: PyTorch (IA/ML)
call :log_info "[4/8] Instalando torch (pode demorar)..."
python -m pip install torch==2.6.0 --quiet
if %ERRORLEVEL% NEQ 0 (
    call :log_warning "Falha ao instalar torch - continuando"
)

:: Pacote 5: Pillow (Processamento de imagens)
call :log_info "[5/8] Instalando Pillow..."
python -m pip install Pillow==10.3.0 --quiet

:: Pacote 6: Requests (HTTP/Web)
call :log_info "[6/8] Instalando requests..."
python -m pip install requests --quiet

:: Pacote 7: Outras dependências do requirements.txt
call :log_info "[7/8] Instalando dependencias restantes..."
if exist "requirements.txt" (
    python -m pip install -r requirements.txt --quiet 2>>"%ERROR_LOG%"
    if %ERRORLEVEL% NEQ 0 (
        call :log_warning "Algumas dependencias falharam - veja %ERROR_LOG%"
        call :log_info "Isto e normal para pacotes que requerem compilacao (dlib, etc)"
    )
)

:: Pacote 8: Dependências ML opcionais
call :log_info "[8/8] Instalando dependencias ML opcionais..."
if exist "requirements_ml.txt" (
    python -m pip install -r requirements_ml.txt --quiet 2>>"%ERROR_LOG%"
    if %ERRORLEVEL% NEQ 0 (
        call :log_info "Dependencias ML opcionais falharam - OK, nao sao obrigatorias"
    )
)

call :log_success "Instalacao de dependencias concluida"

:verify_install
call :log_info "Verificando instalacao..."
python -c "import PyQt6; print('✓ PyQt6')" 2>nul
python -c "import cv2; print('✓ OpenCV')" 2>nul
python -c "import torch; print('✓ PyTorch')" 2>nul
python -c "import numpy; print('✓ NumPy')" 2>nul
call :log_success "Verificacao concluida"

:skip_install

:: ============================================================================
:: ETAPA 6: CONFIGURAÇÃO
:: ============================================================================
call :log_step "6" "7" "Verificando Configuracao"

if exist "config.yaml" (
    call :log_success "Arquivo de configuracao encontrado"
) else (
    call :log_warning "config.yaml nao encontrado - usando configuracao padrao"
)

:: Verificar API keys (opcional)
if defined GROQ_API_KEY (
    call :log_info "API Key Groq configurada"
)
if defined GEMINI_API_KEY (
    call :log_info "API Key Gemini configurada"
)

:: ============================================================================
:: ETAPA 7: INICIAR JARVIS
:: ============================================================================
call :log_step "7" "7" "Iniciando JARVIS Singularity"

if not exist "main.py" (
    call :log_error "main.py nao encontrado!"
    pause
    exit /b 1
)

echo.
echo %COLOR_GREEN%╔════════════════════════════════════════════════════════════════════════╗%COLOR_RESET%
echo %COLOR_GREEN%║                        JARVIS ONLINE                                   ║%COLOR_RESET%
echo %COLOR_GREEN%║                   Sistema Operacional e Pronto                         ║%COLOR_RESET%
echo %COLOR_GREEN%╚════════════════════════════════════════════════════════════════════════╝%COLOR_RESET%
echo.
call :log_success "Lancando JARVIS..."
echo.

:: ============================================================================
:: LOOP DE EXECUÇÃO COM AUTO-RESTART
:: ============================================================================
:start_jarvis
set /a RETRY_COUNT+=1

:: Executar JARVIS
python main.py
set "EXIT_CODE=%ERRORLEVEL%"

:: Registrar saída
call :log_separator
call :log_info "JARVIS encerrado com codigo: %EXIT_CODE%"

:: Analisar código de saída
if %EXIT_CODE% EQU 0 (
    call :log_success "Encerramento normal solicitado pelo usuario"
    goto :end_launcher
)

if %EXIT_CODE% EQU 130 (
    call :log_info "Interrompido pelo usuario (Ctrl+C)"
    goto :end_launcher
)

if %EXIT_CODE% EQU 1 (
    call :log_warning "Erro durante execucao"
    if !RETRY_COUNT! LEQ %MAX_RETRIES% (
        call :log_info "Reiniciando (tentativa !RETRY_COUNT!/%MAX_RETRIES%)..."
        timeout /t 5 /nobreak >nul
        goto :start_jarvis
    ) else (
        call :log_error "Numero maximo de tentativas (%MAX_RETRIES%) excedido"
        goto :show_help
    )
)

:: Outros códigos de erro
call :log_error "Erro inesperado (codigo: %EXIT_CODE%)"
if !RETRY_COUNT! LEQ %MAX_RETRIES% (
    call :log_info "Tentando reiniciar..."
    timeout /t 3 /nobreak >nul
    goto :start_jarvis
) else (
    goto :show_help
)

:: ============================================================================
:: FIM DO LAUNCHER
:: ============================================================================
:end_launcher
call :log_separator
call :log_info "Launcher finalizado"
echo.
echo Pressione qualquer tecla para sair...
pause >nul
exit /b %EXIT_CODE%

:show_help
call :log_separator
echo.
echo %COLOR_YELLOW%AJUDA E DIAGNOSTICO:%COLOR_RESET%
echo.
echo 1. Verifique os logs:
echo    - %LOG_FILE%
echo    - %ERROR_LOG%
echo.
echo 2. Execute o validador:
echo    python validate.py
echo.
echo 3. Teste manualmente:
echo    python main.py
echo.
echo 4. Consulte a documentacao:
echo    - WINDOWS_INSTALL.md
echo    - TROUBLESHOOTING.md
echo.
echo 5. Se o problema persistir:
echo    - Verifique que Python %PYTHON_MIN_VERSION%+ esta instalado
echo    - Reinstale as dependencias: pip install -r requirements.txt
echo    - Abra uma issue no GitHub
echo.
pause
exit /b %EXIT_CODE%

:install_error
call :log_error "Falha critica na instalacao de dependencias"
call :log_info "Tente instalar manualmente:"
echo.
echo    pip install numpy==1.26.4
echo    pip install PyQt6==6.6.1
echo    pip install -r requirements.txt
echo.
pause
exit /b 1

:: ============================================================================
:: FUNÇÕES AUXILIARES
:: ============================================================================

:log_header
echo.
echo ═══════════════════════════════════════════════════════════════════════
echo   %~1
echo ═══════════════════════════════════════════════════════════════════════
echo.
echo [%date% %time%] ========== %~1 ========== >> "%LOG_FILE%"
goto :eof

:log_separator
echo ───────────────────────────────────────────────────────────────────────
echo [%date% %time%] ───────────────────────────────── >> "%LOG_FILE%"
goto :eof

:log_step
echo.
echo %COLOR_CYAN%[%~1/%~2]%COLOR_RESET% %~3...
echo [%date% %time%] [%~1/%~2] %~3 >> "%LOG_FILE%"
goto :eof

:log_success
echo    %COLOR_GREEN%✓%COLOR_RESET% %~1
echo [%date% %time%] [SUCCESS] %~1 >> "%LOG_FILE%"
goto :eof

:log_info
echo    %COLOR_BLUE%ℹ%COLOR_RESET% %~1
echo [%date% %time%] [INFO] %~1 >> "%LOG_FILE%"
goto :eof

:log_warning
echo    %COLOR_YELLOW%⚠%COLOR_RESET% %~1
echo [%date% %time%] [WARNING] %~1 >> "%LOG_FILE%"
goto :eof

:log_error
echo    %COLOR_RED%✗%COLOR_RESET% %~1
echo [%date% %time%] [ERROR] %~1 >> "%LOG_FILE%"
echo [%date% %time%] [ERROR] %~1 >> "%ERROR_LOG%"
goto :eof

:install_python
call :log_info "Tentando instalar Python automaticamente..."

:: Método 1: winget (Windows 11 / Windows 10 atualizado)
where winget >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    call :log_info "Instalando Python 3.11 via winget..."
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    if !ERRORLEVEL! EQU 0 (
        call :log_success "Python instalado via winget"
        call :log_warning "IMPORTANTE: Feche e reabra o terminal!"
        timeout /t 5
        exit /b 0
    )
)

:: Método 2: chocolatey
where choco >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    call :log_info "Instalando Python via chocolatey..."
    choco install python --version=3.11 -y
    if !ERRORLEVEL! EQU 0 (
        call :log_success "Python instalado via chocolatey"
        call :log_warning "IMPORTANTE: Feche e reabra o terminal!"
        timeout /t 5
        exit /b 0
    )
)

:: Se chegou aqui, falhou
call :log_error "Nenhum gerenciador de pacotes disponivel"
exit /b 1

:validate_project_files
:: Arquivos críticos que DEVEM existir
set "VALIDATION_FAILED=0"

set "CRITICAL_FILES=main.py config.yaml requirements.txt setup.py"

for %%F in (%CRITICAL_FILES%) do (
    if not exist "%%F" (
        call :log_error "Arquivo critico nao encontrado: %%F"
        set "VALIDATION_FAILED=1"
    ) else (
        call :log_info "✓ %%F"
    )
)

:: Diretórios críticos
set "CRITICAL_DIRS=src jarvis_core data"

for %%D in (%CRITICAL_DIRS%) do (
    if not exist "%%D\" (
        call :log_error "Diretorio critico nao encontrado: %%D"
        set "VALIDATION_FAILED=1"
    ) else (
        call :log_info "✓ %%D\"
    )
)

if "%VALIDATION_FAILED%"=="1" (
    exit /b 1
)
exit /b 0
