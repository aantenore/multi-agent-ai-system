"""
Nodes (agents) for the LangGraph graph.

Each node represents a specialized agent with:
- Specific system prompt for the role
- Appropriate set of tools
- Decision logic

LangGraph models agents as nodes in a state graph,
where transitions depend on agent output.
"""

from typing import Annotated, TypedDict, Sequence, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models import BaseChatModel
from langgraph.graph import add_messages
from loguru import logger

from multi_agent.shared import create_llm
from multi_agent.tools import ALL_TOOLS


# Shared graph state
class AgentState(TypedDict):
    """
    Shared state between all graph nodes.

    Attributes:
        messages: Message history (managed automatically by add_messages)
        current_agent: Current agent processing
        task_complete: Flag for termination
        final_output: Aggregated final output
    """

    messages: Annotated[Sequence[BaseMessage], add_messages]
    current_agent: str
    task_complete: bool
    final_output: str


class AgentNode:
    """
    Agent node for LangGraph.

    Wraps an LLM with system prompt, tools. and execution logic.

    Example:
        >>> researcher = AgentNode(
        ...     name="researcher",
        ...     system_prompt="You are an expert researcher...",
        ...     tools=[web_search]
        ... )
        >>> state = researcher(current_state)
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        llm: BaseChatModel | None = None,
        tools: list | None = None,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.llm = llm or create_llm()
        self.tools = tools or []

        # Bind tools to LLM if present
        if self.tools:
            self.llm_with_tools = self.llm.bind_tools(self.tools)
        else:
            self.llm_with_tools = self.llm

    def __call__(self, state: AgentState) -> dict:
        """
        Execute the agent on current state.

        Args:
            state: Current graph state

        Returns:
            State updates
        """
        logger.info(f"[{self.name}] Processing...")

        # Prepare messages with system prompt
        messages = [SystemMessage(content=self.system_prompt)]
        messages.extend(state["messages"])

        # Invoke LLM
        response = self.llm_with_tools.invoke(messages)

        logger.info(f"[{self.name}] Response generated")

        return {
            "messages": [response],
            "current_agent": self.name,
        }


def create_agent_node(
    name: str,
    role: Literal["orchestrator", "researcher", "coder", "reviewer"],
    llm: BaseChatModel | None = None,
) -> AgentNode:
    """
    Factory to create pre-configured agent nodes.

    Args:
        name: Unique node name
        role: Agent role
        llm: LLM to use (default: from settings)

    Returns:
        Configured AgentNode
    """
    prompts = {
        "orchestrator": """You are the Team Orchestrator. Your role is:
1. Analyze the user's task
2. Decide which agent should work on it (researcher, coder, reviewer)
3. Coordinate the workflow
4. Aggregate final results

Always respond in this format:
NEXT_AGENT: [researcher|coder|reviewer|FINISH]
INSTRUCTION: [instructions for next agent or final result]""",
        "researcher": """You are an Expert Researcher. Your role is:
1. Search for relevant information
2. Analyze and synthesize data
3. Provide context and background

You have access to search tools. Always use tools when needed.
Respond with structured information and cite sources when possible.""",
        "coder": """You are a Senior Developer. Your role is:
1. Write clean, working code
2. Implement solutions based on requirements
3. Follow best practices

Always write complete, testable code.
Include explanatory comments.""",
        "reviewer": """You are an Expert Code Reviewer. Your role is:
1. Analyze the produced code
2. Identify bugs and issues
3. Suggest improvements

Be constructive and specific in feedback.
If the code is good, confirm it.""",
    }

    tools_map = {
        "orchestrator": [],
        "researcher": [
            t for t in ALL_TOOLS if t.name in ["web_search_mock", "read_file"]
        ],
        "coder": [
            t for t in ALL_TOOLS if t.name in ["write_file", "read_file", "calculate"]
        ],
        "reviewer": [t for t in ALL_TOOLS if t.name in ["read_file"]],
    }

    return AgentNode(
        name=name,
        system_prompt=prompts[role],
        llm=llm,
        tools=tools_map[role],
    )
