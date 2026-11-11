# =============================================================================
# Automated Setup Script for Windows PowerShell
# =============================================================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host " 🤖 Setting up Gemini Terminal AI Chatbot (PowerShell)" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

# 1. Check Python
try {
    $pyVersion = python --version 2>&1
    Write-Host "[✔] Detected: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "[Error] Python was not found in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3 from https://www.python.org/downloads/ and ensure 'Add Python to PATH' is checked." -ForegroundColor Yellow
    Exit 1
}

# 2. Create Virtual Environment
if (-not (Test-Path ".venv")) {
    Write-Host "[*] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
}

# 3. Activate Virtual Environment
$ActivateScript = Join-Path $ScriptDir ".venv\Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
}

# 4. Install Dependencies & Package
Write-Host "[*] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "[*] Installing 'chatbot' CLI command in editable mode..." -ForegroundColor Yellow
pip install -e .

# 5. Prepare .env configuration
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[*] Created .env from template." -ForegroundColor Green
}

Write-Host "`n======================================================" -ForegroundColor Green
Write-Host " [✔] Setup completed successfully!" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure your API key in .env (e.g. notepad .env)" -ForegroundColor White
Write-Host "2. Run: chatbot" -ForegroundColor Yellow
Write-Host "======================================================" -ForegroundColor Green
