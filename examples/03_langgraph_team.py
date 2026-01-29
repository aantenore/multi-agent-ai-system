"""
Example 3: Interactive Multi-Agent Team with LangGraph.

Demonstrates a team of collaborating agents with interactive task submission:
- Orchestrator: coordinates the work
- Researcher: searches for information
- Coder: implements code
- Reviewer: validates the work

Usage:
    python examples/03_langgraph_team.py
    python examples/03_langgraph_team.py "Write a function to sort a list"
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loguru import logger

from multi_agent.langgraph_agents import run_task


async def run_single_task(task: str):
    """Run a single task through the multi-agent team."""
    print(f"\n📋 Task: {task}")
    print("-" * 60)

    print("\n🚀 Starting team...")
    print("   Orchestrator → analyzes and delegates")
    print("   Researcher → searches for info")
    print("   Coder → implements")
    print("   Reviewer → validates")
    print("-" * 60 + "\n")

    try:
        result = await run_task(task, max_iterations=8)

        print("\n" + "=" * 60)
        print("✅ FINAL RESULT:")
        print("=" * 60)
        print(result)
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("Error during execution")
        print("\nMake sure your LLM provider is configured correctly.")
        return False


async def main():
    print("\n🔷 Interactive Multi-Agent Team with LangGraph")
    print("=" * 60)

    # Check if task provided via command line
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
        await run_single_task(task)
        return

    # Interactive mode
    print("Enter tasks for the multi-agent team to work on.")
    print("Type 'exit' or 'quit' to end.\n")

    while True:
        try:
            task = input("\n📝 Enter your task: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            break

        if not task:
            continue
        if task.lower() in ("exit", "quit"):
            print("\n👋 Goodbye!")
            break

        await run_single_task(task)
        print("\n" + "=" * 60)
        print("Ready for next task...")


if __name__ == "__main__":
    asyncio.run(main())
