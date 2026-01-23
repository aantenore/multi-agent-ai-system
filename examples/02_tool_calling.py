"""
Example 2: Agent with Tool Calling.

Demonstrates how to create an agent that can use tools to
interact with the environment (calculations, files, etc.).

Usage:
    python examples/02_tool_calling.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from multi_agent.shared import create_llm
from multi_agent.tools import (
    calculate,
    get_current_time,
    list_directory,
    web_search_mock,
)


def main():
    print("\n🛠️ Agent with Tool Calling")
    print("=" * 50)

    # Create LLM with tools
    llm = create_llm()
    tools = [calculate, get_current_time, list_directory, web_search_mock]
    llm_with_tools = llm.bind_tools(tools)

    # System prompt instructing agent on tool usage
    system_prompt = """You are an AI assistant with access to various tools.
Use tools when necessary to answer questions.

Available tools:
- calculate: for mathematical calculations
- get_current_time: to get current date and time
- list_directory: to see contents of folders
- web_search_mock: to search for information

When using a tool, explain what you are doing."""

    # Example queries that require tools
    queries = [
        "What is 15 * 7 + 23?",
        "What time is it now?",
        "Search for information about Python",
        "List files in the current directory",
    ]

    for query in queries:
        print(f"\n👤 Query: {query}")
        print("-" * 40)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query),
        ]

        # First call - LLM decides whether to use a tool
        response = llm_with_tools.invoke(messages)

        # Check if there are tool calls
        if hasattr(response, "tool_calls") and response.tool_calls:
            print("🔧 Tool calls requested:")
            for tc in response.tool_calls:
                print(f"   - {tc['name']}: {tc['args']}")

                # Execute the tool
                tool_map = {t.name: t for t in tools}
                if tc["name"] in tool_map:
                    result = tool_map[tc["name"]].invoke(tc["args"])
                    print(f"   📤 Result: {result}")
        else:
            print(f"🤖 Direct response: {response.content[:200]}")

    print("\n" + "=" * 50)
    print("✅ Demo completed!")


if __name__ == "__main__":
    main()
