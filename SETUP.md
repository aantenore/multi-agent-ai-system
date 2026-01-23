# Complete Setup Guide - Multi-Agent AI System

Step-by-step instructions to set up and run the multi-agent system from scratch.

## Prerequisites

- **Python 3.11+**: Required for modern type hints and asyncio
- **Git**: For version control
- **Windows/macOS/Linux**: Cross-platform

## Step 1: Install Ollama (Local LLM)

### Windows
```powershell
winget install Ollama.Ollama
```

### macOS
```bash
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## Step 2: Download a Model

```bash
ollama serve              # Start service
ollama pull mistral       # Download (~4GB)
ollama list               # Verify
```

## Step 3: Clone and Setup

```bash
git clone https://github.com/aantenore/multi-agent-ai-system.git
cd multi-agent-ai-system
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate # macOS/Linux
pip install -e ".[dev]"
```

## Step 4: Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

## Step 5: Run Examples

```bash
# Basic
python examples/01_simple_chat.py
python examples/02_tool_calling.py

# Multi-Agent
python examples/03_langgraph_team.py
python examples/04_autogen_team.py

# Advanced
python examples/05_memory_demo.py
python examples/06_rag_example.py
python examples/07_mcp_example.py
python examples/08_a2a_example.py
```

## Project Structure

```
src/multi_agent/
├── shared/
│   ├── config.py        # Configuration
│   ├── llm_factory.py   # LLM abstraction
│   ├── memory.py        # Agent memory
│   ├── rag.py           # RAG with ChromaDB
│   ├── mcp.py           # Model Context Protocol
│   └── a2a.py           # Agent-to-Agent
├── tools/               # Agent capabilities
├── langgraph_agents/    # LangGraph implementation
└── autogen_agents/      # AutoGen implementation
```

## Key Concepts

### 1. LLM Factory
```python
from multi_agent.shared import create_llm
llm = create_llm()  # Uses settings
```

### 2. Agent Memory
```python
from multi_agent.shared.memory import AgentMemory, SharedMemory
memory = AgentMemory(agent_name="assistant")
shared = SharedMemory()
```

### 3. RAG (Retrieval-Augmented Generation)
```python
from multi_agent.shared.rag import RAGStore, RAGAgent
rag = RAGStore(collection_name="docs")
rag.add_documents(["Document 1", "Document 2"])
results = rag.search("query", n_results=3)
```

### 4. MCP (Model Context Protocol)
```python
from multi_agent.shared.mcp import MCPServer
server = MCPServer(name="my-server")

@server.tool(name="calc", description="Calculate", input_schema={...})
def calculate(expr: str) -> str:
    return str(eval(expr))
```

### 5. A2A (Agent-to-Agent)
```python
from multi_agent.shared.a2a import AgentCard, A2AServer, AgentNetwork
card = AgentCard(name="coder", url="http://localhost:8001", skills=["python"])
network = AgentNetwork()
await network.register("http://localhost:8001")
```

### 6. LangGraph Multi-Agent
```python
from multi_agent.langgraph_agents import run_task
result = await run_task("Write a function")
```

### 7. AutoGen Multi-Agent
```python
from multi_agent.autogen_agents import run_autogen_task
result = await run_autogen_task("Create a class")
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Ollama not responding | `ollama serve` |
| Model not found | `ollama pull mistral` |
| Import errors | `pip install -e ".[dev]"` |

## Next Steps

1. Modify agent prompts in `langgraph_agents/nodes.py`
2. Add custom tools in `tools/common_tools.py`
3. Extend RAG with more documents
4. Create custom MCP servers
5. Build distributed agent networks with A2A
