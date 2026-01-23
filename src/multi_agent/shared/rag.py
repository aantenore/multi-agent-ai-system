"""
RAG (Retrieval-Augmented Generation) module.

Provides document storage and retrieval capabilities using ChromaDB
for semantic search. Agents can use this to access relevant knowledge.
"""

from pathlib import Path
from typing import Any

from loguru import logger

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    logger.warning("ChromaDB not installed. RAG features disabled.")


class RAGStore:
    """
    Document store with semantic search for RAG.

    Uses ChromaDB for vector storage and retrieval.
    Supports in-memory or persistent storage.

    Example:
        >>> rag = RAGStore(collection_name="my_docs")
        >>> rag.add_documents([
        ...     "Python is a programming language",
        ...     "LangGraph creates agent workflows"
        ... ])
        >>> results = rag.search("What is Python?", n_results=2)
        >>> print(results)
    """

    def __init__(
        self,
        collection_name: str = "default",
        persist_directory: str | None = None,
    ):
        """
        Initialize RAG store.

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Path for persistent storage (None = in-memory)
        """
        if not HAS_CHROMADB:
            raise ImportError("ChromaDB required. Install with: pip install chromadb")

        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # Create client
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
            logger.info(
                f"RAG store initialized with persistent storage: {persist_directory}"
            )
        else:
            self.client = chromadb.Client()
            logger.info("RAG store initialized with in-memory storage")

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity
        )

    def add_documents(
        self,
        documents: list[str],
        ids: list[str] | None = None,
        metadatas: list[dict] | None = None,
    ) -> list[str]:
        """
        Add documents to the store.

        Args:
            documents: List of text documents
            ids: Optional list of IDs (auto-generated if not provided)
            metadatas: Optional metadata for each document

        Returns:
            List of document IDs
        """
        if ids is None:
            # Generate IDs based on current count
            start_id = self.collection.count()
            ids = [f"doc_{start_id + i}" for i in range(len(documents))]

        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas,
        )

        logger.info(
            f"Added {len(documents)} documents to collection '{self.collection_name}'"
        )
        return ids

    def add_from_file(self, file_path: str | Path, chunk_size: int = 500) -> list[str]:
        """
        Add documents from a text file, splitting into chunks.

        Args:
            file_path: Path to text file
            chunk_size: Approximate characters per chunk

        Returns:
            List of document IDs
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = path.read_text(encoding="utf-8")

        # Simple chunking by paragraphs or size
        chunks = []
        current_chunk = ""

        for line in content.split("\n"):
            if len(current_chunk) + len(line) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = line
            else:
                current_chunk += "\n" + line

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        # Add metadata with source file
        metadatas = [{"source": str(path.name)} for _ in chunks]

        return self.add_documents(chunks, metadatas=metadatas)

    def search(
        self,
        query: str,
        n_results: int = 3,
        where: dict | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            n_results: Number of results to return
            where: Optional filter criteria

        Returns:
            List of results with document, metadata, and distance
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )

        # Format results
        formatted = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                formatted.append(
                    {
                        "document": doc,
                        "id": results["ids"][0][i] if results["ids"] else None,
                        "metadata": (
                            results["metadatas"][0][i] if results["metadatas"] else {}
                        ),
                        "distance": (
                            results["distances"][0][i] if results["distances"] else None
                        ),
                    }
                )

        return formatted

    def delete(self, ids: list[str]) -> None:
        """Delete documents by ID."""
        self.collection.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} documents")

    def clear(self) -> None:
        """Delete all documents in collection."""
        # ChromaDB doesn't have a clear method, so recreate collection
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name, metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Cleared collection '{self.collection_name}'")

    @property
    def count(self) -> int:
        """Number of documents in store."""
        return self.collection.count()


class RAGAgent:
    """
    Agent with RAG capabilities.

    Combines an LLM with a RAG store to answer questions
    using retrieved context.

    Example:
        >>> agent = RAGAgent(rag_store=my_rag_store)
        >>> answer = agent.query("What is Python used for?")
    """

    def __init__(
        self,
        rag_store: RAGStore,
        llm=None,
        system_prompt: str | None = None,
    ):
        from multi_agent.shared import create_llm

        self.rag_store = rag_store
        self.llm = llm or create_llm()
        self.system_prompt = system_prompt or (
            "You are a helpful assistant that answers questions based on the provided context. "
            "If the context doesn't contain relevant information, say so clearly. "
            "Always cite the source when available."
        )

    def query(self, question: str, n_context: int = 3) -> str:
        """
        Answer a question using RAG.

        Args:
            question: User's question
            n_context: Number of context documents to retrieve

        Returns:
            Generated answer
        """
        from langchain_core.messages import SystemMessage, HumanMessage

        # Retrieve relevant context
        results = self.rag_store.search(question, n_results=n_context)

        # Build context string
        context_parts = []
        for i, r in enumerate(results, 1):
            source = r.get("metadata", {}).get("source", "Unknown")
            context_parts.append(f"[{i}] Source: {source}\n{r['document']}")

        context = "\n\n".join(context_parts)

        # Build prompt with context
        user_message = f"""Based on the following context, answer the question.

CONTEXT:
{context}

QUESTION: {question}

Answer:"""

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_message),
        ]

        # Generate response
        response = self.llm.invoke(messages)

        return response.content
