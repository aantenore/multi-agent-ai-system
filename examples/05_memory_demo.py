"""
Example 5: Interactive Agent with Memory and Basic RAG.

Demonstrates:
- Persistent conversational memory
- Shared memory between agents
- Simple RAG with ChromaDB
- Interactive chat with memory context

Usage:
    python examples/05_memory_demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from loguru import logger

from multi_agent.shared import create_llm
from multi_agent.shared.memory import AgentMemory, SharedMemory, create_agent_memory


def demo_agent_memory():
    """Demo private agent memory."""
    print("\n📝 Demo: Agent Memory (Conversational)")
    print("-" * 50)

    # Create memory with system prompt
    memory = create_agent_memory(
        agent_name="assistant", system_prompt="You are an expert Python assistant."
    )

    # Simulate conversation
    memory.add_user("How do I create a list in Python?")
    memory.add_assistant(
        "To create a list in Python, use square brackets: `my_list = [1, 2, 3]`"
    )
    memory.add_user("How do I add an element?")
    memory.add_assistant("Use the append method: `my_list.append(4)`")

    print(f"Messages in memory: {len(memory)}")
    print("\nLast 2 messages:")
    for msg in memory.get_last_n(2):
        print(f"  [{msg.role}]: {msg.content[:50]}...")

    # LangChain format
    print("\nLangChain format:")
    for role, content in memory.get_messages()[:3]:
        print(f"  ({role}, '{content[:40]}...')")


def demo_shared_memory():
    """Demo shared memory between agents."""
    print("\n\n🔗 Demo: Shared Memory (Inter-Agent)")
    print("-" * 50)

    # Singleton - same instance everywhere
    shared = SharedMemory()

    # Simulate Researcher agent saving results
    print("Researcher saves research results...")
    shared.set(
        "research_findings",
        {
            "topic": "Design Patterns",
            "patterns": ["Singleton", "Factory", "Observer"],
            "source": "Gang of Four",
        },
    )

    # Simulate Coder agent reading and logging
    print("Coder reads research and logs activity...")
    findings = shared.get("research_findings")
    print(f"  Coder read: {findings['patterns']}")

    shared.append("task_log", "Researcher: analysis completed")
    shared.append("task_log", "Coder: implemented Singleton")
    shared.append("task_log", "Reviewer: code approved")

    # Display log
    print("\nShared task log:")
    for entry in shared.get("task_log", []):
        print(f"  • {entry}")

    # Cleanup
    shared.clear()


def demo_simple_rag():
    """Demo basic RAG with in-memory embeddings."""
    print("\n\n🔍 Demo: Simple RAG (Knowledge Base)")
    print("-" * 50)

    try:
        import chromadb

        # Create in-memory collection
        client = chromadb.Client()
        collection = client.create_collection("demo_kb")

        # Add documents
        documents = [
            "LangGraph is a framework for creating stateful agent graphs.",
            "AutoGen is developed by Microsoft for conversational agents.",
            "Ollama allows running LLMs locally on your own computer.",
            "Python is a high-level programming language.",
            "Google Gemini is a powerful multimodal AI model family.",
        ]

        collection.add(
            documents=documents,
            ids=[f"doc_{i}" for i in range(len(documents))],
        )

        print(f"Knowledge base created with {len(documents)} documents")

        # Example query
        query = "How can I run AI models on my PC?"
        results = collection.query(query_texts=[query], n_results=2)

        print(f"\nQuery: '{query}'")
        print("Most relevant results:")
        for i, doc in enumerate(results["documents"][0]):
            print(f"  {i+1}. {doc}")

    except ImportError:
        print("ChromaDB not installed. Install with: pip install chromadb")
        print("This example is optional to demonstrate RAG.")


def interactive_memory_chat():
    """Interactive chat with memory demonstration."""
    print("\n\n💬 Interactive Chat with Memory")
    print("-" * 50)
    print("Chat with an AI that remembers context!")
    print(
        "Type 'exit' or 'quit' to end, 'clear' to clear memory, 'history' to see memory\n"
    )

    try:
        llm = create_llm()
    except Exception as e:
        print(f"❌ Error creating LLM: {e}")
        print("Skipping interactive demo.")
        return

    memory = AgentMemory(agent_name="memory_demo")
    memory.set_system_prompt(
        "You are a helpful assistant demonstrating memory capabilities. "
        "Reference previous parts of our conversation when relevant."
    )

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
        if user_input.lower() == "clear":
            memory.clear()
            print("🗑️ Memory cleared!")
            continue
        if user_input.lower() == "history":
            print(f"\n📜 Memory contains {len(memory)} messages:")
            for msg in memory._messages:
                preview = (
                    msg.content[:60] + "..." if len(msg.content) > 60 else msg.content
                )
                print(f"   [{msg.role}]: {preview}")
            continue

        # Add user message
        memory.add_user(user_input)

        # Build messages
        messages = []
        if memory._system_prompt:
            messages.append(SystemMessage(content=memory._system_prompt))
        for msg in memory._messages:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))

        # Generate and stream response
        print("\n🤖 Assistant: ", end="", flush=True)
        try:
            full_response = ""
            for chunk in llm.stream(messages):
                # Handle different response formats (Gemini returns list of dicts)
                content = chunk.content if hasattr(chunk, "content") else str(chunk)
                if isinstance(content, list):
                    content = "".join(
                        item.get("text", "")
                        for item in content
                        if isinstance(item, dict) and item.get("type") == "text"
                    )
                print(content, end="", flush=True)
                full_response += content
            print()
            memory.add_assistant(full_response)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.exception("Error during generation")


def main():
    print("\n" + "=" * 60)
    print("🧠 Multi-Agent Memory System Demo")
    print("=" * 60)

    demo_agent_memory()
    demo_shared_memory()
    demo_simple_rag()
    interactive_memory_chat()

    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
