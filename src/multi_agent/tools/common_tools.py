"""
Common tools for agents.

These tools demonstrate how to create capabilities for agents.
Each tool is a function decorated with @tool that can be
called by the LLM.
"""

import os
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool


@tool
def calculate(expression: str) -> str:
    """
    Calculate a mathematical expression.

    Args:
        expression: Mathematical expression to calculate (e.g., "2 + 2 * 3")

    Returns:
        Calculation result as string
    """
    try:
        # Safe eval only for numeric expressions
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "Error: invalid expression. Use only numbers and operators +-*/."
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"


@tool
def get_current_time(timezone: str = "local") -> str:
    """
    Return current date and time.

    Args:
        timezone: Timezone (currently only supports 'local')

    Returns:
        Formatted date and time
    """
    now = datetime.now()
    return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


@tool
def read_file(file_path: str) -> str:
    """
    Read the content of a text file.

    Args:
        file_path: Path to the file to read

    Returns:
        File content or error message
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: file '{file_path}' not found"
        if not path.is_file():
            return f"Error: '{file_path}' is not a file"

        content = path.read_text(encoding="utf-8")
        # Limit output to avoid overly long responses
        if len(content) > 5000:
            content = content[:5000] + "\n... [truncated]"
        return content
    except Exception as e:
        return f"Read error: {e}"


@tool
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a text file.

    Args:
        file_path: Path to the file to write
        content: Content to write

    Returns:
        Confirmation or error message
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"File '{file_path}' written successfully ({len(content)} characters)"
    except Exception as e:
        return f"Write error: {e}"


@tool
def list_directory(directory_path: str) -> str:
    """
    List the contents of a directory.

    Args:
        directory_path: Path to the directory

    Returns:
        List of files and folders
    """
    try:
        path = Path(directory_path)
        if not path.exists():
            return f"Error: directory '{directory_path}' not found"
        if not path.is_dir():
            return f"Error: '{directory_path}' is not a directory"

        items = []
        for item in sorted(path.iterdir()):
            prefix = "📁" if item.is_dir() else "📄"
            items.append(f"{prefix} {item.name}")

        if not items:
            return "Empty directory"

        return "\n".join(items[:50])  # Limit to 50 items
    except Exception as e:
        return f"Error: {e}"


@tool
def web_search_mock(query: str) -> str:
    """
    Simulate a web search (mock for demo).

    In production, replace with real API like Google, Bing, or Tavily.

    Args:
        query: Search query

    Returns:
        Simulated results
    """
    # Mock results for demo
    mock_results = {
        "python": "Python is a high-level, interpreted, general-purpose programming language.",
        "langgraph": "LangGraph is a framework for creating stateful agent graphs, developed by LangChain.",
        "autogen": "AutoGen is a Microsoft framework for creating multi-party conversational agents.",
        "ollama": "Ollama allows running LLMs locally like Llama, Mistral, and others.",
    }

    query_lower = query.lower()
    for key, result in mock_results.items():
        if key in query_lower:
            return f"Results for '{query}':\n\n{result}"

    return f"Results for '{query}':\n\nNo results found in mock knowledge base. In production, connect a real search API."


# List of all available tools
ALL_TOOLS = [
    calculate,
    get_current_time,
    read_file,
    write_file,
    list_directory,
    web_search_mock,
]


def get_tools_for_agent(tool_names: list[str] | None = None):
    """
    Return tools filtered by name.

    Args:
        tool_names: List of tool names to include (None = all)

    Returns:
        List of tools
    """
    if tool_names is None:
        return ALL_TOOLS

    name_to_tool = {t.name: t for t in ALL_TOOLS}
    return [name_to_tool[name] for name in tool_names if name in name_to_tool]
