"""
Example 7: MCP (Model Context Protocol)

Demonstrates how to create an MCP server that exposes tools
and resources to AI assistants.

MCP enables standardized tool exposure across different AI systems.

Usage:
    python examples/07_mcp_example.py
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from multi_agent.shared.mcp import MCPServer, MCPTool, MCPResource


def demo_mcp_server():
    """Demonstrate MCP server setup."""
    print("\n" + "=" * 60)
    print("🔌 MCP (Model Context Protocol) Demo")
    print("=" * 60)

    # Create MCP server
    server = MCPServer(name="demo-mcp-server", version="1.0.0")

    # Register tools using decorator
    @server.tool(
        name="calculate",
        description="Calculate a mathematical expression",
        input_schema={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate",
                }
            },
            "required": ["expression"],
        },
    )
    def calculate(expression: str) -> str:
        try:
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {e}"

    @server.tool(
        name="get_time",
        description="Get current date and time",
        input_schema={"type": "object", "properties": {}},
    )
    def get_time() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @server.tool(
        name="greet",
        description="Generate a greeting message",
        input_schema={
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Name to greet"}},
            "required": ["name"],
        },
    )
    def greet(name: str) -> str:
        return f"Hello, {name}! Welcome to the MCP demo."

    # Add a resource
    server.add_resource(
        uri="file://config.json",
        name="Configuration",
        description="Server configuration",
        reader=lambda: '{"version": "1.0", "mode": "demo"}',
        mime_type="application/json",
    )

    print("\n📋 Registered Tools:")
    for name, tool in server.tools.items():
        print(f"   • {name}: {tool.description}")

    print("\n📁 Registered Resources:")
    for uri, resource in server.resources.items():
        print(f"   • {uri}: {resource.description}")

    # Simulate MCP messages
    print("\n\n🔄 Simulating MCP Protocol Messages...")

    # 1. Initialize
    print("\n1️⃣ Initialize Request:")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "test-client", "version": "1.0.0"},
        },
    }
    response = server.handle_message(init_request)
    print(f"   Server: {response['result']['serverInfo']['name']}")
    print(f"   Capabilities: {list(response['result']['capabilities'].keys())}")

    # 2. List tools
    print("\n2️⃣ List Tools Request:")
    list_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    response = server.handle_message(list_request)
    tools = response["result"]["tools"]
    print(f"   Found {len(tools)} tools:")
    for t in tools:
        print(f"      - {t['name']}")

    # 3. Call a tool
    print("\n3️⃣ Call Tool Request (calculate):")
    call_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "calculate", "arguments": {"expression": "2 ** 10"}},
    }
    response = server.handle_message(call_request)
    result = response["result"]["content"][0]["text"]
    print(f"   Expression: 2 ** 10")
    print(f"   Result: {result}")

    # 4. Call another tool
    print("\n4️⃣ Call Tool Request (greet):")
    call_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {"name": "greet", "arguments": {"name": "Developer"}},
    }
    response = server.handle_message(call_request)
    result = response["result"]["content"][0]["text"]
    print(f"   Result: {result}")

    # 5. List resources
    print("\n5️⃣ List Resources Request:")
    list_request = {"jsonrpc": "2.0", "id": 5, "method": "resources/list", "params": {}}
    response = server.handle_message(list_request)
    resources = response["result"]["resources"]
    print(f"   Found {len(resources)} resources:")
    for r in resources:
        print(f"      - {r['uri']}: {r['name']}")

    # 6. Read resource
    print("\n6️⃣ Read Resource Request:")
    read_request = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "resources/read",
        "params": {"uri": "file://config.json"},
    }
    response = server.handle_message(read_request)
    content = response["result"]["contents"][0]["text"]
    print(f"   Content: {content}")

    print("\n" + "=" * 60)
    print("✅ MCP Demo completed!")
    print("=" * 60)
    print("\n💡 To run a real MCP server, use:")
    print("   server.run_stdio()")
    print("   and connect with an MCP-compatible client (e.g., Claude Desktop)")


if __name__ == "__main__":
    demo_mcp_server()
