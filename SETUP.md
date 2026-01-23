# Complete Setup Guide - Multi-Agent AI System

This guide provides step-by-step instructions to set up and run the multi-agent system from scratch.

## Prerequisites

- **Python 3.11+**: Required for modern type hints and asyncio features
- **Git**: For version control
- **Windows/macOS/Linux**: Project is cross-platform

## Step 1: Install Ollama (Local LLM)

Ollama allows running LLMs locally on your machine.

### Windows
```powershell
# Using winget
winget install Ollama.Ollama

# Or download from https://ollama.ai/download
```

### macOS
```bash
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Verify Installation
```bash
ollama --version
```

## Step 2: Download a Model

```bash
# Start Ollama service (runs in background)
ollama serve

# Download Mistral (recommended, ~4GB)
ollama pull mistral

# Alternative models:
ollama pull llama3.2      # Latest Llama
ollama pull codellama     # Optimized for code
ollama pull phi3          # Smaller, faster

# List downloaded models
ollama list
```

## Step 3: Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/multi-agent-ai-system.git
cd multi-agent-ai-system

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

## Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
```

### .env Configuration Options

```bash
# === LLM Provider ===
# Choose "ollama" for local or "openai" for remote
LLM_PROVIDER=ollama

# Model to use
LLM_MODEL=mistral

# === Ollama Settings ===
OLLAMA_HOST=http://localhost:11434

# === OpenAI Settings (optional, for remote) ===
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# === Anthropic Settings (optional) ===
ANTHROPIC_API_KEY=sk-ant-your-key-here

# === Agent Settings ===
# Temperature: 0.0 = deterministic, 1.0 = creative
# AGENT_TEMPERATURE=0.7
# AGENT_MAX_TOKENS=4096

# === Memory Settings ===
# Max messages to keep in conversational memory
# MEMORY_MAX_MESSAGES=20

# === Logging ===
LOG_LEVEL=INFO
```

## Step 5: Verify Setup

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Run tests
pytest tests/ -v

# Try simple chat example
python examples/01_simple_chat.py
```

## Step 6: Run Examples

```bash
# 1. Simple chat with local model
python examples/01_simple_chat.py

# 2. Agent with tool calling
python examples/02_tool_calling.py

# 3. Multi-agent team with LangGraph
python examples/03_langgraph_team.py

# 4. Multi-agent team with AutoGen
python examples/04_autogen_team.py

# 5. Memory and RAG demo
python examples/05_memory_demo.py
```

## Project Structure Explained

```
multi_agent_system/
├── pyproject.toml          # Project config & dependencies
├── .env.example            # Environment template
├── .env                    # Your local config (git-ignored)
├── README.md               # Project overview
├── SETUP.md                # This file
│
├── src/multi_agent/        # Main package
│   ├── __init__.py
│   │
│   ├── shared/             # Shared components
│   │   ├── config.py       # Pydantic settings (loads .env)
│   │   ├── llm_factory.py  # Creates LLM instances
│   │   └── memory.py       # Agent memory systems
│   │
│   ├── tools/              # Agent capabilities
│   │   ├── base.py         # Tool interface
│   │   └── common_tools.py # Calculate, file ops, search
│   │
│   ├── langgraph_agents/   # LangGraph implementation
│   │   ├── nodes.py        # Agent definitions
│   │   └── graph.py        # Workflow graph
│   │
│   └── autogen_agents/     # AutoGen implementation
│       ├── agents.py       # Agent definitions
│       └── team.py         # Team execution
│
├── examples/               # Learning examples
│   ├── 01_simple_chat.py
│   ├── 02_tool_calling.py
│   ├── 03_langgraph_team.py
│   ├── 04_autogen_team.py
│   └── 05_memory_demo.py
│
└── tests/                  # Automated tests
    ├── test_providers.py
    ├── test_memory.py
    └── test_tools.py
```

## Key Concepts

### 1. LLM Abstraction (llm_factory.py)
```python
from multi_agent.shared import create_llm, LLMType

# Use default from settings
llm = create_llm()

# Specify provider and model
from multi_agent.shared.config import LLMProvider
llm = create_llm(provider=LLMProvider.OPENAI, model="gpt-4o")

# Auto-select model for task type
llm = create_llm(llm_type=LLMType.CODING)
```

### 2. Agent Memory (memory.py)
```python
from multi_agent.shared.memory import AgentMemory, SharedMemory

# Private conversational memory
memory = AgentMemory(agent_name="assistant")
memory.set_system_prompt("You are a helpful assistant.")
memory.add_user("Hello!")
memory.add_assistant("Hi there!")

# Shared memory between agents (singleton)
shared = SharedMemory()
shared.set("research_results", {"data": [...]})
shared.append("task_log", "Step 1 completed")
```

### 3. Tool Calling (tools/)
```python
from langchain_core.tools import tool

@tool
def my_custom_tool(param: str) -> str:
    """Description of what this tool does."""
    return f"Result for {param}"

# Bind tools to LLM
llm_with_tools = llm.bind_tools([my_custom_tool])
```

### 4. LangGraph Multi-Agent
```python
from multi_agent.langgraph_agents import run_task

# Async
result = await run_task("Build a calculator function")

# Sync
from multi_agent.langgraph_agents.graph import run_task_sync
result = run_task_sync("Build a calculator function")
```

### 5. AutoGen Multi-Agent
```python
from multi_agent.autogen_agents import run_autogen_task

result = await run_autogen_task("Create a data analysis script")
```

## Troubleshooting

### Ollama not responding
```bash
# Start Ollama service manually
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

### Model not found
```bash
# List available models
ollama list

# Pull if missing
ollama pull mistral
```

### Import errors
```bash
# Reinstall in editable mode
pip install -e ".[dev]"
```

### OpenAI API errors
```bash
# Verify API key is set
echo $OPENAI_API_KEY  # macOS/Linux
echo %OPENAI_API_KEY% # Windows

# Or check .env file
```

## Next Steps

1. **Modify agent prompts** in `langgraph_agents/nodes.py` or `autogen_agents/agents.py`
2. **Add custom tools** in `tools/common_tools.py`
3. **Extend memory** with vector storage (ChromaDB already included)
4. **Add new agents** by creating new node/agent classes
5. **Connect real APIs** (replace mock web search, etc.)
