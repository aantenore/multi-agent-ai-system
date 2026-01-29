"""
Example 2: Interactive Agent with Tool Calling.

Demonstrates how to create an interactive agent that can use tools to
interact with the environment (calculations, files, time, etc.).

Usage:
    python examples/02_tool_calling.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from loguru import logger

from multi_agent.shared import create_llm
from multi_agent.tools import (
    calculate,
    get_current_time,
    list_directory,
    read_file,
    web_search_mock,
    ALL_TOOLS,
)


def main():
    print("\n🛠️ Interactive Agent with Tool Calling")
    print("=" * 50)
    print("Type 'exit' or 'quit' to end the chat")
    print("Ask questions that might require tools (math, time, files, search)\n")

    # Create LLM with tools bound
    llm = create_llm()
    tools = ALL_TOOLS
    llm_with_tools = llm.bind_tools(tools)

    # Create tool lookup map
    tool_map = {t.name: t for t in tools}

    # System prompt instructing agent on tool usage
    system_prompt = """You are an AI assistant with access to various tools.
Use tools when necessary to answer questions accurately.

Available tools:
- calculate: for mathematical calculations (e.g., "2 + 2 * 3")
- get_current_time: to get current date and time
- list_directory: to see contents of folders
- read_file: to read text files
- web_search_mock: to search for information

When you need to use a tool, call it. After receiving the tool result, 
provide a helpful response to the user based on that result."""

    # Conversation history
    messages = [SystemMessage(content=system_prompt)]

    # Interactive chat loop
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("\n👋 Goodbye!")
            break

        # Add user message to history
        messages.append(HumanMessage(content=user_input))

        # Call LLM - it may request tool calls
        try:
            response = llm_with_tools.invoke(messages)
            messages.append(response)

            # Process tool calls if any
            while hasattr(response, "tool_calls") and response.tool_calls:
                print("\n🔧 Using tools...")
                for tc in response.tool_calls:
                    tool_name = tc["name"]
                    tool_args = tc["args"]
                    print(f"   → {tool_name}: {tool_args}")

                    # Execute the tool
                    if tool_name in tool_map:
                        result = tool_map[tool_name].invoke(tool_args)
                        print(
                            f"   ✓ Result: {result[:100]}..."
                            if len(str(result)) > 100
                            else f"   ✓ Result: {result}"
                        )

                        # Add tool result to messages
                        messages.append(
                            ToolMessage(content=str(result), tool_call_id=tc["id"])
                        )
                    else:
                        messages.append(
                            ToolMessage(
                                content=f"Tool '{tool_name}' not found",
                                tool_call_id=tc["id"],
                            )
                        )

                # Get next response after tool execution
                response = llm_with_tools.invoke(messages)
                messages.append(response)

            # Print final response
            print(f"\n🤖 Assistant: {response.content}")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.exception("Error during tool calling")
            # Remove the last user message to avoid issues
            messages.pop()

    print("\n" + "=" * 50)
    print("✅ Chat ended!")


if __name__ == "__main__":
    main()
