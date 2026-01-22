# Script de Monitoramento de Performance - JARVIS 5.0
# Monitora recursos, saúde e performance dos containers

Write-Host "📊 Monitor de Performance JARVIS 5.0" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

function Show-Status {
    Write-Host "`n📦 Status dos Containers:" -ForegroundColor Cyan
    docker ps --filter "name=jarvis" --format "table {{.Names}}\t{{.Status}}\t{{.Health}}\t{{.Ports}}"
}

function Show-Resources {
    Write-Host "`n💻 Uso de Recursos:" -ForegroundColor Cyan
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}"
}

function Show-Logs {
    param(
        [int]$Lines = 20,
        [string]$Service = "jarvis"
    )
    Write-Host "`n📝 Últimos $Lines linhas de log ($Service):" -ForegroundColor Cyan
    # Mudar para diretório raiz do projeto
    $projectRoot = Split-Path -Parent $PSScriptRoot
    Push-Location $projectRoot
    docker-compose -f docker/docker-compose.yml logs --tail=$Lines $Service
    Pop-Location
}

function Test-Endpoints {
    Write-Host "`n🔍 Testando Endpoints:" -ForegroundColor Cyan
    
    # Testar JARVIS
    try {
        $jarvis = Invoke-WebRequest -Uri "http://localhost:8000/api/status" -Method Get -UseBasicParsing -TimeoutSec 5
        if ($jarvis.StatusCode -eq 200) {
            Write-Host "✅ JARVIS API: OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ JARVIS API: Não disponível" -ForegroundColor Red
    }
    
    # Testar Ollama
    try {
        $ollama = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method Get -UseBasicParsing -TimeoutSec 5
        if ($ollama.StatusCode -eq 200) {
            Write-Host "✅ Ollama API: OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ Ollama API: Não disponível" -ForegroundColor Red
    }
}

function Show-HealthChecks {
    Write-Host "`n🏥 Healthchecks:" -ForegroundColor Cyan
    docker inspect jarvis_ai jarvis_ollama --format="{{.Name}}: {{.State.Health.Status}}"
}

# Menu interativo
function Show-Menu {
    Write-Host "`n🔄 Menu de Monitoramento:" -ForegroundColor Yellow
    Write-Host "  1. Mostrar tudo"
    Write-Host "  2. Status dos containers"
    Write-Host "  3. Uso de recursos (atualizado em tempo real)"
    Write-Host "  4. Logs recentes"
    Write-Host "  5. Testar endpoints"
    Write-Host "  6. Healthchecks"
    Write-Host "  0. Sair"
    Write-Host ""
}

# Executar monitoramento
while ($true) {
    Show-Menu
    $choice = Read-Host "Escolha uma opção"
    
    switch ($choice) {
        "1" {
            Show-Status
            Show-Resources
            Show-Logs
            Test-Endpoints
            Show-HealthChecks
        }
        "2" { Show-Status }
        "3" {
            Write-Host "Pressione Ctrl+C para parar o monitoramento de recursos" -ForegroundColor Yellow
            docker stats jarvis_ai jarvis_ollama
        }
        "4" { 
            $lines = Read-Host "Quantas linhas de log mostrar? (padrão: 50)"
            if ([string]::IsNullOrEmpty($lines)) { $lines = 50 }
            Show-Logs -Lines $lines
        }
        "5" { Test-Endpoints }
        "6" { Show-HealthChecks }
        "0" { 
            Write-Host "`n👋 Até logo!" -ForegroundColor Green
            break 
        }
        default {
            Write-Host "Opção inválida!" -ForegroundColor Red
        }
    }
    
    if ($choice -eq "0") { break }
}

# Se executado sem menu, mostrar tudo uma vez
if (-not $PSBoundParameters.ContainsKey('Interactive')) {
    Show-Status
    Show-Resources
    Test-Endpoints
    Show-HealthChecks
}

