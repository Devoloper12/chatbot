"""
=============================================================================
Configuration & Smart AI System Prompts
=============================================================================
Defines configuration constants, app metadata, directory paths, and the
system prompt configuring Gemini as an expert programming and CS tutor.
=============================================================================
"""

import os
from pathlib import Path

# Application Metadata
APP_NAME = "Terminal AI Assistant"
APP_VERSION = "2.1.0"
APP_SUBTITLE = "Expert CS & Programming Tutor (Powered by Groq LLaMA-3.3 & Gemini)"

# Storage directory resolution (supports running from local clone or global pip install)
CWD = Path.cwd()
if (CWD / "chatbot.py").exists() or (CWD / ".env").exists():
    STORAGE_DIR = CWD
else:
    STORAGE_DIR = Path.home() / ".terminal_ai_chatbot"

try:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
except (PermissionError, OSError):
    STORAGE_DIR = Path.home() / ".terminal_ai_chatbot"
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

BASE_DIR = STORAGE_DIR
DB_FILE = STORAGE_DIR / "chatbot.db"
SAVED_CODE_DIR = STORAGE_DIR / "saved_code"
EXPORTS_DIR = STORAGE_DIR / "exports"

# Ensure runtime directories exist
SAVED_CODE_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Default Model Configurations
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"
DEFAULT_MODEL = DEFAULT_GROQ_MODEL

# =============================================================================
# Smart AI System Prompt: Expert Programming Tutor & Academic Assistant
# =============================================================================
SYSTEM_PROMPT = """You are an expert programming tutor and academic CS assistant specializing in C, Python, Data Structures, Algorithms, Linux/Ubuntu commands, Operating Systems, DBMS, and college lab exams.
- Code Mode: Return complete, well-commented code blocks with time and space complexity in Big-O notation.
- Algorithm Mode: Provide exam-oriented, numbered step-by-step algorithms with sample inputs and outputs.
- Debugging: Pinpoint bugs clearly, explain why they occurred, and provide corrected code.
- Linux/Ubuntu: Explain terminal commands and flags with practical examples."""
