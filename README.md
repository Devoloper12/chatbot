# Terminal AI Chatbot

A simple, fast, and minimalist multi-provider terminal AI chatbot with automatic fallback and conversation memory.

Provider Priority:
1. **Groq** (Primary)
2. **OpenRouter** (Secondary)
3. **Ollama** (Fallback)

Runs entirely in your terminal with zero visual clutter: no banners, no colors, no decorative boxes, and no animations.

---

## Features

- **Automatic Provider Fallback:** Seamlessly shifts from Groq -> OpenRouter -> Ollama if a provider hits rate limits, runs out of credits, times out, or fails.
- **Remember Last Working Provider:** Stays on the successful provider for subsequent requests to avoid repeated failure delays.
- **Manual Provider Selection:** Switch providers anytime using simple slash commands.
- **Persistent Conversation Memory:** Conversations are safely stored in local SQLite database (`chatbot.db`).
- **College Lab Exam Tutor:** Structured for MCA and B.Tech students with exam-ready, concise DSA algorithms and clean code.

---

## Usage

```text
You: simple quick sort algorithm

Bot:
Algorithm:
1. Choose a pivot element.
2. Partition the array around the pivot.
3. Recursively sort left subarray.
4. Recursively sort right subarray.
5. Repeat until sorted.

Current Provider: Groq
```

### Commands

| Command | Description |
|---|---|
| `/provider` | Display the current active provider and model |
| `/showproviders` | List all providers, priority, and configuration status |
| `/groq` | Manually switch active provider to Groq |
| `/openrouter` | Manually switch active provider to OpenRouter |
| `/ollama` | Manually switch active provider to Ollama |
| `/clear` | Clear the current conversation history |
| `/help` | Show available commands |
| `/exit` | Exit the chatbot (also `exit`, `quit`, `:q`) |

---

## Fallback Example

```text
You: Explain Quick Sort

Trying provider: Groq...
Groq unavailable. Switching to OpenRouter...
Response received.

Bot:
Quick Sort is a divide-and-conquer sorting algorithm...

Current Provider: OpenRouter
```

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/Devoloper12/chatbot.git
cd chatbot
pip install -r requirements.txt
pip install -e .
```

### 2. Configure Environment Variables

Create or edit your `.env` file:

```env
# 1. Groq (Primary)
GROQ_API_KEY=gsk_...
GROQ_MODEL=openai/gpt-oss-120b

# 2. OpenRouter (Secondary)
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct:free

# 3. Ollama (Fallback)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

- Get a free Groq API key: [https://console.groq.com/keys](https://console.groq.com/keys)
- Get an OpenRouter API key: [https://openrouter.ai/keys](https://openrouter.ai/keys)
- Download and run Ollama: [https://ollama.com](https://ollama.com)

### 3. Run

```bash
chatbot
```
*(Or `python chatbot.py`)*

---

## Cross-Platform Compatibility

Works natively on:
- Windows (Command Prompt & PowerShell)
- Ubuntu / Debian / Linux
- macOS

---

## License

MIT License.
