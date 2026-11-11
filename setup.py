#!/usr/bin/env python3
"""
Setup and packaging configuration for Terminal AI Chatbot.
"""

from setuptools import setup

setup(
    name="gemini-terminal-chatbot",
    version="2.2.0",
    description="Minimalist terminal AI chatbot with conversation memory",
    author="Devoloper12",
    py_modules=["chatbot", "config", "database"],
    install_requires=[
        "groq>=0.11.0",
        "google-genai>=1.0.0",
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
