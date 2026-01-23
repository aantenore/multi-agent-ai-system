"""
Example 4: Multi-Agent Team with AutoGen.

Demonstrates AutoGen's conversational paradigm where
agents communicate like in a group chat.

Usage:
    python examples/04_autogen_team.py
    python examples/04_autogen_team.py "Create a class to manage inventory"
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loguru import logger

from multi_agent.autogen_agents import run_autogen_task


async def main():
    print("\n🔶 Multi-Agent Team with AutoGen")
    print("=" * 60)

    # Task from command line or default
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = "Create a Python class to manage a shopping list with add, remove, and list methods"

    print(f"\n📋 Task: {task}")
    print("-" * 60)

    print("\n🚀 Starting AutoGen team...")
    print("   Planner → plans the approach")
    print("   Coder → implements the solution")
    print("   Reviewer → validates and approves")
    print("-" * 60 + "\n")

    try:
        result = await run_autogen_task(task)

        print("\n" + "=" * 60)
        print("✅ COMPLETE CONVERSATION:")
        print("=" * 60)
        print(result)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("Error during execution")
        print("\nMake sure Ollama is running with an available model.")


if __name__ == "__main__":
    asyncio.run(main())
