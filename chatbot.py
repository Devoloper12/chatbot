#!/usr/bin/env python3
"""
=============================================================================
Terminal AI Chatbot (Powered by Groq & Gemini)
=============================================================================
A modern, persistent, and academic-oriented terminal AI assistant powered
primarily by Groq (LLaMA-3.3-70B / 8B) with fallback Gemini support.

Key Capabilities:
  - Ultra-fast responses powered by Groq LPU inference
  - Persistent SQLite chat memory across sessions
  - Rich-formatted terminal interface with spinners and Markdown rendering
  - Smart system prompt acting as an expert CS & programming tutor
  - College lab code generation (C, Python, DSA, Algorithms, Linux)
  - Code extraction and auto-saving to local files
  - Full-text conversation search and Markdown export
  - Cross-platform support (Windows, Ubuntu, Linux, macOS)
=============================================================================
"""

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Check & Load Essential Third-Party Libraries
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
except ImportError:
    print("\n[Error] The 'python-dotenv' package is not installed.")
    print("Please install dependencies: pip install -r requirements.txt\n")
    sys.exit(1)

try:
    from rich.console import Console
except ImportError:
    print("\n[Error] The 'rich' package is not installed.")
    print("Please install dependencies: pip install -r requirements.txt\n")
    sys.exit(1)

# Check Groq SDK
GROQ_AVAILABLE = False
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    pass

# Check Gemini SDK
GEMINI_AVAILABLE = False
try:
    from google import genai
    from google.genai import types as genai_types
    GEMINI_AVAILABLE = True
except ImportError:
    pass

# Import local modules
from config import (
    APP_NAME,
    APP_VERSION,
    BASE_DIR,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_GROQ_MODEL,
    DEFAULT_MODEL,
    SAVED_CODE_DIR,
    SYSTEM_PROMPT,
)
from database import ChatDatabase
from ui import (
    clear_screen,
    console,
    extract_code_blocks,
    print_about_panel,
    print_error,
    print_help_table,
    print_history_table,
    print_search_results,
    print_sessions_table,
    print_startup_banner,
    print_system_info,
    print_user_prompt,
    render_bot_response,
    save_code_to_file,
)


# ---------------------------------------------------------------------------
# Unified AI Client (Groq & Gemini)
# ---------------------------------------------------------------------------
class UnifiedAIClient:
    """Manages AI connections, multi-turn history, and responses across Groq and Gemini."""

    def __init__(self, provider: str, api_key: str, model_name: str):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model_name = model_name
        self.history_cache: List[Dict[str, Any]] = []
        self.groq_client = None
        self.gemini_client = None
        self.gemini_chat = None
        self._init_client()

    def _init_client(self) -> None:
        """Initializes the active provider client."""
        if self.provider == "groq":
            if not GROQ_AVAILABLE:
                raise ImportError("The 'groq' package is required. Install it using: pip install groq")
            self.groq_client = Groq(api_key=self.api_key)
        else:
            if not GEMINI_AVAILABLE:
                raise ImportError("The 'google-genai' package is required. Install it using: pip install google-genai")
            self.gemini_client = genai.Client(api_key=self.api_key)

    def initialize_chat(self, history_messages: Optional[List[Dict[str, Any]]] = None) -> None:
        """Initializes or restores conversation history."""
        self.history_cache = history_messages or []

        if self.provider == "gemini":
            contents = []
            for msg in self.history_cache:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(
                    genai_types.Content(
                        role=role,
                        parts=[genai_types.Part.from_text(text=msg["content"])],
                    )
                )
            config = genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            )
            self.gemini_chat = self.gemini_client.chats.create(
                model=self.model_name,
                config=config,
                history=contents if contents else None,
            )

    def send_message(self, user_message: str) -> str:
        """Routes message to the active provider."""
        if self.provider == "groq":
            return self._send_groq(user_message)
        else:
            return self._send_gemini(user_message)

    def _send_groq(self, user_message: str) -> str:
        """Sends chat request to Groq API (LLaMA-3.3-70B / 8B)."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        # Load multi-turn history
        for m in self.history_cache:
            role = "assistant" if m["role"] == "bot" else "user"
            messages.append({"role": role, "content": m["content"]})
        # Add current user prompt
        messages.append({"role": "user", "content": user_message})

        try:
            completion = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.6,
                max_tokens=4096,
            )
            reply = completion.choices[0].message.content
            return reply if reply else "(No response generated by model)"
        except Exception as error:
            error_str = str(error)
            # Automatic fallback to 20b if rate limited or unavailable
            if ("rate_limit" in error_str.lower() or "404" in error_str or "not_found" in error_str.lower()) and self.model_name != "openai/gpt-oss-20b":
                console.print("[dim yellow][System] Switching to openai/gpt-oss-20b...[/dim yellow]")
                self.model_name = "openai/gpt-oss-20b"
                completion = self.groq_client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.6,
                    max_tokens=4096,
                )
                reply = completion.choices[0].message.content
                return reply if reply else "(No response generated by model)"
            raise error

    def _send_gemini(self, user_message: str) -> str:
        """Sends chat request to Gemini API."""
        if not self.gemini_chat:
            self.initialize_chat(self.history_cache)
        try:
            response = self.gemini_chat.send_message(user_message)
            return response.text if response.text else "(No response generated by model)"
        except Exception as error:
            error_str = str(error)
            if "client has been closed" in error_str.lower():
                self.initialize_chat(self.history_cache)
                response = self.gemini_chat.send_message(user_message)
                return response.text if response.text else "(No response generated by model)"
            raise error


# ---------------------------------------------------------------------------
# API Key Verification & Provider Auto-Detection
# ---------------------------------------------------------------------------
def load_and_validate_api_key() -> Tuple[str, str, str]:
    """
    Loads API key and determines provider (Groq or Gemini).
    Returns: (provider, api_key, model_name)
    """
    load_dotenv()
    load_dotenv(BASE_DIR / ".env")
    load_dotenv(Path.home() / ".terminal_ai_chatbot" / ".env")
    load_dotenv(Path.home() / ".gemini_chatbot" / ".env")

    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    # 1. Check for Groq API Key
    if groq_key and groq_key.strip() and groq_key.strip() != "your_groq_api_key_here":
        model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip() or DEFAULT_GROQ_MODEL
        return "groq", groq_key.strip(), model

    # 2. Check for Gemini API Key (valid format)
    if gemini_key and gemini_key.strip().startswith("AIzaSy"):
        model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL
        return "gemini", gemini_key.strip(), model

    # 3. Interactive Setup for Groq Key (100% Free & Fast)
    console.print("\n[bold cyan]🚀 Groq AI Configuration (Ultra-Fast & 100% Free)[/bold cyan]")
    console.print("[dim]Get your free Groq API key in 5 seconds at: [bold green]https://console.groq.com/keys[/bold green][/dim]\n")

    try:
        prompt_key = console.input("[bold yellow]Enter your GROQ_API_KEY (starts with gsk_...): [/bold yellow]").strip()
        if prompt_key and (prompt_key.startswith("gsk_") or len(prompt_key) > 20):
            # Save key to local and home configuration
            for env_dir in [BASE_DIR, Path.home() / ".terminal_ai_chatbot", Path.home() / ".gemini_chatbot"]:
                try:
                    env_dir.mkdir(parents=True, exist_ok=True)
                    env_file = env_dir / ".env"
                    lines = []
                    if env_file.exists():
                        with open(env_file, "r", encoding="utf-8") as f:
                            lines = [line for line in f if not line.startswith("GROQ_API_KEY=")]
                    lines.append(f"GROQ_API_KEY={prompt_key}\n")
                    lines.append(f"GROQ_MODEL={DEFAULT_GROQ_MODEL}\n")
                    with open(env_file, "w", encoding="utf-8") as f:
                        f.writelines(lines)
                except Exception:
                    pass
            console.print("[bold green][✔] Groq API key configured successfully![/bold green]\n")
            return "groq", prompt_key, DEFAULT_GROQ_MODEL
    except (KeyboardInterrupt, EOFError):
        pass

    print_error(
        "API Key Required",
        "A free Groq API key is required to run the chatbot.\n\n"
        "👉 Steps to get a free key in 10 seconds:\n"
        "1. Open https://console.groq.com/keys\n"
        "2. Click 'Create API Key'\n"
        "3. Paste it when prompted or save in .env: GROQ_API_KEY=gsk_...\n"
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Interactive Command Handlers
# ---------------------------------------------------------------------------
class ChatbotApp:
    """Main application controller managing state, commands, and chat flow."""

    def __init__(self):
        self.provider, self.api_key, self.model_name = load_and_validate_api_key()
        self.auto_save_code = os.getenv("AUTO_SAVE_CODE", "false").lower() in ("true", "1", "yes")

        self.db = ChatDatabase()
        self.ai_client = UnifiedAIClient(
            provider=self.provider,
            api_key=self.api_key,
            model_name=self.model_name,
        )

        # Active Session State
        self.current_session_id, self.current_session_title = self.db.get_or_create_active_session()
        self.last_bot_response: Optional[str] = None

        # Re-sync AI conversation memory from SQLite
        self._load_active_session_into_ai()

    def _load_active_session_into_ai(self) -> None:
        """Loads previous messages from database into AI chat context."""
        history = self.db.get_session_messages(self.current_session_id)
        try:
            self.ai_client.initialize_chat(history)
        except Exception as e:
            print_error("Failed to Initialize Session", str(e))

    def handle_command(self, cmd_line: str) -> bool:
        """
        Processes terminal commands. Returns True if handled as a command,
        or False if it should be treated as a normal chat prompt.
        """
        tokens = cmd_line.strip().split(maxsplit=1)
        command = tokens[0].lower()
        args = tokens[1].strip() if len(tokens) > 1 else ""

        # Normalize slash commands and plain keywords
        if command in ("/exit", "exit", "/quit", "quit", ":q"):
            print_system_info("Closing chat session. Happy coding!")
            sys.exit(0)

        elif command in ("/help", "help", "/?"):
            print_help_table()
            return True

        elif command in ("/clear", "clear"):
            self.db.clear_session_messages(self.current_session_id)
            self._load_active_session_into_ai()
            clear_screen()
            print_startup_banner(f"{self.provider.upper()}: {self.model_name}", self.current_session_id, self.current_session_title)
            print_system_info(f"Chat history cleared for session #{self.current_session_id}. Fresh context ready.")
            return True

        elif command in ("/history", "history"):
            limit = int(args) if args.isdigit() else None
            messages = self.db.get_session_messages(self.current_session_id, limit=limit)
            print_history_table(messages, self.current_session_title)
            return True

        elif command in ("/new", "new"):
            new_title = args if args else None
            self.current_session_id, self.current_session_title = self.db.create_session(new_title)
            self._load_active_session_into_ai()
            clear_screen()
            print_startup_banner(f"{self.provider.upper()}: {self.model_name}", self.current_session_id, self.current_session_title)
            print_system_info(f"Created new session #{self.current_session_id}: '{self.current_session_title}'.")
            return True

        elif command in ("/list", "list", "/sessions"):
            sessions = self.db.list_sessions()
            print_sessions_table(sessions, self.current_session_id)
            return True

        elif command in ("/switch", "switch"):
            if not args or not args.isdigit():
                print_error("Invalid Usage", "Please provide a valid session ID. Example: /switch 2")
                return True
            target_id = int(args)
            if not self.db.session_exists(target_id):
                print_error("Session Not Found", f"No session exists with ID #{target_id}.")
                return True

            self.current_session_id = target_id
            self.current_session_title = self.db.get_session_title(target_id) or f"Session #{target_id}"
            self._load_active_session_into_ai()
            clear_screen()
            print_startup_banner(f"{self.provider.upper()}: {self.model_name}", self.current_session_id, self.current_session_title)
            print_system_info(f"Switched to session #{self.current_session_id}: '{self.current_session_title}'.")
            return True

        elif command in ("/delete", "delete"):
            target_id = int(args) if args.isdigit() else self.current_session_id
            if not self.db.session_exists(target_id):
                print_error("Session Not Found", f"No session with ID #{target_id} to delete.")
                return True

            deleted = self.db.delete_session(target_id)
            if deleted:
                print_system_info(f"Session #{target_id} has been deleted.")
                if target_id == self.current_session_id:
                    self.current_session_id, self.current_session_title = self.db.get_or_create_active_session()
                    self._load_active_session_into_ai()
                    print_system_info(f"Switched to active session #{self.current_session_id}: '{self.current_session_title}'.")
            return True

        elif command in ("/export", "export", "/save", "save"):
            fmt = args.lower() if args else "markdown"
            export_path = self.db.export_session(self.current_session_id, export_format=fmt)
            if export_path:
                print_system_info(f"Conversation exported successfully to:\n  [bold cyan]{export_path}[/bold cyan]")
            else:
                print_error("Export Failed", "Could not export session messages.")
            return True

        elif command in ("/savecode", "savecode", "/copy"):
            if not self.last_bot_response:
                print_error("No Code Found", "The bot hasn't generated any code in the current interaction.")
                return True

            blocks = extract_code_blocks(self.last_bot_response)
            if not blocks:
                print_error("No Code Blocks Found", "The previous response did not contain any fenced code blocks (```).")
                return True

            custom_name = args if args else None
            saved_paths = save_code_to_file(blocks, custom_filename=custom_name)
            for path in saved_paths:
                print_system_info(f"Extracted and saved code to: [bold green]{path}[/bold green]")
            return True

        elif command in ("/search", "search"):
            if not args:
                print_error("Search Query Missing", "Usage: /search <keyword>. Example: /search binary search")
                return True
            results = self.db.search_messages(args)
            print_search_results(results, args)
            return True

        elif command in ("/about", "about"):
            stats = self.db.get_database_stats()
            print_about_panel(stats, f"{self.provider.upper()} ({self.model_name})")
            return True

        return False

    def process_chat_message(self, user_input: str) -> None:
        """Sends user message to AI provider, measures latency, and renders response."""
        start_time = time.perf_counter()
        bot_reply = ""
        duration = 0.0

        try:
            # Rich animated spinner typing indicator
            with console.status(
                f"[bold cyan]Thinking & compiling response ({self.provider.upper()} {self.model_name})...[/bold cyan]",
                spinner="dots",
            ):
                bot_reply = self.ai_client.send_message(user_input)
                duration = time.perf_counter() - start_time

            # Update state and local SQLite storage
            self.last_bot_response = bot_reply
            self.db.add_message(self.current_session_id, "user", user_input)
            self.db.add_message(self.current_session_id, "bot", bot_reply, duration=duration)

            # Render formatted Markdown response
            render_bot_response(bot_reply, duration_seconds=duration)

            # Optional automatic code saving
            if self.auto_save_code:
                blocks = extract_code_blocks(bot_reply)
                if blocks:
                    paths = save_code_to_file(blocks)
                    for p in paths:
                        console.print(f"[dim]📁 Auto-saved code block to {p.name}[/dim]")

        except Exception as error:
            error_str = str(error)
            error_lower = error_str.lower()

            if "rate_limit" in error_lower or "429" in error_str:
                print_error(
                    "Rate Limit Exceeded (HTTP 429)",
                    "You have hit the provider rate limit. Please wait a few seconds before asking another question.",
                )
            elif "authentication" in error_lower or "401" in error_str or "api_key" in error_lower:
                print_error(
                    "Authentication Failure",
                    f"Invalid {self.provider.upper()} API key. Check your key in .env.",
                )
            elif any(net in error_lower for net in ["connection", "timeout", "timed out", "dns", "getaddrinfo"]):
                print_error(
                    "Network Connection Failure",
                    "Unable to reach AI servers. Check your internet connection.",
                )
            else:
                print_error(f"{self.provider.upper()} API Error", error_str)

    def run(self) -> None:
        """Main application execution loop."""
        clear_screen()
        print_startup_banner(f"{self.provider.upper()}: {self.model_name}", self.current_session_id, self.current_session_title)

        while True:
            try:
                user_input = print_user_prompt(self.current_session_id)

                # Skip empty input
                if not user_input:
                    continue

                # Handle slash commands or plain commands
                if user_input.startswith("/") or user_input.lower() in [
                    "exit", "quit", "help", "clear", "history", "list", "save", "about"
                ]:
                    was_command = self.handle_command(user_input)
                    if was_command:
                        continue

                # Normal conversational question
                self.process_chat_message(user_input)

            except (KeyboardInterrupt, EOFError):
                print_system_info("\nSession interrupted. Goodbye!")
                break


# ---------------------------------------------------------------------------
# Application Entry Point (CLI launcher)
# ---------------------------------------------------------------------------
def main() -> None:
    """Main CLI entrypoint for the 'chatbot' command."""
    app = ChatbotApp()
    app.run()


if __name__ == "__main__":
    main()
