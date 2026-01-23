"""
MCP (Model Context Protocol) integration.

MCP is an open protocol for connecting AI assistants to external
data sources and tools. This module provides:
- MCP server implementation for exposing tools
- MCP client for connecting to MCP servers

Learn more: https://modelcontextprotocol.io/
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable
from enum import Enum

from loguru import logger


class MCPMessageType(str, Enum):
    """MCP message types."""

    INITIALIZE = "initialize"
    INITIALIZED = "initialized"
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"


@dataclass
class MCPTool:
    """
    MCP Tool definition.

    Represents a tool that can be called through MCP.
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., Any] = field(repr=False)

    def to_dict(self) -> dict[str, Any]:
        """Convert to MCP tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }

    def call(self, **kwargs) -> Any:
        """Execute the tool."""
        return self.handler(**kwargs)


@dataclass
class MCPResource:
    """
    MCP Resource definition.

    Represents a data resource that can be read through MCP.
    """

    uri: str
    name: str
    description: str
    mime_type: str = "text/plain"
    reader: Callable[[], str] = field(repr=False, default=lambda: "")

    def to_dict(self) -> dict[str, Any]:
        """Convert to MCP resource format."""
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type,
        }

    def read(self) -> str:
        """Read the resource content."""
        return self.reader()


class MCPServer:
    """
    MCP Server implementation.

    Exposes tools and resources via the MCP protocol.
    Can be used with stdio transport or HTTP.

    Example:
        >>> server = MCPServer(name="my-server")
        >>>
        >>> @server.tool(
        ...     name="calculate",
        ...     description="Calculate math expression",
        ...     input_schema={"type": "object", "properties": {"expr": {"type": "string"}}}
        ... )
        >>> def calculate(expr: str) -> str:
        ...     return str(eval(expr))
        >>>
        >>> server.run_stdio()
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: dict[str, MCPTool] = {}
        self.resources: dict[str, MCPResource] = {}
        self._initialized = False

    def tool(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
    ) -> Callable:
        """
        Decorator to register a tool.

        Args:
            name: Tool name
            description: Tool description
            input_schema: JSON Schema for input parameters
        """

        def decorator(func: Callable) -> Callable:
            self.tools[name] = MCPTool(
                name=name,
                description=description,
                input_schema=input_schema,
                handler=func,
            )
            logger.debug(f"Registered MCP tool: {name}")
            return func

        return decorator

    def add_resource(
        self,
        uri: str,
        name: str,
        description: str,
        reader: Callable[[], str],
        mime_type: str = "text/plain",
    ) -> None:
        """Add a resource to the server."""
        self.resources[uri] = MCPResource(
            uri=uri,
            name=name,
            description=description,
            mime_type=mime_type,
            reader=reader,
        )
        logger.debug(f"Registered MCP resource: {uri}")

    def handle_message(self, message: dict[str, Any]) -> dict[str, Any]:
        """
        Handle incoming MCP message.

        Args:
            message: MCP JSON-RPC message

        Returns:
            Response message
        """
        method = message.get("method", "")
        msg_id = message.get("id")
        params = message.get("params", {})

        try:
            if method == MCPMessageType.INITIALIZE:
                return self._handle_initialize(msg_id, params)
            elif method == MCPMessageType.TOOLS_LIST:
                return self._handle_tools_list(msg_id)
            elif method == MCPMessageType.TOOLS_CALL:
                return self._handle_tools_call(msg_id, params)
            elif method == MCPMessageType.RESOURCES_LIST:
                return self._handle_resources_list(msg_id)
            elif method == MCPMessageType.RESOURCES_READ:
                return self._handle_resources_read(msg_id, params)
            else:
                return self._error_response(
                    msg_id, -32601, f"Method not found: {method}"
                )
        except Exception as e:
            logger.exception(f"Error handling MCP message: {e}")
            return self._error_response(msg_id, -32603, str(e))

    def _handle_initialize(self, msg_id: Any, params: dict) -> dict:
        """Handle initialize request."""
        self._initialized = True
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": self.name,
                    "version": self.version,
                },
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                },
            },
        }

    def _handle_tools_list(self, msg_id: Any) -> dict:
        """Handle tools/list request."""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": [t.to_dict() for t in self.tools.values()],
            },
        }

    def _handle_tools_call(self, msg_id: Any, params: dict) -> dict:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in self.tools:
            return self._error_response(msg_id, -32602, f"Unknown tool: {tool_name}")

        result = self.tools[tool_name].call(**arguments)

        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [{"type": "text", "text": str(result)}],
            },
        }

    def _handle_resources_list(self, msg_id: Any) -> dict:
        """Handle resources/list request."""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "resources": [r.to_dict() for r in self.resources.values()],
            },
        }

    def _handle_resources_read(self, msg_id: Any, params: dict) -> dict:
        """Handle resources/read request."""
        uri = params.get("uri")

        if uri not in self.resources:
            return self._error_response(msg_id, -32602, f"Unknown resource: {uri}")

        content = self.resources[uri].read()

        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": self.resources[uri].mime_type,
                        "text": content,
                    }
                ],
            },
        }

    def _error_response(self, msg_id: Any, code: int, message: str) -> dict:
        """Create error response."""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": code, "message": message},
        }

    def run_stdio(self) -> None:
        """
        Run server with stdio transport.

        Reads JSON-RPC messages from stdin, writes responses to stdout.
        """
        import sys

        logger.info(f"Starting MCP server '{self.name}' on stdio")

        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                message = json.loads(line)
                response = self.handle_message(message)

                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
            except KeyboardInterrupt:
                break

        logger.info("MCP server stopped")


class MCPClient:
    """
    MCP Client for connecting to MCP servers.

    Simple client to interact with MCP servers via stdio.

    Example:
        >>> client = MCPClient()
        >>> tools = client.list_tools()
        >>> result = client.call_tool("calculate", expr="2+2")
    """

    def __init__(self, server_command: list[str] | None = None):
        """
        Initialize MCP client.

        Args:
            server_command: Command to start MCP server subprocess
        """
        self.server_command = server_command
        self._process = None
        self._msg_id = 0

    def _next_id(self) -> int:
        """Get next message ID."""
        self._msg_id += 1
        return self._msg_id

    def connect(self) -> dict[str, Any]:
        """
        Connect to MCP server and initialize.

        Returns:
            Server capabilities
        """
        import subprocess

        if self.server_command:
            self._process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
            )

        # Send initialize
        response = self._send(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "clientInfo": {"name": "multi-agent-client", "version": "1.0.0"},
                },
            }
        )

        return response.get("result", {})

    def _send(self, message: dict[str, Any]) -> dict[str, Any]:
        """Send message and receive response."""
        if not self._process:
            raise RuntimeError("Not connected to MCP server")

        self._process.stdin.write(json.dumps(message) + "\n")
        self._process.stdin.flush()

        response_line = self._process.stdout.readline()
        return json.loads(response_line)

    def list_tools(self) -> list[dict[str, Any]]:
        """List available tools."""
        response = self._send(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/list",
                "params": {},
            }
        )
        return response.get("result", {}).get("tools", [])

    def call_tool(self, name: str, **arguments) -> str:
        """Call a tool."""
        response = self._send(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }
        )
        content = response.get("result", {}).get("content", [])
        if content:
            return content[0].get("text", "")
        return ""

    def list_resources(self) -> list[dict[str, Any]]:
        """List available resources."""
        response = self._send(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "resources/list",
                "params": {},
            }
        )
        return response.get("result", {}).get("resources", [])

    def read_resource(self, uri: str) -> str:
        """Read a resource."""
        response = self._send(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "resources/read",
                "params": {"uri": uri},
            }
        )
        contents = response.get("result", {}).get("contents", [])
        if contents:
            return contents[0].get("text", "")
        return ""

    def close(self) -> None:
        """Close connection."""
        if self._process:
            self._process.terminate()
            self._process = None
