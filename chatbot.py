#!/usr/bin/env python3
"""
Simple Terminal AI Chatbot
A minimalist terminal chatbot with multi-provider automatic fallback
(Groq -> OpenRouter -> Ollama) and conversation memory.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from config import BASE_DIR, APP_NAME, APP_VERSION
from database import ChatDatabase
from providers import MultiProviderManager, reload_env_vars


def print_help():
    """Prints list of supported commands."""
    print("""
Commands:
  /provider       - Display current active provider
  /showproviders  - Show all providers, status, and priority
  /groq           - Switch to Groq (Primary)
  /openrouter     - Switch to OpenRouter (Secondary)
  /ollama         - Switch to Ollama (Fallback)
  /clear          - Clear current conversation history
  /help           - Show this help message
  /exit           - Exit the chatbot
""")


def ensure_api_keys(provider_manager: MultiProviderManager):
    """Prompts for an API key on first run if no provider is configured."""
    groq_p = provider_manager.providers.get("groq")
    or_p = provider_manager.providers.get("openrouter")
    ollama_p = provider_manager.providers.get("ollama")

    if not groq_p.is_configured() and not or_p.is_configured() and not ollama_p.is_configured():
        print("No API Key or Provider Configured.")
        print("Get a free Groq key at: https://console.groq.com/keys")
        print("Or an OpenRouter key at: https://openrouter.ai/keys")
        try:
            user_key = input("Enter GROQ_API_KEY (or press Enter to skip): ").strip()
            if user_key:
                env_file = BASE_DIR / ".env"
                with open(env_file, "a", encoding="utf-8") as f:
                    f.write(f"\nGROQ_API_KEY={user_key}\n")
                reload_env_vars()
                groq_p.refresh_config()
                provider_manager.current_provider_name = "groq"
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)


def main():
    reload_env_vars()
    provider_manager = MultiProviderManager()
    ensure_api_keys(provider_manager)

    db = ChatDatabase()
    session_id, _ = db.get_or_create_active_session()
    raw_history = db.get_session_messages(session_id)
    history = [{"role": m["role"], "content": m["content"]} for m in raw_history]

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            cmd = user_input.lower()

            # Exit command
            if cmd in ("/exit", "exit", "quit", ":q"):
                break

            # Help command
            if cmd == "/help":
                print_help()
                continue

            # Display active provider
            if cmd == "/provider":
                active = provider_manager.get_current_provider()
                model_info = getattr(active, "model", "")
                print(f"\nCurrent Provider: {active.display_name}" + (f" (Model: {model_info})\n" if model_info else "\n"))
                continue

            # Show all providers and status
            if cmd == "/showproviders":
                print(f"\n{provider_manager.show_providers()}\n")
                continue

            # Switch to Groq
            if cmd == "/groq":
                _, msg = provider_manager.set_provider("groq")
                print(f"\n{msg}\n")
                continue

            # Switch to OpenRouter
            if cmd == "/openrouter":
                _, msg = provider_manager.set_provider("openrouter")
                print(f"\n{msg}\n")
                continue

            # Switch to Ollama
            if cmd == "/ollama":
                _, msg = provider_manager.set_provider("ollama")
                print(f"\n{msg}\n")
                continue

            # Clear session history
            if cmd in ("/clear", "clear"):
                db.clear_session_messages(session_id)
                history.clear()
                print("\n[Chat history cleared]\n")
                continue

            # Process AI query with multi-provider fallback
            response, winning_provider = provider_manager.generate(user_input, history)

            if response:
                # Save to database memory and local history
                db.add_message(session_id, "user", user_input)
                db.add_message(session_id, "bot", response)
                history.append({"role": "user", "content": user_input})
                history.append({"role": "bot", "content": response})

                print(f"\nBot:\n\n{response}\n\nCurrent Provider: {winning_provider}\n")
            else:
                print("\nError: All AI providers failed. Check your API keys and internet connection.\n")

        except (KeyboardInterrupt, EOFError):
            print()
            break
        except Exception as err:
            print(f"\nError: {err}\n")


if __name__ == "__main__":
    main()
