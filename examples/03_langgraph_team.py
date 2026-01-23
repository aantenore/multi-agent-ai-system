"""
Example 3: Multi-Agent Team with LangGraph.

Demonstrates a team of collaborating agents:
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


async def main():
    print("\n🔷 Multi-Agent Team with LangGraph")
    print("=" * 60)

    # Task from command line or default
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = "Write a Python function that calculates prime numbers up to N"

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

    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("Error during execution")
        print("\nMake sure Ollama is running with an available model.")


if __name__ == "__main__":
    asyncio.run(main())
