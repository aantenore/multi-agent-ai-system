"""
Example 8: A2A (Agent-to-Agent) Protocol

Demonstrates distributed agent communication using A2A protocol.
Agents can discover each other and delegate tasks.

This example shows:
1. Creating agent cards
2. A2A message format
3. Task delegation
4. Agent network management

Usage:
    python examples/08_a2a_example.py
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from multi_agent.shared.a2a import (
    AgentCard,
    A2AMessage,
    A2ATask,
    TaskState,
    A2AServer,
    AgentNetwork,
)


def demo_agent_cards():
    """Demonstrate Agent Card concept."""
    print("\n📇 Agent Cards - Agent Identity & Capabilities")
    print("-" * 50)

    # Create agent cards for different specialized agents
    agents = [
        AgentCard(
            name="researcher",
            description="Expert at finding and synthesizing information",
            url="http://localhost:8001",
            skills=["research", "analysis", "summarization"],
            input_modes=["text"],
            output_modes=["text", "structured_data"],
        ),
        AgentCard(
            name="coder",
            description="Senior developer skilled in multiple languages",
            url="http://localhost:8002",
            skills=["python", "javascript", "code_review"],
            input_modes=["text", "code"],
            output_modes=["text", "code"],
        ),
        AgentCard(
            name="reviewer",
            description="Quality assurance and code review specialist",
            url="http://localhost:8003",
            skills=["code_review", "testing", "documentation"],
            input_modes=["text", "code"],
            output_modes=["text", "structured_data"],
        ),
    ]

    for card in agents:
        print(f"\n   🤖 {card.name.upper()}")
        print(f"      Description: {card.description}")
        print(f"      URL: {card.url}")
        print(f"      Skills: {', '.join(card.skills)}")


def demo_messages():
    """Demonstrate A2A message format."""
    print("\n\n📨 A2A Messages - Inter-Agent Communication")
    print("-" * 50)

    # Create example messages
    messages = [
        A2AMessage(
            sender="orchestrator",
            receiver="researcher",
            content="Please research best practices for Python async programming",
            metadata={"priority": "high", "context": "user_request_123"},
        ),
        A2AMessage(
            sender="researcher",
            receiver="coder",
            content="Here's the research summary: Use asyncio with await...",
            metadata={"research_id": "res_456"},
        ),
        A2AMessage(
            sender="coder",
            receiver="reviewer",
            content="Code implementation ready for review",
            content_type="code",
            metadata={"language": "python", "lines": 50},
        ),
    ]

    for msg in messages:
        print(f"\n   📤 {msg.sender} → {msg.receiver}")
        print(f"      Content: {msg.content[:50]}...")
        print(f"      Type: {msg.content_type}")
        print(f"      Metadata: {msg.metadata}")


def demo_tasks():
    """Demonstrate A2A task format."""
    print("\n\n📋 A2A Tasks - Distributed Task Management")
    print("-" * 50)

    # Create example tasks in different states
    tasks = [
        A2ATask(
            description="Research Python best practices",
            state=TaskState.COMPLETED,
            result="Found 5 key best practices: 1) Use type hints...",
        ),
        A2ATask(
            description="Implement async file handler",
            state=TaskState.RUNNING,
            metadata={"assigned_to": "coder", "estimated_time": "30min"},
        ),
        A2ATask(
            description="Review code for security issues",
            state=TaskState.PENDING,
            metadata={"assigned_to": "reviewer"},
        ),
    ]

    status_icons = {
        TaskState.PENDING: "⏳",
        TaskState.RUNNING: "🔄",
        TaskState.COMPLETED: "✅",
        TaskState.FAILED: "❌",
    }

    for task in tasks:
        icon = status_icons.get(task.state, "❓")
        print(f"\n   {icon} Task: {task.description}")
        print(f"      ID: {task.id[:8]}...")
        print(f"      State: {task.state.value}")
        if task.result:
            print(f"      Result: {task.result[:50]}...")


async def demo_server_client():
    """Demonstrate A2A server concept (without actually starting server)."""
    print("\n\n🖥️ A2A Server/Client Architecture")
    print("-" * 50)

    # Create a sample server configuration
    coder_card = AgentCard(
        name="coder",
        description="Code generation agent",
        url="http://localhost:8002",
        skills=["python", "javascript"],
    )

    server = A2AServer(coder_card)

    @server.on_task
    async def handle_task(task: A2ATask) -> str:
        # In real scenario, this would invoke an LLM
        return f"Completed task: {task.description}"

    @server.on_message
    async def handle_message(msg: A2AMessage) -> str:
        return f"Received message from {msg.sender}"

    print(
        f"""
   Server Configuration:
   ----------------------
   Agent: {server.agent_card.name}
   URL: {server.agent_card.url}
   Skills: {server.agent_card.skills}
   
   Endpoints exposed:
   • GET  /.well-known/agent.json  - Agent Card (discovery)
   • POST /tasks                    - Submit a task
   • GET  /tasks/{{id}}              - Get task status
   • POST /messages                 - Send a message
   
   To run the server:
      server.run(host="0.0.0.0", port=8002)
    """
    )


def demo_network():
    """Demonstrate agent network concept."""
    print("\n🌐 Agent Network - Distributed Agent Orchestration")
    print("-" * 50)

    print(
        """
   Agent Network enables:
   
   1. 🔍 Discovery
      - Agents publish their cards at /.well-known/agent.json
      - Network discovers and registers available agents
      
   2. 🎯 Skill-Based Routing
      - Tasks are routed to agents with matching skills
      - "Need Python code" → routes to agent with 'python' skill
      
   3. 📊 Load Distribution
      - Tasks can be distributed across multiple agents
      - Enables scaling horizontally
      
   4. 💬 Broadcast
      - Send messages to all agents in the network
      - Useful for synchronization and updates
   
   Example Network Topology:
   
   ┌─────────────────────────────────────────────────────┐
   │                   Agent Network                      │
   │                                                      │
   │  ┌──────────┐   ┌──────────┐   ┌──────────┐        │
   │  │Researcher│   │  Coder   │   │ Reviewer │        │
   │  │ :8001    │   │  :8002   │   │  :8003   │        │
   │  │[research]│   │ [python] │   │ [review] │        │
   │  └────┬─────┘   └────┬─────┘   └────┬─────┘        │
   │       │              │              │               │
   │       └──────────────┼──────────────┘               │
   │                      │                              │
   │              ┌───────┴───────┐                      │
   │              │  Orchestrator │                      │
   │              │    (client)   │                      │
   │              └───────────────┘                      │
   └─────────────────────────────────────────────────────┘
   
   Usage:
      network = AgentNetwork()
      await network.register("http://localhost:8001")
      await network.register("http://localhost:8002")
      
      # Route by skill
      result = await network.submit_task(
          "Write a Python function",
          skill="python"
      )
    """
    )


def main():
    print("\n" + "=" * 60)
    print("🔗 A2A (Agent-to-Agent) Protocol Demo")
    print("=" * 60)

    demo_agent_cards()
    demo_messages()
    demo_tasks()
    asyncio.run(demo_server_client())
    demo_network()

    print("\n" + "=" * 60)
    print("✅ A2A Demo completed!")
    print("=" * 60)
    print("\n💡 To run real distributed agents:")
    print("   1. Start multiple A2A servers on different ports")
    print("   2. Register them with an AgentNetwork")
    print("   3. Submit tasks that get routed automatically")


if __name__ == "__main__":
    main()
