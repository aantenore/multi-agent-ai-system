"""
Example 4: Interactive Multi-Agent Team with AutoGen.

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


async def run_single_task(task: str):
    """Run a single task through the AutoGen team."""
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
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("Error during execution")
        print("\nMake sure your LLM provider is configured correctly.")
        return False


async def main():
    print("\n🔶 Interactive Multi-Agent Team with AutoGen")
    print("=" * 60)

    # Check if task provided via command line
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
        await run_single_task(task)
        return

    # Interactive mode
    print("Enter tasks for the AutoGen team to work on.")
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
