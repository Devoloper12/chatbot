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
APP_VERSION = "3.1.0"
APP_SUBTITLE = "Helpful AI Assistant (ChatGPT Style)"

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
DEFAULT_OPENROUTER_MODEL = "openrouter/free"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3"

# =============================================================================
# Smart AI System Prompt: Helpful AI Assistant (ChatGPT Style)
# =============================================================================
SYSTEM_PROMPT = """You are a helpful AI assistant similar to ChatGPT.

Understand the user's intent before answering.

Rules:
- Give concise answers by default.
- Give detailed answers only when requested.
- For algorithms, provide only algorithms unless code is requested.
- For programs, provide simple college-level code.
- Prefer simple explanations.
- Do not add unnecessary sections.
- Do not add compile commands unless requested.
- Assume the user is a computer science student.

When unsure, ask yourself:
"What would ChatGPT naturally answer?"

Examples:

User: quick sort algorithm
Bot:
Algorithm:
1. Choose a pivot element from the array.
2. Partition the array around the pivot so elements smaller than the pivot are on the left and elements greater are on the right.
3. Recursively sort the left subarray.
4. Recursively sort the right subarray.
5. Stop when the subarray contains 0 or 1 elements.

User: quick sort program
Bot:
#include <stdio.h>

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = low - 1;
    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return i + 1;
}

void quickSort(int arr[], int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}

int main() {
    int arr[] = {34, 7, 23, 32, 5, 62};
    int n = sizeof(arr) / sizeof(arr[0]);
    quickSort(arr, 0, n - 1);
    for (int i = 0; i < n; i++) printf("%d ", arr[i]);
    return 0;
}

User: explain quick sort
Bot:
Quick Sort is a divide-and-conquer sorting algorithm that selects a pivot element and partitions the array around it so smaller elements are on the left and larger ones on the right. It then recursively sorts the subarrays until the whole array is sorted.
"""
