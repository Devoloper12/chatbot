# Contributing to Gemini Terminal AI Chatbot

Thank you for your interest in contributing! We welcome contributions from developers of all skill levels.

---

## 🛠️ How to Contribute

### 1. Report Bugs
- Search existing issues to ensure the bug hasn't been reported already.
- Open an issue with clear reproduction steps, terminal output, and your operating system (Windows, Ubuntu/Debian, macOS).

### 2. Suggest Features
- We love suggestions for new terminal commands, UI improvements, and educational CS features.
- Open a feature request issue describing your idea and the motivation behind it.

### 3. Submit Pull Requests

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/gemini-terminal-chatbot.git
   cd gemini-terminal-chatbot
   ```
3. **Create a branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/my-new-feature
   ```
4. **Set up virtual environment & install dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # or .\venv\Scripts\Activate.ps1 on Windows
   pip install -r requirements.txt
   ```
5. **Make your changes** while adhering to:
   - Python 3.8+ compatibility.
   - Cross-platform support (no OS-specific shell commands).
   - Clean type annotations and descriptive docstrings.
6. **Commit & Push**:
   ```bash
   git commit -m "Add feature: my new feature"
   git push origin feature/my-new-feature
   ```
7. **Open a Pull Request** against the `main` branch.

---

## 📋 Code Style Guidelines

- Follow PEP 8 formatting conventions.
- Keep terminal output cross-platform using `rich`.
- Ensure database interactions in `database.py` use parameterized queries to prevent SQL injection.
- Keep API error handling resilient and non-crashing.

Thank you for contributing to open source!
