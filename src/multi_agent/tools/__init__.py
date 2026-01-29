"""Tools package - Agent Skills and Capabilities."""

from multi_agent.tools.base import Tool, tool
from multi_agent.tools.common_tools import (
    # Core tools
    calculate,
    get_current_time,
    read_file,
    write_file,
    list_directory,
    web_search_mock,
    # New skills
    analyze_code,
    format_json,
    text_stats,
    convert_units,
    generate_uuid,
    encode_base64,
    decode_base64,
    # Collections and helpers
    ALL_TOOLS,
    get_tools_for_agent,
    list_available_skills,
)

__all__ = [
    # Base
    "Tool",
    "tool",
    # Core tools
    "calculate",
    "get_current_time",
    "read_file",
    "write_file",
    "list_directory",
    "web_search_mock",
    # New skills
    "analyze_code",
    "format_json",
    "text_stats",
    "convert_units",
    "generate_uuid",
    "encode_base64",
    "decode_base64",
    # Collections and helpers
    "ALL_TOOLS",
    "get_tools_for_agent",
    "list_available_skills",
]
