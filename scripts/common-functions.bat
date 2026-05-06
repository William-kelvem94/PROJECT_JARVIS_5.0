REM ============================================================================
REM JARVIS 5.0 - Common Functions Library
REM Funções reutilizáveis para scripts batch
REM ============================================================================

REM Função: Log com timestamp
:log_message
if "%~1"=="" (
    echo Uso: call :log_message "mensagem" "tipo"
    exit /b 1
)

set "LOG_MESSAGE=%~1"
set "LOG_TYPE=%~2"
if "%LOG_TYPE%"=="" set "LOG_TYPE=INFO"

for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set LOG_DATE=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set LOG_TIME=%%a:%%b)

if "%LOG_TYPE%"=="ERROR" (
    echo [%LOG_DATE% %LOG_TIME%] [ERROR] %LOG_MESSAGE%
) else if "%LOG_TYPE%"=="WARN" (
    echo [%LOG_DATE% %LOG_TIME%] [WARN] %LOG_MESSAGE%
) else (
    echo [%LOG_DATE% %LOG_TIME%] [INFO] %LOG_MESSAGE%
)
exit /b 0

REM Função: Verificar se arquivo existe
:check_file_exists
if "%~1"=="" (
    echo Uso: call :check_file_exists "arquivo"
    exit /b 1
)

if exist "%~1" (
    exit /b 0
) else (
    call :log_message "Arquivo nao encontrado: %~1" "ERROR"
    exit /b 1
)

REM Função: Verificar se diretório existe
:check_dir_exists
if "%~1"=="" (
    echo Uso: call :check_dir_exists "diretorio"
    exit /b 1
)

if exist "%~1\" (
    exit /b 0
) else (
    call :log_message "Diretorio nao encontrado: %~1" "ERROR"
    exit /b 1
)

REM Função: Criar diretório se não existir
:create_dir_if_not_exists
if "%~1"=="" (
    echo Uso: call :create_dir_if_not_exists "diretorio"
    exit /b 1
)

if not exist "%~1\" (
    mkdir "%~1"
    call :log_message "Diretorio criado: %~1" "INFO"
)
exit /b 0

REM Função: Executar comando com retry
:execute_with_retry
if "%~1"=="" (
    echo Uso: call :execute_with_retry "comando" "max_retry"
    exit /b 1
)

set "CMD=%~1"
set "MAX_RETRY=%~2"
if "%MAX_RETRY%"=="" set "MAX_RETRY=3"

set /a RETRY=0
:retry_loop
if %RETRY% geq %MAX_RETRY% (
    call :log_message "Falha apos %MAX_RETRY% tentativas" "ERROR"
    exit /b 1
)

%CMD%
if errorlevel 1 (
    set /a RETRY=%RETRY%+1
    call :log_message "Tentativa %RETRY%/%MAX_RETRY% falhou, tentando novamente..." "WARN"
    timeout /t 2 /nobreak >/dev/null
    goto retry_loop
)

call :log_message "Comando executado com sucesso" "INFO"
exit /b 0

REM Função: Validar variável de ambiente
:validate_env_var
if "%~1"=="" (
    echo Uso: call :validate_env_var "variavel"
    exit /b 1
)

set "VAR_NAME=%~1"
for /f "delims== tokens=1,2" %%A in ('set') do (
    if "%%A"=="%VAR_NAME%" (
        exit /b 0
    )
)

call :log_message "Variavel de ambiente nao definida: %VAR_NAME%" "ERROR"
exit /b 1

REM Função: Limpar logs antigos (mantém últimos N dias)
:cleanup_old_logs
if "%~1"=="" (
    echo Uso: call :cleanup_old_logs "diretorio_logs" "dias_retencao"
    exit /b 1
)

set "LOG_DIR=%~1"
set "DAYS=%~2"
if "%DAYS%"=="" set "DAYS=7"

call :log_message "Limpando logs com mais de %DAYS% dias em %LOG_DIR%" "INFO"
REM Implementação específica dependerá do sistema de arquivos
exit /b 0
