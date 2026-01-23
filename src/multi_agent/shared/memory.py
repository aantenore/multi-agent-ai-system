"""
Memory system for agents.

Implements:
- AgentMemory: private conversational memory for each agent
- SharedMemory: shared memory between agents (thread-safe)

Memory is fundamental for maintaining context and allowing
agents to "remember" previous interactions.
"""

import threading
from collections import deque
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from loguru import logger

from multi_agent.shared.config import settings


class Message(BaseModel):
    """Single message in memory."""

    role: str = Field(description="Role: user, assistant, system, tool")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_langchain(self) -> tuple[str, str]:
        """Convert to LangChain format."""
        return (self.role, self.content)


class AgentMemory:
    """
    Private conversational memory for an agent.

    Maintains a sliding window of recent messages
    to provide context to the LLM without exceeding token limits.

    Example:
        >>> memory = AgentMemory(max_messages=10)
        >>> memory.add("user", "Hello!")
        >>> memory.add("assistant", "Hello! How can I help you?")
        >>> print(memory.get_messages())
    """

    def __init__(self, max_messages: int | None = None, agent_name: str = "agent"):
        self.max_messages = max_messages or settings.memory_max_messages
        self.agent_name = agent_name
        self._messages: deque[Message] = deque(maxlen=self.max_messages)
        self._system_prompt: str | None = None

    def set_system_prompt(self, prompt: str) -> None:
        """Set the system prompt (doesn't count in message limit)."""
        self._system_prompt = prompt
        logger.debug(f"[{self.agent_name}] System prompt set")

    def add(self, role: str, content: str, **metadata: Any) -> None:
        """Add a message to memory."""
        msg = Message(role=role, content=content, metadata=metadata)
        self._messages.append(msg)
        logger.debug(f"[{self.agent_name}] Added message: {role[:20]}...")

    def add_user(self, content: str, **metadata: Any) -> None:
        """Shortcut for user message."""
        self.add("user", content, **metadata)

    def add_assistant(self, content: str, **metadata: Any) -> None:
        """Shortcut for assistant message."""
        self.add("assistant", content, **metadata)

    def get_messages(self, include_system: bool = True) -> list[tuple[str, str]]:
        """
        Return messages in LangChain format.

        Returns:
            List of tuples (role, content)
        """
        messages = []

        if include_system and self._system_prompt:
            messages.append(("system", self._system_prompt))

        for msg in self._messages:
            messages.append(msg.to_langchain())

        return messages

    def get_last_n(self, n: int) -> list[Message]:
        """Return the last N messages."""
        return list(self._messages)[-n:]

    def clear(self) -> None:
        """Clear memory (keeps system prompt)."""
        self._messages.clear()
        logger.info(f"[{self.agent_name}] Memory cleared")

    def __len__(self) -> int:
        return len(self._messages)


class SharedMemory:
    """
    Shared memory between agents (thread-safe).

    Allows agents to share information and results.
    Useful for patterns like blackboard or publish-subscribe.

    Example:
        >>> shared = SharedMemory()
        >>> shared.set("research_results", {"topic": "AI", "findings": [...]})
        >>> results = shared.get("research_results")
        >>>
        >>> # Append to shared list
        >>> shared.append("task_log", "Researcher: completed analysis")
        >>> shared.append("task_log", "Coder: implemented solution")
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Thread-safe singleton."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._store: dict[str, Any] = {}
                    cls._instance._store_lock = threading.RLock()
        return cls._instance

    def set(self, key: str, value: Any) -> None:
        """Set a value in shared memory."""
        with self._store_lock:
            self._store[key] = value
            logger.debug(f"[SharedMemory] Set: {key}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from shared memory."""
        with self._store_lock:
            return self._store.get(key, default)

    def delete(self, key: str) -> bool:
        """Remove a value."""
        with self._store_lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def append(self, key: str, value: Any) -> None:
        """Append to a list (creates if doesn't exist)."""
        with self._store_lock:
            if key not in self._store:
                self._store[key] = []
            if isinstance(self._store[key], list):
                self._store[key].append(value)
            else:
                raise TypeError(f"Key '{key}' is not a list")

    def get_all(self) -> dict[str, Any]:
        """Return copy of all memory."""
        with self._store_lock:
            return dict(self._store)

    def clear(self) -> None:
        """Clear all shared memory."""
        with self._store_lock:
            self._store.clear()
            logger.info("[SharedMemory] Shared memory cleared")

    def keys(self) -> list[str]:
        """List of keys."""
        with self._store_lock:
            return list(self._store.keys())


# Factory to create agent memory
def create_agent_memory(
    agent_name: str, system_prompt: str | None = None
) -> AgentMemory:
    """
    Factory to create agent memory with standard configuration.

    Args:
        agent_name: Agent name
        system_prompt: Optional system prompt

    Returns:
        Configured AgentMemory
    """
    memory = AgentMemory(agent_name=agent_name)
    if system_prompt:
        memory.set_system_prompt(system_prompt)
    return memory
