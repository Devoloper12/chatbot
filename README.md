# 🤖 Gemini Terminal AI Chatbot & Programming Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Platform: Cross--Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-green.svg)]()
[![Powered By: Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini%20API-orange.svg)](https://aistudio.google.com/)

An advanced, interactive terminal AI chatbot and expert programming tutor powered by the **Google Gemini API**. Built with local **SQLite persistence**, multi-session memory, **Rich terminal styling**, syntax-highlighted code rendering, and academic CS lab capabilities.

Compatible with **Windows (CMD/PowerShell)**, **Ubuntu / Debian**, **Linux**, and **macOS**.

---

## 📸 Terminal Preview & Screenshots

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

## ✨ Key Features

### 1. 🧠 Persistent Multi-Session Chat Memory
- Saves all conversations locally using **SQLite** (`chatbot.db`).
- Resumes the most recent conversation automatically on startup.
- Supports switching, creating, listing, searching, and deleting separate sessions.

### 2. 🎨 Rich Terminal UI
- Rendered using Python's **`rich`** library.
- Animated typing spinner (`⠋ Thinking & compiling response...`).
- Full terminal **Markdown rendering** (tables, lists, syntax-highlighted code).
- Accurate generation latency display (`⚡ Generated in 1.25s`).

### 3. 🎓 Smart AI Programming Tutor
Configured via an academic system instruction specializing in:
- **C Programming** & System Calls (Pointers, Memory Allocation, Structures, Fork, Threads).
- **Python Programming** (OOP, Generators, Async, Data Analysis, Scripting).
- **Data Structures & Algorithms (DSA)** (Linked Lists, Stacks, Queues, Trees, Graphs, DP).
- **Exam Algorithms** (Step-by-step algorithms with time/space complexity analysis).
- **Code Debugging** & Line-by-Line explanations.
- **Linux & Ubuntu Terminal Commands** (`grep`, `find`, `awk`, `chmod`, shell scripting).
- **Core CS Subjects** (OS, DBMS, SQL, Computer Networks).

### 4. 💾 Code Extraction & Auto-Saving
- Automatically extract code blocks from AI replies with `/savecode [filename]`.
- Saves code with appropriate extensions (`.c`, `.py`, `.sh`, `.sql`) into `saved_code/`.
- Optional `AUTO_SAVE_CODE=true` flag in `.env` to save code automatically.

### 5. 🔍 Full-Text Conversation Search
- Search through all previous chats and lab sessions with `/search <keyword>`.
- Displays snippet matches with timestamps and session IDs in a formatted table.

---

## 📁 Project Structure

```text
gemini-terminal-chatbot/
├── chatbot.py          # Main entrypoint and interactive command loop
├── config.py           # Configuration, models, and smart AI system prompts
├── database.py         # SQLite persistence: sessions, messages, search, export
├── ui.py               # Rich UI components: banners, tables, markdown rendering
├── requirements.txt    # Project dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules (protects API keys, database, code)
├── CONTRIBUTING.md     # Contribution guidelines
├── LICENSE             # MIT License
└── README.md           # Documentation
```

---

## 🔑 Getting a Free Google Gemini API Key

1. Go to **[Google AI Studio](https://aistudio.google.com/)**.
2. Sign in with your Google account.
3. Click **"Get API key"** in the left navigation menu.
4. Click **"Create API key"**.
5. Copy your generated key string.

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/gemini-terminal-chatbot.git
cd gemini-terminal-chatbot
```

---

### 2. Set Up a Virtual Environment

#### On Windows (PowerShell / Command Prompt)

```powershell
# Create virtual environment
python -m venv venv

# Activate on PowerShell:
.\venv\Scripts\Activate.ps1

# Or activate on Command Prompt (cmd.exe):
.\venv\Scripts\activate.bat
```

> **Note for Windows PowerShell:** If script execution is blocked, enable it by running:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

#### On Ubuntu / Debian Linux

```bash
# Install Python 3 venv tools if not present
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

#### On macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

With your virtual environment activated:

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create your `.env` configuration file from the template:

#### Linux / macOS:
```bash
cp .env.example .env
```

#### Windows (PowerShell):
```powershell
Copy-Item .env.example .env
```

#### Windows (Command Prompt):
```cmd
copy .env.example .env
```

Open `.env` in any text editor and paste your API key:

```env
# Required: Your Google Gemini API Key
GEMINI_API_KEY=AIzaSyYourActualKeyHere

# Optional: Preferred Gemini Model (default: gemini-2.5-flash)
GEMINI_MODEL=gemini-2.5-flash

# Optional: Automatically save extracted code blocks to saved_code/ (true/false)
AUTO_SAVE_CODE=false
```

---

## 💬 Running the Chatbot

Make sure your virtual environment is activated, then launch:

```bash
python chatbot.py
```
*(Or `python3 chatbot.py` on Linux/macOS)*

---

## 🛠️ Complete Command Reference

| Command | Description | Example |
| :--- | :--- | :--- |
| `/help` | Show full command table and academic tips | `/help` |
| `/new [title]` | Create and switch to a new conversation session | `/new DSA Lab Exam Prep` |
| `/list` | List all saved conversation sessions with message counts | `/list` |
| `/switch <id>` | Switch to an existing conversation session | `/switch 2` |
| `/history [limit]` | View conversation history for the active session | `/history 10` |
| `/clear` | Clear message history for the active session | `/clear` |
| `/delete <id>` | Delete a session and its message history | `/delete 3` |
| `/savecode [name]` | Extract and save code from the last bot response to `saved_code/` | `/savecode dijkstra.c` |
| `/search <query>` | Full-text search across all previous chats | `/search binary tree` |
| `/export [md\|txt]` | Export current conversation to Markdown or TXT in `exports/` | `/export md` |
| `/save` | Quick-save conversation to `exports/` | `/save` |
| `/about` | View bot version, active model, and database statistics | `/about` |
| `/exit`, `/quit` | Gracefully quit the chatbot | `/exit` |

---

## 🎯 Example Academic & Programming Prompts

Try asking these questions in the terminal:

- **College Lab Programs:**
  > *"Write a menu-driven C program to implement a Circular Queue with enqueue, dequeue, and display functions."*
- **Exam Algorithms:**
  > *"Give an exam-oriented algorithm for Kruskal's Minimum Spanning Tree with time complexity analysis and sample I/O."*
- **Line-by-Line Code Explanation:**
  > *"Explain how this Python quicksort implementation works line by line."*
- **Code Debugging:**
  > *"Debug this C program that produces a Segmentation Fault when inserting into a linked list: [paste code]"*
- **Linux & Shell Commands:**
  > *"Explain how to use find and xargs to delete all .tmp files recursively on Ubuntu."*

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on submitting issues, feature requests, and pull requests.

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).
