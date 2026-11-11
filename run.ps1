# =============================================================================
# Gemini Terminal AI Chatbot - 1-Line PowerShell Remote Streamer
# Run with: irm https://raw.githubusercontent.com/Devoloper12/chatbot/main/run.ps1 | iex
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " 🤖 Launching Gemini Terminal AI Assistant..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Locate or install python package in user cache
$AppDir = Join-Path $env:LOCALAPPDATA "GeminiChatbot"
if (-not (Test-Path $AppDir)) {
    New-Item -ItemType Directory -Path $AppDir -Force | Out-Null
}

$VenvDir = Join-Path $AppDir ".venv"
if (-not (Test-Path $VenvDir)) {
    Write-Host "[*] First time initialization (setting up isolated environment)..." -ForegroundColor Yellow
    python -m venv $VenvDir
    & "$VenvDir\Scripts\pip.exe" install --upgrade pip --quiet
    & "$VenvDir\Scripts\pip.exe" install git+https://github.com/Devoloper12/chatbot.git --quiet
}

# 2. Check API Key
$EnvFile = Join-Path $AppDir ".env"
if (-not (Test-Path $EnvFile) -and -not $env:GEMINI_API_KEY) {
    Write-Host "`n🔑 Gemini API Key Required" -ForegroundColor Yellow
    Write-Host "Get your free API key at: https://aistudio.google.com/" -ForegroundColor DarkGray
    $key = Read-Host "Enter your GEMINI_API_KEY"
    if ($key) {
        "GEMINI_API_KEY=$key" | Out-File -FilePath $EnvFile -Encoding utf8
        $env:GEMINI_API_KEY = $key
    }
}

# 3. Launch Chatbot directly in the terminal
& "$VenvDir\Scripts\chatbot.exe"
