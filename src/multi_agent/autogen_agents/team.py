"""
AutoGen team execution.

Manages task execution with the AutoGen multi-agent team.
"""

from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from loguru import logger

from multi_agent.autogen_agents.agents import create_autogen_team


async def run_autogen_task(task: str) -> str:
    """
    Execute a task with the AutoGen team.

    Args:
        task: Task description to complete

    Returns:
        Final conversation output

    Example:
        >>> result = await run_autogen_task("Create a Python class to manage a todo list")
        >>> print(result)
    """
    logger.info(f"Starting AutoGen task: {task[:50]}...")

    # Create team
    agents, team = create_autogen_team()

    # Execute the conversation
    result = await team.run(
        task=task,
        cancellation_token=CancellationToken(),
    )

    # Extract output
    messages = result.messages

    # Format output
    output_parts = []
    for msg in messages:
        if hasattr(msg, "source") and hasattr(msg, "content"):
            output_parts.append(f"**{msg.source}**: {msg.content}")

    final_output = "\n\n".join(output_parts)

    logger.info("AutoGen task completed")

    return final_output


def run_autogen_task_sync(task: str) -> str:
    """Synchronous version of run_autogen_task."""
    import asyncio

    return asyncio.run(run_autogen_task(task))


async def run_autogen_stream(task: str):
    """
    Execute task with message streaming.

    Yields:
        Messages as they are generated

    Example:
        >>> async for msg in run_autogen_stream("Write a function..."):
        ...     print(msg)
    """
    logger.info(f"Starting AutoGen streaming task: {task[:50]}...")

    agents, team = create_autogen_team()

    async for message in team.run_stream(
        task=task,
        cancellation_token=CancellationToken(),
    ):
        if hasattr(message, "source") and hasattr(message, "content"):
            yield f"**{message.source}**: {message.content}"
