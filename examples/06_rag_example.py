"""
Example 6: Interactive RAG (Retrieval-Augmented Generation)

Demonstrates how to use RAG to give agents access to a knowledge base.
The agent retrieves relevant context before generating answers.

Usage:
    python examples/06_rag_example.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loguru import logger
from multi_agent.shared.rag import RAGStore, RAGAgent


def create_knowledge_base():
    """Create and populate the knowledge base."""
    print("\n📚 Creating knowledge base...")
    rag = RAGStore(collection_name="demo_knowledge")

    # Add some documents
    documents = [
        """LangGraph is a library for building stateful, multi-actor applications 
        with LLMs. It extends LangChain with support for cycles and state management.
        LangGraph is great for creating agent workflows with complex logic.""",
        """AutoGen is a framework from Microsoft for building multi-agent 
        conversational AI systems. Agents in AutoGen can chat with each other
        to solve complex tasks collaboratively.""",
        """MCP (Model Context Protocol) is an open protocol that enables 
        AI assistants to securely connect with data sources and tools.
        It provides a standardized way to expose tools to LLMs.""",
        """A2A (Agent-to-Agent) Protocol enables communication between 
        distributed AI agents. Agents can discover each other's capabilities
        and delegate tasks across a network.""",
        """RAG (Retrieval-Augmented Generation) enhances LLM responses by 
        retrieving relevant information from a knowledge base before generating.
        This reduces hallucinations and provides up-to-date information.""",
        """Ollama is a tool for running large language models locally.
        It supports models like Mistral, Llama, and CodeLlama.
        Running models locally provides privacy and no API costs.""",
        """Google Gemini is a multimodal AI model developed by Google DeepMind.
        It can understand text, images, audio, and video. The Gemini family
        includes models like gemini-3-pro-preview for advanced reasoning tasks.""",
        """Skills in multi-agent systems are reusable capabilities that agents
        can invoke to perform specific tasks. Examples include calculations,
        file operations, web searches, and code execution.""",
    ]

    rag.add_documents(documents)
    print(f"   Added {len(documents)} documents to knowledge base")
    print(f"   Total documents: {rag.count}")
    return rag


def demo_semantic_search(rag: RAGStore):
    """Test semantic search functionality."""
    print("\n🔎 Testing semantic search...")
    queries = [
        "How can agents communicate with each other?",
        "What is the best way to run AI models privately?",
        "How do I connect external tools to an AI assistant?",
    ]

    for query in queries:
        print(f"\n   Query: '{query}'")
        results = rag.search(query, n_results=2)
        print("   Top results:")
        for i, r in enumerate(results, 1):
            snippet = r["document"][:80].replace("\n", " ") + "..."
            print(f"      {i}. {snippet}")


def interactive_rag_chat(rag: RAGStore):
    """Interactive chat using RAG for knowledge retrieval."""
    print("\n\n💬 Interactive RAG Chat")
    print("-" * 50)
    print("Ask questions about the knowledge base!")
    print("Type 'exit' or 'quit' to end, 'search <query>' for raw search\n")

    try:
        agent = RAGAgent(rag_store=rag)
    except Exception as e:
        print(f"⚠️ Could not create RAG agent: {e}")
        print("   Make sure your LLM provider is configured correctly.")
        return

    while True:
        try:
            user_input = input("\n❓ You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("\n👋 Goodbye!")
            break

        # Raw search mode
        if user_input.lower().startswith("search "):
            query = user_input[7:]
            print(f"\n🔎 Raw search for: '{query}'")
            results = rag.search(query, n_results=3)
            for i, r in enumerate(results, 1):
                print(f"\n   Result {i}:")
                print(f"   {r['document'][:200]}...")
            continue

        # RAG-enhanced answer
        print("\n   🔍 Retrieving relevant context...")
        try:
            # We peek at internals to show what's happening
            results = rag.search(user_input, n_results=3)
            print(f"   📄 Found {len(results)} relevant documents.")

            print("   🤖 Querying LLM with context...", end="", flush=True)
            answer = agent.query(user_input, n_context=3)
            print("\n\n🤖 Assistant:")
            print(answer)
        except Exception as e:
            print(f"\n⚠️ Error: {e}")
            logger.exception("RAG query error")


def main():
    print("\n" + "=" * 60)
    print("🔍 Interactive RAG (Retrieval-Augmented Generation) Demo")
    print("=" * 60)

    rag = create_knowledge_base()
    demo_semantic_search(rag)
    interactive_rag_chat(rag)

    # Cleanup
    rag.clear()

    print("\n" + "=" * 60)
    print("✅ RAG Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
