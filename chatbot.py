#!/usr/bin/env python3
"""
=============================================================================
Gemini Terminal AI Chatbot
=============================================================================
A modern, persistent, and academic-oriented terminal AI assistant powered
by the Google Gemini API.

Key Capabilities:
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

# Check Gemini SDK (Modern google-genai vs legacy google-generativeai)
SDK_MODE = None
try:
    from google import genai
    from google.genai import types as genai_types
    from google.genai import errors as genai_errors
    SDK_MODE = "google-genai"
except ImportError:
    try:
        import google.generativeai as legacy_genai
        from google.api_core import exceptions as legacy_errors
        SDK_MODE = "google-generativeai"
    except ImportError:
        print("\n[Error] Neither 'google-genai' nor 'google-generativeai' is installed.")
        print("Please install required packages: pip install -r requirements.txt\n")
        sys.exit(1)

# Import local modules
from config import (
    APP_NAME,
    APP_VERSION,
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
# Gemini AI Client & Session Wrapper
# ---------------------------------------------------------------------------
class GeminiClient:
    """Manages connection, system prompts, context history, and communication."""

    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.chat = None

    def initialize_chat(self, history_messages: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Initializes or restores a chat session with the expert CS tutor
        system prompt and historical conversation turns.
        """
        history_messages = history_messages or []

        if SDK_MODE == "google-genai":
            client = genai.Client(api_key=self.api_key)
            contents = []
            for msg in history_messages:
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
            self.chat = client.chats.create(
                model=self.model_name,
                config=config,
                history=contents if contents else None,
            )
        else:
            legacy_genai.configure(api_key=self.api_key)
            model = legacy_genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=SYSTEM_PROMPT,
            )
            legacy_history = []
            for msg in history_messages:
                role = "user" if msg["role"] == "user" else "model"
                legacy_history.append({"role": role, "parts": [msg["content"]]})
            self.chat = model.start_chat(history=legacy_history)

    def send_message(self, user_message: str) -> str:
        """Sends a message to the active chat session and returns the AI reply."""
        if not self.chat:
            self.initialize_chat()

        response = self.chat.send_message(user_message)
        return response.text if response.text else "(No response generated by model)"


# ---------------------------------------------------------------------------
# API Key Verification
# ---------------------------------------------------------------------------
def load_and_validate_api_key() -> str:
    """Loads and validates the Gemini API key from the environment."""
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    placeholder = "your_gemini_api_key_here"

    if not key or key.strip() == "" or key.strip() == placeholder:
        print_error(
            "Missing or Invalid GEMINI_API_KEY",
            "Please configure your Gemini API Key in the '.env' file.\n\n"
            "Steps to configure:\n"
            "1. Visit https://aistudio.google.com/ to generate a free API key.\n"
            "2. Copy '.env.example' to '.env'.\n"
            "3. Set GEMINI_API_KEY=AIzaSy...your_actual_key_here\n"
        )
        sys.exit(1)

    return key.strip()


# ---------------------------------------------------------------------------
# Interactive Command Handlers
# ---------------------------------------------------------------------------
class ChatbotApp:
    """Main application controller managing state, commands, and chat flow."""

    def __init__(self):
        self.api_key = load_and_validate_api_key()
        self.model_name = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
        self.auto_save_code = os.getenv("AUTO_SAVE_CODE", "false").lower() in ("true", "1", "yes")

        self.db = ChatDatabase()
        self.ai_client = GeminiClient(api_key=self.api_key, model_name=self.model_name)

        # Active Session State
        self.current_session_id, self.current_session_title = self.db.get_or_create_active_session()
        self.last_bot_response: Optional[str] = None

        # Re-sync AI conversation memory from SQLite
        self._load_active_session_into_ai()

    def _load_active_session_into_ai(self) -> None:
        """Loads previous messages from database into Gemini chat context."""
        history = self.db.get_session_messages(self.current_session_id)
        try:
            self.ai_client.initialize_chat(history)
        except Exception as e:
            print_error("Failed to Initialize Gemini Session", str(e))

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
            print_startup_banner(self.model_name, self.current_session_id, self.current_session_title)
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
            print_startup_banner(self.model_name, self.current_session_id, self.current_session_title)
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
            print_startup_banner(self.model_name, self.current_session_id, self.current_session_title)
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
                # If deleted current session, switch to or create another
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
            print_about_panel(stats, self.model_name)
            return True

        return False

    def process_chat_message(self, user_input: str) -> None:
        """Sends user message to Gemini API, measures latency, and handles errors."""
        start_time = time.perf_counter()
        bot_reply = ""
        duration = 0.0

        try:
            # Rich animated spinner typing indicator
            with console.status(
                f"[bold cyan]Thinking & compiling response ({self.model_name})...[/bold cyan]",
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

            if "429" in error_str or "quota" in error_lower or "resource_exhausted" in error_lower:
                print_error(
                    "Rate Limit Exceeded (HTTP 429)",
                    "You have hit the Gemini API rate limit or free tier quota.\n"
                    "Please wait a few seconds before asking another question.",
                )
            elif "400" in error_str or "403" in error_str or "api_key" in error_lower:
                print_error(
                    "Authentication Failure",
                    "The Gemini API rejected your key. Please verify your GEMINI_API_KEY in .env.",
                )
            elif any(net in error_lower for net in ["connection", "timeout", "timed out", "dns", "getaddrinfo"]):
                print_error(
                    "Network Connection Failure",
                    "Unable to reach Google Gemini servers. Check your internet connection.",
                )
            else:
                print_error("Gemini API Error", error_str)

    def run(self) -> None:
        """Main application execution loop."""
        clear_screen()
        print_startup_banner(self.model_name, self.current_session_id, self.current_session_title)

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
# Application Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = ChatbotApp()
    app.run()
