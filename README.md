# Multi-Agent AI System - Educational Project

A comprehensive multi-agent system using **LangGraph** and **AutoGen** with support for local models (Ollama) and remote models (OpenAI). Includes **RAG**, **MCP**, and **A2A** protocols.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Configure environment variables
cp .env.example .env
# Edit .env with your API keys (optional for remote models)

# 3. Verify Ollama is running
ollama list

# 4. Run an example
python examples/01_simple_chat.py
```

## 📁 Project Structure

```
multi_agent_system/
├── src/multi_agent/
│   ├── shared/              # Core components
│   │   ├── config.py        # Centralized configuration
│   │   ├── llm_factory.py   # Factory for local/remote LLMs
│   │   ├── memory.py        # Agent memory system
│   │   ├── rag.py           # RAG with ChromaDB
│   │   ├── mcp.py           # Model Context Protocol
│   │   └── a2a.py           # Agent-to-Agent protocol
│   ├── tools/               # Agent tools
│   ├── langgraph_agents/    # LangGraph implementation
│   └── autogen_agents/      # AutoGen implementation
├── examples/                # 8 practical examples
└── tests/                   # Automated tests
```

## 🤖 Supported Models

### Local (Ollama)
- `mistral` - Balanced, great for general tasks
- `codellama` - Optimized for code generation
- `llama3.2` - Latest, good performance

### Remote
- OpenAI: `gpt-4o`, `gpt-4o-mini`
- Anthropic: `claude-3-sonnet`, `claude-3-haiku`

## 📚 Concepts Implemented

| Concept | Module | Description |
|---------|--------|-------------|
| **LLM Abstraction** | `llm_factory.py` | Transparent local/remote switching |
| **Agent Memory** | `memory.py` | Conversational + shared memory |
| **Tool Calling** | `tools/` | Extensible tool system |
| **LangGraph** | `langgraph_agents/` | State-based multi-agent |
| **AutoGen** | `autogen_agents/` | Conversational multi-agent |
| **RAG** | `rag.py` | ChromaDB semantic search |
| **MCP** | `mcp.py` | Model Context Protocol |
| **A2A** | `a2a.py` | Agent-to-Agent distributed |

## 🎓 Examples

| File | Description |
|------|-------------|
| `01_simple_chat.py` | Basic chat with local model |
| `02_tool_calling.py` | Agent with tool calling |
| `03_langgraph_team.py` | Multi-agent team with LangGraph |
| `04_autogen_team.py` | Multi-agent team with AutoGen |
| `05_memory_demo.py` | Agent memory and basic RAG |
| `06_rag_example.py` | Full RAG with ChromaDB |
| `07_mcp_example.py` | MCP server/client demo |
| `08_a2a_example.py` | Distributed agent communication |

## 🧪 Running Tests

```bash
pytest tests/ -v
```

## 📖 Learning Path

1. **Basic**: `01_simple_chat.py` - LLM abstraction
2. **Tools**: `02_tool_calling.py` - Agent capabilities
3. **Multi-Agent**: `03_langgraph_team.py` & `04_autogen_team.py`
4. **Memory**: `05_memory_demo.py` - Context management
5. **RAG**: `06_rag_example.py` - Knowledge retrieval
6. **Protocols**: `07_mcp_example.py` & `08_a2a_example.py`

## 🔧 Configuration

Edit `.env` file:

```bash
LLM_PROVIDER=ollama
LLM_MODEL=mistral
OPENAI_API_KEY=sk-your-key-here  # Optional
```

## 📜 License

MIT License - Feel free to use for learning and projects!
