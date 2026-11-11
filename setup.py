#!/usr/bin/env python3
"""
Setup and packaging configuration for Gemini Terminal Chatbot.
Enables running 'chatbot' directly from the command line after installation.
"""

from setuptools import setup

setup(
    name="gemini-terminal-chatbot",
    version="2.0.0",
    description="Cross-platform terminal AI chatbot and CS tutor powered by Google Gemini",
    author="Devoloper12",
    py_modules=["chatbot", "config", "database", "ui"],
    install_requires=[
        "google-genai>=1.0.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
        "colorama>=0.4.6",
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
        "Environment :: Console",
    ],
)
