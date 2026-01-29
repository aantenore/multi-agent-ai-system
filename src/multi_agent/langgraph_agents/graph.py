"""
Multi-agent graph with LangGraph.

LangGraph allows defining complex workflows as graphs,
where nodes are agents and edges are state-based transitions.

This module implements a team of collaborating agents:
1. Orchestrator analyzes the task and decides who should work on it
2. Researcher searches for information
3. Coder implements solutions
4. Reviewer validates the work
"""

import re
from typing import Literal

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from loguru import logger

from multi_agent.langgraph_agents.nodes import AgentState, create_agent_node
from multi_agent.shared import create_llm


def should_continue(
    state: AgentState,
) -> Literal["researcher", "coder", "reviewer", "end"]:
    """
    Router: decide next step based on orchestrator output.

    Analyzes the last message to extract NEXT_AGENT.
    """
    messages = state["messages"]
    if not messages:
        return "end"

    last_message = messages[-1]
    content = (
        last_message.content if hasattr(last_message, "content") else str(last_message)
    )

    # Look for pattern NEXT_AGENT: xxx
    match = re.search(r"NEXT_AGENT:\s*(\w+)", content, re.IGNORECASE)
    if match:
        next_agent = match.group(1).lower()
        if next_agent == "finish":
            print(f"   [Router] Decision: FINISH (Task completed)")
            return "end"
        if next_agent in ["researcher", "coder", "reviewer"]:
            print(f"   [Router] Decision: Transfer to {next_agent.upper()}")
            return next_agent

    # If orchestrator doesn't specify, end
    print(f"   [Router] No next agent specified. Ending.")
    return "end"


def create_multi_agent_graph(llm=None):
    """
    Create the multi-agent graph.

    Structure:
    ```
    START -> orchestrator -> [researcher|coder|reviewer] -> orchestrator -> ... -> END
    ```

    Args:
        llm: LLM to use for all agents (default: from settings)

    Returns:
        CompiledGraph ready to use
    """
    llm = llm or create_llm()

    # Create agents
    orchestrator = create_agent_node("orchestrator", "orchestrator", llm)
    researcher = create_agent_node("researcher", "researcher", llm)
    coder = create_agent_node("coder", "coder", llm)
    reviewer = create_agent_node("reviewer", "reviewer", llm)

    # Build the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("orchestrator", orchestrator)
    workflow.add_node("researcher", researcher)
    workflow.add_node("coder", coder)
    workflow.add_node("reviewer", reviewer)

    # Entry point
    workflow.set_entry_point("orchestrator")

    # Conditional edges from orchestrator
    workflow.add_conditional_edges(
        "orchestrator",
        should_continue,
        {
            "researcher": "researcher",
            "coder": "coder",
            "reviewer": "reviewer",
            "end": END,
        },
    )

    # Agents always return to orchestrator
    workflow.add_edge("researcher", "orchestrator")
    workflow.add_edge("coder", "orchestrator")
    workflow.add_edge("reviewer", "orchestrator")

    # Compile
    graph = workflow.compile()
    logger.info("Multi-agent graph created successfully")

    return graph


async def run_task(task: str, llm=None, max_iterations: int = 10) -> str:
    """
    Execute a task with the multi-agent team.

    Args:
        task: Task description
        llm: LLM to use (default: from settings)
        max_iterations: Max iterations to avoid infinite loops

    Returns:
        Aggregated final output

    Example:
        >>> result = await run_task("Write a Python function that calculates factorial")
        >>> print(result)
    """
    graph = create_multi_agent_graph(llm)

    # Initial state
    initial_state: AgentState = {
        "messages": [HumanMessage(content=task)],
        "current_agent": "",
        "task_complete": False,
        "final_output": "",
    }

    logger.info(f"Starting task: {task[:50]}...")

    # Execute the graph
    config = {"recursion_limit": max_iterations}
    final_state = await graph.ainvoke(initial_state, config)

    # Extract final output
    if final_state["messages"]:
        last_message = final_state["messages"][-1]
        output = (
            last_message.content
            if hasattr(last_message, "content")
            else str(last_message)
        )
    else:
        output = "No output generated"

    logger.info("Task completed")
    return output


def run_task_sync(task: str, llm=None, max_iterations: int = 10) -> str:
    """Synchronous version of run_task."""
    import asyncio

    return asyncio.run(run_task(task, llm, max_iterations))
