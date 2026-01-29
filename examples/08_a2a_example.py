"""
Example 8: Interactive A2A (Agent-to-Agent) Protocol

Demonstrates distributed agent communication using A2A protocol.
Agents can discover each other and delegate tasks.

This example shows:
1. Creating agent cards
2. A2A message format
3. Task delegation
4. Interactive agent simulation

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


# Define specialized agents
AGENTS = {
    "researcher": AgentCard(
        name="researcher",
        description="Expert at finding and synthesizing information",
        url="http://localhost:8001",
        skills=["research", "analysis", "summarization"],
        input_modes=["text"],
        output_modes=["text", "structured_data"],
    ),
    "coder": AgentCard(
        name="coder",
        description="Senior developer skilled in multiple languages",
        url="http://localhost:8002",
        skills=["python", "javascript", "code_review"],
        input_modes=["text", "code"],
        output_modes=["text", "code"],
    ),
    "reviewer": AgentCard(
        name="reviewer",
        description="Quality assurance and code review specialist",
        url="http://localhost:8003",
        skills=["code_review", "testing", "documentation"],
        input_modes=["text", "code"],
        output_modes=["text", "structured_data"],
    ),
}


def demo_agent_cards():
    """Demonstrate Agent Card concept."""
    print("\n📇 Agent Cards - Agent Identity & Capabilities")
    print("-" * 50)

    for card in AGENTS.values():
        print(f"\n   🤖 {card.name.upper()}")
        print(f"      Description: {card.description}")
        print(f"      URL: {card.url}")
        print(f"      Skills: {', '.join(card.skills)}")


def demo_network_topology():
    """Show agent network topology."""
    print("\n\n🌐 Agent Network Topology")
    print("-" * 50)
    print(
        """
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
   │              │    (you)      │                      │
   │              └───────────────┘                      │
   └─────────────────────────────────────────────────────┘
    """
    )


def simulate_task_execution(agent_name: str, task_desc: str) -> str:
    """Simulate task execution by an agent."""
    agent = AGENTS.get(agent_name)
    if not agent:
        return f"Unknown agent: {agent_name}"

    # Simulate different responses based on agent type
    if agent_name == "researcher":
        return f"[Research Complete] Found 3 relevant sources on: {task_desc}"
    elif agent_name == "coder":
        return f"[Code Generated] Implemented solution for: {task_desc}\n```python\ndef solution():\n    pass  # Implementation here\n```"
    elif agent_name == "reviewer":
        return (
            f"[Review Complete] Code quality: Good. Minor suggestions for: {task_desc}"
        )
    return f"Task completed: {task_desc}"


def interactive_a2a_orchestrator():
    """Interactive A2A orchestrator simulation."""
    print("\n\n💬 Interactive A2A Orchestrator")
    print("-" * 50)
    print("Simulate delegating tasks to agents in the network!")
    print("\nCommands:")
    print("  agents              - List all agents and their skills")
    print("  send <agent> <task> - Send a task to an agent")
    print("  broadcast <message> - Send message to all agents")
    print("  exit/quit           - Exit the demo\n")

    task_log = []

    while True:
        try:
            user_input = input("\n🎯 Orchestrator> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("\n👋 Goodbye!")
            break

        parts = user_input.split(maxsplit=2)
        cmd = parts[0].lower()

        if cmd == "agents":
            print("\n📋 Available Agents:")
            for name, card in AGENTS.items():
                print(f"   • {name}: {card.description}")
                print(f"     Skills: {', '.join(card.skills)}")

        elif cmd == "send" and len(parts) >= 3:
            agent_name = parts[1].lower()
            task_desc = parts[2]

            if agent_name not in AGENTS:
                print(f"❌ Unknown agent: {agent_name}")
                print(f"   Available: {', '.join(AGENTS.keys())}")
                continue

            # Create and "send" task
            task = A2ATask(description=task_desc)
            print(f"\n📤 Sending task to {agent_name}...")
            print(f"   Task ID: {task.id[:8]}...")
            print(f"   Description: {task_desc}")

            # Simulate processing
            task.state = TaskState.RUNNING
            print(f"   Status: {task.state.value}")

            print(f"   📡 Connecting to {agent_name} at {AGENTS[agent_name].url}...")
            print(f"   ⏳ Waiting for agent response...")

            # Get "result"
            result = simulate_task_execution(agent_name, task_desc)
            task.state = TaskState.COMPLETED
            task.result = result

            print(f"\n✅ Task completed!")
            print(f"   Result: {result}")

            task_log.append(
                {
                    "agent": agent_name,
                    "task": task_desc,
                    "result": result[:50] + "..." if len(result) > 50 else result,
                }
            )

        elif cmd == "broadcast":
            message = " ".join(parts[1:]) if len(parts) > 1 else "Hello agents!"
            print(f"\n📢 Broadcasting to all agents: '{message}'")
            for name in AGENTS:
                print(f"   ✓ Sent to {name}")

        elif cmd == "log":
            if not task_log:
                print("📜 No tasks executed yet.")
            else:
                print("\n📜 Task Log:")
                for i, entry in enumerate(task_log, 1):
                    print(f"   {i}. [{entry['agent']}] {entry['task']}")

        else:
            print("❓ Unknown command. Try 'agents', 'send <agent> <task>', or 'exit'")


def main():
    print("\n" + "=" * 60)
    print("🔗 Interactive A2A (Agent-to-Agent) Protocol Demo")
    print("=" * 60)

    demo_agent_cards()
    demo_network_topology()
    interactive_a2a_orchestrator()

    print("\n" + "=" * 60)
    print("✅ A2A Demo completed!")
    print("=" * 60)
    print("\n💡 To run real distributed agents:")
    print("   1. Start multiple A2A servers on different ports")
    print("   2. Register them with an AgentNetwork")
    print("   3. Submit tasks that get routed automatically")


if __name__ == "__main__":
    main()
