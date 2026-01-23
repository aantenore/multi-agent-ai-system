"""Shared components package."""

from multi_agent.shared.config import settings
from multi_agent.shared.llm_factory import create_llm, LLMType
from multi_agent.shared.memory import AgentMemory, SharedMemory

# RAG components
try:
    from multi_agent.shared.rag import RAGStore, RAGAgent
except ImportError:
    RAGStore = None
    RAGAgent = None

# MCP components
try:
    from multi_agent.shared.mcp import MCPServer, MCPClient, MCPTool
except ImportError:
    MCPServer = None
    MCPClient = None
    MCPTool = None

# A2A components
try:
    from multi_agent.shared.a2a import AgentCard, A2AServer, A2AClient, AgentNetwork
except ImportError:
    AgentCard = None
    A2AServer = None
    A2AClient = None
    AgentNetwork = None

__all__ = [
    "settings",
    "create_llm",
    "LLMType",
    "AgentMemory",
    "SharedMemory",
    "RAGStore",
    "RAGAgent",
    "MCPServer",
    "MCPClient",
    "MCPTool",
    "AgentCard",
    "A2AServer",
    "A2AClient",
    "AgentNetwork",
]
