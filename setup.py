#!/usr/bin/env python3
"""
Setup and packaging configuration for Multi-Provider Terminal AI Chatbot.
"""

from setuptools import setup

setup(
    name="gemini-terminal-chatbot",
    version="3.0.0",
    description="Multi-provider terminal AI chatbot with automatic fallback (Groq -> OpenRouter -> Ollama)",
    author="Devoloper12",
    py_modules=["chatbot", "config", "database", "providers"],
    install_requires=[
        "groq>=0.11.0",
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "chatbot=chatbot:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
