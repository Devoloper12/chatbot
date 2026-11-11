# 🤖 Gemini Terminal AI Chatbot & Programming Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Platform: Cross--Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-green.svg)]()
[![Powered By: Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini%20API-orange.svg)](https://aistudio.google.com/)

An advanced, cross-platform terminal AI assistant and academic programming tutor powered by the **Google Gemini API**. Built with local **SQLite persistence**, multi-session memory, **Rich terminal styling**, syntax-highlighted code rendering, and academic CS lab capabilities.

Installable as a global terminal command (`chatbot`) on **Windows Command Prompt**, **PowerShell**, **Ubuntu / Debian**, **Linux**, and **macOS**.

---

## ⚡ Quick Start (The 4-Step Workflow)

Clone the repository and run the chatbot directly from any terminal:

```bash
# 1. Clone the repository
git clone https://github.com/Devoloper12/chatbot.git
cd chatbot

# 2. Install dependencies & register the 'chatbot' CLI command
pip install -r requirements.txt
pip install -e .

# 3. Configure your API key
cp .env.example .env     # On Windows CMD: copy .env.example .env
nano .env               # On Windows: notepad .env

# 4. Launch from any terminal!
chatbot
```

---

## 📸 Terminal Preview

```text
╭──────────────────────────────── ● ONLINE ────────────────────────────────╮
│ 🤖 Gemini Terminal AI Assistant v2.0.0                                   │
│ 🎓 Expert Programming Tutor & Computer Science Assistant                 │
│                                                                          │
│ Active Model   : gemini-2.5-flash                                        │
│ Current Session: #1 - 'C Programming & DSA Lab'                          │
│ Commands       : /help, /new, /list, /history, /savecode, /search, /exit │
╰──────────────────────────────────────────────────────────────────────────╯

You (#1): Write a C program to implement Quick Sort with time complexity.

Bot:
Here is the complete, exam-oriented C implementation of Quick Sort:

```c
#include <stdio.h>

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int partition(int arr[], int low, int high) {
    int pivot = arr[high]; // Choosing the last element as pivot
    int i = (low - 1);

    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return (i + 1);
}

void quickSort(int arr[], int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}
```

### ⏱️ Complexity Analysis
- **Best Case:** O(n log n)
- **Average Case:** O(n log n)
- **Worst Case:** O(n²) (when pivot is repeatedly smallest/largest element)
- **Space Complexity:** O(log n) (recursion stack)

⚡ Generated in 1.18s

You (#1): /savecode quicksort.c
[System] Extracted and saved code to: saved_code/quicksort.c
```

---

## ✨ Features

- **CLI Launcher (`chatbot`)**: Packaged with `setup.py` and `pyproject.toml` so you can launch the bot by simply typing `chatbot`.
- **Cross-Platform**: Tested on Windows Command Prompt, PowerShell, Ubuntu, Debian, Fedora, Arch Linux, and macOS.
- **Persistent Multi-Session Memory**: SQLite database (`chatbot.db`) automatically saves conversations and resumes your last session on startup.
- **Rich Terminal UI**: Animated typing spinner (`⠋ Thinking & compiling response...`), Markdown syntax highlighting, tables, and latency indicators.
- **Academic CS Tutor Persona**: Expert tutoring in C, Python, Data Structures, Algorithms, Linux/Ubuntu commands, Operating Systems, DBMS, and exam preparations.
- **Code Extraction & Saving**: Extract and save code blocks directly to files in `saved_code/` using `/savecode [filename]`.
- **Search & Export**: Search prior chats with `/search <query>` and export sessions to Markdown/TXT with `/export`.

---

## 📁 Project Structure

```text
chatbot/
├── chatbot.py          # Main entrypoint and interactive command loop
├── config.py           # Configuration, models, and smart AI system prompts
├── database.py         # SQLite persistence: sessions, messages, search, export
├── ui.py               # Rich UI components: banners, tables, markdown rendering
├── setup.py            # Packaging script for 'chatbot' console command
├── pyproject.toml      # Modern PEP 517 build configuration
├── requirements.txt    # Project dependencies
├── setup.sh            # Automated setup script for Linux & macOS
├── setup.bat           # Automated setup script for Windows CMD
├── setup.ps1           # Automated setup script for Windows PowerShell
├── chatbot.bat         # Direct Windows command runner
├── chatbot             # Direct Linux/macOS executable runner
├── run.sh              # Linux launcher script
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules (protects API keys, database, code)
├── CONTRIBUTING.md     # Contribution guidelines
├── LICENSE             # MIT License
└── README.md           # Documentation
```

---

## 🔑 Getting a Free Google Gemini API Key

1. Visit **[Google AI Studio](https://aistudio.google.com/)**.
2. Sign in with your Google account.
3. Click **"Get API key"** in the sidebar.
4. Click **"Create API key"** and copy your generated key string.

---

## 🚀 Installation by Operating System

### 1. Windows (Command Prompt & PowerShell)

#### Automated Setup (Fastest):
Double-click `setup.bat` (or run `.\setup.ps1` in PowerShell). It will create the virtual environment, install dependencies, and register the `chatbot` command.

#### Manual Setup:
```powershell
# 1. Clone the repository
git clone https://github.com/Devoloper12/chatbot.git
cd chatbot

# 2. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # On Command Prompt: .venv\Scripts\activate.bat

# 3. Install dependencies and CLI package
pip install -r requirements.txt
pip install -e .

# 4. Configure your API key
copy .env.example .env
notepad .env

# 5. Launch the chatbot!
chatbot
```

> **PowerShell Note:** If execution of scripts is blocked on Windows, run once:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

### 2. Ubuntu / Debian Linux

#### Automated Setup (Fastest):
```bash
chmod +x setup.sh
./setup.sh
```

#### Manual Setup:
```bash
# 1. Install Python 3 and venv tools if not present
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

# 2. Clone the repository
git clone https://github.com/Devoloper12/chatbot.git
cd chatbot

# 3. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install dependencies and register 'chatbot' command
pip install -r requirements.txt
pip install -e .

# 5. Configure API key
cp .env.example .env
nano .env

# 6. Launch!
chatbot
```

---

### 3. macOS

```bash
# 1. Clone repository
git clone https://github.com/Devoloper12/chatbot.git
cd chatbot

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies and CLI command
pip install -r requirements.txt
pip install -e .

# 4. Configure API key
cp .env.example .env
nano .env

# 5. Launch!
chatbot
```

---

## 🛠️ In-Chat Commands Reference

| Command | Description | Example |
| :--- | :--- | :--- |
| `/help` | Display command reference and CS tutor tips | `/help` |
| `/new [title]` | Create a fresh conversation session | `/new DSA Exam Prep` |
| `/list` | List all saved sessions with message counts | `/list` |
| `/switch <id>` | Switch to an existing conversation session | `/switch 2` |
| `/history [limit]` | View conversation messages for active session | `/history 10` |
| `/clear` | Clear message memory for active session | `/clear` |
| `/delete <id>` | Delete a session and its saved messages | `/delete 3` |
| `/savecode [name]` | Save code from last bot response to `saved_code/` | `/savecode dijkstra.c` |
| `/search <query>` | Full-text search across all saved sessions | `/search binary search` |
| `/export [md\|txt]` | Export conversation to Markdown or TXT | `/export md` |
| `/save` | Quick-save conversation to `exports/` | `/save` |
| `/about` | View bot version, active model, and stats | `/about` |
| `/exit`, `/quit` | Gracefully quit the chatbot | `/exit` |

---

## 🤝 Contributing

Contributions are warmly welcomed! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on submitting issues, features, and pull requests.

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).
