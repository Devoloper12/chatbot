@echo off
REM =============================================================================
REM Automated Setup Script for Windows (Command Prompt & PowerShell)
REM =============================================================================

echo ======================================================
echo  🤖 Setting up Gemini Terminal AI Chatbot (Windows)
echo ======================================================

cd /d "%~dp0"

REM 1. Verify Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [Error] Python 3 was not found in your PATH.
    echo Please install Python 3 from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM 2. Create Virtual Environment
if not exist ".venv" (
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [Error] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM 3. Activate Virtual Environment
call .venv\Scripts\activate.bat

REM 4. Install Dependencies & Package
echo [*] Installing dependencies from requirements.txt...
python -m pip install --upgrade pip >nul 2>nul
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [Error] Dependency installation failed.
    pause
    exit /b 1
)

echo [*] Installing 'chatbot' CLI command in editable mode...
pip install -e .
if %ERRORLEVEL% NEQ 0 (
    echo [Error] Package installation failed.
    pause
    exit /b 1
)

REM 5. Prepare .env configuration
if not exist ".env" (
    copy .env.example .env >nul
    echo [*] Created .env file from template.
)

echo.
echo ======================================================
echo  [✔] Setup completed successfully!
echo ======================================================
echo Next Steps:
echo 1. Configure your API key in .env:
echo    notepad .env
echo 2. Run the chatbot command:
echo    chatbot
echo ======================================================
pause
