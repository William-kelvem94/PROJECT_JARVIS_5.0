# INSTALAR E CORRIGIR WSL2
# Execute como ADMINISTRADOR

Write-Host "`n==== INSTALACAO COMPLETA DO WSL2 ====`n" -ForegroundColor Cyan

# 1. Habilitar recursos do Windows
Write-Host "[1/5] Habilitando recursos necessarios..." -ForegroundColor Yellow
Write-Host "Isso vai requerer reinicializacao do Windows!`n" -ForegroundColor Red

dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

Write-Host "`n[OK] Recursos habilitados!" -ForegroundColor Green

# 2. Baixar e instalar pacote WSL2
Write-Host "`n[2/5] Baixando pacote de atualizacao do WSL2..." -ForegroundColor Yellow
$wslUpdateUrl = "https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi"
$wslInstaller = "$env:TEMP\wsl_update_x64.msi"

try {
    Invoke-WebRequest -Uri $wslUpdateUrl -OutFile $wslInstaller -UseBasicParsing
    Write-Host "[OK] Download concluido!" -ForegroundColor Green
    
    Write-Host "`n[3/5] Instalando WSL2..." -ForegroundColor Yellow
    Start-Process msiexec.exe -Wait -ArgumentList "/i $wslInstaller /quiet /norestart"
    Write-Host "[OK] WSL2 instalado!" -ForegroundColor Green
} catch {
    Write-Host "[AVISO] Erro ao baixar/instalar: $_" -ForegroundColor Yellow
}

# 3. Definir WSL2 como padrao
Write-Host "`n[4/5] Configurando WSL2 como padrao..." -ForegroundColor Yellow
try {
    wsl --set-default-version 2
    Write-Host "[OK] WSL2 configurado como padrao!" -ForegroundColor Green
} catch {
    Write-Host "[AVISO] Erro ao configurar: $_" -ForegroundColor Yellow
}

# 4. Instalar Ubuntu
Write-Host "`n[5/5] Instalando Ubuntu..." -ForegroundColor Yellow
try {
    wsl --install -d Ubuntu
    Write-Host "[OK] Ubuntu instalado!" -ForegroundColor Green
} catch {
    Write-Host "[AVISO] Erro ao instalar Ubuntu: $_" -ForegroundColor Yellow
    Write-Host "Voce pode instalar manualmente pela Microsoft Store" -ForegroundColor Gray
}

# Resultado
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "              WSL2 INSTALADO!" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "IMPORTANTE: Reinicie o Windows agora!" -ForegroundColor Red
Write-Host "`nApos reiniciar:" -ForegroundColor Yellow
Write-Host "1. Abra Docker Desktop" -ForegroundColor White
Write-Host "2. Va em Settings > General" -ForegroundColor White
Write-Host "3. Marque 'Use the WSL 2 based engine'" -ForegroundColor White
Write-Host "4. Execute: .\INSTALL_AND_RUN.ps1`n" -ForegroundColor White

$resposta = Read-Host "Deseja reiniciar agora? (S/N)"
if ($resposta -eq "S" -or $resposta -eq "s") {
    Write-Host "`nReiniciando em 10 segundos..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    Restart-Computer -Force
} else {
    Write-Host "`nLembre-se de reiniciar antes de usar o Docker!`n" -ForegroundColor Yellow
}

