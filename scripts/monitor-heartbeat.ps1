<#
.SYNOPSIS
    JARVIS 5.0 — Process Monitor & Auto-Restart
    Keeps backend, agent worker and frontend alive as long as this script runs.
    Launch via start-jarvis.bat (runs in background).
#>

param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent)
)

$BackendUrl   = "http://localhost:8000/health"
$FrontendUrl  = "http://localhost:3000"
$CheckEvery   = 15   # seconds between health checks
$RestartDelay = 5    # seconds before restarting a dead process
$MaxRestarts  = 10   # give up restarting after this many consecutive failures
$LogFile      = Join-Path $Root "backend\data\logs\monitor.log"

# Ensure log dir exists
$null = New-Item -ItemType Directory -Force -Path (Split-Path $LogFile)

function Write-Log([string]$msg, [string]$level = "INFO") {
    $ts   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts][$level] $msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

function Start-Backend {
    Write-Log "Starting Backend (uvicorn)..." "RESTART"
    $proc = Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/k", "cd /d `"$Root\backend`" && call venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000" `
        -PassThru -WindowStyle Normal
    return $proc
}

function Start-Agent {
    Write-Log "Starting Agent Worker..." "RESTART"
    $proc = Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/k", "cd /d `"$Root\backend`" && call venv\Scripts\activate.bat && python -m app.agents start" `
        -PassThru -WindowStyle Normal
    return $proc
}

function Start-Frontend {
    Write-Log "Starting Frontend (Next.js)..." "RESTART"
    # Detect package manager
    $pm = "npm"
    if (Get-Command pnpm -ErrorAction SilentlyContinue) { $pm = "pnpm" }
    $proc = Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/k", "cd /d `"$Root\frontend`" && $pm dev" `
        -PassThru -WindowStyle Normal
    return $proc
}

function Test-Http([string]$url) {
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 4 -ErrorAction Stop
        return $r.StatusCode -eq 200
    } catch {
        return $false
    }
}

# ── Initial process handles (may be $null on first run, monitor will start them) ──
$backendProc  = $null
$agentProc    = $null
$frontendProc = $null

$backendFails  = 0
$agentFails    = 0
$frontendFails = 0

Write-Log "JARVIS Monitor started. Root=$Root" "START"

while ($true) {
    Start-Sleep -Seconds $CheckEvery

    # ── Backend health check ──────────────────────────────────────────────────
    $backendAlive = Test-Http $BackendUrl
    if (-not $backendAlive) {
        $backendFails++
        if ($backendFails -le $MaxRestarts) {
            Write-Log "Backend unreachable (attempt $backendFails/$MaxRestarts). Restarting in ${RestartDelay}s..." "WARN"
            Start-Sleep -Seconds $RestartDelay
            if ($backendProc -and -not $backendProc.HasExited) { $backendProc.Kill() }
            $backendProc = Start-Backend
        } else {
            Write-Log "Backend exceeded max restarts ($MaxRestarts). Giving up." "ERROR"
        }
    } else {
        if ($backendFails -gt 0) { Write-Log "Backend recovered." "INFO" }
        $backendFails = 0
    }

    # ── Agent process check ───────────────────────────────────────────────────
    $agentAlive = ($agentProc -ne $null) -and (-not $agentProc.HasExited)
    if (-not $agentAlive) {
        $agentFails++
        if ($agentFails -le $MaxRestarts) {
            Write-Log "Agent Worker dead (attempt $agentFails/$MaxRestarts). Restarting in ${RestartDelay}s..." "WARN"
            Start-Sleep -Seconds $RestartDelay
            $agentProc = Start-Agent
        } else {
            Write-Log "Agent exceeded max restarts ($MaxRestarts). Giving up." "ERROR"
        }
    } else {
        if ($agentFails -gt 0) { Write-Log "Agent recovered." "INFO" }
        $agentFails = 0
    }

    # ── Frontend health check ─────────────────────────────────────────────────
    $frontendAlive = Test-Http $FrontendUrl
    if (-not $frontendAlive) {
        $frontendFails++
        if ($frontendFails -le $MaxRestarts) {
            Write-Log "Frontend unreachable (attempt $frontendFails/$MaxRestarts). Restarting in ${RestartDelay}s..." "WARN"
            Start-Sleep -Seconds $RestartDelay
            if ($frontendProc -and -not $frontendProc.HasExited) { $frontendProc.Kill() }
            $frontendProc = Start-Frontend
        } else {
            Write-Log "Frontend exceeded max restarts ($MaxRestarts). Giving up." "ERROR"
        }
    } else {
        if ($frontendFails -gt 0) { Write-Log "Frontend recovered." "INFO" }
        $frontendFails = 0
    }

    # ── Heartbeat log (every ~5 minutes) ─────────────────────────────────────
    $now = [int](Get-Date -UFormat "%s")
    if ($now % 300 -lt $CheckEvery) {
        Write-Log "Heartbeat | Backend:$backendAlive Agent:$agentAlive Frontend:$frontendAlive" "HEARTBEAT"
    }
}
