"""
AutoGen agent definitions.

AutoGen (Microsoft) uses a conversational paradigm where agents
communicate with each other like in a group chat.

Key differences with LangGraph:
- LangGraph: state graphs with explicit transitions
- AutoGen: multi-party conversations with automatic routing
"""

from typing import Any

from autogen_core.models import ModelFamily
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from loguru import logger

from multi_agent.shared.config import settings, LLMProvider


def get_autogen_model_client():
    """
    Create the model client for AutoGen.

    AutoGen uses a different interface than LangChain.
    Supports OpenAI-compatible APIs (including Ollama via endpoint).
    """
    if settings.llm_provider == LLMProvider.OLLAMA:
        # Ollama exposes an OpenAI-compatible endpoint
        # Determine capabilities based on model name
        is_thinking = "thinking" in settings.llm_model

        return OpenAIChatCompletionClient(
            model=settings.llm_model,
            base_url=f"{settings.ollama_host}/v1",
            api_key="ollama",  # Ollama doesn't require API key
            model_info={
                "vision": False,
                "function_calling": not is_thinking,  # Thinking models might struggle with tools or output thought traces
                "json_output": False,
                "family": ModelFamily.UNKNOWN,
            },
        )
    elif settings.llm_provider == LLMProvider.OPENAI:
        return OpenAIChatCompletionClient(
            model=settings.llm_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
    else:
        raise ValueError(f"Provider {settings.llm_provider} not supported in AutoGen")


def create_autogen_team() -> tuple[list[AssistantAgent], Any]:
    """
    Create a team of AutoGen agents.

    Returns:
        Tuple of (agent list, configured team)

    The team includes:
    - Planner: plans the approach
    - Coder: implements the code
    - Reviewer: validates the work
    """
    model_client = get_autogen_model_client()

    # Planner Agent
    planner = AssistantAgent(
        name="Planner",
        model_client=model_client,
        system_message="""You are an expert Project Planner.
Your role is:
1. Analyze task requirements
2. Create an implementation plan
3. Identify potential issues

Always respond with a structured plan in bullet points.
When the plan is ready, pass to the Coder.""",
    )

    # Coder Agent
    coder = AssistantAgent(
        name="Coder",
        model_client=model_client,
        system_message="""You are an expert Senior Developer.
Your role is:
1. Implement code according to the plan
2. Write clean, documented, testable code
3. Follow best practices

Always write complete, working code.
When done, ask the Reviewer to validate.""",
    )

    # Reviewer Agent
    reviewer = AssistantAgent(
        name="Reviewer",
        model_client=model_client,
        system_message="""You are a Senior Code Reviewer.
Your role is:
1. Analyze the produced code
2. Verify correctness and quality
3. Identify bugs and improvements

If you find issues, explain what to fix.
If everything is ok, write "APPROVED" and summarize the work done.
When finished, write TERMINATE to conclude.""",
    )

    agents = [planner, coder, reviewer]

    # Termination condition
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(15)

    # Create team with round-robin (each agent speaks in turn)
    team = RoundRobinGroupChat(
        participants=agents,
        termination_condition=termination,
    )

    logger.info("AutoGen team created: Planner, Coder, Reviewer")

    return agents, team
