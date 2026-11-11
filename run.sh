#!/usr/bin/env bash
# =============================================================================
# Gemini Terminal AI Chatbot - Linux Launcher & Auto-Setup Script
# =============================================================================
# Usage:
#   chmod +x run.sh
#   ./run.sh
# =============================================================================

set -e

# Resolve script directory or fallback for remote curl piping
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"

if [ -z "$SCRIPT_DIR" ] || [ ! -f "$SCRIPT_DIR/chatbot.py" ]; then
    APP_DIR="$HOME/.gemini_chatbot_app"
    mkdir -p "$APP_DIR"
    cd "$APP_DIR"
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        .venv/bin/pip install --upgrade pip --quiet 2>/dev/null || true
        .venv/bin/pip install git+https://github.com/Devoloper12/chatbot.git --quiet
    fi
    source .venv/bin/activate
    exec chatbot "$@"
fi

cd "$SCRIPT_DIR"

# Text Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}====================================================${NC}"
echo -e "${CYAN}   🤖 Gemini Terminal AI Assistant - Linux Launcher ${NC}"
echo -e "${CYAN}====================================================${NC}"

# 1. Check Python 3 installation
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[Error] python3 is not installed.${NC}"
    echo -e "On Ubuntu/Debian, run: ${YELLOW}sudo apt update && sudo apt install -y python3 python3-venv python3-pip${NC}"
    echo -e "On Fedora/RHEL, run:   ${YELLOW}sudo dnf install -y python3 python3-pip${NC}"
    echo -e "On Arch Linux, run:    ${YELLOW}sudo pacman -S python python-pip${NC}"
    exit 1
fi

# 2. Setup Virtual Environment (.venv)
VENV_DIR="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}[*] Creating virtual environment (.venv)...${NC}"
    python3 -m venv "$VENV_DIR" || {
        echo -e "${RED}[Error] Failed to create virtual environment.${NC}"
        echo -e "Make sure 'python3-venv' is installed: ${YELLOW}sudo apt install -y python3-venv${NC}"
        exit 1
    }
fi

# 3. Activate Virtual Environment
source "$VENV_DIR/bin/activate"

# 4. Check & Install Dependencies
MARKER_FILE="$VENV_DIR/.deps_installed"
if [ ! -f "$MARKER_FILE" ] || [ requirements.txt -nt "$MARKER_FILE" ]; then
    echo -e "${YELLOW}[*] Installing/updating project dependencies...${NC}"
    pip install --upgrade pip > /dev/null 2>&1 || true
    pip install -r requirements.txt
    touch "$MARKER_FILE"
    echo -e "${GREEN}[✔] Dependencies installed successfully!${NC}"
fi

# 5. Check .env Configuration
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}[!] Created .env from .env.example.${NC}"
    else
        echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
    fi
fi

# Check if user has entered an actual API key
if grep -q "your_gemini_api_key_here" .env || ! grep -q "GEMINI_API_KEY=" .env; then
    echo ""
    echo -e "${RED}[Attention] Your Gemini API key is not configured in .env!${NC}"
    echo -e "1. Get a free API key at: ${CYAN}https://aistudio.google.com/${NC}"
    echo -e "2. Edit the .env file:     ${YELLOW}nano .env${NC}"
    echo -e "   Set: ${GREEN}GEMINI_API_KEY=AIzaSy...your_actual_key${NC}"
    echo ""
    read -p "Would you like to enter your API key now? (y/N): " choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        read -p "Enter GEMINI_API_KEY: " user_key
        if [ -n "$user_key" ]; then
            sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$user_key/" .env
            echo -e "${GREEN}[✔] API Key saved to .env!${NC}"
        else
            echo -e "${RED}No key entered. Exiting.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Please edit .env manually and run ./run.sh again.${NC}"
        exit 1
    fi
fi

# 6. Launch Chatbot
echo -e "${GREEN}[✔] Starting Gemini Terminal AI Chatbot...${NC}"
python3 chatbot.py "$@"
