#!/usr/bin/env python3
"""
Simple Terminal AI Chatbot
A minimalist terminal chatbot with conversation memory powered by Groq and Gemini.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Database and configuration
from config import BASE_DIR, DEFAULT_GROQ_MODEL, SYSTEM_PROMPT
from database import ChatDatabase

# Groq and Gemini clients
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from google import genai
    from google.genai import types as genai_types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def load_api_key():
    """Loads API key from .env files or environment."""
    load_dotenv()
    load_dotenv(BASE_DIR / ".env")
    load_dotenv(Path.home() / ".terminal_ai_chatbot" / ".env")
    load_dotenv(Path.home() / ".gemini_chatbot" / ".env")

    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and groq_key.strip() and groq_key != "your_groq_api_key_here":
        return "groq", groq_key.strip(), os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)

    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key and gemini_key.strip() and gemini_key != "your_gemini_api_key_here":
        return "gemini", gemini_key.strip(), os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    # Prompt if missing
    print("API Key Required.")
    print("Get a free Groq key at: https://console.groq.com/keys")
    user_key = input("Enter GROQ_API_KEY: ").strip()
    if user_key:
        env_file = BASE_DIR / ".env"
        with open(env_file, "a", encoding="utf-8") as f:
            f.write(f"\nGROQ_API_KEY={user_key}\n")
        return "groq", user_key, DEFAULT_GROQ_MODEL

    sys.exit(1)


class SimpleAIClient:
    def __init__(self, provider, api_key, model_name):
        self.provider = provider
        self.api_key = api_key
        self.model_name = model_name
        self.history = []

        if self.provider == "groq":
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = genai.Client(api_key=self.api_key)
            self.chat = None

    def initialize_chat(self, past_messages=None):
        self.history = past_messages or []
        if self.provider == "gemini":
            contents = []
            for msg in self.history:
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
            self.chat = self.client.chats.create(
                model=self.model_name,
                config=config,
                history=contents if contents else None,
            )

    def get_response(self, user_message):
        if self.provider == "groq":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in self.history:
                role = "assistant" if m["role"] == "bot" else "user"
                messages.append({"role": role, "content": m["content"]})
            messages.append({"role": "user", "content": user_message})

            try:
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.6,
                    max_tokens=4096,
                )
                return completion.choices[0].message.content.strip()
            except Exception as e:
                if "rate_limit" in str(e).lower() and self.model_name != "openai/gpt-oss-20b":
                    self.model_name = "openai/gpt-oss-20b"
                    completion = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        temperature=0.6,
                        max_tokens=4096,
                    )
                    return completion.choices[0].message.content.strip()
                raise e
        else:
            if not self.chat:
                self.initialize_chat(self.history)
            res = self.chat.send_message(user_message)
            return res.text.strip()


def main():
    provider, api_key, model = load_api_key()
    db = ChatDatabase()
    session_id, _ = db.get_or_create_active_session()

    client = SimpleAIClient(provider, api_key, model)
    past_messages = db.get_session_messages(session_id)
    client.initialize_chat(past_messages)

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", ":q"):
                break

            if user_input.lower() == "clear":
                db.clear_session_messages(session_id)
                client.initialize_chat([])
                print("\n[Chat history cleared]\n")
                continue

            response = client.get_response(user_input)

            # Record into database memory
            db.add_message(session_id, "user", user_input)
            db.add_message(session_id, "bot", response)
            client.history.append({"role": "user", "content": user_input})
            client.history.append({"role": "bot", "content": response})

            print(f"\nBot: {response}\n")

        except (KeyboardInterrupt, EOFError):
            print()
            break
        except Exception as err:
            print(f"\nError: {err}\n")


if __name__ == "__main__":
    main()
