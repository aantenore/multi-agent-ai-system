# Multi-Agent AI System - Educational Project

A comprehensive multi-agent system powered by **Google Gemini** using **LangGraph** and **AutoGen**. Features **interactive CLI chats**, extensible agent skills, **RAG**, **MCP**, and **A2A** protocols.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Configure environment variables
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# 3. Run an interactive example
python examples/01_simple_chat.py
```

## ✨ Features

- 🤖 **Google Gemini** as primary AI engine (gemini-3-pro-preview)
- 💬 **Interactive CLI chats** - all examples are interactive
- 🛠️ **13 Agent Skills** - extensible tool system
- 🧠 **Memory & RAG** - context-aware conversations
- 🔗 **Multi-Agent Teams** - LangGraph & AutoGen orchestration
- 🌐 **MCP & A2A Protocols** - standardized agent communication

## 📁 Project Structure

```
multi_agent_system/
├── src/multi_agent/
│   ├── shared/              # Core components
│   │   ├── config.py        # Centralized configuration
│   │   ├── llm_factory.py   # Factory for Gemini/Ollama/OpenAI
│   │   ├── memory.py        # Agent memory system
│   │   ├── rag.py           # RAG with ChromaDB
│   │   ├── mcp.py           # Model Context Protocol
│   │   └── a2a.py           # Agent-to-Agent protocol
│   ├── tools/               # Agent skills (13 tools)
│   ├── langgraph_agents/    # LangGraph implementation
│   └── autogen_agents/      # AutoGen implementation
├── examples/                # 8 interactive examples
└── tests/                   # Automated tests
```

## 🤖 Supported Models

### Google Gemini (Recommended)
- `gemini-2.5-flash-lite` - Ultra-fast, lightweight (default)
- `gemini-3-flash-preview` - Fast, capable general model
- `gemini-3-pro-preview` - Best for coding and complex reasoning
- `gemini-2.0-flash` - Balanced performance

### Local (Ollama)
- `mistral` - Balanced, great for general tasks
- `codellama` - Optimized for code generation
- `llama3.2` - Latest, good performance

### Remote
- OpenAI: `gpt-4o`, `gpt-4o-mini`
- Anthropic: `claude-3-sonnet`, `claude-3-haiku`

## 🛠️ Agent Skills

| Skill | Description |
|-------|-------------|
| `calculate` | Mathematical calculations |
| `get_current_time` | Current date/time |
| `read_file` | Read text files |
| `write_file` | Write text files |
| `list_directory` | List folder contents |
| `web_search_mock` | Simulated web search |
| `analyze_code` | Code metrics & issues |
| `format_json` | JSON formatting/validation |
| `text_stats` | Text statistics |
| `convert_units` | Unit conversions |
| `generate_uuid` | Generate UUIDs |
| `encode_base64` | Base64 encoding |
| `decode_base64` | Base64 decoding |

## 🎓 Interactive Examples

All examples feature **interactive CLI chat loops**. Type `exit` or `quit` to end.

| File | Description |
|------|-------------|
| `01_simple_chat.py` | Interactive chat with any model |
| `02_tool_calling.py` | Agent with skill invocation |
| `03_langgraph_team.py` | Multi-agent team tasks |
| `04_autogen_team.py` | AutoGen conversational team |
| `05_memory_demo.py` | Memory-aware chat |
| `06_rag_example.py` | Knowledge-based Q&A |
| `07_mcp_example.py` | MCP tool testing |
| `08_a2a_example.py` | Agent network simulation |

## 🔧 Configuration

Edit `.env` file:

```bash
# Recommended: Google Gemini
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3-pro-preview
GOOGLE_API_KEY=your-google-api-key-here

# Alternative: OpenAI
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4o-mini
# OPENAI_API_KEY=sk-your-key-here

# Alternative: Local Ollama
# LLM_PROVIDER=ollama
# LLM_MODEL=mistral
```

## 🧪 Running Tests

```bash
pytest tests/ -v
```

## 📚 Concepts Implemented

| Concept | Module | Description |
|---------|--------|-------------|
| **LLM Abstraction** | `llm_factory.py` | Transparent provider switching |
| **Agent Memory** | `memory.py` | Conversational + shared memory |
| **Agent Skills** | `tools/` | 13 extensible capabilities |
| **LangGraph** | `langgraph_agents/` | State-based multi-agent |
| **AutoGen** | `autogen_agents/` | Conversational multi-agent |
| **RAG** | `rag.py` | ChromaDB semantic search |
| **MCP** | `mcp.py` | Model Context Protocol |
| **A2A** | `a2a.py` | Agent-to-Agent distributed |

## 📖 Learning Path

1. **Basic**: `01_simple_chat.py` - LLM abstraction with Gemini
2. **Skills**: `02_tool_calling.py` - Agent capabilities
3. **Multi-Agent**: `03_langgraph_team.py` & `04_autogen_team.py`
4. **Memory**: `05_memory_demo.py` - Context management
5. **RAG**: `06_rag_example.py` - Knowledge retrieval
6. **Protocols**: `07_mcp_example.py` & `08_a2a_example.py`

## 📜 License

MIT License - Feel free to use for learning and projects!
