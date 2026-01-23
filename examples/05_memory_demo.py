"""
Example 5: Agent with Memory and Basic RAG.

Demonstrates:
- Persistent conversational memory
- Shared memory between agents
- Simple RAG with ChromaDB (optional)

Usage:
    python examples/05_memory_demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

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


def main():
    print("\n" + "=" * 60)
    print("🧠 Multi-Agent Memory System Demo")
    print("=" * 60)

    demo_agent_memory()
    demo_shared_memory()
    demo_simple_rag()

    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
