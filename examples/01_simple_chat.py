"""
Example 1: Simple chat with local model.

This is the most basic example - a 1:1 chat with an LLM.
Demonstrates how to use the LLM factory for transparent local/remote switching.

Usage:
    python examples/01_simple_chat.py
    python examples/01_simple_chat.py --provider openai --model gpt-4o-mini
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from loguru import logger

from multi_agent.shared import create_llm, settings
from multi_agent.shared.config import LLMProvider
from multi_agent.shared.memory import AgentMemory


def main():
    parser = argparse.ArgumentParser(description="Simple chat with LLM")
    parser.add_argument("--provider", choices=["ollama", "openai"], default="ollama")
    parser.add_argument("--model", default=None, help="Model to use")
    args = parser.parse_args()

    # Configure provider
    provider = LLMProvider(args.provider)
    model = args.model or (
        "mistral" if provider == LLMProvider.OLLAMA else "gpt-4o-mini"
    )

    print(f"\n🤖 Chat with {provider.value}:{model}")
    print("=" * 50)
    print("Type 'exit' to quit, 'clear' to clear memory\n")

    # Create LLM and memory
    try:
        llm = create_llm(provider=provider, model=model)
    except Exception as e:
        print(f"❌ Error creating LLM: {e}")
        print("\nMake sure Ollama is running: ollama serve")
        return

    memory = AgentMemory(agent_name="chat_agent")
    memory.set_system_prompt(
        "You are a friendly and knowledgeable AI assistant. "
        "Respond concisely but completely."
    )

    # Chat loop
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("\n👋 Goodbye!")
            break
        if user_input.lower() == "clear":
            memory.clear()
            print("🗑️ Memory cleared!")
            continue

        # Add user message to memory
        memory.add_user(user_input)

        # Prepare messages for LLM using proper LangChain message types
        messages = []
        if memory._system_prompt:
            messages.append(SystemMessage(content=memory._system_prompt))

        for msg in memory._messages:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))

        # Generate response
        print("\n🤖 Assistant: ", end="", flush=True)
        try:
            # Streaming response
            full_response = ""
            for chunk in llm.stream(messages):
                content = chunk.content if hasattr(chunk, "content") else str(chunk)
                print(content, end="", flush=True)
                full_response += content
            print()  # Final newline

            # Save response to memory
            memory.add_assistant(full_response)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.exception("Error during generation")


if __name__ == "__main__":
    main()
