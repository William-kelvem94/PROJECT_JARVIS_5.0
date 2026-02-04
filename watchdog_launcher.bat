@echo off
REM ============================================
REM JARVIS SINGULARITY - Auto-Restart Watchdog
REM ============================================

echo.
echo ========================================
echo   JARVIS SINGULARITY - WATCHDOG ATIVO
echo ========================================
echo.

:loop
echo [%date% %time%] Iniciando JARVIS...
python main_singularity.py

REM Verificar código de saída
if %errorlevel% equ 0 (
    echo.
    echo [%date% %time%] JARVIS encerrado normalmente.
    goto end
) else (
    echo.
    echo [%date% %time%] JARVIS CRASHED! Codigo de erro: %errorlevel%
    echo [%date% %time%] Aguardando 5 segundos antes de reiniciar...
    timeout /t 5 /nobreak
    echo [%date% %time%] Reiniciando...
    goto loop
)

:end
echo.
echo Watchdog encerrado.
pause
