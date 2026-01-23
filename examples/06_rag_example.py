"""
Example 6: RAG (Retrieval-Augmented Generation)

Demonstrates how to use RAG to give agents access to a knowledge base.
The agent retrieves relevant context before generating answers.

Usage:
    python examples/06_rag_example.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from multi_agent.shared.rag import RAGStore, RAGAgent


def main():
    print("\n" + "=" * 60)
    print("🔍 RAG (Retrieval-Augmented Generation) Demo")
    print("=" * 60)

    # Create RAG store
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
    ]

    rag.add_documents(documents)
    print(f"   Added {len(documents)} documents to knowledge base")
    print(f"   Total documents: {rag.count}")

    # Test semantic search
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
            # Show first 80 chars of each result
            snippet = r["document"][:80].replace("\n", " ") + "..."
            print(f"      {i}. {snippet}")

    # Create RAG Agent
    print("\n\n🤖 Creating RAG Agent...")
    try:
        agent = RAGAgent(rag_store=rag)

        # Ask questions
        questions = [
            "What frameworks can I use for multi-agent AI systems?",
            "How can I run LLMs without paying for API calls?",
        ]

        for question in questions:
            print(f"\n❓ Question: {question}")
            print("-" * 50)

            try:
                answer = agent.query(question, n_context=3)
                print(f"💡 Answer: {answer}")
            except Exception as e:
                print(f"⚠️ Could not generate answer: {e}")
                print("   (Make sure Ollama is running)")

    except Exception as e:
        print(f"⚠️ Could not create RAG agent: {e}")
        print("   The semantic search still works without an LLM!")

    # Cleanup
    rag.clear()

    print("\n" + "=" * 60)
    print("✅ RAG Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
