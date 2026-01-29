"""
Example 7: Interactive MCP (Model Context Protocol)

Demonstrates how to create an MCP server that exposes tools
and resources to AI assistants, with an interactive testing interface.

MCP enables standardized tool exposure across different AI systems.

Usage:
    python examples/07_mcp_example.py
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from multi_agent.shared.mcp import MCPServer, MCPTool, MCPResource


def create_mcp_server():
    """Create and configure the MCP server with tools."""
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
            allowed = set("0123456789+-*/.() ")
            if not all(c in allowed for c in expression):
                return "Error: Only numbers and operators +-*/ allowed"
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

    @server.tool(
        name="reverse_text",
        description="Reverse the given text",
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to reverse"}
            },
            "required": ["text"],
        },
    )
    def reverse_text(text: str) -> str:
        return text[::-1]

    # Add a resource
    server.add_resource(
        uri="file://config.json",
        name="Configuration",
        description="Server configuration",
        reader=lambda: '{"version": "1.0", "mode": "demo", "provider": "gemini"}',
        mime_type="application/json",
    )

    return server


def demo_mcp_protocol(server):
    """Demonstrate MCP protocol messages."""
    print("\n📋 Registered Tools:")
    for name, tool in server.tools.items():
        print(f"   • {name}: {tool.description}")

    print("\n📁 Registered Resources:")
    for uri, resource in server.resources.items():
        print(f"   • {uri}: {resource.description}")

    print("\n\n🔄 Simulating MCP Protocol Messages...")

    # Initialize
    print("\n1️⃣ Initialize:")
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


def interactive_mcp_testing(server):
    """Interactive MCP tool testing interface."""
    print("\n\n💬 Interactive MCP Tool Testing")
    print("-" * 50)
    print("Commands:")
    print("  list              - List all available tools")
    print("  call <tool> <arg> - Call a tool (e.g., 'call calculate 2+2')")
    print("  resource <uri>    - Read a resource")
    print("  exit/quit         - Exit the demo\n")

    while True:
        try:
            user_input = input("\n🔌 MCP> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("\n👋 Goodbye!")
            break

        parts = user_input.split(maxsplit=2)
        cmd = parts[0].lower()

        if cmd == "list":
            print("\n📋 Available Tools:")
            for name, tool in server.tools.items():
                print(f"   • {name}: {tool.description}")

        elif cmd == "call" and len(parts) >= 2:
            tool_name = parts[1]
            arg_value = parts[2] if len(parts) > 2 else ""

            if tool_name not in server.tools:
                print(f"❌ Unknown tool: {tool_name}")
                continue

            # Build arguments based on tool schema
            tool = server.tools[tool_name]
            schema = tool.input_schema
            props = schema.get("properties", {})

            if props:
                first_param = list(props.keys())[0]
                arguments = {first_param: arg_value}
            else:
                arguments = {}

            call_request = {
                "jsonrpc": "2.0",
                "id": 99,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
            }
            print(f"\n   📤 Sending JSON-RPC Request:")
            print(f"      Method: tools/call")
            print(f"      Params: {call_request['params']}")

            response = server.handle_message(call_request)

            print(f"\n   📥 Received JSON-RPC Response:")
            if "error" in response:
                print(f"      Error: {response['error']}")
            else:
                print(f"      Result: {response['result']}")
            result = response["result"]["content"][0]["text"]
            print(f"✅ Result: {result}")

        elif cmd == "resource" and len(parts) >= 2:
            uri = parts[1]
            read_request = {
                "jsonrpc": "2.0",
                "id": 99,
                "method": "resources/read",
                "params": {"uri": uri},
            }
            response = server.handle_message(read_request)
            if "error" in response:
                print(f"❌ Error: {response['error']['message']}")
            else:
                content = response["result"]["contents"][0]["text"]
                print(f"📄 Content: {content}")

        else:
            print("❓ Unknown command. Try 'list', 'call <tool> <arg>', or 'exit'")


def main():
    print("\n" + "=" * 60)
    print("🔌 Interactive MCP (Model Context Protocol) Demo")
    print("=" * 60)

    server = create_mcp_server()
    demo_mcp_protocol(server)
    interactive_mcp_testing(server)

    print("\n" + "=" * 60)
    print("✅ MCP Demo completed!")
    print("=" * 60)
    print("\n💡 To run a real MCP server, use:")
    print("   server.run_stdio()")
    print("   and connect with an MCP-compatible client (e.g., Claude Desktop)")


if __name__ == "__main__":
    main()
