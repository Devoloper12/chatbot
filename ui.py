"""
=============================================================================
Terminal UI Module: Rich Formatting, Banners, Tables & Markdown Rendering
=============================================================================
Provides cross-platform visual components including color themes, status
spinners, tables for commands and sessions, and markdown code syntax highlighting.
=============================================================================
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from config import APP_NAME, APP_SUBTITLE, APP_VERSION, SAVED_CODE_DIR

# Global Rich console instance
console = Console()


def clear_screen() -> None:
    """Clears the terminal screen cross-platform."""
    os.system("cls" if os.name == "nt" else "clear")


def print_startup_banner(model_name: str, session_id: int, session_title: str) -> None:
    """Renders a visual startup banner in a panel."""
    header_text = Text()
    header_text.append(f"🤖 {APP_NAME} v{APP_VERSION}\n", style="bold cyan")
    header_text.append(f"🎓 {APP_SUBTITLE}\n\n", style="italic bright_black")
    header_text.append("Active Model   : ", style="bold yellow")
    header_text.append(f"{model_name}\n", style="white")
    header_text.append("Current Session: ", style="bold green")
    header_text.append(f"#{session_id} - '{session_title}'\n", style="white")
    header_text.append("Commands       : ", style="bold magenta")
    header_text.append("/help, /new, /list, /history, /savecode, /search, /exit", style="bright_white")

    panel = Panel(
        header_text,
        title="[bold green]● ONLINE[/bold green]",
        subtitle="[dim]Type /help for full command list | Press Ctrl+C to exit[/dim]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)
    console.print()


def print_user_prompt(session_id: int) -> str:
    """Prompts the user for input and returns clean stripped string."""
    try:
        user_input = console.input(f"[bold green]You[/bold green] [dim](#{session_id})[/dim][bold green]:[/bold green] ")
        return user_input.strip()
    except (KeyboardInterrupt, EOFError):
        return "/exit"


def render_bot_response(response_text: str, duration_seconds: float = 0.0) -> None:
    """
    Renders the bot's markdown response cleanly with syntax highlighting
    and displays the elapsed generation time.
    """
    console.print()
    console.print("[bold magenta]Bot:[/bold magenta]")

    # Render Markdown response (headers, bold, lists, and syntax-highlighted code blocks)
    markdown_content = Markdown(response_text)
    console.print(markdown_content)

    # Display timing indicator
    if duration_seconds > 0:
        console.print(f"[dim bright_black]⚡ Generated in {duration_seconds:.2f}s[/dim bright_black]")
    console.print()


def print_system_info(message: str) -> None:
    """Prints a standard system notification."""
    console.print(f"[bold yellow][System][/bold yellow] {message}")


def print_error(title: str, detail: str = "") -> None:
    """Prints a standardized error box or alert."""
    err_text = Text()
    err_text.append(f"{title}\n", style="bold red")
    if detail:
        err_text.append(f"{detail}", style="white")

    panel = Panel(
        err_text,
        title="[bold red]Error[/bold red]",
        border_style="red",
        padding=(0, 2),
    )
    console.print(panel)


def print_help_table() -> None:
    """Renders the comprehensive /help command table."""
    table = Table(
        title="🤖 Gemini Chatbot Command Reference",
        header_style="bold cyan",
        border_style="blue",
        show_lines=True,
    )

    table.add_column("Command", style="bold yellow", width=22)
    table.add_column("Description", style="white")
    table.add_column("Example Usage", style="italic green", width=30)

    table.add_row("/help", "Display this command guide and tips", "/help")
    table.add_row("/new [title]", "Create and switch to a new conversation session", "/new Python Lab 3")
    table.add_row("/list", "List all saved conversation sessions", "/list")
    table.add_row("/switch <id>", "Switch to an existing conversation session", "/switch 2")
    table.add_row("/history [limit]", "View conversation messages for this session", "/history 10")
    table.add_row("/clear", "Clear chat memory for the active session", "/clear")
    table.add_row("/delete <id>", "Delete a chat session and its history", "/delete 3")
    table.add_row("/savecode [name]", "Extract & save code from last bot reply to disk", "/savecode quicksort.c")
    table.add_row("/search <query>", "Search message history across all sessions", "/search binary search")
    table.add_row("/export [md|txt]", "Export conversation to a Markdown or TXT file", "/export md")
    table.add_row("/save", "Quick-save active conversation to exports/", "/save")
    table.add_row("/about", "Show chatbot status, model, and database statistics", "/about")
    table.add_row("/exit, /quit", "Gracefully terminate the chatbot session", "/exit")

    console.print()
    console.print(table)
    console.print()

    # Academic & CS Tips Box
    tips_text = Text()
    tips_text.append("💡 Academic & Programming Tips:\n", style="bold green")
    tips_text.append("• Ask for exam algorithms: ", style="bold white")
    tips_text.append("'Algorithm for Dijkstra with complexity and sample I/O'\n", style="dim")
    tips_text.append("• Ask for college lab programs: ", style="bold white")
    tips_text.append("'Write a C program for Singly Linked List with menu'\n", style="dim")
    tips_text.append("• Ask for code debugging: ", style="bold white")
    tips_text.append("'Explain why this Python recursion causes RecursionError'\n", style="dim")
    tips_text.append("• Ask for Linux explanations: ", style="bold white")
    tips_text.append("'Explain grep, sed, and awk with Ubuntu examples'\n", style="dim")

    console.print(Panel(tips_text, border_style="green", padding=(0, 2)))
    console.print()


def print_sessions_table(sessions: List[Dict[str, Any]], current_session_id: int) -> None:
    """Renders a table of all available sessions."""
    if not sessions:
        print_system_info("No saved sessions found. Start chatting to create one!")
        return

    table = Table(
        title="📁 Saved Chat Sessions",
        header_style="bold cyan",
        border_style="bright_blue",
        show_lines=True,
    )

    table.add_column("ID", justify="center", style="bold yellow", width=6)
    table.add_column("Title", style="white")
    table.add_column("Messages", justify="center", style="green", width=10)
    table.add_column("Last Active", style="dim", width=22)
    table.add_column("Status", justify="center", width=12)

    for s in sessions:
        is_current = s["id"] == current_session_id
        status_text = "[bold green]● Active[/bold green]" if is_current else "[dim]Available[/dim]"
        title_text = f"[bold]{s['title']}[/bold]" if is_current else s["title"]
        table.add_row(
            str(s["id"]),
            title_text,
            str(s["message_count"]),
            str(s["updated_at"]),
            status_text,
        )

    console.print()
    console.print(table)
    console.print("[dim]Use [bold cyan]/switch <id>[/bold cyan] to change session, or [bold cyan]/new [title][/bold cyan] to create a new one.[/dim]\n")


def print_history_table(messages: List[Dict[str, Any]], session_title: str) -> None:
    """Renders the message history for a session."""
    if not messages:
        print_system_info(f"No messages yet in session: '{session_title}'.")
        return

    table = Table(
        title=f"📜 Message History: {session_title}",
        header_style="bold cyan",
        border_style="magenta",
        show_lines=True,
    )

    table.add_column("#", justify="center", width=4)
    table.add_column("Sender", justify="center", width=10)
    table.add_column("Message Preview", style="white")
    table.add_column("Time", style="dim", width=20)

    for idx, msg in enumerate(messages, 1):
        sender_label = "[bold green]You[/bold green]" if msg["role"] == "user" else "[bold magenta]Bot[/bold magenta]"
        # Truncate preview for table readability
        preview = msg["content"].replace("\n", " ")
        if len(preview) > 90:
            preview = preview[:87] + "..."
        table.add_row(str(idx), sender_label, preview, str(msg["created_at"]))

    console.print()
    console.print(table)
    console.print()


def print_search_results(results: List[Dict[str, Any]], query: str) -> None:
    """Displays search results across previous chat sessions."""
    if not results:
        print_system_info(f"No messages found matching '{query}'.")
        return

    table = Table(
        title=f"🔍 Search Results for: '{query}'",
        header_style="bold cyan",
        border_style="yellow",
        show_lines=True,
    )

    table.add_column("Session", justify="center", style="bold yellow", width=10)
    table.add_column("Sender", justify="center", width=8)
    table.add_column("Matching Snippet", style="white")
    table.add_column("Date", style="dim", width=20)

    for row in results:
        sender_label = "[bold green]You[/bold green]" if row["role"] == "user" else "[bold magenta]Bot[/bold magenta]"
        content = row["content"].replace("\n", " ")
        # Highlight match in snippet
        snippet_len = 100
        lower_content = content.lower()
        lower_q = query.lower()
        find_idx = lower_content.find(lower_q)
        if find_idx != -1:
            start = max(0, find_idx - 30)
            end = min(len(content), find_idx + len(query) + 50)
            snippet = content[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(content):
                snippet = snippet + "..."
        else:
            snippet = content[:snippet_len] + ("..." if len(content) > snippet_len else "")

        table.add_row(
            f"#{row['session_id']}",
            sender_label,
            snippet,
            str(row["created_at"]),
        )

    console.print()
    console.print(table)
    console.print()


def print_about_panel(stats: Dict[str, Any], model_name: str) -> None:
    """Renders the /about dialog."""
    about_text = Text()
    about_text.append(f"🤖 {APP_NAME}\n", style="bold cyan")
    about_text.append(f"Version        : {APP_VERSION}\n", style="white")
    about_text.append(f"AI Model       : {model_name}\n", style="white")
    about_text.append(f"Persistence    : SQLite (Local & Private)\n", style="white")
    about_text.append(f"License        : MIT Open Source\n\n", style="white")

    about_text.append("📊 Usage Statistics:\n", style="bold yellow")
    about_text.append(f"• Total Saved Sessions : {stats['total_sessions']}\n", style="white")
    about_text.append(f"• Total Messages Stored: {stats['total_messages']}\n", style="white")
    about_text.append(f"• User Inquiries       : {stats['user_messages']}\n", style="white")
    about_text.append(f"• Bot Responses        : {stats['bot_messages']}\n", style="white")

    panel = Panel(
        about_text,
        title="[bold green]About Gemini Terminal Chatbot[/bold green]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


# ---------------------------------------------------------------------------
# Code Extraction & Auto-Saving Utility
# ---------------------------------------------------------------------------
EXTENSIONS_MAP = {
    "c": ".c",
    "cpp": ".cpp",
    "c++": ".cpp",
    "python": ".py",
    "py": ".py",
    "bash": ".sh",
    "sh": ".sh",
    "shell": ".sh",
    "sql": ".sql",
    "html": ".html",
    "css": ".css",
    "javascript": ".js",
    "js": ".js",
    "java": ".java",
}


def extract_code_blocks(text: str) -> List[Tuple[str, str]]:
    """
    Finds and extracts code blocks with their language from markdown text.
    Returns list of tuples: (language, code_content)
    """
    pattern = r"```([a-zA-Z0-9_\-\+\#]*)\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    blocks = []
    for lang, code in matches:
        lang_clean = lang.strip().lower() or "text"
        blocks.append((lang_clean, code.rstrip()))
    return blocks


def save_code_to_file(
    code_blocks: List[Tuple[str, str]],
    custom_filename: Optional[str] = None
) -> List[Path]:
    """
    Saves extracted code blocks to files in the saved_code directory.
    Returns list of created Paths.
    """
    saved_paths = []
    if not code_blocks:
        return saved_paths

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for i, (lang, code) in enumerate(code_blocks, 1):
        ext = EXTENSIONS_MAP.get(lang, ".txt")
        if custom_filename:
            if i == 1:
                filename = custom_filename
            else:
                base, orig_ext = os.path.splitext(custom_filename)
                filename = f"{base}_{i}{orig_ext or ext}"
        else:
            filename = f"program_{timestamp}_{i}{ext}"

        file_path = SAVED_CODE_DIR / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code + "\n")
        saved_paths.append(file_path)

    return saved_paths
