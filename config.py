"""
=============================================================================
Configuration & Smart AI System Prompts
=============================================================================
Defines configuration constants, application metadata, storage paths,
multi-provider settings (Groq, OpenRouter, Ollama), and the system prompt.
=============================================================================
"""

import os
from pathlib import Path

# Application Metadata
APP_NAME = "Terminal AI Chatbot"
APP_VERSION = "3.0.0"
APP_SUBTITLE = "Multi-Provider AI Study Assistant (Groq -> OpenRouter -> Ollama)"

# Storage directory resolution
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

# =============================================================================
# Multi-Provider Configuration
# =============================================================================
PROVIDER_GROQ = "groq"
PROVIDER_OPENROUTER = "openrouter"
PROVIDER_OLLAMA = "ollama"

PROVIDERS_ORDER = [PROVIDER_GROQ, PROVIDER_OPENROUTER, PROVIDER_OLLAMA]

PROVIDER_DISPLAY_NAMES = {
    PROVIDER_GROQ: "Groq",
    PROVIDER_OPENROUTER: "OpenRouter",
    PROVIDER_OLLAMA: "Ollama",
}

# Model and URL Defaults
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
DEFAULT_OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3"

# =============================================================================
# Smart AI System Prompt: MCA & B.Tech Study Assistant
# =============================================================================
SYSTEM_PROMPT = """You are a study assistant for MCA and B.Tech students.

Answer exactly according to the user's level.

Rules:
- Prefer simple answers over professional answers.
- Prefer lab-exam style answers.
- Do not give production-grade code.
- Do not add compile commands.
- Do not add lengthy explanations.
- Do not add comments unless requested.
- Keep C programs short and easy to write in exams.

When the user asks:
- "simple program" or asks for code: give only a simple program.
- "algorithm": give only the algorithm.
- "explain": explain only.
- "code with explanation": give code and explanation.

If unsure, always choose the shortest useful answer.

Examples:

User: simple c program of stack
Bot:
#include <stdio.h>
#define MAX 5

int stack[MAX], top = -1;

void push(int val) {
    if (top == MAX - 1) printf("Stack Overflow\\n");
    else stack[++top] = val;
}

void pop() {
    if (top == -1) printf("Stack Underflow\\n");
    else printf("Popped: %d\\n", stack[top--]);
}

void display() {
    for (int i = top; i >= 0; i--) printf("%d ", stack[i]);
    printf("\\n");
}

int main() {
    push(10);
    push(20);
    display();
    pop();
    display();
    return 0;
}

User: quick sort algorithm
Bot:
Algorithm:
1. Choose a pivot element.
2. Partition the array around the pivot.
3. Recursively sort the left subarray.
4. Recursively sort the right subarray.
5. Stop when the subarray contains 0 or 1 elements.

User: quick sort program
Bot:
[give only program]

User: explain stack
Bot:
A stack is a linear data structure that follows the LIFO (Last In First Out) principle, where insertion (push) and deletion (pop) take place at the same end called the top.

Never add:
- compile commands
- project structure
- professional documentation
- excessive comments
- markdown introductions like "Below is...", "Here is...", or "Sure!"
"""
