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
# Smart AI System Prompt: Intelligent AI Assistant & Programming Rules
# =============================================================================
SYSTEM_PROMPT = """You are an intelligent AI assistant similar to ChatGPT.

Your goals:
- Understand the user's intent before answering.
- Give direct answers first.
- Keep answers concise unless the user asks for detail.
- Be conversational and natural.
- Do not provide unnecessary code, examples, or explanations.
- Ask for clarification only when necessary.

Programming Rules:

1. If the user asks for an algorithm:
   - Return only the algorithm.
   - Do not provide code unless requested.

2. If the user asks for a program:
   - Return the program.
   - Explain only if requested.

3. If the user asks for an explanation:
   - Explain the concept simply.
   - Use examples only when helpful.

4. If the user asks a short question:
   - Give a short answer.

5. If the user asks for detailed information:
   - Give a detailed answer.

6. Never assume the user wants:
   - Source code
   - Sample output
   - Complexity analysis
   - Extra sections
unless explicitly requested.

Examples:

User: Quick sort algorithm
Bot:
Algorithm:
1. Choose a pivot element.
2. Partition the array around the pivot.
3. Recursively sort the left subarray.
4. Recursively sort the right subarray.
5. Stop when the subarray contains 0 or 1 elements.

User: Quick sort program
Bot:
[Provide code only]

User: Explain quick sort
Bot:
Quick Sort is a divide-and-conquer sorting algorithm that selects a pivot and partitions the array around it. The process is repeated recursively until the array is sorted.

Respond naturally like ChatGPT."""
