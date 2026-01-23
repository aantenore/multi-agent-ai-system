"""Tests for memory system."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from multi_agent.shared.memory import AgentMemory, SharedMemory, create_agent_memory


class TestAgentMemory:
    """Test agent memory."""

    def test_create_memory(self):
        """Test memory creation."""
        memory = AgentMemory(agent_name="test")
        assert len(memory) == 0

    def test_add_messages(self):
        """Test adding messages."""
        memory = AgentMemory(max_messages=5, agent_name="test")
        memory.add_user("Hello")
        memory.add_assistant("Hi! How can I help you?")

        assert len(memory) == 2

    def test_max_messages_limit(self):
        """Test message limit."""
        memory = AgentMemory(max_messages=3, agent_name="test")

        for i in range(5):
            memory.add_user(f"Message {i}")

        assert len(memory) == 3

    def test_system_prompt(self):
        """Test system prompt."""
        memory = create_agent_memory("test", "You are an assistant.")
        messages = memory.get_messages()

        assert len(messages) == 1
        assert messages[0][0] == "system"
        assert "assistant" in messages[0][1]

    def test_clear(self):
        """Test memory clearing."""
        memory = AgentMemory(agent_name="test")
        memory.set_system_prompt("System")
        memory.add_user("Test")

        memory.clear()

        assert len(memory) == 0
        # System prompt preserved
        messages = memory.get_messages()
        assert len(messages) == 1


class TestSharedMemory:
    """Test shared memory."""

    def test_singleton(self):
        """Test singleton pattern."""
        mem1 = SharedMemory()
        mem2 = SharedMemory()

        assert mem1 is mem2

    def test_set_get(self):
        """Test set/get."""
        shared = SharedMemory()
        shared.clear()

        shared.set("key1", "value1")
        assert shared.get("key1") == "value1"

    def test_get_default(self):
        """Test get with default."""
        shared = SharedMemory()
        shared.clear()

        result = shared.get("nonexistent", "default")
        assert result == "default"

    def test_append(self):
        """Test append to list."""
        shared = SharedMemory()
        shared.clear()

        shared.append("log", "entry1")
        shared.append("log", "entry2")

        log = shared.get("log")
        assert log == ["entry1", "entry2"]

    def test_delete(self):
        """Test delete."""
        shared = SharedMemory()
        shared.clear()

        shared.set("temp", "data")
        assert shared.delete("temp") == True
        assert shared.get("temp") is None

    def test_keys(self):
        """Test key listing."""
        shared = SharedMemory()
        shared.clear()

        shared.set("a", 1)
        shared.set("b", 2)

        keys = shared.keys()
        assert "a" in keys
        assert "b" in keys
