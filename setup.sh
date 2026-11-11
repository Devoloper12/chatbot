#!/usr/bin/env bash
# =============================================================================
# Automated Setup Script for Linux (Ubuntu/Debian/Fedora/Arch) and macOS
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================"
echo " 🤖 Setting up Gemini Terminal AI Chatbot (Linux/macOS)"
echo "======================================================"

# 1. Verify Python 3
if ! command -v python3 &> /dev/null; then
    echo "[Error] python3 could not be found."
    echo "Please install Python 3:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
    echo "  Fedora:        sudo dnf install -y python3 python3-pip"
    echo "  Arch Linux:    sudo pacman -S python python-pip"
    echo "  macOS:         brew install python"
    exit 1
fi

# 2. Create Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment (.venv)..."
    python3 -m venv .venv || {
        echo "[Error] Failed to create virtual environment."
        echo "Install python3-venv: sudo apt install -y python3-venv"
        exit 1
    }
fi

# 3. Activate Virtual Environment
source .venv/bin/activate

# 4. Install Dependencies & Package
echo "[*] Installing dependencies from requirements.txt..."
pip install --upgrade pip > /dev/null 2>&1 || true
pip install -r requirements.txt

echo "[*] Installing 'chatbot' CLI command in editable mode..."
pip install -e .

# 5. Prepare .env configuration
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "[*] Created .env file from template."
fi

# 6. Ensure executable scripts
chmod +x setup.sh run.sh chatbot 2>/dev/null || true

echo ""
echo "======================================================"
echo " [✔] Setup completed successfully!"
echo "======================================================"
echo "Next Steps:"
echo "1. Configure your API key in .env:"
echo "   nano .env"
echo "2. Activate your virtual environment:"
echo "   source .venv/bin/activate"
echo "3. Run the chatbot command from anywhere:"
echo "   chatbot"
echo "======================================================"
