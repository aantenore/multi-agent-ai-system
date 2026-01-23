# Multi-Agent AI System - Educational Project

A comprehensive multi-agent system using **LangGraph** and **AutoGen** with support for local models (Ollama) and remote models (OpenAI).

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
│   ├── shared/              # Shared components
│   │   ├── config.py        # Centralized configuration
│   │   ├── llm_factory.py   # Factory for local/remote LLMs
│   │   └── memory.py        # Agent memory system
│   ├── tools/               # Agent tools
│   │   ├── base.py          # Base tool interface
│   │   └── common_tools.py  # Common tools (web, file, calc)
│   ├── langgraph_agents/    # LangGraph implementation
│   │   ├── graph.py         # Multi-agent graph
│   │   └── nodes.py         # Graph nodes (agents)
│   └── autogen_agents/      # AutoGen implementation
│       ├── team.py          # Agent team
│       └── agents.py        # Agent definitions
├── examples/                # Practical examples
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
- Groq: `llama-3.1-70b-versatile`

## 📚 Concepts Implemented

1. **LLM Abstraction**: Factory pattern for transparent local/remote switching
2. **Agent Memory**: Conversational + short-term memory for context
3. **Tool Calling**: Tool system with JSON schema
4. **Multi-Agent Orchestration**: Coordination between specialized agents
5. **State Management**: State management with LangGraph

## 🎓 Examples

| File | Description |
|------|-------------|
| `01_simple_chat.py` | Basic chat with local model |
| `02_tool_calling.py` | Agent with tool calling |
| `03_langgraph_team.py` | Multi-agent team with LangGraph |
| `04_autogen_team.py` | Multi-agent team with AutoGen |
| `05_memory_demo.py` | Agent with memory and basic RAG |

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_memory.py -v
```

## 📖 Learning Path

1. Start with `01_simple_chat.py` to understand LLM abstraction
2. Explore `02_tool_calling.py` to learn about agent capabilities
3. Study `03_langgraph_team.py` for state-based multi-agent workflows
4. Compare with `04_autogen_team.py` for conversational multi-agent patterns
5. Dive into `05_memory_demo.py` for memory and RAG concepts

## 🔧 Configuration

Edit `.env` file to configure:

```bash
# LLM Provider: "ollama" for local, "openai" for remote
LLM_PROVIDER=ollama
LLM_MODEL=mistral

# For remote providers
OPENAI_API_KEY=sk-your-key-here
```

## 📜 License

MIT License - Feel free to use for learning and projects!
