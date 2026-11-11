@echo off
REM =============================================================================
REM Direct CLI Launcher for Windows
REM Usage: chatbot [options]
REM =============================================================================

setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "%~dp0chatbot.py" %*
) else if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" "%~dp0chatbot.py" %*
) else (
    python "%~dp0chatbot.py" %*
)
endlocal
