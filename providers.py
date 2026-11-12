"""
=============================================================================
Multi-Provider Architecture with Automatic Fallback
=============================================================================
Implements Groq (Primary), OpenRouter (Secondary), and Ollama (Fallback).
Features automatic fallback on failure/rate-limit, manual provider switching,
and remembering the last working provider.
=============================================================================
"""

import os
import sys
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

from config import (
    BASE_DIR,
    DEFAULT_GROQ_MODEL,
    DEFAULT_OLLAMA_BASE_URL,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OPENROUTER_MODEL,
    PROVIDER_DISPLAY_NAMES,
    PROVIDER_GROQ,
    PROVIDER_OLLAMA,
    PROVIDER_OPENROUTER,
    PROVIDERS_ORDER,
    SYSTEM_PROMPT,
)

# Optional Groq SDK
try:
    from groq import Groq
    GROQ_SDK_AVAILABLE = True
except ImportError:
    GROQ_SDK_AVAILABLE = False


def reload_env_vars() -> None:
    """Reloads environment variables from known .env files."""
    load_dotenv(override=False)
    load_dotenv(BASE_DIR / ".env", override=False)
    load_dotenv(Path.home() / ".terminal_ai_chatbot" / ".env", override=False)
    load_dotenv(Path.home() / ".gemini_chatbot" / ".env", override=False)


class BaseProvider:
    """Base class for all AI model providers."""

    def __init__(self, name: str, display_name: str):
        self.name = name
        self.display_name = display_name

    def is_configured(self) -> bool:
        raise NotImplementedError

    def get_status_line(self) -> str:
        raise NotImplementedError

    def generate(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError


class GroqProvider(BaseProvider):
    """
    Groq Provider (Primary)
    Uses Groq SDK or direct OpenAI-compatible API.
    """

    def __init__(self):
        super().__init__(PROVIDER_GROQ, PROVIDER_DISPLAY_NAMES[PROVIDER_GROQ])
        self.api_key: Optional[str] = None
        self.model: str = DEFAULT_GROQ_MODEL
        self._groq_client = None
        self.refresh_config()

    def refresh_config(self) -> None:
        reload_env_vars()
        key = os.getenv("GROQ_API_KEY", "").strip()
        if key and key != "your_groq_api_key_here":
            self.api_key = key
        else:
            self.api_key = None
        self.model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip() or DEFAULT_GROQ_MODEL
        if GROQ_SDK_AVAILABLE and self.api_key:
            try:
                self._groq_client = Groq(api_key=self.api_key)
            except Exception:
                self._groq_client = None

    def is_configured(self) -> bool:
        self.refresh_config()
        return bool(self.api_key)

    def get_status_line(self) -> str:
        self.refresh_config()
        if not self.api_key:
            return f"{self.display_name} (Primary) - Not Configured [Set GROQ_API_KEY in .env]"
        masked = self.api_key[:8] + "..." + self.api_key[-4:] if len(self.api_key) > 12 else "***"
        return f"{self.display_name} (Primary) - Configured [Key: {masked}, Model: {self.model}]"

    def generate(self, messages: List[Dict[str, str]]) -> str:
        self.refresh_config()
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY not configured.")

        # Attempt with primary model, then auto-fallback models
        models_to_try = [self.model]
        if "openai/gpt-oss-20b" not in models_to_try:
            models_to_try.append("openai/gpt-oss-20b")
        if "llama-3.3-70b-versatile" not in models_to_try:
            models_to_try.append("llama-3.3-70b-versatile")

        last_error = None
        for current_model in models_to_try:
            try:
                # 1. Use Groq SDK if available
                if GROQ_SDK_AVAILABLE and self._groq_client:
                    completion = self._groq_client.chat.completions.create(
                        model=current_model,
                        messages=messages,
                        temperature=0.6,
                        max_tokens=4096,
                        timeout=20.0,
                    )
                    content = completion.choices[0].message.content
                    if content:
                        return content.strip()

                # 2. Direct HTTP fallback if SDK is unavailable or failed
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": current_model,
                    "messages": messages,
                    "temperature": 0.6,
                    "max_tokens": 4096,
                }
                res = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=20.0,
                )
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"].strip()

                error_data = {}
                try:
                    error_data = res.json()
                except Exception:
                    pass
                msg = error_data.get("error", {}).get("message", res.text)
                raise RuntimeError(f"HTTP {res.status_code}: {msg}")

            except Exception as e:
                err_str = str(e).lower()
                last_error = e
                if ("rate_limit" in err_str or "not exist" in err_str or "model" in err_str) and current_model != models_to_try[-1]:
                    continue
                raise e

        if last_error:
            raise last_error
        raise RuntimeError("Groq request failed.")


class OpenRouterProvider(BaseProvider):
    """
    OpenRouter Provider (Secondary)
    Uses OpenAI-compatible endpoint at https://openrouter.ai/api/v1/chat/completions
    """

    def __init__(self):
        super().__init__(PROVIDER_OPENROUTER, PROVIDER_DISPLAY_NAMES[PROVIDER_OPENROUTER])
        self.api_key: Optional[str] = None
        self.model: str = DEFAULT_OPENROUTER_MODEL
        self.refresh_config()

    def refresh_config(self) -> None:
        reload_env_vars()
        key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if key and key != "your_openrouter_api_key_here":
            self.api_key = key
        else:
            self.api_key = None
        self.model = os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL).strip() or DEFAULT_OPENROUTER_MODEL

    def is_configured(self) -> bool:
        self.refresh_config()
        return bool(self.api_key)

    def get_status_line(self) -> str:
        self.refresh_config()
        if not self.api_key:
            return f"{self.display_name} (Secondary) - Not Configured [Set OPENROUTER_API_KEY in .env]"
        masked = self.api_key[:8] + "..." + self.api_key[-4:] if len(self.api_key) > 12 else "***"
        return f"{self.display_name} (Secondary) - Configured [Key: {masked}, Model: {self.model}]"

    def generate(self, messages: List[Dict[str, str]]) -> str:
        self.refresh_config()
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not configured.")

        # Candidate models including active free tier fallbacks
        models_to_try = [self.model]
        free_fallbacks = [
            "openrouter/free",
            "nvidia/nemotron-3.5-lightning:free",
            "liquid/lfm-2.5-2.6b:free",
            "liquid/lfm-3-1.7b:free",
        ]
        for fb in free_fallbacks:
            if fb not in models_to_try:
                models_to_try.append(fb)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Devoloper12/chatbot",
            "X-Title": "Terminal AI Chatbot",
        }

        last_error = None
        for current_model in models_to_try:
            try:
                payload = {
                    "model": current_model,
                    "messages": messages,
                    "temperature": 0.6,
                    "max_tokens": 4096,
                }
                res = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=25.0,
                )

                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    if content:
                        return content.strip()

                error_data = {}
                try:
                    error_data = res.json()
                except Exception:
                    pass
                msg = error_data.get("error", {}).get("message", res.text)

                if res.status_code == 401:
                    raise RuntimeError("Invalid OPENROUTER_API_KEY.")
                if res.status_code == 402:
                    raise RuntimeError("OpenRouter credits exhausted or insufficient.")

                # If model is unavailable (404), rate-limited (429), or server error (5xx)
                if current_model != models_to_try[-1]:
                    continue

                raise RuntimeError(f"HTTP {res.status_code}: {msg}")

            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                if "invalid openrouter_api_key" in err_str or "credits exhausted" in err_str:
                    raise e
                if current_model != models_to_try[-1]:
                    continue
                raise e

        if last_error:
            raise last_error
        raise RuntimeError("OpenRouter request failed.")


class OllamaProvider(BaseProvider):
    """
    Ollama Provider (Fallback)
    Uses local Ollama daemon (default: http://localhost:11434).
    """

    def __init__(self):
        super().__init__(PROVIDER_OLLAMA, PROVIDER_DISPLAY_NAMES[PROVIDER_OLLAMA])
        self.base_url: str = DEFAULT_OLLAMA_BASE_URL
        self.model: str = DEFAULT_OLLAMA_MODEL
        self.refresh_config()

    def refresh_config(self) -> None:
        reload_env_vars()
        url = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).strip()
        self.base_url = url.rstrip("/") if url else DEFAULT_OLLAMA_BASE_URL
        self.model = os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL).strip() or DEFAULT_OLLAMA_MODEL

    def is_configured(self) -> bool:
        self.refresh_config()
        return bool(self.base_url)

    def get_status_line(self) -> str:
        self.refresh_config()
        return f"{self.display_name} (Fallback) - Configured [URL: {self.base_url}, Model: {self.model}]"

    def generate(self, messages: List[Dict[str, str]]) -> str:
        self.refresh_config()
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.6,
                },
            }
            res = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=30.0,
            )

            if res.status_code == 200:
                data = res.json()
                content = data.get("message", {}).get("content", "")
                if content:
                    return content.strip()

            if res.status_code == 404:
                # Try to see if there is another model available
                try:
                    tags_res = requests.get(f"{self.base_url}/api/tags", timeout=2.0)
                    if tags_res.status_code == 200:
                        tags_data = tags_res.json()
                        models = [m.get("name") for m in tags_data.get("models", []) if m.get("name")]
                        if models:
                            alt_model = models[0]
                            payload["model"] = alt_model
                            alt_res = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=30.0)
                            if alt_res.status_code == 200:
                                return alt_res.json().get("message", {}).get("content", "").strip()
                except Exception:
                    pass
                raise RuntimeError(f"Model '{self.model}' not found in Ollama.")

            raise RuntimeError(f"Ollama HTTP {res.status_code}: {res.text}")

        except requests.exceptions.ConnectionError:
            raise RuntimeError(f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?")
        except requests.exceptions.Timeout:
            raise RuntimeError(f"Ollama request to {self.base_url} timed out.")
        except Exception as e:
            raise e


class MultiProviderManager:
    """
    Orchestrates Groq, OpenRouter, and Ollama.
    Handles automatic fallback, manual switching, and remembers the last working provider.
    """

    def __init__(self):
        reload_env_vars()
        self.providers: Dict[str, BaseProvider] = {
            PROVIDER_GROQ: GroqProvider(),
            PROVIDER_OPENROUTER: OpenRouterProvider(),
            PROVIDER_OLLAMA: OllamaProvider(),
        }
        self.priority_order: List[str] = list(PROVIDERS_ORDER)
        self.current_provider_name: str = PROVIDER_GROQ

        # If Groq is not configured, pick the first configured provider
        if not self.providers[PROVIDER_GROQ].is_configured():
            for name in self.priority_order:
                if self.providers[name].is_configured():
                    self.current_provider_name = name
                    break

    def set_provider(self, name: str) -> Tuple[bool, str]:
        """Manually switches the active provider."""
        name_clean = name.strip().lower()
        if name_clean in self.providers:
            self.current_provider_name = name_clean
            display = self.providers[name_clean].display_name
            return True, f"Switched to {display}."
        valid = ", ".join(self.providers.keys())
        return False, f"Unknown provider '{name}'. Available: {valid}"

    def get_current_provider(self) -> BaseProvider:
        return self.providers[self.current_provider_name]

    def show_providers(self) -> str:
        lines = ["Available Providers:"]
        for idx, key in enumerate(self.priority_order, 1):
            p = self.providers[key]
            lines.append(f"{idx}. {p.get_status_line()}")
        current = self.providers[self.current_provider_name].display_name
        lines.append(f"\nCurrent Active Provider: {current}")
        lines.append(f"Priority Order: {' -> '.join(PROVIDER_DISPLAY_NAMES[k] for k in self.priority_order)}")
        return "\n".join(lines)

    def generate(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Generates a response using the current provider, with automatic fallback
        through the remaining providers in priority order.

        Returns (response_text, winning_provider_display_name).
        """
        # Build prompt messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in conversation_history:
            role = "assistant" if m.get("role") in ("bot", "assistant") else "user"
            messages.append({"role": role, "content": m.get("content", "")})
        messages.append({"role": "user", "content": user_message})

        # Sequence starts with current_provider, then remaining in priority order
        attempt_sequence = [self.current_provider_name]
        for key in self.priority_order:
            if key not in attempt_sequence:
                attempt_sequence.append(key)

        fallback_occurred = False

        for i, provider_key in enumerate(attempt_sequence):
            provider = self.providers[provider_key]
            is_last = (i == len(attempt_sequence) - 1)
            next_provider = self.providers[attempt_sequence[i + 1]] if not is_last else None

            # If not configured (e.g. missing API key)
            if not provider.is_configured():
                if not fallback_occurred:
                    print(f"Trying provider: {provider.display_name}...")
                    fallback_occurred = True
                if next_provider:
                    print(f"{provider.display_name} unavailable. Switching to {next_provider.display_name}...")
                else:
                    print(f"{provider.display_name} unavailable.")
                continue

            try:
                # If we are failing over, show which provider is being tried
                if fallback_occurred and i > 0:
                    pass

                content = provider.generate(messages)
                if content:
                    if fallback_occurred:
                        print("Response received.")
                    # Remember last working provider
                    self.current_provider_name = provider.name
                    return content, provider.display_name

                raise RuntimeError("Empty response received.")

            except Exception:
                if not fallback_occurred:
                    print(f"Trying provider: {provider.display_name}...")
                    fallback_occurred = True

                if next_provider:
                    print(f"{provider.display_name} unavailable. Switching to {next_provider.display_name}...")
                else:
                    print(f"{provider.display_name} unavailable.")

        return None, None
