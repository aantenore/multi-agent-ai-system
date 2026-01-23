"""
Base for the tool system.

Tools allow agents to interact with the environment:
- Execute calculations
- Read/write files
- Web searches
- Execute code

We use LangChain's @tool decorator for compatibility.
"""

from typing import Callable, Any
from langchain_core.tools import tool as langchain_tool, BaseTool

# Re-export for convenience
Tool = BaseTool
tool = langchain_tool


def create_tool_from_function(
    func: Callable,
    name: str | None = None,
    description: str | None = None,
) -> BaseTool:
    """
    Create a LangChain tool from a Python function.

    Args:
        func: Function to wrap
        name: Tool name (default: function name)
        description: Description (default: docstring)

    Returns:
        LangChain Tool

    Example:
        >>> def my_calculator(expression: str) -> str:
        ...     '''Calculate a mathematical expression.'''
        ...     return str(eval(expression))
        >>> tool = create_tool_from_function(my_calculator)
    """
    return langchain_tool(func)


def get_tool_schema(tool_instance: BaseTool) -> dict[str, Any]:
    """
    Extract JSON schema of a tool for documentation.

    Useful for debugging and understanding what the tool expects.
    """
    return {
        "name": tool_instance.name,
        "description": tool_instance.description,
        "parameters": (
            tool_instance.args_schema.model_json_schema()
            if tool_instance.args_schema
            else {}
        ),
    }
