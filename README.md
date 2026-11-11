# Terminal AI Chatbot

A simple, fast, and minimalist terminal AI chatbot with conversation memory. Powered by Groq and Google Gemini.

Runs entirely in your terminal with zero visual clutter: no banners, no colors, no decorative boxes, and no loading indicators.

---

## Usage

```text
You: Hello
Bot: Hi, how can I help you?

You: Write a C program for BFS
Bot: [answer]
```

Commands:
- `clear` — Clear the conversation history
- `exit` or `quit` — Quit the chatbot

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/Devoloper12/chatbot.git
cd chatbot
pip install -r requirements.txt
pip install -e .
```

### 2. Configure API Key

Create `.env` or set your environment variable:

```bash
# In .env
GROQ_API_KEY=gsk_...
```
*(Get a free Groq API key at https://console.groq.com/keys)*

### 3. Run

```bash
chatbot
```
*(Or `python chatbot.py`)*

---

## Cross-Platform Compatibility

Works natively on:
- Windows (Command Prompt & PowerShell)
- Ubuntu / Debian
- Linux
- macOS

---

## License

MIT License.
