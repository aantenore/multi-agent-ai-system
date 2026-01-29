"""
Common tools (skills) for agents.

These tools demonstrate how to create capabilities for agents.
Each tool is a function decorated with @tool that can be
called by the LLM to perform specific actions.

Skills include:
- Mathematical calculations
- Date/time operations
- File system operations
- Text manipulation
- Code analysis
- Web search (mock)
"""

import os
import re
import json
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
        "gemini": "Google Gemini is a multimodal AI model family by Google DeepMind, capable of understanding text, images, audio, and video.",
    }

    query_lower = query.lower()
    for key, result in mock_results.items():
        if key in query_lower:
            return f"Results for '{query}':\n\n{result}"

    return f"Results for '{query}':\n\nNo results found in mock knowledge base. In production, connect a real search API."


# ============================================================
# New Skills - Enhanced Agent Capabilities
# ============================================================


@tool
def analyze_code(code: str, language: str = "python") -> str:
    """
    Analyze code for basic metrics and potential issues.

    Args:
        code: Source code to analyze
        language: Programming language (default: python)

    Returns:
        Analysis report
    """
    lines = code.strip().split("\n")
    total_lines = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))

    # Basic pattern detection
    functions = len(re.findall(r"def \w+\(", code))
    classes = len(re.findall(r"class \w+", code))
    imports = len(re.findall(r"^import |^from .+ import", code, re.MULTILINE))

    # Simple issue detection
    issues = []
    if "eval(" in code:
        issues.append("⚠️ Use of eval() detected - potential security risk")
    if "exec(" in code:
        issues.append("⚠️ Use of exec() detected - potential security risk")
    if "password" in code.lower() and "=" in code:
        issues.append("⚠️ Possible hardcoded password detected")

    report = f"""Code Analysis Report ({language}):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Metrics:
   • Total lines: {total_lines}
   • Blank lines: {blank_lines}
   • Comment lines: {comment_lines}
   • Code lines: {total_lines - blank_lines - comment_lines}

🏗️ Structure:
   • Functions: {functions}
   • Classes: {classes}
   • Imports: {imports}
"""

    if issues:
        report += "\n⚠️ Potential Issues:\n"
        for issue in issues:
            report += f"   {issue}\n"
    else:
        report += "\n✅ No obvious issues detected"

    return report


@tool
def format_json(json_string: str) -> str:
    """
    Format and validate a JSON string.

    Args:
        json_string: JSON string to format

    Returns:
        Formatted JSON or error message
    """
    try:
        data = json.loads(json_string)
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        return f"Formatted JSON:\n{formatted}"
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"


@tool
def text_stats(text: str) -> str:
    """
    Calculate statistics about a text.

    Args:
        text: Text to analyze

    Returns:
        Text statistics
    """
    words = text.split()
    sentences = re.split(r"[.!?]+", text)
    sentences = [s for s in sentences if s.strip()]
    paragraphs = text.split("\n\n")
    paragraphs = [p for p in paragraphs if p.strip()]

    char_count = len(text)
    word_count = len(words)
    sentence_count = len(sentences)
    paragraph_count = len(paragraphs)
    avg_word_length = sum(len(w) for w in words) / max(word_count, 1)
    avg_sentence_length = word_count / max(sentence_count, 1)

    return f"""Text Statistics:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Counts:
   • Characters: {char_count}
   • Words: {word_count}
   • Sentences: {sentence_count}
   • Paragraphs: {paragraph_count}

📊 Averages:
   • Avg word length: {avg_word_length:.1f} chars
   • Avg sentence length: {avg_sentence_length:.1f} words
"""


@tool
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert between common units.

    Args:
        value: Numeric value to convert
        from_unit: Source unit (e.g., 'km', 'miles', 'celsius', 'fahrenheit')
        to_unit: Target unit

    Returns:
        Converted value
    """
    conversions = {
        ("km", "miles"): lambda x: x * 0.621371,
        ("miles", "km"): lambda x: x * 1.60934,
        ("celsius", "fahrenheit"): lambda x: (x * 9 / 5) + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5 / 9,
        ("kg", "lbs"): lambda x: x * 2.20462,
        ("lbs", "kg"): lambda x: x * 0.453592,
        ("meters", "feet"): lambda x: x * 3.28084,
        ("feet", "meters"): lambda x: x * 0.3048,
        ("liters", "gallons"): lambda x: x * 0.264172,
        ("gallons", "liters"): lambda x: x * 3.78541,
    }

    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        return f"{value} {from_unit} = {result:.4f} {to_unit}"

    return f"Conversion from '{from_unit}' to '{to_unit}' not supported. Supported: km/miles, celsius/fahrenheit, kg/lbs, meters/feet, liters/gallons"


@tool
def generate_uuid() -> str:
    """
    Generate a random UUID.

    Returns:
        A new UUID v4 string
    """
    import uuid

    return f"Generated UUID: {uuid.uuid4()}"


@tool
def encode_base64(text: str) -> str:
    """
    Encode text to base64.

    Args:
        text: Text to encode

    Returns:
        Base64 encoded string
    """
    import base64

    encoded = base64.b64encode(text.encode()).decode()
    return f"Base64 encoded: {encoded}"


@tool
def decode_base64(encoded_text: str) -> str:
    """
    Decode base64 to text.

    Args:
        encoded_text: Base64 string to decode

    Returns:
        Decoded text
    """
    import base64

    try:
        decoded = base64.b64decode(encoded_text.encode()).decode()
        return f"Decoded text: {decoded}"
    except Exception as e:
        return f"Decode error: {e}"


# List of all available tools/skills
ALL_TOOLS = [
    # Core tools
    calculate,
    get_current_time,
    read_file,
    write_file,
    list_directory,
    web_search_mock,
    # New skills
    analyze_code,
    format_json,
    text_stats,
    convert_units,
    generate_uuid,
    encode_base64,
    decode_base64,
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


def list_available_skills() -> dict:
    """
    Return a dictionary of all available skills with descriptions.

    Returns:
        Dictionary mapping skill names to descriptions
    """
    return {tool.name: tool.description for tool in ALL_TOOLS}
