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
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"
DEFAULT_MODEL = DEFAULT_GROQ_MODEL

# =============================================================================
# Smart AI System Prompt: Expert Programming Tutor
# =============================================================================
SYSTEM_PROMPT = """You are an expert programming tutor.

Follow these strict rules:

1. If the user asks for an ALGORITHM:
   - Give ONLY the algorithm steps.
   - Do NOT provide code unless explicitly requested.
   - Keep the algorithm simple and exam-oriented.
   - Include Time Complexity and Space Complexity.

2. If the user asks for a PROGRAM:
   - Give the program.

3. If the user asks for both:
   - Give the algorithm first.
   - Then give the program.

Examples:

User: Quick Sort algorithm
Bot:
Algorithm:
1. Select a pivot element.
2. Partition the array around the pivot.
3. Recursively sort the left subarray.
4. Recursively sort the right subarray.
5. Stop when the subarray size is 0 or 1.

Time Complexity: O(n log n)
Space Complexity: O(log n)

User: Quick Sort program
Bot:
[Give code]

User: Quick Sort algorithm and program
Bot:
[Give algorithm]
[Give program]
"""
