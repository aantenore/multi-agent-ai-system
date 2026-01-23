"""Tests for tools."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from multi_agent.tools import (
    calculate,
    get_current_time,
    web_search_mock,
    get_tools_for_agent,
    ALL_TOOLS,
)


class TestCalculateTool:
    """Test calculate tool."""

    def test_addition(self):
        """Test addition."""
        result = calculate.invoke({"expression": "2 + 2"})
        assert "4" in result

    def test_complex_expression(self):
        """Test complex expression."""
        result = calculate.invoke({"expression": "10 * 5 + 3"})
        assert "53" in result

    def test_invalid_expression(self):
        """Test invalid expression."""
        result = calculate.invoke({"expression": "import os"})
        assert "Error" in result


class TestTimeTool:
    """Test time tool."""

    def test_get_time(self):
        """Test getting time."""
        result = get_current_time.invoke({"timezone": "local"})
        assert "date" in result.lower() or "time" in result.lower()


class TestWebSearchMock:
    """Test search tool."""

    def test_search_python(self):
        """Test Python search."""
        result = web_search_mock.invoke({"query": "python programming"})
        assert "Python" in result

    def test_search_unknown(self):
        """Test unknown search."""
        result = web_search_mock.invoke({"query": "xyz123abc"})
        assert "No results" in result or "mock" in result.lower()


class TestToolsRegistry:
    """Test tools registry."""

    def test_all_tools_exist(self):
        """Test that ALL_TOOLS is not empty."""
        assert len(ALL_TOOLS) > 0

    def test_get_tools_all(self):
        """Test get all tools."""
        tools = get_tools_for_agent(None)
        assert len(tools) == len(ALL_TOOLS)

    def test_get_tools_filtered(self):
        """Test get filtered tools."""
        tools = get_tools_for_agent(["calculate"])
        assert len(tools) == 1
        assert tools[0].name == "calculate"
